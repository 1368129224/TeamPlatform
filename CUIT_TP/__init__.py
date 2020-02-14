from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager().init_app(app)

from .config import Config
app.config.from_object(Config)

from .views import home, account
app.register_blueprint(home.bp, url_prefix='/home')
app.register_blueprint(account.bp, url_prefix='/account')
