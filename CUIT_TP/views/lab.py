import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import current_user, login_required
from CUIT_TP.forms.lab import (
    CreateLabTaskForm, CreateTeamForm, CreateLabActivityForm,
    ChangeLabActivityForm, ChangeLabTaskForm, MonitorForm,
    ChangeLabSettingsForm
)
from CUIT_TP.models import db, User, LabTask, Asset, Team, UserProfile, LabActivity, Monitor
from CUIT_TP import login, app

bp = Blueprint('lab', __name__)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# 系统设置
@bp.route('/settings/', methods=('POST', 'GET'))
@login_required
def settings():
    if current_user.role != 'admin':
        abort(403)
    form = ChangeLabSettingsForm(
        admin_email=str(app.config.get('ADMIN_EMAIL')),
        lab_name=str(app.config.get('LAB_NAME')),
        lab_set_num=int(app.config.get('LAB_SET_NUM')),
        mail_server=str(app.config.get('MAIL_SERVER')),
        mail_port=int(app.config.get('MAIL_PORT')),
        mail_use_tls=app.config.get('MAIL_USE_TLS'),
        mail_use_ssl=app.config.get('MAIL_USE_SSL'),
        mail_username=str(app.config.get('MAIL_USERNAME')),
        mail_password=str(app.config.get('MAIL_PASSWORD')),
    )
    if request.method == 'POST':
        form = ChangeLabSettingsForm()
        if form.validate_on_submit():
            app.config['ADMIN_EMAIL'] = form.admin_email.data
            app.config['LAB_NAME'] = form.lab_name.data
            app.config['LAB_SET_NUM'] = form.lab_set_num.data
            app.config['MAIL_SERVER'] = form.mail_server.data
            app.config['MAIL_PORT'] = form.mail_port.data
            app.config['MAIL_USE_TLS'] = form.mail_use_tls.data
            app.config['MAIL_USE_SSL'] = form.mail_use_ssl.data
            app.config['MAIL_USERNAME'] = form.mail_username.data
            app.config['MAIL_PASSWORD'] = form.mail_password.data
            from CUIT_TP.utils import save_config
            save_config()
            return make_response('true', 200)
        else:
            print(form.admin_email.errors)
            print(form.lab_name.errors)
            print(form.lab_set_num.errors)
            print(form.mail_server.errors)
            print(form.mail_port.errors)
            print(form.mail_use_tls.errors)
            print(form.mail_use_ssl.errors)
            print(form.mail_username.errors)
            print(form.mail_password.errors)
            return make_response('false', 200)
    else:
        return render_template('lab/settings.html', form=form)


# 展示学生信息
@bp.route('/member/')
@bp.route('/member/<int:page>/')
@login_required
def member(page=1):
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_student_profile) or current_user.role == 'admin':
        users = User.query.filter(User.role != 'admin').order_by(User.id).paginate(page, 8, False)
        return render_template('lab/member.html', users=users)
    else:
        abort(403)


# 展示事务
@bp.route('/task/')
@bp.route('/task/<int:page>/')
@login_required
def task(page=1):
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_task) or current_user.role == 'admin':
        tasks = LabTask.query.order_by(LabTask.status.asc(), LabTask.execute_datetime).paginate(page, 5, False)
        return render_template('lab/task.html', tasks=tasks)
    else:
        abort(403)


# 创建事务
@bp.route('/create_task/', methods=('GET', 'POST'))
@login_required
def create_task():
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_task) or current_user.role == 'admin':
        form = CreateLabTaskForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                new_lab_task = LabTask(
                    task_name=form.task_name.data,
                    desc=form.desc.data,
                    executor=form.executor.data,
                    execute_datetime=form.execute_time.data
                )
                form.executor.data.lab_task.append(new_lab_task)
                db.session.add(new_lab_task)
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            return render_template('lab/create_task.html', form=form, is_create=True)
    else:
        abort(403)


# 删除事务
@bp.route('/delete_task/', methods=('POST',))
@login_required
def delete_task():
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_task) or current_user.role == 'admin':
        task_id = json.loads(request.get_data().decode(encoding='utf-8')).get('task_id')
        task = LabTask.query.filter(LabTask.id == task_id).first_or_404()
        task.executor.lab_task.remove(task)
        db.session.delete(task)
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 事务详情
@bp.route('/task_detail/<int:task_id>')
@login_required
def task_detail(task_id):
    task = LabTask.query.filter(LabTask.id == task_id).first()
    return render_template('lab/task_detail.html', task=task)


