from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.lab import ChangeProfileForm
from CUIT_TP.models import db, User
from CUIT_TP import login

bp = Blueprint('lab', __name__)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@bp.route('/member/')
@bp.route('/member/<int:page>/')
@login_required
def member(page=1):
    if current_user.permission.manage_lab_student_profile:
        users = User.query.order_by(User.id).paginate(page, 2, False)
        return render_template('lab/member.html', users=users)
    else:
        abort(403)


@bp.route('/change_profile/<int:stu_num>/', methods=('GET', 'POST'))
@login_required
def change_profile(stu_num):
    user = User.query.filter(User.stu_num==stu_num).first()
    if not user:
        abort(404)
    elif user.stu_num == '0000000000':
        abort(403)
    else:
        form = ChangeProfileForm(
            username=user.username,
            email=user.email,
            stu_num=user.stu_num,
            role=user.role,
            phone=user.profile.phone,
            college=user.profile.college,
            grade=user.profile.grade,
            c_lass=user.profile._class,
            manage_lab_student_profile=user.permission.manage_lab_student_profile,
            manage_lab_task=user.permission.manage_lab_task,
            change_set=user.permission.change_set,
            verify_asset=user.permission.verify_asset,
            change_lab_info=user.permission.change_lab_info,
            publish_lab_activity=user.permission.publish_lab_activity,
            change_team_info=user.permission.change_team_info,
            publish_team_activity=user.permission.publish_team_activity,
        )
        if request.method == 'POST':
            form = ChangeProfileForm()
            if form.validate_on_submit():
                user.username = form.username.data
                user.email = form.email.data
                user.stu_num = form.stu_num.data
                user.role = form.role.data
                user.profile.phone = form.phone.data
                user.profile.college = form.college.data
                user.profile.grade = form.grade.data
                user.profile._class = form.c_lass.data
                user.permission.manage_lab_student_profile = form.manage_lab_student_profile.data
                user.permission.manage_lab_task = form.manage_lab_task.data
                user.permission.change_set = form.change_set.data
                user.permission.verify_asset = form.verify_asset.data
                user.permission.change_lab_info = form.change_lab_info.data
                user.permission.publish_lab_activity = form.publish_lab_activity.data
                user.permission.change_team_info = form.change_team_info.data
                user.permission.publish_team_activity = form.publish_team_activity.data
                db.session.commit()
                return redirect(url_for('lab.change_profile', stu_num=stu_num))
            else:
                return render_template('/lab/change_profile.html', user=user, form=form)
        else:
            return render_template('/lab/change_profile.html', user=user, form=form)

@bp.route('/task/')
@login_required
def task():
    if current_user.permission.manage_lab_task:
        return render_template('lab/member.html')
    else:
        abort(403)


@bp.route('/change_set/')
@login_required
def change_set():
    if current_user.permission.change_set:
        return render_template('lab/change_set.html')
    else:
        abort(403)


@bp.route('/verify_asset/')
@login_required
def verify_asset():
    if current_user.permission.verify_asset:
        return render_template('lab/verify_asset.html')
    else:
        abort(403)
