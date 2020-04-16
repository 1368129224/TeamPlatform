import jwt
from time import time
from datetime import datetime
from sqlalchemy.orm import relationship
from CUIT_TP import db, login, app
from flask_login import UserMixin

# 实验室事务表
class LabTask(db.Model):
    __tablename__ = 'LabTask'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='事务ID')
    uid = db.Column(db.Integer, db.ForeignKey('User.id'))
    task_name = db.Column(db.String(32), nullable=False, comment='事务')
    desc = db.Column(db.String(256), nullable=False, comment='事务详情')
    execute_datetime = db.Column(db.DateTime, comment='开始时间')
    status = db.Column(db.Enum('0', '1'), server_default='0', nullable=False, comment='状态')

# 用户相关
class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(64), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(64), unique=True, nullable=False, comment='邮箱')
    stu_num = db.Column(db.String(32), unique=True, nullable=False, comment='学号')
    password = db.Column(db.String(128), nullable=False, comment='密码')
    role = db.Column(db.Enum('admin', 'monitor', 'student'), server_default='student')
    lab_task = relationship('LabTask', backref=db.backref('executor'), foreign_keys=[LabTask.uid], cascade="all, delete-orphan", single_parent=True)
    manage_team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    manage_team = relationship("Team", backref=db.backref('leader', uselist=False), cascade="all, delete-orphan", foreign_keys=[manage_team_id])

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

# 用户信息表
class UserProfile(db.Model):
    __tablename__ = 'UserProfile'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    user = relationship("User", backref=db.backref('profile', uselist=False), cascade="all, delete-orphan")
    QQ = db.Column(db.String(11), comment='QQ')
    wechat = db.Column(db.String(64), comment='微信')
    phone = db.Column(db.String(11), nullable=False, comment='电话')
    set_num = db.Column(db.Integer, default=0, comment='座位号')
    college = db.Column(db.String(32), nullable=False, comment='专业')
    grade = db.Column(db.String(4), nullable=False, comment='年级')
    _class = db.Column(db.String(4), nullable=False, comment='班级')

    def __repr__(self):
        return '<UserProfile {}>'.format(self.user.username)

# 实验室活动表
class LabActivity(db.Model):
    __tablename__ = 'LabActivity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='活动ID')
    activity_name = db.Column(db.String(64), nullable=False, comment='活动名称')
    desc = db.Column(db.String(256), nullable=False, comment='活动内容')
    start_time = db.Column(db.DateTime, comment='开始时间')
    status = db.Column(db.Enum('0', '1'), server_default='0', nullable=False, comment='状态')

    def __repr__(self):
        return '<LabActivity {}>'.format(self.id)

# 小组活动表
class TeamActivity(db.Model):
    __tablename__ = 'TeamActivity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='活动ID')
    activity_name = db.Column(db.String(64), nullable=False, comment='活动名称')
    desc = db.Column(db.String(256), nullable=False, comment='活动内容')
    start_time = db.Column(db.DateTime, comment='开始时间')
    status = db.Column(db.Enum('0', '1'), server_default='0', nullable=False, comment='状态')

    def __repr__(self):
        return '<TeamActivity {}>'.format(self.id)

# 需求表
class Backlog(db.Model):
    __tablename__ = 'Backlog'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    backlog_name = db.Column(db.String(16), comment='需求')
    desc = db.Column(db.String(256), comment='描述')
    create_time = db.Column(db.DateTime, default=datetime.now(),comment='创建时间')
    status = db.Column(db.Enum('0', '1', '2', '3'), server_default='0', nullable=False, comment='状态')
    priority = db.Column(db.Enum('0', '1', '2', '3'), server_default='1', nullable=False, comment='优先级')
    executor_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    executor = relationship('User', backref=db.backref('project_backlog'), foreign_keys=[executor_id], cascade="all, delete-orphan", single_parent=True)

    def __repr__(self):
        return '<Backlog {}>'.format(self.id)

# 缺陷表
class Bug(db.Model):
    __tablename__ = 'Bug'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bug_name = db.Column(db.String(16), comment='缺陷')
    desc = db.Column(db.String(256), comment='描述')
    create_time = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    status = db.Column(db.Enum('0', '1', '2', '3'), server_default='0', nullable=False, comment='状态')
    priority = db.Column(db.Enum('0', '1', '2', '3'), server_default='1', nullable=False, comment='优先级')
    executor_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    executor = relationship('User', backref=db.backref('project_bug'), foreign_keys=[executor_id], cascade="all, delete-orphan", single_parent=True)

    def __repr__(self):
        return '<Bug {}>'.format(self.id)

