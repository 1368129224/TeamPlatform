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
    mail_server = StringField('服务器地址', validators=(DataRequired(), ))
    mail_port = IntegerField('端口号', validators=(DataRequired(), ))
    mail_use_tls = BooleanField('是否使用TLS')
    mail_use_ssl = BooleanField('是否使用SSL')
    mail_username = StringField('邮箱用户名', validators=(DataRequired(), ))
    mail_password = StringField('邮箱密码', validators=(DataRequired(), ))


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

class ChangeTeamInfoForm(FlaskForm):
    team_name = StringField('Team name', validators=[DataRequired(), Length(max=32)], render_kw={
        'class': 'form-control',
    })
    desc = TextAreaField('Team description', validators=[DataRequired(), Length(max=256)], render_kw={
        'style': "resize:none;"
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

def get_ChangeLeaderForm(team_id):
    class ChangeLeaderForm(FlaskForm):
        new_leader = QuerySelectField('新组长', validators=[DataRequired()], query_factory=lambda :User.query.filter(User.belong_team_id==team_id),
                                        get_label='username', render_kw={
                'class': 'custom-select'
            })
    return ChangeLeaderForm

