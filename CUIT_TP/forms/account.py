from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from CUIT_TP.models import User


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=8, max=28)])
    stu_num = StringField('Stu_num', validators=[DataRequired(), Length(min=10, max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=48)])
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
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=48)])
    remember_me = BooleanField('Remember Me')

class ForgetPasswordForm(FlaskForm):
    email_or_stu_num = StringField('Id', validators=[DataRequired()])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=48)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

class ProfileForm(FlaskForm):
    phone = StringField('Phone', validators=[DataRequired()])
    college = StringField('College', validators=[DataRequired()])
    grade = IntegerField('Grade', validators=[DataRequired()])
    c_lass = StringField('Class', validators=[DataRequired()])

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=10, max=48)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
