from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.models import User


bp = Blueprint('lab', __name__)


@bp.route('/member')
@login_required
def member():
    return render_template('lab/member.html')



