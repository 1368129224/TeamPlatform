from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegisterForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(min=8, max=28)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=48)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
