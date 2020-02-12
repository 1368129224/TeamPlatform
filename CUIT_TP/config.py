import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'A__VERY__LONG__KEY'
    SQLALCHEMY_DATABASE_URI = os.environ.get('MySql_URL') or 'mysql+pymysql://root:zzc()1214@www.zooter.com.cn/TeamPlatform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
