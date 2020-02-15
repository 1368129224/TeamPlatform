from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from werkzeug.urls import url_parse
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.account import RegisterForm, LoginForm
from CUIT_TP.models import User
from .. import db

bp = Blueprint('account', __name__)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        stu_num = form.stu_num.data
        email = form.email.data
        password = form.password.data
        github = form.github_link.data
        if User.query.filter(User.email == email).first():
            flash('此邮箱已注册。', 'error')
            return render_template('account/register.html', form=form)
        new_user = User(username=username, stu_num=stu_num, email=email, github_link=github, password=generate_password_hash(password))
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
def logout():
    logout_user()
    return redirect(url_for('account.login'))
