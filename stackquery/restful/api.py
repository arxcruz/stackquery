from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal_with
from flask_restful import reqparse
from flask_restful import Api
from flask_restful import Resource

from stackquery import app
from stackquery import auth
from stackquery.database import db_session
from stackquery.models.authuser import AuthUser
from stackquery.models.harvester import Harvester
from stackquery.models.project import Project
from stackquery.models.report import RedHatBugzillaReport
from stackquery.models.release import Release
from stackquery.models.filter import ScenarioFilter
from stackquery.models.user import User
from stackquery.models.team import Team
from stackquery.libs import stackalytics
from stackquery.libs import utils

# Users

user_fields = {
    'id': fields.Integer,
    'user_id': fields.String,
    'name': fields.String,
    'email': fields.String,
    'created': fields.DateTime(dt_format='iso8601'),
    'modified': fields.DateTime(dt_format='iso8601'),
    'url': fields.Url('user', absolute=True)
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('user_id')
user_parser.add_argument('name')
user_parser.add_argument('email')


class UserResource(Resource):
    # decorators = [auth.login_required]
    def get(self, id):
        user = User.query.get(id)
        if user:
            return user
        abort(404, message='User doesn\'t exist')

    @marshal_with(user_fields)
    def put(self, id):
        user = User.query.get(id)
        if not user:
            abort(404)

        args = user_parser.parse_args()
        user.name = args['name']
        user.email = args['email']
        user.user_id = args['user_id']
        db_session.commit()
        return user, 201

    def delete(self, id):
        user = User.query.get(id)
        if not user:
            abort(404)
        db_session.delete(user)
        db_session.commit()
        return {'result': True}


class UserListResource(Resource):
    # decorators = [auth.login_required]
    @marshal_with(user_fields)
    def get(self):
        users = User.query.all()
        return users

    @marshal_with(user_fields)
    def post(self):
        args = user_parser.parse_args()
        user = User(name=args['name'],
                    email=args['email'],
                    user_id=args['user_id'])
        db_session.add(user)
        db_session.commit()

        return user, 201


# Releases

release_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'modified': fields.DateTime(dt_format='iso8601'),
    'created': fields.DateTime(dt_format='iso8601')
}

release_parser = reqparse.RequestParser()
release_parser.add_argument('name')


class ReleaseListResource(Resource):
    # decorators = [auth.login_required]

    @marshal_with(release_fields)
    def get(self):
        releases = Release.query.all()
        return releases

# Projects

project_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'uri': fields.Url('project', absolute=True),
    'git_url': fields.String,
    'gerrit_server': fields.String
}

project_parser = reqparse.RequestParser()
project_parser.add_argument('name')
project_parser.add_argument('git_url')
project_parser.add_argument('gerrit_server')


class ProjectResource(Resource):
    # decorators = [auth.login_required]

    def get(self, id):
        project = Project.query.get(id)
        if project:
            return project
        abort(404, message='Project doesn\'t exist')

    @marshal_with(user_fields)
    def put(self, id):
        project = Project.query.get(id)
        if not project:
            abort(404)

        args = project_parser.parse_args()
        project.name = args['name']
        project.git_url = args['git_url']
        project.gerrit_server = args['gerrit_server']
        db_session.commit()

        return project, 201

    def delete(self, id):
        project = Project.query.get(id)
        if not project:
            abort(404)
        db_session.delete(project)
        db_session.commit()
        return {'result': True}


class ProjectListResource(Resource):
    # decorators = [auth.login_required]

    @marshal_with(project_fields)
    def get(self):
        projects = Project.query.all()
        return projects

    @marshal_with(project_fields)
    def post(self):
        args = project_parser.parse_args()
        project = Project(name=args['name'], git_url=args['git_url'],
                          gerrit_server=args['gerrit_server'])
        db_session.add(project)
        db_session.commit()
        return project, 201

# Teams

team_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created': fields.DateTime(dt_format='iso8601'),
    'modified': fields.DateTime(dt_format='iso8601'),
    'uri': fields.Url('team', absolute=True),
    'users': fields.List(fields.Nested(user_fields)),
}

