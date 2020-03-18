import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import current_user, login_required
from CUIT_TP.forms.lab import ChangeProfileForm, CreateLabTaskForm, CreateTeamForm
from CUIT_TP.models import db, User, LabTask, Asset, Team
from CUIT_TP import login

bp = Blueprint('lab', __name__)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# 展示学生信息
@bp.route('/member/')
@bp.route('/member/<int:page>/')
@login_required
def member(page=1):
    if current_user.permission.manage_lab_student_profile:
        users = User.query.order_by(User.id).paginate(page, 2, False)
        return render_template('lab/member.html', users=users)
    else:
        abort(403)

# 修改学生信息
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
                return render_template('lab/change_profile.html', user=user, form=form)
        else:
            return render_template('lab/change_profile.html', user=user, form=form)

# 日常事务
@bp.route('/task/')
@bp.route('/task/<int:page>/')
@login_required
def task(page=1):
    if current_user.permission.manage_lab_task:
        tasks = LabTask.query.order_by(LabTask.id).paginate(page, 5, False)
        return render_template('lab/task.html', tasks=tasks)
    else:
        abort(403)

# 创建事务
@bp.route('/create_task/', methods=('GET', 'POST'))
@login_required
def create_task():
    if current_user.permission.manage_lab_task:
        form = CreateLabTaskForm()
        if request.method == 'POST':
            print(form.task_name.data)
            print(form.desc.data)
            print(form.executor.data)
            print(form.execute_time.data)
            if form.validate_on_submit():
                new_lab_task = LabTask(
                    task_name=form.task_name.data,
                    desc=form.desc.data,
                    executor=form.executor.data,
                    execute_datetime=form.execute_time.data
                )
                db.session.add(new_lab_task)
                db.session.commit()
                return redirect(url_for('lab.task'))
            else:
                print(form.task_name.errors)
                print(form.desc.errors)
                print(form.executor.errors)
                print(form.execute_time.errors)
                return render_template('lab/create_task.html', form=form)
        return render_template('lab/create_task.html', form=form)
    else:
        abort(403)

# 删除事务
@bp.route('/delete_task/', methods=('POST', ))
@login_required
def delete_task():
    if current_user.permission.manage_lab_task:
        task = LabTask.query.filter(LabTask.id)
        # TODO 删除事务
    else:
        abort(403)

def takeSecond(elem):
    return elem[1]

# 展示座位
@bp.route('/set/')
@login_required
def set():
    users = User.query.all()
    set_users, unset_users = [], []
    for user in users:
        if user.profile.set_num == 0:
            unset_users.append((user.username, user.profile.set_num, user.stu_num))
        else:
            set_users.append((user.username, user.profile.set_num, user.stu_num))
    set_users.sort(key=takeSecond)
    return render_template('lab/set.html', unset_users=unset_users, set_users=set_users)

# 修改座位
@bp.route('/change_set/', methods=('POST', ))
@login_required
def change_set():
    if current_user.permission.change_set:
        json_data = json.loads(request.get_data().decode(encoding='utf-8'))
        user = User.query.filter(User.stu_num==json_data.get('stu_num')).first()
        user.profile.set_num = json_data.get('set_num')
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)



# 资产审核
@bp.route('/verify_asset/')
@bp.route('/verify_asset/<int:page>/')
@login_required
def verify_asset(page=1):
    if current_user.permission.verify_asset:
        assets = Asset.query.order_by(Asset.id).paginate(page, 5, False)
        return render_template('lab/verify_asset.html', assets=assets)
    else:
        abort(403)

# 管理小组
@bp.route('/teams/')
@bp.route('/teams/<int:page>')
@login_required
def teams(page=1):
    if current_user.permission.manage_lab_teams:
        teams = Team.query.order_by(Team.id).paginate(page, 5, False)
        return render_template('lab/team.html', teams=teams)
    else:
        abort(403)

# 新建小组
@bp.route('/create_team/', methods=('GET', 'POST'))
@login_required
def create_team():
    if current_user.permission.manage_lab_teams:
        form = CreateTeamForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                new_team = Team(
                    team_name=form.team_name.data,
                    desc=form.desc.data,
                    leader=form.leader.data,
                )
                leader = User.query.filter(User.id==form.leader.data.id).first()
                new_team.teammates.append(leader)
                leader.permission.change_team_info = True
                leader.permission.publish_team_activity = True
                db.session.add(new_team)
                db.session.commit()
                return redirect(url_for('lab.teams'))
            else:
                return render_template('lab/create_team.html', form=form)
        else:
            return render_template('lab/create_team.html', form=form)
    else:
        abort(403)
