import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.team import (
    AddTeammateForm, CreateProjectForm, ChangeProjectForm,
    get_CreateBacklogForm, get_ChangeBacklogForm, get_CreateBugForm,
    get_ChangeBugForm, CreateTeamActivityForm
)
from CUIT_TP.models import db, User, Team, Project, TeamActivity, Backlog, Bug
from CUIT_TP import login, app
from CUIT_TP.utils import send_email


bp = Blueprint('team', __name__)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@bp.route('/')
@bp.route('/<int:team_id>')
@login_required
def home(team_id):
    team = Team.query.filter(Team.id==team_id).first_or_404()
    teammates = team.teammates
    projects = Project.query.filter(Project.belong_team==team).order_by(Project.status, Project.end_time).all()
    activities = TeamActivity.query.filter(TeamActivity.belong_team_id==team_id).order_by(TeamActivity.status, TeamActivity.start_time).all()
    return render_template('team/home.html', team=team, teammates=teammates, projects=projects, activities=activities, now=datetime.now())


# 删除成员
@bp.route('/delete_teammate/<int:team_id>/', methods=('POST',))
@login_required
def delete_teammate(team_id):
    if current_user.manage_team_id == team_id or current_user.role == 'admin':
        stu_num = json.loads(request.get_data().decode(encoding='utf-8')).get('stu_num')
        team = Team.query.filter(Team.id==team_id).first()
        user = User.query.filter(User.stu_num==stu_num).first()
        team.teammates.remove(user)
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)

# 添加成员
@bp.route('/add_teammate/<int:team_id>/', methods=('GET', 'POST'))
@login_required
def add_teammate(team_id):
    if current_user.manage_team_id == team_id or current_user.role == 'admin':
        form = AddTeammateForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                team = Team.query.filter(Team.id == team_id).first()
                team.teammates.append(form.new_teammate.data)
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            return render_template('team/add_teammate.html', form=form, team_id=team_id)
    else:
        abort(403)

# 创建项目
@bp.route('/create_project/', methods=('POST', 'GET'))
@login_required
def create_project():
    if current_user.manage_team:
        form = CreateProjectForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                new_project = Project(
                    project_name=form.project_name.data,
                    desc=form.desc.data,
                    end_time=form.end_time.data,
                )
                team = Team.query.filter(Team.leader==current_user).first()
                team.projects.append(new_project)
                db.session.add(new_project)
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            return render_template('team/create_project.html', form=form, is_create=True)
    else:
        abort(403)

# 修改项目信息
@bp.route('/change_project/<int:project_id>', methods=('GET', 'POST'))
@login_required
def change_project(project_id):
    project = Project.query.filter(Project.id==project_id).first_or_404()
    if project in current_user.manage_team.projects:
        if request.method == 'POST':
            form = ChangeProjectForm()
            if form.validate_on_submit():
                project.project_name = form.project_name.data
                project.desc = form.desc.data
                project.end_time = form.end_time.data
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            form = ChangeProjectForm(
                project_name=project.project_name,
                desc=project.desc,
                end_time=project.end_time
            )
            return render_template('team/create_project.html', form=form, project_id=project_id, is_create=False)
    else:
        abort(403)

# 项目详情
@bp.route('/project_detail/<int:project_id>/')
@login_required
def project_detail(project_id):
    project = Project.query.filter(Project.id==project_id).first_or_404()
    return render_template('team/project_detail.html', project=project)

# 删除项目
@bp.route('/delete_project/', methods=('POST', ))
@login_required
def delete_project():
    if current_user.manage_team:
        project_id = json.loads(request.get_data().decode(encoding='utf-8')).get('project_id')
        project = Project.query.filter(Project.id==project_id).first_or_404()
        if project in current_user.manage_team.projects:
            db.session.delete(project)
            project.belong_team.projects.remove(project)
            db.session.commit()
            return make_response('true', 200)
        else:
            abort(403)
    else:
        abort(403)

# 结束项目
@bp.route('/end_project/', methods=('POST', ))
@login_required
def end_project():
    if current_user.manage_team:
        project_id = json.loads(request.get_data().decode('utf-8')).get('project_id')
        project = Project.query.filter(Project.id==project_id).first_or_404()
        if project in current_user.manage_team.projects:
            project.status = '1'
            db.session.commit()
            return make_response('true', 200)
        else:
            abort(403)
    else:
        abort(403)

