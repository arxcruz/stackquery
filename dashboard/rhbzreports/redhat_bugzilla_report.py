from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from database import db_session
from models import RedHatBugzillaReport
from rhbzreports.forms import RedHatBugzillaReportForm
import utils

redhat_bugzilla_report = Blueprint('redhat_bugzilla_report', __name__,
                                   url_prefix='/rhbzreports',
                                   template_folder='templates')


@redhat_bugzilla_report.route('/')
def redhat_bugzilla_report_index():
    reports = RedHatBugzillaReport.query.all()
    return render_template('reports/index.html', reports=reports)


@redhat_bugzilla_report.route('/show/<int:report_id>',
                              methods=['GET', 'POST'])
def show_report(report_id):
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']

    username = session.get('username', None)
    password = session.get('password', None)

    if username and password:
        reports = utils.get_report_by_id(report_id, username, password)

        if not reports:
            session['username'] = None
            session['password'] = None
            return render_template('reports/report.html', require_auth=True,
                                   failure=True)
        return render_template('reports/report.html', reports=reports)
    else:
        return render_template('reports/report.html', require_auth=True)


@redhat_bugzilla_report.route('/create/', methods=['GET', 'POST'])
def create_report():
    form = RedHatBugzillaReportForm(request.form)
    if request.method == 'POST' and form.validate():
        rhbz_report = RedHatBugzillaReport()
        rhbz_report.name = form.name.data
        rhbz_report.url = utils.parse_url(form.url.data)
        rhbz_report.description = form.description.data

        db_session.add(rhbz_report)
        db_session.commit()
        return redirect(url_for(
            'redhat_bugzilla_report.redhat_bugzilla_report_index'))

    return render_template('reports/create_report.html', form=form)


@redhat_bugzilla_report.route('/edit/<int:report_id>/',
                              methods=['GET', 'POST'])
def edit_report(report_id):
    rhbz_report = RedHatBugzillaReport.query.get(report_id)
    if rhbz_report is None:
        abort(404)
    form = RedHatBugzillaReportForm(request.form, rhbz_report)
    if request.method == 'POST':
        rhbz_report.name = form.name.data
        rhbz_report.url = form.url.data
        rhbz_report.description = form.description.data
        return redirect(url_for(
            'redhat_bugzilla_report.redhat_bugzilla_report_index'))
    return render_template('reports/create_report.html', form=form)
