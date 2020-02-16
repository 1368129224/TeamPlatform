import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'A__VERY__LONG__KEY'
    # database
    SQLALCHEMY_DATABASE_URI = os.environ.get('MySql_URL') or 'mysql+pymysql://root:zzc()1214@www.zooter.com.cn/TeamPlatform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # mail
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'zzc1368129224@qq.com'
    MAIL_PASSWORD = 'qxsqntzjbtbahdgb'
