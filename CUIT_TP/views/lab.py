import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import current_user, login_required
from CUIT_TP.forms.lab import ChangeProfileForm, CreateLabTaskForm, CreateTeamForm, CreateLabActivityForm, ChangeLabActivityForm, ChangeLabTaskForm
from CUIT_TP.models import db, User, LabTask, Asset, Team, UserProfile, LabActivity
from CUIT_TP import login, app

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
    if current_user.role != 'admin' and stu_num == '0000000000':
        abort(403)
    elif not current_user.monitor_permission:
        abort(403)
    else:
        user = User.query.filter(User.stu_num == stu_num).first_or_404()
        form = ChangeProfileForm(
            username=user.username,
            email=user.email,
            stu_num=user.stu_num,
            role=user.role,
            phone=user.profile.phone,
            college=user.profile.college,
            grade=user.profile.grade,
            c_lass=user.profile._class,
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
    if current_user.monitor_permission.manage_lab_task:
        tasks = LabTask.query.order_by(LabTask.id).paginate(page, 5, False)
        return render_template('lab/task.html', tasks=tasks)
    else:
        abort(403)

# 创建事务
@bp.route('/create_task/', methods=('GET', 'POST'))
@login_required
def create_task():
    if current_user.monitor_permission.manage_lab_task:
        form = CreateLabTaskForm()
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
            return render_template('lab/create_task.html', form=form, is_create=True)
    else:
        abort(403)

# 删除事务
@bp.route('/delete_task/', methods=('POST', ))
@login_required
def delete_task():
    if current_user.monitor_permission.manage_lab_task:
        task_id = json.loads(request.get_data().decode(encoding='utf-8')).get('task_id')
        task = LabTask.query.filter(LabTask.id==task_id).first_or_404()
        db.session.delete(task)
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)

# 事务详情
@bp.route('/task_detail/')
@login_required
def task_detail():
    task_id = request.args.get('task_id')
    task = LabTask.query.filter(LabTask.id==task_id).first()
    return render_template('lab/task_detail.html', task=task)

# 修改事务
@bp.route('/change_task/<int:task_id>/', methods=('POST', 'GET'))
@login_required
def change_task(task_id):
    if not current_user.monitor_permission.publish_lab_activity:
        abort(403)
    task = LabTask.query.filter(LabTask.id == task_id).first_or_404()
    if request.method == 'POST':
        form = ChangeLabTaskForm()
        if form.validate_on_submit():
            task.task_name = form.task_name.data
            task.desc = form.desc.data
            task.executor = form.executor.data
            task.execute_datetime = form.execute_time.data
            db.session.commit()
            return redirect(url_for('lab.task_detail', task_id=task_id))
        else:
            return render_template('lab/create_task.html', form=form, is_create=False)
    else:
        form = ChangeLabTaskForm(
            task_name=task.task_name,
            desc=task.desc,
            executor=task.executor,
            execute_datetime=task.execute_datetime,
        )
        return render_template('lab/create_task.html', form=form, is_create=False)
def takeSecond(elem):
    return elem[1]

# 展示座位
@bp.route('/set/')
@login_required
def set():
    if not current_user.monitor_permission.change_set:
        abort(403)
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
    if current_user.monitor_permission.change_set:
        json_data = json.loads(request.get_data().decode(encoding='utf-8'))
        user = User.query.filter(User.stu_num==json_data.get('stu_num')).first()
        try:
            n = int(json_data.get('set_num'))
        except ValueError:
            return make_response('valueError', 200)
        if UserProfile.query.filter(UserProfile.set_num==n).first():
            return make_response('valueExist', 200)
        if n > app.config['LAB_SET_NUM']:
            return make_response('valueOverflow', 200)
        user.profile.set_num = json_data.get('set_num')
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)

# 资产展示
@bp.route('/verify_asset/')
@bp.route('/verify_asset/<int:page>/')
@login_required
def verify_asset(page=1):
    if current_user.monitor_permission.verify_asset:
        assets = Asset.query.order_by(Asset.id).paginate(page, 5, False)
        return render_template('lab/verify_asset.html', assets=assets, now=datetime.now())
    else:
        abort(403)

# 资产审核
@bp.route('/deliver_asset/', methods=('POST', ))
@login_required
def deliver_asset():
    if current_user.monitor_permission.verify_asset:
        json_data = json.loads(request.get_data().decode(encoding='utf-8'))
        asset_id = json_data.get('asset_id')
        asset = Asset.query.filter(Asset.id==asset_id).first()
        asset.status = json_data.get('status')
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)

# 管理小组
@bp.route('/teams/')
@bp.route('/teams/<int:page>')
@login_required
def teams(page=1):
    if current_user.monitor_permission.manage_lab_teams:
        teams = Team.query.order_by(Team.id).paginate(page, 5, False)
        return render_template('lab/team.html', teams=teams)
    else:
        abort(403)

# 新建小组
@bp.route('/create_team/', methods=('GET', 'POST'))
@login_required
def create_team():
    if current_user.monitor_permission.manage_lab_teams:
        form = CreateTeamForm()
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
        abort(403)


# 创建活动
@bp.route('/create_activity/', methods=('GET', 'POST'))
@login_required
def create_activity():
    form = CreateLabActivityForm()
    if current_user.role == 'admin' or current_user.monitor_permission.publish_lab_activity:
        if form.validate_on_submit():
            new_activity = LabActivity(
                activity_name=form.activity_name.data,
                desc=form.desc.data,
                start_time=form.start_time.data,
                is_lab_activity=True,
            )
            db.session.add(new_activity)
            db.session.commit()
            return redirect(url_for('lab.activity'))
        else:
            return render_template('lab/create_activity.html', form=form, is_create=True)
    else:
        abort(403)

# 展示活动
@bp.route('/activity/')
@bp.route('/activity/<int:page>')
@login_required
def activity(page=1):
    if current_user.role == 'admin' or current_user.monitor_permission.publish_lab_activity:
        activities = LabActivity.query.order_by(LabActivity.id).paginate(page, 5, False)
        return render_template('lab/activity.html', activities=activities, now=datetime.now())
    else:
        abort(403)

# 活动详情
@bp.route('/activity_detail/<int:activity_id>')
@login_required
def activity_detail(activity_id):
    activity = LabActivity.query.filter(LabActivity.id == activity_id).first()
    return render_template('lab/activity_detail.html', activity=activity)

# 修改活动
@bp.route('/change_activity/<int:activity_id>', methods=('GET', 'POST'))
@login_required
def change_activity(activity_id):
    if current_user.role == 'admin' or current_user.monitor_permission.publish_lab_activity:
        activity = LabActivity.query.filter(LabActivity.id == activity_id).first()
        if request.method == 'POST':
            form = ChangeLabActivityForm()
            if form.validate_on_submit():
                activity.activity_name = form.activity_name.data
                activity.desc = form.desc.data
                activity.start_time = form.start_time.data
                db.session.commit()
                return redirect(url_for('lab.activity_detail', activity_id=activity_id))
            else:
                return render_template('lab/create_activity.html', form=form, is_create=False)
        else:
            form = ChangeLabActivityForm(
                activity_name=activity.activity_name,
                desc=activity.desc,
                start_time=activity.start_time,
            )
            return render_template('lab/create_activity.html', form=form, is_create=False)
    else:
        abort(403)


