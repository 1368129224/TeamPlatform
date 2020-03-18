from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateTimeField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.widgets import html_params
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from CUIT_TP.models import User, db


def new_teammate():
    return User.query.filter(User.belong_team_id==None,User.stu_num!=0000000000)


class AddTeammateForm(FlaskForm):
    new_teammate = QuerySelectField('New teammate', validators=[DataRequired()], query_factory=new_teammate, get_label='username', render_kw={
        'class': 'custom-select'
    })

class CreateProjectForm(FlaskForm):
    project_name = StringField('项目名称', validators=(Length(max=32), DataRequired()))
    desc = TextAreaField('项目简介', validators=[DataRequired(), Length(max=256)], render_kw={
        'style': "resize:none;"
    })
    end_time = DateTimeField('结束时间', validators=[DataRequired()], format='%Y-%m-%d %H:%M', render_kw={
        'data-target': '#end_time_datetimepicker',
    })