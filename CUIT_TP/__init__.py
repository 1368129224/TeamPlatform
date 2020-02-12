from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .views import home, account
from .config import Config


app = Flask(__name__)
db = SQLAlchemy(app)

app.config.from_object(Config)

app.register_blueprint(home.bp, url_prefix='/home')
app.register_blueprint(account.bp, url_prefix='/account')
