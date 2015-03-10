from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request

from database import db_session
from models import CustomReport
import utils

import simplejson as json

report_rest_api = Blueprint('report_rest_api', __name__)


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


@report_rest_api.route('/api/report/')
def get_reports():
    releases = CustomReport.query.all()
    return json.dumps(list(releases), default=date_handler)


@report_rest_api.route('/api/report/<int:report_id>/delete',
                       methods=['DELETE'])
def delete_report(report_id):
    report = CustomReport.query.get(report_id)
    if report is None:
        request = jsonify({'status': 'Not Found'})
        request.status = 404
        return request

    db_session.delete(report)
    db_session.commit()
    return jsonify({'status': 'OK'})


@report_rest_api.route('/api/report/<int:report_id>/')
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
