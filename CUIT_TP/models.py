import jwt
from time import time
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from . import db, login, app
from flask_login import UserMixin


# 用户相关
class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(64), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(64), unique=True, nullable=False, comment='邮箱')
    stu_num = db.Column(db.String(32), unique=True, nullable=False, comment='学号')
    password = db.Column(db.String(128), nullable=False, comment='密码')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class UserProfile(db.Model):
    __tablename__ = 'UserProfile'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.id'))
    user = relationship('User', backref=db.backref('profile', uselist=False))
    # avatar = db.Column(db.Integer, default=1)
    phone = db.Column(db.String(11), unique=True, nullable=False, comment='电话')
    college = db.Column(db.String(32), nullable=False, comment='专业')
    grade = db.Column(db.String(4), nullable=False, comment='年级')
    _class = db.Column(db.String(2), nullable=False, comment='班级')

    def __repr__(self):
        return '<UserProfile {}>'.format(self.user.username)

class UserPermission(db.Model):
    __tablename__ = 'UserPermission'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.id'))
    user = relationship('User', backref=db.backref('permission', uselist=False))
    manage_lab_task = db.Column(db.Boolean, default=False, comment='管理实验室事务')
    change_set = db.Column(db.Boolean, default=False, comment='修改座位')
    verify_asset = db.Column(db.Boolean, default=False, comment='资产审核')
    change_lab_info = db.Column(db.Boolean, default=False, comment='修改实验室信息')
    publish_lab_activity = db.Column(db.Boolean, default=False, comment='发布实验室活动')
    change_team_info = db.Column(db.Boolean, default=False, comment='修改组信息')
    publish_team_activity = db.Column(db.Boolean, default=False, comment='发布组活动')

    def __repr__(self):
        return '<UserPermission {}>'.format(self.user.username)


# 小组相关

class Team(db.Model):
    __tablename__ = 'Team'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(32), unique=True, nullable=False, comment='小组名')
    desc = db.Column(db.String(256), comment='小组简介')
    leader = relationship('User', backref=db.backref('manage_team', uselist=False))
    teammate = relationship('Teammate', backref="team")
    activity = relationship('Activity', backref="belong_team")
    project = relationship('Project', backref=db.backref('belong_team', uselist=False))

class Project(db.Model):
    __tablename__ = 'Project'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.ForeignKey("Team.id"))
    desc = db.Column(db.String(256), comment='项目简介')
    item = relationship('Item', backref='belong_project')

class Item(db.Model):
    __tablename__ = 'Item'
    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.Enum('需求', 'bug'), server_default='需求', nullable=False, comment='类型')
    desc = db.Column(db.String(256), comment='描述')
    create_time = db.Column(db.DateTime, comment='创建时间')
    status = db.Column(db.Enum('待处理', '开发中', '测试中', '已处理'), server_default='待处理', nullable=False, comment='状态')
    priority = db.Column(db.Enum('低', '普通', '高', '紧急'), server_default='普通', nullable=False, comment='优先级')
    executor = relationship('User', backref=db.backref('task', uselist=False))
    note = relationship('Note', backref='belong_item')


# 其他表
class Activity(db.Model):
    __tablename__ = 'Activity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='活动ID')
    desc = db.Column(db.String(256), nullable=False, comment='活动内容')
    datetime = db.Column(db.DateTime, comment='开始时间')

class Note(db.Model):
    __tablename__ = 'Note'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='记录ID')
    content = db.Column(db.String(256), unique=False, comment='记录内容')
    datetime = db.Column(db.DateTime, comment='创建时间')
    writer = relationship('User', backref=db.backref('note', uselist=False))