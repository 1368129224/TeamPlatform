import jwt
from time import time
from sqlalchemy.orm import relationship
from . import db, login, app
from flask_login import UserMixin


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
    phone = db.Column(db.String(11), unique=True, nullable=False, comment='手机号')
    college = db.Column(db.String(32), nullable=False, comment='专业')
    grade = db.Column(db.String(4), nullable=False, comment='年级')
    _class = db.Column(db.String(2), nullable=False, comment='班级')

    def __repr__(self):
        return '<UserProfile {}>'.format(self.user.username)

class UserPermission(db.Model):
    __tablename__ = 'UserPermission'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.id'))
    user = relationship('User', backref=db.backref('profile', uselist=False))
    change_lab_info = db.Column(db.Boolean, default=False, comment='修改实验室信息')
    change_set = db.Column(db.Boolean, default=False, comment='修改座位')
    verify_asset = db.Column(db.Boolean, default=False, comment='资产审核')
    publish_lab_activity = db.Column(db.Boolean, default=False, comment='发布实验室活动')
    manage_lab_task = db.Column(db.Boolean, default=False, comment='管理实验室事务')
    change_team_info = db.Column(db.Boolean, default=False, comment='修改组信息')
    publish_team_activity = db.Column(db.Boolean, default=False, comment='发布组活动')


class Team(db.Model):
    __tablename__ = 'Team'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(32), )