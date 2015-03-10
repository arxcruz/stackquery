from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from database import db_session
from models import CustomReport
from reports.forms import CustomReportForm
import utils

import stackalytics
import json

import requests

custom_report = Blueprint('custom_report', __name__,
                          template_folder='templates')


@custom_report.route('/reports/')
def custom_report_index():
    reports = CustomReport.query.all()
    return render_template('reports/index.html', reports=reports)


@custom_report.route('/reports/show/<int:report_id>', methods=['GET', 'POST'])
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


@custom_report.route('/reports/create/', methods=['GET', 'POST'])
def create_report():
    form = CustomReportForm(request.form)
    if request.method == 'POST' and form.validate():
        custom_report = CustomReport()
        custom_report.name = form.name.data
        custom_report.url = utils.parse_url(form.url.data)
        custom_report.description = form.description.data

        db_session.add(custom_report)
        db_session.commit()
        return redirect(url_for('custom_report.custom_report_index'))

    return render_template('reports/create_report.html', form=form)


@custom_report.route('/reports/edit/<int:report_id>/', methods=['GET', 'POST'])
def edit_report(report_id):
    custom_report = CustomReport.query.get(report_id)
    if custom_report is None:
        abort(404)
    form = CustomReportForm(request.form, custom_report)
    if request.method == 'POST':
        custom_report.name = form.name.data
        custom_report.url = form.url.data
        custom_report.description = form.description.data
        return redirect(url_for('custom_report.custom_report_index'))
    return render_template('reports/create_report.html', form=form)
