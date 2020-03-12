from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.lab import ChangeProfileForm, CreateLabTaskForm
from CUIT_TP.models import db, User, Team, Project, Activity
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
    projects = Project.query.filter(Project.belong_team==team)
    if current_user.manage_team == team or current_user.role == 'admin':
        normal_user = False
    else:
        normal_user = True

    return render_template('team/home.html', team=team, teammates=teammates, normal_user=normal_user)

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