# 项目需求
@bp.route('/project_backlog/<int:project_id>/')
@bp.route('/project_backlog/<int:project_id>/<int:page>/')
@login_required
def project_backlog(project_id, page=1):
    project = Project.query.filter(Project.id==project_id).first_or_404()
    backlogs = Backlog.query.filter(Backlog.belong_project_id==project_id).order_by(Backlog.status.asc(), Backlog.priority.desc()).paginate(page, 5, False)
    return render_template('team/project_backlog.html', backlogs=backlogs, project=project)

# 项目缺陷
@bp.route('/project_bug/<int:project_id>/')
@bp.route('/project_bug/<int:project_id>/<int:page>/')
@login_required
def project_bug(project_id, page=1):
    project = Project.query.filter(Project.id == project_id).first_or_404()
    bugs = Bug.query.filter(Bug.belong_project_id==project_id).order_by(Bug.status.asc(), Bug.priority.desc()).paginate(page, 5, False)
    return render_template('team/project_bug.html', bugs=bugs, project=project)


# 新增需求
@bp.route('/create_backlog/<int:project_id>', methods=('POST', 'GET'))
@login_required
def create_backlog(project_id):
    project = Project.query.filter(Project.id==project_id).first_or_404()
    if current_user.belong_team_id == project.belong_team_id or current_user.role == 'admin':
        CreateBacklogForm = get_CreateBacklogForm(current_user.belong_team_id)
        form = CreateBacklogForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                new_backlog = Backlog(
                    backlog_name=form.backlog_name.data,
                    desc=form.desc.data,
                    priority=form.priority.data,
                )
                form.executor.data.project_backlog.append(new_backlog)
                project.backlogs.append(new_backlog)
                db.session.add(new_backlog)
                db.session.commit()
                return make_response('true', 200)
            return make_response('false', 200)
        else:
            return render_template('team/create_backlog.html', form=form, project=project)
    else:
        abort(403)

# 需求详情
@bp.route('/backlog_detail/<int:backlog_id>')
@login_required
def backlog_detail(backlog_id):
    backlog = Backlog.query.filter(Backlog.id==backlog_id).first_or_404()
    if current_user.belong_team_id == backlog.belong_project.belong_team_id or current_user.role == 'admin':
        return render_template('team/backlog_detail.html', backlog=backlog)
    else:
        abort(403)

# 修改需求
@bp.route('/change_backlog/<int:backlog_id>', methods=('POST', 'GET'))
@login_required
def change_backlog(backlog_id):
    backlog = Backlog.query.filter(Backlog.id==backlog_id).first_or_404()
    if current_user.belong_team_id == backlog.belong_project.belong_team_id or current_user.role == 'admin':
        if request.method == 'POST':
            ChangeBacklogForm = get_ChangeBacklogForm(current_user.belong_team_id)
            form = ChangeBacklogForm()
            if form.validate_on_submit():
                backlog.backlog_name = form.backlog_name.data
                backlog.desc = form.desc.data
                backlog.priority = form.priority.data
                backlog.status = form.status.data
                if backlog.executor != form.executor.data:
                    backlog.executor = form.executor.data
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            ChangeBacklogForm = get_ChangeBacklogForm(current_user.belong_team_id)
            form = ChangeBacklogForm(
                backlog_name = backlog.backlog_name,
                desc = backlog.desc,
                priority = backlog.priority,
                executor = backlog.executor
            )
            return render_template('team/change_backlog.html', form=form, backlog=backlog)
    else:
        abort(403)

# 新增缺陷
@bp.route('/create_bug/<int:project_id>', methods=('POST', 'GET'))
@login_required
def create_bug(project_id):
    project = Project.query.filter(Project.id == project_id).first_or_404()
    if current_user.belong_team_id == project.belong_team_id or current_user.role == 'admin':
        CreateBugForm = get_CreateBugForm(current_user.belong_team_id)
        form = CreateBugForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                new_bug = Bug(
                    bug_name=form.bug_name.data,
                    desc=form.desc.data,
                    priority=form.priority.data,
                )
                project.bugs.append(new_bug)
                form.executor.data.project_bug.append(new_bug)
                db.session.add(new_bug)
                db.session.commit()
                return make_response('true', 200)
            return make_response('false', 200)
        else:
            return render_template('team/create_bug.html', form=form, project=project)
    else:
        abort(403)

