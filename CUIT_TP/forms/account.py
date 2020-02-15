from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from CUIT_TP.models import User


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=8, max=28)])
    stu_num = StringField('Stu_num', validators=[DataRequired(), Length(min=10, max=10)])
    github_link = StringField('Github', validators=[Length(max=128)])
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
        user = User.query.filter_by(email=stu_num.data).first()
        if user is not None:
            raise ValidationError('此学号已注册。')


class LoginForm(FlaskForm):
    stu_num_or_email = StringField('Id', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=48)])
    remember_me = BooleanField('Remember Me')