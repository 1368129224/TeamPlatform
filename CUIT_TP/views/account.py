from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from CUIT_TP.forms.account import RegisterForm, LoginForm
from CUIT_TP.models import User
from .. import db


bp = Blueprint('account', __name__)
@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            if User.query.filter(User.email==email).first():
                flash('此邮箱已注册。', 'error')
                return render_template('account/register.html', form=form)
            new_user = User(username=username, email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home.index'))
        else:
            return render_template('account/register.html', form=form)
    else:
        return render_template('account/register.html', form=form)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            stu_num_or_email = form.stu_num_or_email.data
            password = form.password.data
            user = User.query.filter(User.stu_num==stu_num_or_email)
            if not user:
                user = User.query.filter(User.email==stu_num_or_email)
            if user:
                if check_password_hash(user.password, password):
                    return redirect(url_for('home.index'))
            else:
                flash('登录失败。', 'error')
