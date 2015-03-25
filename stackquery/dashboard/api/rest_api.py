from flask import Blueprint
from flask import jsonify

from stackquery.db.database import db_session
from stackquery.db.models import Release
from stackquery.db.models import Team
from stackquery.db.models import User

import simplejson as json

rest_api = Blueprint('rest_api', __name__)


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


@rest_api.route('/api/releases/')
def get_releases():
    releases = Release.query.all()
    return json.dumps(list(releases), default=date_handler)


@rest_api.route('/api/teams/')
def get_teams():
    teams = Team.query.all()
    return json.dumps(list(teams), default=date_handler)


@rest_api.route('/api/users/')
def get_users():
    users = User.query.all()
    return json.dumps(list(users), default=date_handler)


@rest_api.route('/api/users/<int:user_id>/delete/', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        request = jsonify({'status': 'Not Found'})
        request.status = 404
        return request

    db_session.delete(user)
    db_session.commit()
    return jsonify({'status': 'OK'})


@rest_api.route('/api/teams/<int:team_id>/delete', methods=['DELETE'])
def delete_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        request = jsonify({'status': 'Not Found'})
        request.status = 404
        return request

    db_session.delete(team)
    db_session.commit()
    return jsonify({'status': 'OK'})


@rest_api.route('/api/teams/<int:team_id>/<int:user_id>/delete',
                methods=['DELETE'])
def delete_user_from_team(team_id, user_id):
    team = Team.query.get(team_id)
    user = User.query.get(user_id)
    if team is None or user is None:
        request = jsonify({'status': 'Not Found'})
        request.status = 404
        return request

    team.users.remove(user)
    db_session.commit()
    return jsonify({'status': 'OK'})


@rest_api.route('/api/teams/<int:team_id>/users/')
def get_users_from_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        request = jsonify({'status': 'Not Found'})
        request.status = 404
        return request

    return json.dumps(list(team.users), default=date_handler)
