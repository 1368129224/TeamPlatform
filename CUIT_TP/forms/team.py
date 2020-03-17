from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateTimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.widgets import html_params
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from CUIT_TP.models import User


def new_teammate():
    return User.query.filter(User.belong_team_id==None,User.stu_num!=0000000000)


class AddTeammateForm(FlaskForm):
    new_teammate = QuerySelectField('New teammate', validators=[DataRequired()], query_factory=new_teammate, get_label='username', render_kw={
        'class': 'custom-select'
    })