from flask_restful import abort
from flask_restful import fields
from flask_restful import marshal_with
from flask_restful import reqparse
from flask_restful import Api
from flask_restful import Resource

from stackquery import app
from stackquery.database import db_session
from stackquery.models.user import User

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

def setup_restful_api():
    api = Api(app)
    api.add_resource(UserResource, '/api/v1.0/users/<int:id>', endpoint='user')
    api.add_resource(UserListResource, '/api/v1.0/users', endpoint='users')

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj