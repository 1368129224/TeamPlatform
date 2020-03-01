from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.models import User


bp = Blueprint('lab', __name__)

@bp.route('/member')
@login_required
def member():
    if current_user.permission.manage_lab_student_profile:
        return render_template('lab/member.html')
    else:
        abort(403)

@bp.route('/task')
@login_required
def task():
    if current_user.permission.manage_lab_task:
        return render_template('lab/member.html')
    else:
        abort(403)

@bp.route('/change_set')
@login_required
def change_set():
    if current_user.permission.change_set:
        return render_template('lab/change_set.html')
    else:
        abort(403)

@bp.route('/verify_asset')
@login_required
def verify_asset():
    if current_user.permission.verify_asset:
        return render_template('lab/verify_asset.html')
    else:
        abort(403)