team_parser = reqparse.RequestParser()
team_parser.add_argument('name')
team_parser.add_argument('users', type=dict, action='append')


class TeamResource(Resource):
    # decorators = [auth.login_required]

    @marshal_with(team_fields)
    def get(self, id):
        team = Team.query.get(id)
        if team:
            return team
        abort(404, message='Team doesn\'t exist')

    def delete(self, id):
        team = Team.query.get(id)
        if not team:
            abort(404)
        db_session.delete(team)
        db_session.commit()
        return {'result': True}

    @marshal_with(team_fields)
    def put(self, id):
        team = Team.query.get(id)
        if not team:
            abort(404)

        args = team_parser.parse_args()
        team.name = args["name"]
        if args.get('users', None):
            users_ids = [user.get('id', None) for user
                         in args.get('users')]
            users = User.query.filter(
                User.id.in_(users_ids)).all() if users_ids else []
            users_remove = [user for user in team.users
                            if user not in users]
            for user in users_remove:
                team.users.remove(user)
            for user in users:
                if user not in team.users:
                    team.users.append(user)

        db_session.commit()
        return team, 201


class TeamListResource(Resource):
    # decorators = [auth.login_required]

    @marshal_with(team_fields)
    def get(self):
        teams = Team.query.all()
        return teams

    @marshal_with(team_fields)
    def post(self):
        args = team_parser.parse_args()
        team = Team(name=args['name'])
        users = args.get('users', None)
        if users:
            user_ids = [user['id'] for user in users]
            selected_users = User.query.filter(User.id.in_(user_ids)).all()
            for selected_user in selected_users:
                team.users.append(selected_user)

        db_session.add(team)
        db_session.commit()
        return team, 201


# Stackalytics

stack_parser = reqparse.RequestParser()
stack_parser.add_argument('users', type=dict, action='append')
stack_parser.add_argument('project_type')
stack_parser.add_argument('release')
stack_parser.add_argument('type')


class StackalyticsListResource(Resource):
    # decorators = [auth.login_required]

    def post(self):
        args = stack_parser.parse_args()
        users = args.get('users', None)
        users_ids = []
        if users:
            users_ids = [user['user_id'] for user in args['users']]

        user_list = stackalytics.get_status_from_users(
            users_ids, 'Red Hat', 'all', args['release'],
            args['project_type'] if args['project_type'] != 'all' else None)

        metric = []

        metric.append({'title': 'Drafted blueprints',
                       'value': sum([x['drafted_blueprint_count']
                                    for x in user_list])
                       })
        metric.append({'title': 'Completed blueprints',
                       'value': sum([x['completed_blueprint_count']
                                    for x in user_list])
                       })
        metric.append({'title': 'Bugs filled',
                       'value': sum([x['filed_bug_count']
                                    for x in user_list])
                       })
        metric.append({'title': 'Bugs resolved',
                       'value': sum([x['resolved_bug_count']
                                    for x in user_list])
                       })
        result = {'metrics': metric, 'groups': user_list}

        return result, 201

# Red Hat Bugzilla

bz_parser = reqparse.RequestParser()
bz_parser.add_argument('name')
bz_parser.add_argument('url')
bz_parser.add_argument('description')

bz_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created': fields.DateTime(dt_format='iso8601'),
    'modified': fields.DateTime(dt_format='iso8601'),
    'url': fields.String,
    'require_authentication': fields.Boolean,
    'description': fields.String,
    'uri': fields.Url('report', absolute=True)
}


class RHBugzillaListResource(Resource):
    # decorators = [auth.login_required]

    @marshal_with(bz_fields)
    def get(self):
        reports = RedHatBugzillaReport.query.all()
        return reports

    @marshal_with(bz_fields)
    def post(self):
        args = bz_parser.parse_args()
        tmp_url = args['url']
        if 'GoAheadAndLogIn' not in tmp_url:
            tmp_url = tmp_url + '&GoAheadAndLogIn=1'

        if 'ctype=csv' not in tmp_url:
            tmp_url = tmp_url + '&ctype=csv'

        report = RedHatBugzillaReport()
        report.name = args['name']
        report.url = tmp_url
        report.require_authentication = True
        report.description = args['description'] or ''

        db_session.add(report)
        db_session.commit()

        return report, 201


