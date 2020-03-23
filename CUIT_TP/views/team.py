from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.team import AddTeammateForm, CreateProjectForm
from CUIT_TP.models import db, User, Team, Project, TeamActivity
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
    if current_user.manage_team == team or current_user.role == 'admin':
        normal_user = False
    else:
        normal_user = True

    return render_template('team/home.html', team=team, teammates=teammates, normal_user=normal_user, projects=projects)

# 删除成员
@bp.route('/delete_teammate/<int:team_id>/<int:stu_num>')
@login_required
def delete_teammate(team_id, stu_num):
    if current_user.manage_team_id == team_id or current_user.role == 'admin':
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
                return redirect(url_for('team.home', team_id=team_id))
            else:
                return render_template('team/add_teammate.html', form=form)
        else:
            return render_template('team/add_teammate.html', form=form)
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
                return redirect(url_for('team.home', team_id=current_user.manage_team_id))
            else:
                return render_template('team/create_project.html', form=form)
        else:
            return render_template('team/create_project.html', form=form)
    else:
        abort(403)
