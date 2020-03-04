from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_user, logout_user, login_required
from CUIT_TP.forms.lab import ChangeProfileForm, CreateLabTaskForm
from CUIT_TP.models import db, User, Team, Project, Activity
from CUIT_TP import login


bp = Blueprint('team', __name__)

@bp.route('/')
@bp.route('/<int:team_id>')
@login_required
def home(team_id):
    if current_user.manage_team == Team.query.filter(Team.id==team_id) or current_user.role == 'admin':
        team = Team.query.filter(Team.id==team_id).first()
        teammates = team.teammates
        projects = Project.query.filter(Project.belong_team==team)

        return render_template('team/home.html', team=team, teammates=teammates)
    else:
        abort(403)

