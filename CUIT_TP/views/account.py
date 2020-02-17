from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from werkzeug.urls import url_parse
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.account import RegisterForm, LoginForm, ForgetPasswordForm, ResetPasswordForm, ProfileForm
from CUIT_TP.models import User, UserProfile
from CUIT_TP.utils import send_email
from CUIT_TP import db, app

bp = Blueprint('account', __name__)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter(User.email == form.email.data).first():
            flash('此邮箱已注册。', 'error')
            return render_template('account/register.html', form=form)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            stu_num=form.stu_num.data
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home.index'))
    else:
        return render_template('account/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
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
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home.index')
            return redirect(next_page)
        else:
            # 登录失败
            flash('登录失败。', 'error')
            return redirect(url_for('account.login'))
    else:
        return render_template('account/login.html', form=form)


@bp.route('/logout', methods=('GET', 'POST'))
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))


@bp.route('/forget_password', methods=('GET', 'POST'))
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


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
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

@bp.route('/<stu_num>/profile')
@login_required
def profile(stu_num):
    user = User.query.filter(User.stu_num==stu_num).first()
    if not user:
        abort(404)
    if not user.profile:
        profile = UserProfile(
            github='',
            college='',
            grade=0,
            _class='',
        )
        profile.user = user
        db.session.add(profile)
        db.session.commit()
    return render_template('account/profile.html', user=user, profile=user.profile)

@bp.route('/<stu_num>/change_profile', methods=['GET', 'POST'])
@login_required
def change_profile(stu_num):
    user = User.query.filter(User.stu_num == stu_num).first()
    form = ProfileForm(
        github=user.profile.github,
        college=user.profile.college,
        grade=user.profile.grade,
        c_lass=user.profile._class
    )
    if request.method == 'POST':
        form = ProfileForm()
        if form.validate_on_submit():
            user.profile.github = form.github.data
            user.profile.college = form.college.data
            user.profile.grade = form.grade.data
            user.profile._class = form.c_lass.data
            db.session.commit()
    return render_template('account/change_profile.html', user=user, form=form)