class RHBugzillaResource(Resource):
    # decorators = [auth.login_required]

    @marshal_with(bz_fields)
    def get(self, id):
        report = RedHatBugzillaReport.query.get(id)
        if report:
            return report
        abort(404, message='Report doesn\'t exist')

    def delete(self, id):
        report = RedHatBugzillaReport.query.get(id)
        if not report:
            abort(404)
        db_session.delete(report)
        db_session.commit()
        return {'result': True}

    @marshal_with(bz_fields)
    def put(self, id):
        report = RedHatBugzillaReport.query.get(id)
        if not report:
            abort(404)
        args = bz_parser.parse_args()
        tmp_url = args['url']
        if 'GoAheadAndLogIn' not in tmp_url:
            tmp_url = tmp_url + '&GoAheadAndLogIn=1'

        if 'ctype=csv' not in tmp_url:
            tmp_url = tmp_url + '&ctype=csv'

        report.name = args['name']
        report.url = tmp_url
        report.description = args['description'] or ''
        db_session.commit()
        return report, 201


rhbz_parser = reqparse.RequestParser()
rhbz_parser.add_argument('report', type=dict)
rhbz_parser.add_argument('username', location='cookies')
rhbz_parser.add_argument('password', location='cookies')


class RHBugzillaRealReportResource(Resource):
    # decorators = [auth.login_required]

    def post(self):
        args = rhbz_parser.parse_args()
        username = args['username']
        username = username.replace('%40', '@')
        result = utils.get_report_by_id(args['report']['id'],
                                        username,
                                        args['password'])
        return result


scenario_parser = reqparse.RequestParser()
scenario_parser.add_argument('filters')
scenario_parser.add_argument('team')


class ScenarioContributionListResource(Resource):
    # decorators = [auth.login_required]

    def post(self):
        from stackquery.libs import gerrit
        args = scenario_parser.parse_args()
        filters = args['filters']
        # filters += ' status:MERGED'

        search_filter = gerrit.get_filters(filters)

        try:
            users = utils.get_users_by_team(args['team'])
            users_ids = [user.id for user in users]

            releases = gerrit.get_reviews_by_filter(search_filter, users_ids)
        except Exception:
            releases = None

        return releases

    def get(self):
        from stackquery.libs import gerrit
        return gerrit.get_reviews_by_filter(None, [6, 19, 10, 24])

# Scenario filter

scenario_filter_parser = reqparse.RequestParser()
scenario_filter_parser.add_argument('filter_desc')
scenario_filter_parser.add_argument('name')

scenario_filter_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'filter_desc': fields.String,
    'uri': fields.Url('filtercenario', absolute=True)
}


class ScenarioFilterListResource(Resource):
    # decorators = [auth.login_required]

    def post(self):
        args = scenario_filter_parser.parse_args()
        _filter = ScenarioFilter()
        _filter.filter_desc = args['filter_desc']
        _filter.name = args['name']

        db_session.add(_filter)
        db_session.commit()
        return 201

    @marshal_with(scenario_filter_fields)
    def get(self):
        filters = ScenarioFilter.query.all()
        return filters


class ScenarioFilterResource(Resource):
    # decorators = [auth.login_required]

    def delete(self, id):
        filters = ScenarioFilter.query.get(id)
        if not filters:
            abort(404)
        db_session.delete(filters)
        db_session.commit()
        return {'result': True}

    @marshal_with(scenario_filter_fields)
    def get(self, id):
        filters = ScenarioFilter.query.get(id)
        if filters:
            return filters
        abort(404, message='Filter doesn\'t exist')


# Harvester

harvester_parser = reqparse.RequestParser()
harvester_parser.add_argument('name')
harvester_parser.add_argument('url')
harvester_parser.add_argument('description')

