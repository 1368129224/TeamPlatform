from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, IntegerField, SelectField, DateTimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from CUIT_TP.models import db, User


class ChangeLabSettingsForm(FlaskForm):
    # 对应配置文件
    admin_email = StringField('管理员邮箱', validators=(DataRequired(), ))
    lab_name = StringField('系统名称', validators=(DataRequired(), Length(max=32)))
    lab_set_num = IntegerField('座位数', validators=(DataRequired(), ))
    sqlalchemy_database_url = StringField('数据库连接字符串', validators=(DataRequired(), Length(max=512)))
    mail_server = StringField('服务器地址', validators=(DataRequired(), ))
    mail_port = IntegerField('端口号', validators=(DataRequired(), ))
    mail_use_tls = BooleanField('是否使用TLS', validators=(DataRequired(), ))
    mail_use_ssl = BooleanField('是否使用SSL', validators=(DataRequired(), ))
    mail_username = StringField('邮箱用户名', validators=(DataRequired(), ))
    mail_password = StringField('邮箱密码', validators=(DataRequired(), ))


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

def lab_task_executor():
    return User.query.filter(User.stu_num!='0000000000')

class CreateLabTaskForm(FlaskForm):
    task_name = StringField('事务', validators=[DataRequired(), Length(max=32)])
    desc = TextAreaField('详情', validators=[DataRequired(), Length(max=256)], render_kw={
        'style': "resize:none;"
    })
    executor = QuerySelectField('执行人', validators=[DataRequired()], query_factory=lab_task_executor, get_label='username')
    execute_time = DateTimeField('执行时间', validators=[DataRequired()], format='%Y-%m-%d %H:%M', render_kw={
        'autocomplete':'off'
    })

class ChangeLabTaskForm(CreateLabTaskForm):
    pass


def team_leader():
    return User.query.filter(User.manage_team==None, User.stu_num!=0000000000, User.belong_team==None)

class CreateTeamForm(FlaskForm):
    team_name = StringField('Team name', validators=[DataRequired(), Length(max=32)], render_kw={
        'class': 'form-control',
    })
    desc = TextAreaField('Team description', validators=[DataRequired(), Length(max=256)], render_kw={
        'style': "resize:none;"
    })
    leader = QuerySelectField('Leader', validators=[DataRequired()], query_factory=team_leader, get_label='username', render_kw={
        'class': 'form-control',
    })

class CreateLabActivityForm(FlaskForm):
    activity_name = StringField('活动名', validators=[DataRequired(), Length(max=64)])
    desc = TextAreaField('活动详情', validators=[DataRequired(), Length(max=256)])
    start_time = DateTimeField('活动时间', validators=[DataRequired()], format='%Y-%m-%d %H:%M', render_kw={
        'autocomplete':'off'
    })

class ChangeLabActivityForm(CreateLabActivityForm):
    pass

def monitor():
    return User.query.filter(User.stu_num!=0000000000)

class MonitorForm(FlaskForm):
    user = QuerySelectField('学生', validators=[DataRequired()], query_factory=monitor, get_label='username', render_kw={
        'class': 'form-control',
    })
    manage_lab_student_profile = BooleanField('管理实验室学生信息')
    manage_lab_task = BooleanField('管理实验室事务')
    change_set = BooleanField('修改座位')
    verify_asset = BooleanField('资产审核')
    manage_lab_team = BooleanField('管理小组')
    publish_lab_activity = BooleanField('发布实验室活动')
