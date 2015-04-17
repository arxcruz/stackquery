from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from stackquery.common import gerrit
from stackquery.common import utils
from stackquery.dashboard import stackalytics
from stackquery.dashboard.forms import ProjectForm
from stackquery.dashboard.forms import RedHatBugzillaReportForm
from stackquery.dashboard.forms import UserForm
from stackquery.dashboard.forms import TeamForm
from stackquery.db.database import db_session
from stackquery.db.models import Project
from stackquery.db.models import RedHatBugzillaReport
from stackquery.db.models import Team
from stackquery.db.models import User
from stackquery.db import utils as db_utils

import datetime


dashboard = Blueprint('dashboard', __name__)

# Index


@dashboard.route('/', methods=['GET', 'POST'])
def dashboard_index():
    if request.method == 'POST':
        release = request.form.get('release')
        project_type = request.form.get('project_type')
        metric = True if request.form.get('type') == 'metric' else False

        team_id = request.form.get('team')
        team = Team.query.get(team_id)
        list_users = [user.user_id for user in team.users]
        users = stackalytics.get_status_from_users(list_users,
                                                   'Red Hat',
                                                   project_type, release)
        return render_template('index.html', users=users, metric=metric,
                               release=release, team_id=team_id,
                               project_type=project_type)
    else:
        return render_template('index.html')

# Teams


@dashboard.route('/teams/')
def dashboard_teams():
    teams = Team.query.all()
    return render_template('list_teams.html', teams=teams)


@dashboard.route('/teams/<int:team_id>/edit/', methods=['GET', 'POST'])
def dashboard_edit_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        abort(404)
    form = TeamForm(request.form, team)
    if request.method == 'POST' and form.validate():
        team.name = form.name.data
        users_in = request.form.getlist('selected-users')
        users_out = request.form.getlist('available-users')

        projects_in = request.form.getlist('selected-projects')
        projects_out = request.form.getlist('available-projects')

        users = User.query.filter(User.id.in_(users_in)).all()
        for user in users:
            if user not in team.users:
                team.users.append(user)

        users = User.query.filter(User.id.in_(users_out)).all()
        for user in users:
            if user in team.users:
                team.users.remove(user)

        projects = Project.query.filter(Project.id.in_(projects_in)).all()
        for project in projects:
            if project not in team.projects:
                team.projects.append(project)

        projects = Project.query.filter(Project.id.in_(projects_out)).all()
        for project in projects:
            if project in team.projects:
                team.projects.remove(project)

        db_session.commit()

        return redirect(url_for('dashboard.dashboard_teams'))
    return render_template('create_team.html', form=form, team_id=team_id)


@dashboard.route('/teams/create/', methods=['GET', 'POST'])
def dashboard_create_team():
    form = TeamForm(request.form)
    if request.method == 'POST' and form.validate():
        team = Team()
        team.name = form.name.data
        user_ids = request.form.getlist('selected-users')
        project_ids = request.form.getlist('selected-projects')
        users = User.query.filter(User.id.in_(user_ids)).all()
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
        for user in users:
            team.users.append(user)
        for project in projects:
            team.projects.append(project)
        db_session.add(team)
        db_session.commit()
        return redirect(url_for('dashboard.dashboard_teams'))
    return render_template('create_team.html', form=form)


# Users


@dashboard.route('/users/', methods=['GET'])
def dashboard_users():
    users = User.query.order_by(User.name.asc()).all()
    return render_template('list_users.html', users=users)


@dashboard.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
def dashboard_edit_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = UserForm(request.form, user)
    if request.method == 'POST' and form.validate():
        user.name = form.name.data
        user.user_id = form.user_id.data
        user.email = form.email.data
        db_session.commit()
        return redirect(url_for('dashboard.dashboard_users'))
    return render_template('create_user.html', form=form)


