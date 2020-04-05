from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.account import (
    RegisterForm, LoginForm, ForgetPasswordForm,
    ResetPasswordForm, ProfileForm, ChangePasswordForm,
    AdminRegisterForm, ApplyAssetForm, ForceResetPasswordForm,
    AdminProfileForm)
from CUIT_TP.models import User, UserProfile, Asset
from CUIT_TP.utils import send_email
from CUIT_TP import db, app, login

bp = Blueprint('account', __name__)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# 设置管理员账号
@bp.route('/register_admin/', methods=('GET', 'POST'))
def register_admin():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    if User.query.filter(User.role=='admin').first():
        return redirect(url_for('home.index'))
    form = AdminRegisterForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            stu_num='0000000000',
            password=generate_password_hash(form.password.data),
            role='admin',
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('account.login'))
    else:
        return render_template('account/first_run.html', form=form)

# 注册
@bp.route('/register/', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter(User.email == form.email.data).first():
            flash('此邮箱已注册。', 'error')
            return render_template('account/register.html', form=form)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            stu_num=form.stu_num.data,
        )
        profile = UserProfile(
            phone='0',
            college='',
            grade=0,
            _class='',
        )
        profile.user = new_user
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('account.login'))
    else:
        return render_template('account/register.html', form=form)

# 登录
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account.manage'))
    form = LoginForm()
    if form.validate_on_submit():
        # 使用学号或邮箱登录
        user = User.query.filter(User.stu_num == form.stu_num_or_email.data).first()
        if not user:
            user = User.query.filter(User.email == form.stu_num_or_email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # 登录成功
            login_user(user, remember=form.remember_me.data)
            # TODO next安全检查
            return redirect(request.args.get('next') or url_for('account.manage'))
        else:
            # 登录失败
            flash('登录失败。')
            return redirect(url_for('account.login'))
    else:
        return render_template('account/login.html', form=form)

# 登出
@bp.route('/logout/', methods=('GET', 'POST'))
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))

# 修改密码
@bp.route('/change_password/<int:stu_num>', methods=('GET', 'POST'))
@login_required
def change_password(stu_num):
    if current_user.stu_num == stu_num or stu_num == 0:
        # 主动修改密码
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if check_password_hash(current_user.password, form.old_password.data):
                current_user.password = generate_password_hash(form.password.data)
                db.session.commit()
                return redirect((url_for('account.profile', stu_num=stu_num)))
            else:
                return redirect(url_for('account.change_password', stu_num=stu_num))
        else:
            return render_template('account/change_password.html', form=form, user=current_user)
    elif current_user.role == 'admin':
        form = ForceResetPasswordForm()
        user = User.query.filter(User.stu_num==stu_num).first_or_404()
        if form.validate_on_submit():
            user.password = generate_password_hash(form.password.data)
            db.session.commit()
            return redirect(url_for('account.profile', stu_num=user.stu_num, user=user))
        else:
            return render_template('account/change_password.html', form=form, user=user)

# 忘记密码
@bp.route('/forget_password/', methods=('GET', 'POST'))
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        # 使用学号或邮箱重置密码
        user = User.query.filter(User.email == form.email_or_stu_num.data).first()
        if not user:
            user = User.query.filter(User.stu_num == form.email_or_stu_num.data).first()
        if user:
            send_reset_password_email(user)
        return redirect(url_for('account.login'))
    return render_template('account/forget_password.html', form=form)

# 发送重置密码邮件
def send_reset_password_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password',
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

# 重置密码
@bp.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        return redirect(url_for('account.login'))
    return render_template('account/reset_password.html', form=form)

# 管理界面
@bp.route('/manage/')
@login_required
def manage():
    if current_user.role == 'admin':
        return render_template('account/manage/admin_manage.html')
    elif current_user.role == 'monitor':
        return render_template('account/manage/monitor_manage.html')
    else:
        return render_template('account/manage/manage.html')

# Dashboard
@bp.route('/dashboard/')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('account/dashboard/admin_dashboard.html')
    elif current_user.role == 'monitor':
        return render_template('account/dashboard/monitor_dashboard.html')
    else:
        return render_template('account/dashboard/dashboard.html')

# 个人信息
@bp.route('/profile/<int:stu_num>/')
@login_required
def profile(stu_num):
    user = User.query.filter(User.stu_num==stu_num).first_or_404()
    if not user.profile:
        profile = UserProfile(
            phone='0',
            college='',
            grade=0,
            _class='',
        )
        profile.user = user
        db.session.add(profile)
        db.session.commit()
    return render_template('account/profile.html', user=user)

# 修改管理员信息
@bp.route('/change_admin_profile/', methods=['GET', 'POST'])
@login_required
def change_admin_profile():
    if current_user.role == 'admin':
        form = AdminProfileForm(
            QQ=current_user.profile.QQ,
            wechat=current_user.profile.wechat,
            phone=current_user.profile.phone,
        )
        if request.method == 'POST':
            form = AdminProfileForm()
            if form.validate_on_submit():
                current_user.profile.QQ = form.QQ.data
                current_user.profile.wechat = form.wechat.data
                current_user.profile.phone = form.phone.data
                db.session.commit()
                return redirect(url_for('account.profile', stu_num=current_user.stu_num))
            else:
                return render_template('account/change_profile.html', user=current_user, form=form)
        return render_template('account/change_profile.html', user=current_user, form=form)
    else:
        abort(403)

# 修改个人信息
@bp.route('/change_profile/<int:stu_num>', methods=['GET', 'POST'])
@login_required
def change_profile(stu_num):
    if int(current_user.stu_num) == stu_num or (current_user.role == 'admin' and stu_num != '0000000000') or (current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_student_profile):
        # 学生修改自己的信息/管理员修改学生信息
        user = User.query.filter(User.stu_num==stu_num).first_or_404()
        form = ProfileForm(
            QQ=user.profile.QQ,
            wechat=user.profile.wechat,
            phone=user.profile.phone,
            college=user.profile.college,
            grade=user.profile.grade,
            c_lass=user.profile._class
        )
        if request.method == 'POST':
            form = ProfileForm()
            if form.validate_on_submit():
                user.profile.QQ = form.QQ.data
                user.profile.wechat = form.wechat.data
                user.profile.phone = form.phone.data
                user.profile.college = form.college.data
                user.profile.grade = form.grade.data
                user.profile._class = form.c_lass.data
                db.session.commit()
                return redirect(url_for('account.profile', stu_num=user.stu_num))
            else:
                return render_template('account/change_profile.html', user=user, form=form)
        return render_template('account/change_profile.html', user=user, form=form)
    else:
        abort(403)

# 资产展示
@bp.route('/assets/')
@login_required
def assets():
    assets = Asset.query.all()
    return render_template('account/assets.html', assets=assets)

# 申请资产
@bp.route('/apply_asset/', methods=('GET', 'POST'))
@login_required
def apply_asset():
    form = ApplyAssetForm()
    if form.validate_on_submit():
        new_asset = Asset(
            user=current_user,
            asset_name=form.asset_name.data,
            desc=form.desc.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            status='0'
        )
        db.session.add(new_asset)
        db.session.commit()
        return redirect(url_for('account.assets'))
    else:
        return render_template('account/apply_asset.html', form=form)
