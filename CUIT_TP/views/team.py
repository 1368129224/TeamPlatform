import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.team import (
    AddTeammateForm, CreateProjectForm, ChangeProjectForm,
    get_CreateBacklogForm, get_ChangeBacklogForm, get_CreateBugForm,
    get_ChangeBugForm,
)
from CUIT_TP.models import db, User, Team, Project, TeamActivity, Backlog, Bug
from CUIT_TP import login


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
    projects = Project.query.filter(Project.belong_team==team).all()
    return render_template('team/home.html', team=team, teammates=teammates, projects=projects)


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
                print(form.desc.errors)
                print(form.end_time.errors)
                print(form.project_name.errors)
                return make_response('false', 200)
        else:
            return render_template('team/create_project.html', form=form, is_create=True)
    else:
        abort(403)

# 项目详情
@bp.route('/project_detail/<int:project_id>/')
@login_required
def project_detail(project_id):
    project = Project.query.filter(Project.id==project_id).first_or_404()
    return render_template('team/project_detail.html', project=project)

# 修改项目信息
@bp.route('/change_project/<int:project_id>', methods=('GET', 'POST'))
@login_required
def change_project(project_id):
    project = Project.query.filter(Project.id==project_id).first_or_404()
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

# 新增需求
@bp.route('/create_backlog/<int:project_id>', methods=('POST', 'GET'))
@login_required
def create_backlog(project_id):
    project = Project.query.filter(Project.id==project_id).first_or_404()
    if current_user.belong_team_id == project.belong_team_id or current_user.role == 'admin':
        CreateBacklogForm = get_CreateBacklogForm(current_user.belong_team_id)
        form = CreateBacklogForm()
        if form.validate_on_submit():
            new_backlog = Backlog(
                project_id=project_id,
                backlog_name=form.backlog_name.data,
                desc=form.desc.data,
                priority=form.priority.data,
            )
            form.executor.data.project_backlog.append(new_backlog)
            db.session.add(new_backlog)
            db.session.commit()
            return redirect(url_for('team.project_detail', project_id=project_id))
        return render_template('team/create_backlog.html', form=form)
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
                    backlog.executor.project_backlog.remove(backlog)
                    form.executor.data.project_backlog.append(backlog)
                db.session.commit()
                return redirect(url_for('team.backlog_detail', backlog_id=backlog_id))
            else:
                ChangeBacklogForm = get_ChangeBacklogForm(current_user.belong_team_id)
                form = ChangeBacklogForm(
                    backlog_name=backlog.backlog_name,
                    desc=backlog.desc,
                    priority=backlog.priority,
                    executor=backlog.executor
                )
                return render_template('team/change_backlog.html', form=form)
        else:
            ChangeBacklogForm = get_ChangeBacklogForm(current_user.belong_team_id)
            form = ChangeBacklogForm(
                backlog_name = backlog.backlog_name,
                desc = backlog.desc,
                priority = backlog.priority,
                executor = backlog.executor
            )
            return render_template('team/change_backlog.html', form=form)
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
        if form.validate_on_submit():
            new_bug = Bug(
                project_id=project_id,
                bug_name=form.bug_name.data,
                desc=form.desc.data,
                priority=form.priority.data,
            )
            form.executor.data.project_bug.append(new_bug)
            db.session.add(new_bug)
            db.session.commit()
            return redirect(url_for('team.project_detail', project_id=project_id))
        return render_template('team/create_bug.html', form=form)
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
                    bug.executor.project_bug.remove(bug)
                    form.executor.data.project_bug.append(bug)
                db.session.commit()
                return redirect(url_for('team.bug_detail', bug_id=bug_id))
            else:
                ChangeBugForm = get_ChangeBugForm(current_user.belong_team_id)
                form = ChangeBugForm(
                    bug_name=bug.bug_name,
                    desc=bug.desc,
                    priority=bug.priority,
                    executor=bug.executor
                )
                return render_template('team/change_bug.html', form=form)
        else:
            ChangeBugForm = get_ChangeBugForm(current_user.belong_team_id)
            form = ChangeBugForm(
                bug_name = bug.bug_name,
                desc = bug.desc,
                priority = bug.priority,
                executor = bug.executor
            )
            return render_template('team/change_bug.html', form=form)
    else:
        abort(403)