# 需求记录表
class BacklogNote(db.Model):
    __tablename__ = 'BacklogNote'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='记录ID')
    content = db.Column(db.String(256), unique=False, comment='记录内容')
    create_datetime = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    backlog_id = db.Column(db.Integer, db.ForeignKey('Backlog.id', ondelete='CASCADE'))
    backlog = relationship('Backlog', backref=db.backref('notes'), foreign_keys=[backlog_id], cascade="all, delete-orphan", single_parent=True)
    writer_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    writer = relationship('User', backref=db.backref('backlog_notes'), foreign_keys=[writer_id], cascade="all, delete-orphan", single_parent=True)

    def __repr__(self):
        return '<Note {}>'.format(self.id)

# 缺陷记录表
class BugNote(db.Model):
    __tablename__ = 'BugNote'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='记录ID')
    content = db.Column(db.String(256), unique=False, comment='记录内容')
    create_datetime = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    bug_id = db.Column(db.Integer, db.ForeignKey('Bug.id', ondelete='CASCADE'))
    bug = relationship('Bug', backref=db.backref('notes'), foreign_keys=[bug_id], cascade="all, delete-orphan", single_parent=True)
    writer_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    writer = relationship('User', backref=db.backref('bug_notes'), foreign_keys=[writer_id], cascade="all, delete-orphan", single_parent=True)

    def __repr__(self):
        return '<Note {}>'.format(self.id)

# 项目表
class Project(db.Model):
    __tablename__ = 'Project'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(32), nullable=False, comment='项目名称')
    desc = db.Column(db.String(256), comment='项目简介')
    start_time = db.Column(db.DateTime, default=datetime.now(), comment='开始时间')
    end_time = db.Column(db.DateTime, comment='终止时间')
    status = db.Column(db.Enum('0', '1'), server_default='0', nullable=False, comment='状态')
    backlog_id = db.Column(db.Integer, db.ForeignKey('Backlog.id', ondelete='CASCADE'))
    backlogs = relationship('Backlog', backref=db.backref('belong_project'), foreign_keys=[backlog_id], cascade="all, delete-orphan", single_parent=True)
    bug_id = db.Column(db.Integer, db.ForeignKey('Bug.id', ondelete='CASCADE'))
    bugs = relationship('Bug', backref=db.backref('belong_project'), foreign_keys=[bug_id], cascade="all, delete-orphan", single_parent=True)

    def __repr__(self):
        return '<Project {}>'.format(self.project_name)

# 小组表
class Team(db.Model):
    __tablename__ = 'Team'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(32), unique=True, nullable=False,  comment='小组名')
    desc = db.Column(db.String(256), comment='小组简介')
    # leader_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    # leader = relationship('User', back_populates='manage_team')
    teammate_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    teammates = relationship("User", backref=db.backref('belong_team'), cascade="all, delete-orphan", single_parent=True, foreign_keys=[teammate_id])
    activity_id = db.Column(db.Integer, db.ForeignKey('TeamActivity.id', ondelete='CASCADE'))
    activities = relationship('TeamActivity', backref=db.backref("belong_team"), cascade="all, delete-orphan", single_parent=True, foreign_keys=[activity_id])
    project_id = db.Column(db.Integer, db.ForeignKey('Project.id', ondelete='CASCADE'))
    projects = relationship('Project', backref=db.backref('belong_team'), cascade="all, delete-orphan", single_parent=True, foreign_keys=[project_id])

    def __repr__(self):
        return '<Team {}>'.format(self.team_name)

# 资产表
class Asset(db.Model):
    __tablename__ = 'Asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='资产ID')
    user_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    user = relationship('User', backref=db.backref('asset'), cascade="all, delete-orphan", single_parent=True, uselist=False)
    asset_name = db.Column(db.String(32), nullable=False, comment='资产名称')
    desc = db.Column(db.String(256), nullable=False, comment='详细信息')
    start_time = db.Column(db.DateTime, default=datetime.now(), comment='开始时间')
    end_time = db.Column(db.DateTime, comment='终止时间')
    status = db.Column(db.Enum('0', '1', '2'), server_default='0', nullable=False, comment='状态')

# 班长权限表
class Monitor(db.Model):
    __tablename__ = 'Monitor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'))
    user = relationship('User', backref=db.backref('monitor_permission'), cascade="all, delete-orphan", single_parent=True, uselist=False)
    manage_lab_student_profile = db.Column(db.Boolean, default=False, comment='管理实验室学生信息')
    manage_lab_task = db.Column(db.Boolean, default=False, comment='管理实验室事务')
    change_set = db.Column(db.Boolean, default=False, comment='修改座位')
    verify_asset = db.Column(db.Boolean, default=False, comment='资产审核')
    manage_lab_team = db.Column(db.Boolean, default=False, comment='管理小组')
    publish_lab_activity = db.Column(db.Boolean, default=False, comment='发布实验室活动')
