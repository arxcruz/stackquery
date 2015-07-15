from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from stackquery.database import db_session
from stackquery.libs import stackalytics
from stackquery.models.harvester import Harvester
from stackquery.models.project import Project
from stackquery.models.report import RedHatBugzillaReport
from stackquery.models.team import Team
from stackquery.models.user import User
from stackquery.forms.harvester import HarvesterForm
from stackquery.forms.project import ProjectForm
from stackquery.forms.report import RedHatBugzillaReportForm
from stackquery.forms.team import TeamForm
from stackquery.forms.user import UserForm

from stackquery.libs import utils

import datetime

mod = Blueprint('dashboard', __name__)

# Index


@mod.route('/', methods=['GET', 'POST'])
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


@mod.route('/teams/')
def dashboard_teams():
    teams = Team.query.all()
    return render_template('list_teams.html', teams=teams)


@mod.route('/teams/<int:team_id>/edit/', methods=['GET', 'POST'])
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

        users = User.query.filter(
            User.id.in_(users_in)).all() if users_in else []
        for user in users:
            if user not in team.users:
                team.users.append(user)

        users = User.query.filter(
            User.id.in_(users_out)).all() if users_out else []
        for user in users:
            if user in team.users:
                team.users.remove(user)

        projects = Project.query.filter(
            Project.id.in_(projects_in)).all() if projects_in else []
        for project in projects:
            if project not in team.projects:
                team.projects.append(project)

        projects = Project.query.filter(
            Project.id.in_(projects_out)).all() if projects_out else []
        for project in projects:
            if project in team.projects:
                team.projects.remove(project)

        db_session.commit()

        return redirect(url_for('dashboard.dashboard_teams'))
    return render_template('create_team.html', form=form, team_id=team_id)


@mod.route('/teams/create/', methods=['GET', 'POST'])
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


@mod.route('/users/', methods=['GET'])
def dashboard_users():
    users = User.query.order_by(User.name.asc()).all()
    return render_template('list_users.html', users=users)


@mod.route('/users/<int:user_id>/edit/', methods=['GET', 'POST'])
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


@mod.route('/users/create/', methods=['GET', 'POST'])
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


@mod.route('/users/export/', methods=['GET', 'POST'])
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

        except Exception:
            error = True

    return render_template('export_users.html', users=users, error=error)


# Projects


@mod.route('/projects/')
def dashboard_projects():
    projects = Project.query.order_by(Project.name).all()
    return render_template('list_projects.html', projects=projects)


@mod.route('/projects/create/', methods=['GET', 'POST'])
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


@mod.route('/gerrit/', methods=['GET', 'POST'])
def gerrit_report_index():
    if request.method == 'POST':
        from stackquery.libs import gerrit
        filters = request.form.get('filter')
        filters += ' status:MERGED'
        search_filter = gerrit.get_filters(filters)
        error = None
        before = datetime.datetime.now()
        try:
            team = request.form.get('team')
            releases = gerrit.get_all_reviews_from_database(
                search_filter, team)
        except Exception as e:
            error = 'Invalid query: %s' % e.message
            releases = None
        after = datetime.datetime.now()
        seconds = abs(after - before).seconds
        return render_template('gerrit/index.html',
                               releases=releases, seconds=seconds,
                               error=error)

    return render_template('gerrit/index.html')

# Bugzilla reports


@mod.route('/rhbzreports/')
def redhat_bugzilla_report_index():
    reports = RedHatBugzillaReport.query.all()
    return render_template('bzreports/index.html', reports=reports)


@mod.route('/rhbzreports/show/<int:report_id>',
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


@mod.route('/rhbzreports/create/', methods=['GET', 'POST'])
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


@mod.route('/rhbzreports/edit/<int:report_id>/',
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

# Harvester reports


@mod.route('/harvester/')
def harvester_report_index():
    harvesters = Harvester.query.all()
    return render_template('harvester/index.html', harvesters=harvesters)


@mod.route('/harvester/show/<int:harvester_id>')
def harvester_report_show(harvester_id):
    harvester = Harvester.query.get(harvester_id)
    if harvester:
        return render_template('harvester/report.html', harvester=harvester)
    else:
        return redirect(url_for('dashboard.harvester_report_index'))


@mod.route('/harvester/create/', methods=['GET', 'POST'])
def harvester_report_create():
    form = HarvesterForm(request.form)
    if request.method == 'POST' and form.validate():
        harvester = Harvester()
        harvester.name = form.name.data
        harvester.description = form.description.data
        harvester.url = utils.parse_url(form.url.data)

        db_session.add(harvester)
        db_session.commit()
        return redirect(url_for('dashboard.harvester_report_index'))
    return render_template('harvester/create_report.html', form=form)


@mod.route('/harvester/edit/<int:harvester_id>/',
           methods=['GET', 'POST'])
def harvester_report_edit(harvester_id):
    harvester = Harvester.query.get(harvester_id)
    if harvester is None:
        abort(404)

    form = HarvesterForm(request.form, harvester)
    if request.method == 'POST':
        harvester.name = form.name.data
        harvester.url = form.url.data
        harvester.description = form.description.data
        return redirect(url_for('dashboard.harvester_report_index'))
    return render_template('harvester/create_report.html', form=form)
