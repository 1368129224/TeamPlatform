import os


class Config(object):
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    # 管理员账户邮箱
    ADMIN_EMAIL = "admin@admin.com"
    # 系统名称
    LAB_NAME = "XXX实验室"
    # 实验室座位数
    LAB_SET_NUM = "30"
    # flask-WTF
    CSRF_ENABLED = True
    SECRET_KEY = "A__VERY__LONG__KEY"
    # database
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:password@localhost/TeamPlatform?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 128
    # mail
    MAIL_SERVER = "smtp.qq.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = "admin@qq.com"
    MAIL_PASSWORD = "password"
