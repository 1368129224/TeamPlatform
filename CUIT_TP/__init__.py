from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail


app = Flask(__name__)
from .config import Config
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'account.login'
mail = Mail(app)

from .views import home, account, lab, team
app.register_blueprint(home.bp)
app.register_blueprint(account.bp, url_prefix='/account/')
app.register_blueprint(lab.bp, url_prefix='/lab/')
app.register_blueprint(team.bp, url_prefix='/team/')