# 缺陷详情
@bp.route('/bug_detail/<int:bug_id>')
@login_required
def bug_detail(bug_id):
    bug = Bug.query.filter(Bug.id==bug_id).first_or_404()
    if current_user.belong_team_id == bug.belong_project.belong_team_id or current_user.role == 'admin':
        return render_template('team/bug_detail.html', bug=bug)
    else:
        abort(403)

# 修改缺陷
@bp.route('/change_bug/<int:bug_id>', methods=('POST', 'GET'))
@login_required
def change_bug(bug_id):
    bug = Bug.query.filter(Bug.id==bug_id).first_or_404()
    if current_user.belong_team_id == bug.belong_project.belong_team_id or current_user.role == 'admin':
        if request.method == 'POST':
            ChangeBugForm = get_ChangeBugForm(current_user.belong_team_id)
            form = ChangeBugForm()
            if form.validate_on_submit():
                bug.bug_name = form.bug_name.data
                bug.desc = form.desc.data
                bug.priority = form.priority.data
                bug.status = form.status.data
                if bug.executor != form.executor.data:
                    bug.executor = form.executor.data
                db.session.commit()
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            ChangeBugForm = get_ChangeBugForm(current_user.belong_team_id)
            form = ChangeBugForm(
                bug_name = bug.bug_name,
                desc = bug.desc,
                priority = bug.priority,
                executor = bug.executor
            )
            return render_template('team/change_bug.html', form=form, bug=bug)
    else:
        abort(403)

# 新建活动
@bp.route('/create_activity/', methods=('GET', 'POST'))
@login_required
def create_activity():
    form = CreateTeamActivityForm()
    if current_user.manage_team:
        if request.method =='POST':
            if form.validate_on_submit():
                new_activity = TeamActivity(
                    activity_name=form.activity_name.data,
                    desc=form.desc.data,
                    start_time=form.start_time.data,
                )
                new_activity.belong_team = current_user.belong_team
                db.session.add(new_activity)
                db.session.commit()
                teammates = User.query.filter(User.belong_team == current_user.manage_team).all()
                for teammate in teammates:
                    send_email('新的实验室活动',
                               sender=app.config['MAIL_USERNAME'],
                               recipients=[teammate.email],
                               text_body=render_template('email/new_team_activity.txt',
                                                         user=teammate, activity=new_activity),
                               html_body=render_template('email/new_team_activity.html',
                                                         user=teammate, activity=new_activity))
                return make_response('true', 200)
            else:
                return make_response('false', 200)
        else:
            return render_template('team/create_activity.html', form=form, is_create=True)
    else:
        abort(403)

# 活动详情
@bp.route('/activity_detail/<int:activity_id>')
@login_required
def activity_detail(activity_id):
    activity = TeamActivity.query.filter(TeamActivity.id==activity_id).first_or_404()
    return render_template('team/activity_detail.html', activity=activity)

# 删除活动
@bp.route('/delete_activity/', methods=('POST', ))
@login_required
def delete_activity():
    activity_id = json.loads(request.get_data().decode(encoding='utf-8')).get('activity_id')
    activity = TeamActivity.query.filter(TeamActivity.belong_team_id==activity_id).first_or_404()
    if current_user.manage_team == activity.belong_team:
        activity.belong_team.activities.remove(activity)
        db.session.delete(activity)
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)

# 切换活动状态
@bp.route('/change_activity_status/', methods=('POST', ))
@login_required
def change_activity_status():
    activity_id = json.loads(request.get_data().decode('utf-8')).get('activity_id')
    activity = TeamActivity.query.filter(TeamActivity.id==activity_id).first_or_404()
    if current_user.manage_team == activity.belong_team:
        activity.status = '0' if activity.status == '1' else '1'
        db.session.commit()
        return make_response('true', 200)
    else:
        abort(403)