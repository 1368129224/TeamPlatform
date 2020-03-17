from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from CUIT_TP.models import User


bp = Blueprint('home', __name__)
@bp.route('/')
@bp.route('/home/')
def index():
    if not User.query.filter(User.role=='admin').first():
        return redirect(url_for('account.register_admin'))
    return render_template('home/index.html')