# 切换事务状态
@bp.route('/change_task_status/', methods=('POST',))
@login_required
def change_task_status():
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_task) or current_user.role == 'admin':
        task_id = json.loads(request.get_data().decode('utf-8')).get('task_id')
        task = LabTask.query.filter(LabTask.id == task_id).first_or_404()
        task.status = '0' if task.status == '1' else '1'
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 修改事务
@bp.route('/change_task/<int:task_id>/', methods=('POST', 'GET'))
@login_required
def change_task(task_id):
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_task) or current_user.role == 'admin':
        task = LabTask.query.filter(LabTask.id == task_id).first_or_404()
        if request.method == 'POST':
            form = ChangeLabTaskForm()
            if form.validate_on_submit():
                task.task_name = form.task_name.data
                task.desc = form.desc.data
                task.executor = form.executor.data
                task.execute_datetime = form.execute_time.data
                db.session.commit()

                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            form = ChangeLabTaskForm(
                task_name=task.task_name,
                desc=task.desc,
                executor=task.executor,
                execute_time=task.execute_datetime,
            )
            return render_template('lab/create_task.html', form=form, is_create=False, task=task)
    else:
        abort(403)


def takeSecond(elem):
    return elem[1]


# 展示座位
@bp.route('/set/')
@login_required
def set():
    if (current_user.role == 'monitor' and current_user.monitor_permission.change_set) or current_user.role == 'admin':
        users = User.query.all()
        set_users, unset_users = [], []
        for user in users:
            if user.profile.set_num == 0:
                unset_users.append((user.username, user.profile.set_num, user.stu_num))
            else:
                set_users.append((user.username, user.profile.set_num, user.stu_num))
        set_users.sort(key=takeSecond)
        return render_template('lab/set.html', unset_users=unset_users, set_users=set_users)
    else:
        abort(403)


# 修改座位
@bp.route('/change_set/', methods=('POST',))
@login_required
def change_set():
    if (current_user.role == 'monitor' and current_user.monitor_permission.change_set) or current_user.role == 'admin':
        json_data = json.loads(request.get_data().decode(encoding='utf-8'))
        user = User.query.filter(User.stu_num == json_data.get('stu_num')).first()
        try:
            n = int(json_data.get('set_num'))
            if n < 0:
                raise ValueError
        except ValueError:
            return make_response('valueError', 200)
        if UserProfile.query.filter(UserProfile.set_num == n).first():
            return make_response('valueExist', 200)
        if n > int(app.config['LAB_SET_NUM']):
            return make_response('valueOverflow', 200)
        user.profile.set_num = json_data.get('set_num')
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 待审核资产
@bp.route('/verify_asset/')
@bp.route('/verify_asset/<int:page>/')
@login_required
def verify_asset(page=1):
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.verify_asset) or current_user.role == 'admin':
        assets = Asset.query.order_by(Asset.id).paginate(page, 5, False)
        return render_template('lab/verify_asset.html', assets=assets, now=datetime.now())
    else:
        abort(403)


# 资产审核
@bp.route('/deliver_asset/', methods=('POST',))
@login_required
def deliver_asset():
    if current_user.role == 'admin' or (
            current_user.role == 'monitor' and current_user.monitor_permission.verify_asset):
        json_data = json.loads(request.get_data().decode(encoding='utf-8'))
        asset_id = json_data.get('asset_id')
        asset = Asset.query.filter(Asset.id == asset_id).first()
        asset.status = json_data.get('status')
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 删除资产
@bp.route('/delete_asset/', methods=('POST',))
@login_required
def delete_asset():
    if current_user.role == 'admin' or (
            current_user.role == 'monitor' and current_user.monitor_permission.verify_asset):
        json_data = json.loads(request.get_data().decode(encoding='utf-8'))
        asset_id = json_data.get('asset_id')
        asset = Asset.query.filter(Asset.id == asset_id).first()
        asset.user.assets.remove(asset)
        db.session.delete(asset)
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 管理小组
@bp.route('/teams/')
@bp.route('/teams/<int:page>')
@login_required
def teams(page=1):
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_team) or current_user.role == 'admin':
        teams = Team.query.order_by(Team.id).paginate(page, 5, False)
        return render_template('lab/team.html', teams=teams)
    else:
        abort(403)


# 新建小组
@bp.route('/create_team/', methods=('GET', 'POST'))
@login_required
def create_team():
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_team) or current_user.role == 'admin':
        form = CreateTeamForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                new_team = Team(
                    team_name=form.team_name.data,
                    desc=form.desc.data,
                    leader=form.leader.data,
                )
                leader = User.query.filter(User.id == form.leader.data.id).first()
                new_team.teammates.append(leader)
                db.session.add(new_team)
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            return render_template('lab/create_team.html', form=form)
    else:
        abort(403)


# 删除小组
@bp.route('/delete_team/', methods=('POST',))
@login_required
def delete_team():
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_team) or current_user.role == 'admin':
        team_id = json.loads(request.get_data().decode(encoding='utf-8')).get('team_id')
        team = Team.query.filter(Team.id == team_id).first_or_404()
        db.session.delete(team)
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 创建活动
@bp.route('/create_activity/', methods=('GET', 'POST'))
@login_required
def create_activity():
    form = CreateLabActivityForm()
    if current_user.role == 'admin' or (
            current_user.role == 'monitor' and current_user.monitor_permission.manage_lab_team):
        if request.method == 'POST':
            if form.validate_on_submit():
                new_activity = LabActivity(
                    activity_name=form.activity_name.data,
                    desc=form.desc.data,
                    start_time=form.start_time.data,
                )
                db.session.add(new_activity)
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            return render_template('lab/create_activity.html', form=form, is_create=True)
    else:
        abort(403)


