import jwt
from time import time
from datetime import datetime
from sqlalchemy.orm import relationship
from CUIT_TP import db, login, app
from flask_login import UserMixin


# 用户相关
class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(64), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(64), unique=True, nullable=False, comment='邮箱')
    stu_num = db.Column(db.String(32), unique=True, nullable=False, comment='学号')
    password = db.Column(db.String(128), nullable=False, comment='密码')
    role = db.Column(db.Enum('admin', 'monitor', 'student'), server_default='student')
    enable = db.Column(db.Boolean, default=True, comment='是否启用')

    belong_team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    manage_team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('Note.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'))

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

class UserProfile(db.Model):
    __tablename__ = 'UserProfile'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.id', onupdate='CASCADE', ondelete='CASCADE'))
    user = relationship('User', backref=db.backref('profile', uselist=False))
    # avatar = db.Column(db.Integer, default=1)
    QQ = db.Column(db.String(11), unique=True, comment='QQ')
    wechat = db.Column(db.String(64), unique=True, comment='微信')
    phone = db.Column(db.String(11), unique=True, nullable=False, comment='电话')
    set_num = db.Column(db.Integer, default=0, comment='座位号')
    college = db.Column(db.String(32), nullable=False, comment='专业')
    grade = db.Column(db.String(4), nullable=False, comment='年级')
    _class = db.Column(db.String(4), nullable=False, comment='班级')

    def __repr__(self):
        return '<UserProfile {}>'.format(self.user.username)

class UserPermission(db.Model):
    __tablename__ = 'UserPermission'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.id', onupdate='CASCADE', ondelete='CASCADE'))
    user = relationship('User', backref=db.backref('permission', uselist=False))
    manage_lab_student_profile = db.Column(db.Boolean, default=False, comment='管理实验室学生信息')
    manage_lab_task = db.Column(db.Boolean, default=False, comment='管理实验室事务')
    change_set = db.Column(db.Boolean, default=False, comment='修改座位')
    verify_asset = db.Column(db.Boolean, default=False, comment='资产审核')
    change_lab_info = db.Column(db.Boolean, default=False, comment='修改实验室信息')
    publish_lab_activity = db.Column(db.Boolean, default=False, comment='发布实验室活动')
    manage_lab_teams = db.Column(db.Boolean, default=False, comment='管理小组')
    change_team_info = db.Column(db.Boolean, default=False, comment='修改组信息')
    publish_team_activity = db.Column(db.Boolean, default=False, comment='发布组活动')

    def __repr__(self):
        return '<UserPermission {}>'.format(self.user.username)

# 活动表
class Activity(db.Model):
    __tablename__ = 'Activity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='活动ID')
    belong_team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    desc = db.Column(db.String(256), nullable=False, comment='活动内容')
    create_time = db.Column(db.DateTime, default=datetime.now())
    execute_datetime = db.Column(db.DateTime, comment='开始时间')

    def __repr__(self):
        return '<Activity {}>'.format(self.id)

# 笔记表
class Note(db.Model):
    __tablename__ = 'Note'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='记录ID')
    item_id = db.Column(db.Integer, db.ForeignKey('Item.id'))
    content = db.Column(db.String(256), unique=False, comment='记录内容')
    create_datetime = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    writer = relationship('User', backref='notes', foreign_keys=[User.note_id])

    def __repr__(self):
        return '<Note {}>'.format(self.id)

# 事项表
class Item(db.Model):
    __tablename__ = 'Item'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('Project.id'))
    item_type = db.Column(db.Enum('backlog', 'bug'), server_default='backlog', nullable=False, comment='类型')
    desc = db.Column(db.String(256), comment='描述')
    create_time = db.Column(db.DateTime, comment='创建时间')
    status = db.Column(db.Enum('0', '1', '2', '3'), server_default='0', nullable=False, comment='状态')
    priority = db.Column(db.Enum('0', '1', '2', '3'), server_default='0', nullable=False, comment='优先级')
    executor = relationship('User', backref='task', uselist=False, foreign_keys=[User.item_id])
    notes = relationship('Note', backref='belong_item', foreign_keys=[Note.item_id])

    def __repr__(self):
        return '<Item {}>'.format(self.id)

# 项目表
class Project(db.Model):
    __tablename__ = 'Project'
    id = db.Column(db.Integer, primary_key=True)
    belong_team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    project_name = db.Column(db.String(32), nullable=False, comment='项目名称')
    desc = db.Column(db.String(256), comment='项目简介')
    start_time = db.Column(db.DateTime, default=datetime.now(), comment='开始时间')
    end_time = db.Column(db.DateTime, comment='终止时间')
    status = db.Column(db.Enum('0', '1'), server_default='0', nullable=False, comment='状态')
    items = relationship('Item', backref='belong_project', foreign_keys=[Item.project_id])

    def __repr__(self):
        return '<Project {}>'.format(self.project_name)

# 小组表
class Team(db.Model):
    __tablename__ = 'Team'
    id = db.Column(db.Integer, primary_key=True)
    leader = relationship("User", backref="manage_team", uselist=False, foreign_keys=[User.manage_team_id])
    team_name = db.Column(db.String(32), unique=True, nullable=False,  comment='小组名')
    desc = db.Column(db.String(256), comment='小组简介')
    teammates = relationship("User", backref='belong_team', foreign_keys=[User.belong_team_id])
    activities = relationship('Activity', backref="belong_team", foreign_keys=[Activity.belong_team_id])
    projects = relationship('Project', backref='belong_team', foreign_keys=[Project.belong_team_id])

    def __repr__(self):
        return '<Team {}>'.format(self.team_name)

# 实验室事务表
class LabTask(db.Model):
    __tablename__ = 'LabTask'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='事务ID')
    uid = db.Column(db.Integer, db.ForeignKey('User.id'))
    task_name = db.Column(db.String(32), nullable=False, comment='事务')
    desc = db.Column(db.String(256), nullable=False, comment='事务详情')
    executor = relationship('User', backref='lab_task', uselist=False)
    create_time = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    execute_datetime =  db.Column(db.DateTime, comment='开始时间')

# 资产表
class Asset(db.Model):
    __tablename__ = 'Asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='资产ID')
    uid = db.Column(db.Integer, db.ForeignKey('User.id'))
    user = relationship('User', backref='asset', uselist=False)
    asset_name = db.Column(db.String(32), nullable=False, comment='资产名称')
    desc = db.Column(db.String(256), nullable=False, comment='详细信息')
    start_time = db.Column(db.DateTime, default=datetime.now(), comment='开始时间')
    end_time = db.Column(db.DateTime, comment='终止时间')
    status = db.Column(db.Enum('0', '1', '2'), server_default='0', nullable=False, comment='状态')
