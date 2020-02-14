from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    stu_num = db.Column(db.String(32), unique=True, nullable=False)
    github_link = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)