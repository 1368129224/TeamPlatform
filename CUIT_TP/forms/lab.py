from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from CUIT_TP.models import User


class ChangeProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    stu_num = StringField('Stu_num', validators=[DataRequired(), Length(min=10, max=10)])
    role_choices = [('monitor', '班长'), ('student', '学生')]
    role = SelectField(label='权限', choices=role_choices)
    phone = StringField('Phone', validators=[DataRequired(), Length(min=11, max=11)])
    college = StringField('College', validators=[DataRequired()])
    grade = IntegerField('Grade', validators=[DataRequired()])
    c_lass = StringField('Class', validators=[DataRequired()])
    manage_lab_student_profile = BooleanField('管理实验室学生信息')
    manage_lab_task = BooleanField('管理实验室事务')
    change_set = BooleanField('修改座位')
    verify_asset = BooleanField('资产审核')
    change_lab_info = BooleanField('修改实验室信息')
    publish_lab_activity = BooleanField('发布实验室活动')
    change_team_info = BooleanField('修改组信息')
    publish_team_activity = BooleanField('发布组活动')