@dashboard.route('/users/create/', methods=['GET', 'POST'])
def dashboard_create_user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()
        user.user_id = form.user_id.data
        user.name = form.name.data
        user.email = form.email.data
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('dashboard.dashboard_users'))
    return render_template('create_user.html', form=form)


@dashboard.route('/users/export/', methods=['GET', 'POST'])
def dashboard_export_users():
    users = None
    error = False
    if request.method == 'POST':
        try:
            company = request.form['company']
            users = stackalytics.get_all_users_by_company(
                {'company': company})['stats']
            user_ids = [str(user.user_id.strip()) for user in User.query.all()]
            for user in users:
                if str(user['id'].strip()) in user_ids:
                    users.remove(user)

        except Exception as e:
            error = True

    return render_template('export_users.html', users=users, error=error)


# Projects


@dashboard.route('/projects/')
def dashboard_projects():
    projects = db_utils.get_projects()
    return render_template('list_projects.html', projects=projects)


@dashboard.route('/projects/create/', methods=['GET', 'POST'])
def dashboard_create_project():
    form = ProjectForm(request.form)
    if request.method == 'POST' and form.validate():
        project = Project()
        project.name = form.name.data
        project.git_url = form.git_url.data
        db_session.add(project)
        db_session.commit()
        return redirect(url_for('dashboard.dashboard_projects'))
    return render_template('create_project.html', form=form)

# Gerrit report


@dashboard.route('/gerrit/', methods=['GET', 'POST'])
def gerrit_report_index():
    if request.method == 'POST':
        filters = request.form.get('filter')
        filters += ' status:MERGED'
        search_filter = gerrit.get_filters(filters)
        error = None
        before = datetime.datetime.now()
        #try:
        team = request.form.get('team')
        releases = gerrit.get_all_reviews_from_database(
            search_filter, team)
        #except Exception as e:
        #    error = 'Invalid query: %s' % e.message
        #    releases = None
        after = datetime.datetime.now()
        seconds = abs(after - before).seconds
        return render_template('gerrit/index.html',
                               releases=releases, seconds=seconds,
                               error=error)

    return render_template('gerrit/index.html')

# Bugzilla reports


@dashboard.route('/rhbzreports/')
def redhat_bugzilla_report_index():
    reports = RedHatBugzillaReport.query.all()
    return render_template('bzreports/index.html', reports=reports)


@dashboard.route('/rhbzreports/show/<int:report_id>',
                              methods=['GET', 'POST'])
def redhat_bugzilla_report_show(report_id):
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
            return render_template('bzreports/report.html', require_auth=True,
                                   failure=True)
        return render_template('bzreports/report.html', reports=reports)
    else:
        return render_template('bzreports/report.html', require_auth=True)


@dashboard.route('/rhbzreports/create/', methods=['GET', 'POST'])
def redhat_bugzilla_report_create():
    form = RedHatBugzillaReportForm(request.form)
    if request.method == 'POST' and form.validate():
        rhbz_report = RedHatBugzillaReport()
        rhbz_report.name = form.name.data
        rhbz_report.url = utils.parse_url(form.url.data)
        rhbz_report.description = form.description.data

        db_session.add(rhbz_report)
        db_session.commit()
        return redirect(url_for(
            'dashboard.redhat_bugzilla_report_index'))

    return render_template('bzreports/create_report.html', form=form)


@dashboard.route('/rhbzreports/edit/<int:report_id>/',
                              methods=['GET', 'POST'])
def redhat_bugzilla_report_edit(report_id):
    rhbz_report = RedHatBugzillaReport.query.get(report_id)
    if rhbz_report is None:
        abort(404)
    form = RedHatBugzillaReportForm(request.form, rhbz_report)
    if request.method == 'POST':
        rhbz_report.name = form.name.data
        rhbz_report.url = form.url.data
        rhbz_report.description = form.description.data
        return redirect(url_for(
            'dashboard.redhat_bugzilla_report_index'))
    return render_template('bzreports/create_report.html', form=form)
