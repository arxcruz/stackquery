from flask import Blueprint
from flask import jsonify

from database import db_session
from models import CustomReport

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

