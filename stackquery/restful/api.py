from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal_with
from flask_restful import reqparse
from flask_restful import Api
from flask_restful import Resource

from stackquery import app
from stackquery.database import db_session
from stackquery.models.project import Project
from stackquery.models.release import Release
from stackquery.models.user import User
from stackquery.models.team import Team
from stackquery.libs import stackalytics

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
    @marshal_with(release_fields)
    def get(self):
        releases = Release.query.all()
        return releases

# Projects

project_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'uri': fields.Url('project', absolute=True),
    'git_url': fields.String
}

project_parser = reqparse.RequestParser()
project_parser.add_argument('name')
project_parser.add_argument('git_url')


class ProjectResource(Resource):
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
    @marshal_with(project_fields)
    def get(self):
        projects = Project.query.all()
        return projects

    @marshal_with(project_fields)
    def post(self):
        args = project_parser.parse_args()
        project = Project(name=args['name'], git_url=args['git_url'])
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
    'projects': fields.List(fields.Nested(project_fields))
}

team_parser = reqparse.RequestParser()
team_parser.add_argument('name')
team_parser.add_argument('projects', type=dict, action='append')
team_parser.add_argument('users', type=dict, action='append')


class TeamResource(Resource):
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

        if args.get('projects', None):
            projects_ids = [project.get('id', None) for project
                            in args.get('projects', [])]
            projects = Project.query.filter(
                Project.id.in_(projects_ids)).all() if projects_ids else []

            projects_remove = [project for project in team.projects
                               if project not in projects]

            for project in projects_remove:
                team.projects.remove(project)
            for project in projects:
                if project not in team.projects:
                    team.projects.append(project)

        db_session.commit()
        return team, 201


class TeamListResource(Resource):
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

        projects = args.get('projects', None)
        if projects:
            project_ids = [project['id'] for project in projects]
            selected_projects = Project.query.filter(Project.id.in_(project_ids)).all()
            for selected_project in selected_projects:
                team.projects.append(selected_project)
        db_session.add(team)
        db_session.commit()
        return team, 201


# Stackalytics

stack_parser = reqparse.RequestParser()
stack_parser.add_argument('users', type=dict, action='append')
stack_parser.add_argument('project_type')
stack_parser.add_argument('release')
stack_parser.add_argument('type')


class StackalyticsResource(Resource):
    def post(self):
        args = stack_parser.parse_args()
        users = args.get('users', None)
        users_ids = []
        if users:
            users_ids = [user['user_id'] for user in args['users']]

        user_list = stackalytics.get_status_from_users(
            users_ids, 'Red Hat', args['project_type'], args['release'])

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
    api.add_resource(StackalyticsResource, '/api/v1.0/stackalytics')
