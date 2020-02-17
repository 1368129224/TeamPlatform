import jwt
from time import time
from sqlalchemy.orm import relationship
from . import db, login, app
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    stu_num = db.Column(db.String(32), unique=True, nullable=False)

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
    github = db.Column(db.String(128))
    college = db.Column(db.String(32), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    _class = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return '<UserProfile {}>'.format(self.user.username)