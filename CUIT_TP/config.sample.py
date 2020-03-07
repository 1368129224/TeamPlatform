import os
from datetime import timedelta

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # 实验室名称
    LAB_NAME = 'XX实验室'
    # 实验室座位数
    LAB_SET_NUM = 30
    # flask-WTF
    CSRF_ENABLED = True
    SECRET_KEY = 'A__VERY__LONG__KEY'
    # flask-login 记住登录时长
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    # database
    SQLALCHEMY_DATABASE_URI = os.environ.get('MySql_URL') or 'mysql+pymysql://root:password@localhost/TeamPlatform?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # mail
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'example@qq.com'
    MAIL_PASSWORD = 'password'
