import os
from flask_mail import Message
from threading import Thread
from CUIT_TP import app, mail


def send_async_email(myapp, msg):
    with myapp.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def save_config():
    with open(os.path.join(app.config.get('BASEDIR'), 'config.py'), 'w', encoding='utf-8') as f:
        f.write(f'''import os


class Config(object):
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    # 管理员账户邮箱
    ADMIN_EMAIL = "{str(app.config.get('ADMIN_EMAIL'))}"
    # 系统名称
    LAB_NAME = "{str(app.config.get('LAB_NAME'))}"
    # 实验室座位数
    LAB_SET_NUM = {str(app.config.get('LAB_SET_NUM'))}
    # flask-WTF
    CSRF_ENABLED = {str(app.config.get('CSRF_ENABLED'))}
    SECRET_KEY = "{str(app.config.get('SECRET_KEY'))}"
    # database
    SQLALCHEMY_DATABASE_URI = "{str(app.config.get('SQLALCHEMY_DATABASE_URI'))}"
    SQLALCHEMY_TRACK_MODIFICATIONS = {str(app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS'))}
    SQLALCHEMY_POOL_SIZE = {str(app.config.get('SQLALCHEMY_POOL_SIZE'))}
    # mail
    MAIL_SERVER = "{str(app.config.get('MAIL_SERVER'))}"
    MAIL_PORT = {str(app.config.get('MAIL_PORT'))}
    MAIL_USE_TLS = {str(app.config.get('MAIL_USE_TLS'))}
    MAIL_USE_SSL = {str(app.config.get('MAIL_USE_SSL'))}
    MAIL_USERNAME = "{str(app.config.get('MAIL_USERNAME'))}"
    MAIL_PASSWORD = "{str(app.config.get('MAIL_PASSWORD'))}"
''')
