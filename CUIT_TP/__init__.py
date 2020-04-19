from datetime import timedelta
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_jsglue import JSGlue

app = Flask(__name__)
from .config import Config
app.config.from_object(Config)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'account.login'
mail = Mail(app)
jsglue = JSGlue(app)


from CUIT_TP.models import User
try:
    if not User.query.filter(User.role == 'admin').first():
        print("Administrator account info:\nusername: admin\npassword: adminadmin")
        from werkzeug.security import generate_password_hash
        admin = User(username='admin', email=app.config.get('ADMIN_EMAIL'), stu_num='0000000000', password=generate_password_hash('adminadmin'), role='admin')
        db.session.add(admin)
        db.session.commit()
        db.session.close()
except:
    pass

from .views import account, lab, team
app.register_blueprint(account.bp, url_prefix='/account/')
app.register_blueprint(lab.bp, url_prefix='/lab/')
app.register_blueprint(team.bp, url_prefix='/team/')

@app.route('/')
def index():
    return redirect(url_for('account.manage'))