from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.account import (
    RegisterForm, LoginForm, ForgetPasswordForm,
    ResetPasswordForm, ProfileForm, ChangePasswordForm,
    AdminRegisterForm, AdminProfileForm, ApplyAssetForm)
from CUIT_TP.models import User, UserProfile, UserPermission, Asset
from CUIT_TP.utils import send_email
from CUIT_TP import db, app, login

bp = Blueprint('account', __name__)


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
        new_user_permission = UserPermission(
            manage_lab_student_profile=True,
            manage_lab_task=True,
            change_set=True,
            verify_asset=True,
            change_lab_info=True,
            publish_lab_activity=True,
            manage_lab_teams=True,
            change_team_info=True,
            publish_team_activity=True,
        )
        new_user.permission = new_user_permission
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
        new_user_permission = UserPermission()
        new_user.permission = new_user_permission
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('account.login'))
    else:
        return render_template('account/register.html', form=form)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# 登录
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = LoginForm()
    if form.validate_on_submit():
        # 使用学号或邮箱登录
        user = User.query.filter(User.stu_num == form.stu_num_or_email.data).first()
        if not user:
            user = User.query.filter(User.email == form.stu_num_or_email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            # 登录成功
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for(request.args.get('next', 'home.index')))
        else:
            # 登录失败
            flash('登录失败。', 'error')
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
@bp.route('/change_password/', methods=('GET', 'POST'))
@login_required
def change_password():
    form = ChangePasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if check_password_hash(current_user.password, form.old_password.data):
                current_user.password = generate_password_hash(form.password.data)
                db.session.commit()
                return redirect((url_for('account.profile', stu_num=current_user.stu_num)))
            else:
                flash('密码错误', 'error')
                return redirect(url_for('account.change_password'))
    else:
        return render_template('account/change_password.html', form=form)


#忘记密码
@bp.route('/forget_password/', methods=('GET', 'POST'))
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email_or_stu_num.data).first()
        if not user:
            user = User.query.filter(User.stu_num == form.email_or_stu_num.data).first()
        if user:
            send_reset_password_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('account.login'))
    return render_template('account/forget_password.html', form=form)


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
    return render_template('account/manage.html')


# 个人信息
@bp.route('/<int:stu_num>/profile/')
@login_required
def profile(stu_num):
    user = User.query.filter(User.stu_num==stu_num).first()
    if not user:
        abort(404)
    if not user.profile:
        profile = UserProfile(
            phone='00000000000',
            college='',
            grade=0,
            _class='',
        )
        profile.user = user
        db.session.add(profile)
        db.session.commit()
    return render_template('account/profile.html', user=user, profile=user.profile)


# 修改个人信息
@bp.route('/change_profile/', methods=['GET', 'POST'])
@login_required
def change_profile():
    if current_user.role == 'admin':
        form = AdminProfileForm(
            QQ=current_user.profile.QQ,
            wechat=current_user.profile.wechat,
            phone=current_user.profile.phone
        )
    else:
        form = ProfileForm(
            QQ=current_user.profile.QQ,
            wechat=current_user.profile.wechat,
            phone=current_user.profile.phone,
            college=current_user.profile.college,
            grade=current_user.profile.grade,
            c_lass=current_user.profile._class
        )
    if request.method == 'POST':
        if current_user.role == 'admin':
            form = AdminProfileForm()
        else:
            form = ProfileForm()
        if form.validate_on_submit():
            if current_user.role == 'admin':
                current_user.profile.QQ = form.QQ.data
                current_user.profile.wechat = form.wechat.data
                current_user.profile.phone = form.phone.data
                db.session.commit()
            else:
                current_user.profile.QQ = form.QQ.data
                current_user.profile.wechat = form.wechat.data
                current_user.profile.phone = form.phone.data
                current_user.profile.college = form.college.data
                current_user.profile.grade = form.grade.data
                current_user.profile._class = form.c_lass.data
                db.session.commit()
            return redirect(url_for('account.profile', stu_num=current_user.stu_num))
        else:
            return render_template('account/change_profile.html', user=current_user, form=form)
    return render_template('account/change_profile.html', user=current_user, form=form)

# 申请资产
@bp.route('/apply_asset/', methods=('GET', 'POST'))
@login_required
def apply_asset():
    form = ApplyAssetForm()
    if request.method == 'POST':
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
            return redirect(url_for('home.index'))
        else:
            return render_template('account/apply_asset.html', form=form)
    else:
        return render_template('account/apply_asset.html', form=form)
