from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from CUIT_TP.models import db, User, LabTask, LabActivity


bp = Blueprint('home', __name__)

@bp.route('/')
@bp.route('/home/')
@login_required
def index():
    lab_task = current_user.lab_task
    lab_activity = LabActivity.query.all()
    return render_template('home/index.html', lab_task=lab_task, lab_activity=lab_activity)