# 展示活动
@bp.route('/activity/')
@bp.route('/activity/<int:page>')
@login_required
def activity(page=1):
    if current_user.role == 'admin' or (
            current_user.role == 'monitor' and current_user.monitor_permission.publish_lab_activity):
        activities = LabActivity.query.order_by(LabActivity.status, LabActivity.start_time).paginate(page, 5, False)
        return render_template('lab/activity.html', activities=activities, now=datetime.now())
    else:
        abort(403)


# 活动详情
@bp.route('/activity_detail/<int:activity_id>')
@login_required
def activity_detail(activity_id):
    activity = LabActivity.query.filter(LabActivity.id == activity_id).first()
    return render_template('lab/activity_detail.html', activity=activity)


# 切换活动状态
@bp.route('/change_activity_status/', methods=('POST',))
@login_required
def change_activity_status():
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.publish_lab_activity) or current_user.role == 'admin':
        activity_id = json.loads(request.get_data().decode('utf-8')).get('activity_id')
        activity = LabActivity.query.filter(LabActivity.id == activity_id).first_or_404()
        activity.status = '0' if activity.status == '1' else '1'
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 删除活动
@bp.route('/delete_activity/', methods=('POST',))
@login_required
def delete_activity():
    if (
            current_user.role == 'monitor' and current_user.monitor_permission.publish_lab_activity) or current_user.role == 'admin':
        activity_id = json.loads(request.get_data().decode(encoding='utf-8')).get('activity_id')
        activity = LabActivity.query.filter(LabActivity.id == activity_id).first_or_404()
        db.session.delete(activity)
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)


# 修改活动
@bp.route('/change_activity/<int:activity_id>', methods=('GET', 'POST'))
@login_required
def change_activity(activity_id):
    if current_user.role == 'admin' or (
            current_user.role == 'monitor' and current_user.monitor_permission.publish_lab_activity):
        activity = LabActivity.query.filter(LabActivity.id == activity_id).first()
        if request.method == 'POST':
            form = ChangeLabActivityForm()
            if form.validate_on_submit():
                activity.activity_name = form.activity_name.data
                activity.desc = form.desc.data
                activity.start_time = form.start_time.data
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            form = ChangeLabActivityForm(
                activity_name=activity.activity_name,
                desc=activity.desc,
                start_time=activity.start_time,
            )
            return render_template('lab/create_activity.html', form=form, is_create=False, activity_id=activity_id)
    else:
        abort(403)


# 班长管理
@bp.route('/monitor/', methods=('GET', 'POST'))
@login_required
def monitor():
    if current_user.role == 'admin':
        monitor = Monitor.query.first()
        if monitor:
            if request.method == 'POST':
                form = MonitorForm()
                if form.validate_on_submit():
                    monitor.user.role = 'student'
                    db.session.delete(monitor)
                    new_monitor = Monitor()
                    new_monitor.user = form.user.data
                    new_monitor.manage_lab_student_profile = form.manage_lab_student_profile.data
                    new_monitor.manage_lab_task = form.manage_lab_task.data
                    new_monitor.change_set = form.change_set.data
                    new_monitor.verify_asset = form.verify_asset.data
                    new_monitor.manage_lab_team = form.manage_lab_team.data
                    new_monitor.publish_lab_activity = form.publish_lab_activity.data
                    new_monitor.user.role = 'monitor'
                    db.session.commit()
                    return render_template('lab/monitor.html', user=monitor.user, form=form)
                else:
                    return render_template('lab/monitor.html', user=monitor.user, form=form)
            else:
                form = MonitorForm(
                    user=monitor.user,
                    manage_lab_student_profile=monitor.manage_lab_student_profile,
                    manage_lab_task=monitor.manage_lab_task,
                    change_set=monitor.change_set,
                    verify_asset=monitor.verify_asset,
                    manage_lab_team=monitor.manage_lab_team,
                    publish_lab_activity=monitor.publish_lab_activity,
                )
                return render_template('lab/monitor.html', user=monitor.user, form=form)
        else:
            if request.method == 'POST':
                form = MonitorForm()
                if form.validate_on_submit():
                    new_monitor = Monitor(
                        user=form.user.data,
                        manage_lab_student_profile=form.manage_lab_student_profile.data,
                        manage_lab_task=form.manage_lab_task.data,
                        change_set=form.change_set.data,
                        verify_asset=form.verify_asset.data,
                        manage_lab_team=form.manage_lab_team.data,
                        publish_lab_activity=form.publish_lab_activity.data,
                    )
                    new_monitor.user.role = 'monitor'
                    db.session.add(new_monitor)
                    db.session.commit()
                    return redirect(url_for('lab.monitor', user=new_monitor.user, form=form))
                else:
                    return render_template('lab/monitor.html', form=form)
            else:
                form = MonitorForm()
                return render_template('lab/monitor.html', user=None, form=form)
    else:
        abort(403)
