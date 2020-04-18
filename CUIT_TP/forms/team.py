from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, TextAreaField, SelectField, HiddenField
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
        'autocomplete':'off'
    })

class ChangeProjectForm(CreateProjectForm):
    pass

def get_CreateBacklogForm(team_id):
    class CreateBacklogForm(FlaskForm):
        backlog_name = StringField('需求', validators=(Length(max=16), DataRequired()), render_kw={
            'autocomplete': 'off'
        })
        desc = TextAreaField('详细信息', validators=[DataRequired(), Length(max=256)], render_kw={
            'style': "resize:none;"
        })
        priority = SelectField('优先级', choices=(('0', '低'), ('1', '普通'), ('2', '高'), ('3', '紧急')))
        executor = QuerySelectField('执行人', validators=[DataRequired()], query_factory=lambda :User.query.filter(User.belong_team_id==team_id),
                                    get_label='username', render_kw={
                'class': 'custom-select'
            })
    return CreateBacklogForm

def get_ChangeBacklogForm(team_id):
    class ChangeBacklogForm(FlaskForm):
        backlog_name = StringField('需求', validators=(Length(max=16), DataRequired()), render_kw={
            'autocomplete': 'off'
        })
        desc = TextAreaField('详细信息', validators=[DataRequired(), Length(max=256)], render_kw={
            'style': "resize:none;"
        })
        priority = SelectField('优先级', choices=(('0', '低'), ('1', '普通'), ('2', '高'), ('3', '紧急')))
        status = SelectField('状态', choices=(('0', '待处理'), ('1', '开发中'), ('2', '测试中'), ('3', '已处理')))
        executor = QuerySelectField('执行人', validators=[DataRequired()], query_factory=lambda :User.query.filter(User.belong_team_id==team_id),
                                    get_label='username', render_kw={
                'class': 'custom-select'
            })
    return ChangeBacklogForm

def get_CreateBugForm(team_id):
    class CreateBugForm(FlaskForm):
        bug_name = StringField('缺陷', validators=(Length(max=16), DataRequired()), render_kw={
            'autocomplete': 'off'
        })
        desc = TextAreaField('详细信息', validators=[DataRequired(), Length(max=256)], render_kw={
            'style': "resize:none;"
        })
        priority = SelectField('优先级', choices=(('0', '低'), ('1', '普通'), ('2', '高'), ('3', '紧急')))
        executor = QuerySelectField('执行人', validators=[DataRequired()], query_factory=lambda :User.query.filter(User.belong_team_id==team_id),
                                    get_label='username', render_kw={
                'class': 'custom-select'
            })
    return CreateBugForm

def get_ChangeBugForm(team_id):
    class ChangeBugForm(FlaskForm):
        bug_name = StringField('缺陷', validators=(Length(max=16), DataRequired()), render_kw={
            'autocomplete': 'off'
        })
        desc = TextAreaField('详细信息', validators=[DataRequired(), Length(max=256)], render_kw={
            'style': "resize:none;"
        })
        priority = SelectField('优先级', choices=(('0', '低'), ('1', '普通'), ('2', '高'), ('3', '紧急')))
        status = SelectField('状态', choices=(('0', '待处理'), ('1', '修复中'), ('2', '测试中'), ('3', '已修复')))
        executor = QuerySelectField('执行人', validators=[DataRequired()], query_factory=lambda :User.query.filter(User.belong_team_id==team_id),
                                    get_label='username', render_kw={
                'class': 'custom-select'
            })
    return ChangeBugForm

class CreateTeamActivityForm(FlaskForm):
    activity_name = StringField('活动名', validators=[DataRequired(), Length(max=64)])
    desc = TextAreaField('活动详情', validators=[DataRequired(), Length(max=256)])
    start_time = DateTimeField('活动时间', validators=[DataRequired()], format='%Y-%m-%d %H:%M', render_kw={
        'autocomplete':'off'
    })