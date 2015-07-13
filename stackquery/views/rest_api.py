from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request

from stackquery.database import db_session
from stackquery.models.project import Project
from stackquery.models.report import RedHatBugzillaReport
from stackquery.models.release import Release
from stackquery.models.team import Team
from stackquery.models.user import User

from stackquery.libs import utils

import simplejson as json

mod = Blueprint('rest_api', __name__)


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


@mod.route('/api/releases/')
def get_releases():
    releases = Release.query.all()
    return json.dumps(list(releases), default=date_handler)


@mod.route('/api/teams/')
def get_teams():
    teams = Team.query.all()
    return json.dumps(list(teams), default=date_handler)


@mod.route('/api/users/')
def get_users():
    users = User.query.order_by(User.name.asc()).all()
    return json.dumps(list(users), default=date_handler)


@mod.route('/api/users/<int:user_id>/delete/', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        requests = jsonify({'status': 'Not Found'})
        requests.status = 404
        return requests

    db_session.delete(user)
    db_session.commit()
    return jsonify({'status': 'OK'})


@mod.route('/api/users/create/', methods=['POST'])
def insert_user():
    content = request.get_json(force=True)
    if (not content or 'name' not in content or 'user_id'
            not in content):
        abort(400)

    user = User()
    user.name = content.get('name')
    user.user_id = content.get('user_id')
    db_session.add(user)
    db_session.commit()
    return jsonify({'status': 'OK'})


@mod.route('/api/teams/<int:team_id>/delete', methods=['DELETE'])
def delete_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        requests = jsonify({'status': 'Not Found'})
        requests.status = 404
        return requests

    db_session.delete(team)
    db_session.commit()
    return jsonify({'status': 'OK'})


@mod.route('/api/teams/<int:team_id>/<int:user_id>/delete',
           methods=['DELETE'])
def delete_user_from_team(team_id, user_id):
    team = Team.query.get(team_id)
    user = User.query.get(user_id)
    if team is None or user is None:
        requests = jsonify({'status': 'Not Found'})
        requests.status = 404
        return requests

    team.users.remove(user)
    db_session.commit()
    return jsonify({'status': 'OK'})


@mod.route('/api/teams/<int:team_id>/users/')
def get_users_from_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        requests = jsonify({'status': 'Not Found'})
        requests.status = 404
        return requests

    return json.dumps(list(team.users), default=date_handler)


@mod.route('/api/teams/<int:team_id>/projects/')
def get_projects_from_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        requests = jsonify({'status': 'Not Found'})
        requests.status = 404
        return requests

    return json.dumps(list(team.projects), default=date_handler)


@mod.route('/api/projects/')
def get_projects():
    projects = utils.get_projects()
    if projects is None:
        requests = jsonify({'status': 'Not Found'})
        requests.status = 404
        return requests

    return json.dumps(list(projects), default=date_handler)


@mod.route('/api/projects/<int:project_id>/delete', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if project is None:
        requests = jsonify({'status': 'Not Found'})
        requests.status = 404
        return requests
    db_session.delete(project)
    db_session.commit()
    return jsonify({'status': 'OK'})

# Bugzilla reports


@mod.route('/api/bzreports')
def get_reports():
    releases = RedHatBugzillaReport.query.all()
    return json.dumps(list(releases), default=date_handler)


@mod.route('/api/bzreports/<int:report_id>/delete',
           methods=['DELETE'])
def delete_report(report_id):
    report = RedHatBugzillaReport.query.get(report_id)
    if report is None:
        request = jsonify({'status': 'Not Found'})
        request.status = 404
        return request

    db_session.delete(report)
    db_session.commit()
    return jsonify({'status': 'OK'})


@mod.route('/api/bzreports/<int:report_id>/')
def get_report_by_id(report_id):
    if not request.json or not 'username' and 'password' in request.json:
        abort(404)

    username = request.json['username']
    password = request.json['password']

    reports = utils.get_report_by_id(report_id, username, password)

    if reports:
        return json.dumps(reports, indent=4)
    else:
        return jsonify({'Error': 'Invalid username or password'})