harvester_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'url': fields.String,
    'description': fields.String,
    'uri': fields.Url('harvester', absolute=True)
}


class HarvesterListResource(Resource):
    # decorators = [auth.login_required]

    @marshal_with(harvester_fields)
    def post(self):
        args = harvester_parser.parse_args()
        harvester = Harvester()
        harvester.name = args['name']
        harvester.url = args['url']
        harvester.description = args['description']

        db_session.add(harvester)
        db_session.commit()
        return harvester, 201

    @marshal_with(harvester_fields)
    def get(self):
        harvester = Harvester.query.all()
        return harvester


class HarvesterResource(Resource):
    # decorators = [auth.login_required]

    @marshal_with(harvester_fields)
    def get(self, id):
        harvester = Harvester.query.get(id)
        if harvester:
            return harvester, 201
        abort(404, message='Harvester report doesn\'t exist')

    @marshal_with(harvester_fields)
    def put(self, id):
        harvester = Harvester.query.get(id)
        if not harvester:
            abort(404)
        args = harvester_parser.parse_args()
        harvester.name = args['name']
        harvester.url = args['url']
        harvester.description = args['description']
        db_session.commit()

        return harvester, 201

    def delete(self, id):
        harvester = Harvester.query.get(id)
        if not harvester:
            abort(404)
        db_session.delete(harvester)
        db_session.commit()
        return {'result': True}

# AuthUser

authuser_parser = reqparse.RequestParser()
authuser_parser.add_argument('username')
authuser_parser.add_argument('password')


class AuthUserListResource(Resource):
    def post(self):
        args = authuser_parser.parse_args()
        user = AuthUser.query.filter_by(username=args['username']).first()
        print user.verify_password(args['password'])
        if not user or not user.verify_password(args['password']):
            abort(404, message='Username and/or password invalids')
        return {'token': user.generate_auth_token(), 'success': True}


class AuthUserResource(Resource):
    def post(self):
        args = authuser_parser.parse_args()
        user = AuthUser()
        user.username = args['username']
        user.hash_password(args['password'])
        print user.password_hash
        db_session.add(user)
        db_session.commit()
        return True


def setup_restful_api():
    api = Api(app)
    api.add_resource(UserResource, '/api/v1.0/users/<int:id>', endpoint='user')
    api.add_resource(UserListResource, '/api/v1.0/users', endpoint='users')

    api.add_resource(ReleaseListResource, '/api/v1.0/releases',
                     endpoint='releases')

    api.add_resource(TeamListResource, '/api/v1.0/teams', endpoint='teams')
    api.add_resource(TeamResource, '/api/v1.0/teams/<int:id>', endpoint='team')

    api.add_resource(ProjectResource, '/api/v1.0/projects/<int:id>',
                     endpoint='project')
    api.add_resource(ProjectListResource, '/api/v1.0/projects',
                     endpoint='projects')

    api.add_resource(StackalyticsListResource, '/api/v1.0/stackalytics',
                     endpoint='stackalytics')

    api.add_resource(RHBugzillaListResource, '/api/v1.0/reports',
                     endpoint='reports')
    api.add_resource(RHBugzillaResource, '/api/v1.0/reports/<int:id>',
                     endpoint='report')
    api.add_resource(RHBugzillaRealReportResource, '/api/v1.0/reports/show',
                     endpoint='show')

    api.add_resource(ScenarioContributionListResource, '/api/v1.0/scenarios',
                     endpoint='scenarios')

    api.add_resource(ScenarioFilterResource,
                     '/api/v1.0/filterscenario/<int:id>',
                     endpoint='filtercenario')
    api.add_resource(ScenarioFilterListResource, '/api/v1.0/filterscenario',
                     endpoint='filterscenarios')

    api.add_resource(HarvesterResource, '/api/v1.0/harvester/<int:id>',
                     endpoint='harvester')
    api.add_resource(HarvesterListResource, '/api/v1.0/harvester',
                     endpoint='harvesters')

    api.add_resource(AuthUserListResource, '/api/v1.0/login')
    api.add_resource(AuthUserResource, '/api/v1.0/register')
