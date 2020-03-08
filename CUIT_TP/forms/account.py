from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateTimeField
from wtforms.widgets import html_params
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from CUIT_TP.models import User


class AdminRegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=48)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=16)])
    stu_num = StringField('Stu_num', validators=[DataRequired(), Length(min=10, max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=48)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('此用户名已注册。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('此邮箱已注册。')

    def validate_stu_num(self, stu_num):
        user = User.query.filter_by(stu_num=stu_num.data).first()
        if user is not None:
            raise ValidationError('此学号已注册。')


class LoginForm(FlaskForm):
    stu_num_or_email = StringField('Id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class ForgetPasswordForm(FlaskForm):
    email_or_stu_num = StringField('Id', validators=[DataRequired()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=48)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])


class ProfileForm(FlaskForm):
    QQ = StringField('QQ', validators=[Length(max=11)])
    wechat = StringField('wechat', validators=[Length(max=64)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=11, max=11)])
    college = StringField('College', validators=[DataRequired(), Length(max=32)])
    grade = IntegerField('Grade', validators=[DataRequired()], render_kw={
        'data-container': "body", 'data-toggle': "focus", 'data-placement': "right", 'data-content': "入学年份，如：2016"
    })
    c_lass = StringField('Class', validators=[DataRequired(), Length(max=4)])


class AdminProfileForm(FlaskForm):
    QQ = StringField('QQ', validators=[Length(max=11)])
    wechat = StringField('wechat', validators=[Length(max=64)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=11, max=11)])


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=10, max=48)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])


class ApplyAssetForm(FlaskForm):
    asset_name = StringField('资产名称', validators=[DataRequired(), Length(max=32)])
    desc = StringField('详细信息', validators=[DataRequired(), Length(max=256)])
    start_time = DateTimeField('开始时间', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    end_time = DateTimeField('结束时间', validators=[DataRequired()], format='%Y-%m-%d %H:%M')
