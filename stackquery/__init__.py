from flask import Flask
from flask.ext.httpauth import HTTPBasicAuth

__version__ = "0.5"

app = Flask(__name__)
app.config.from_object('websiteconfig')
app.secret_key = 'why would I tell you my secret key?'

auth = HTTPBasicAuth()


from stackquery.restful import api

api.setup_restful_api()

from stackquery.views import dashboard


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()


@auth.verify_password
def verify_password(username_or_token, password):
    from stackquery.models.authuser import AuthUser
    user = AuthUser.verify_auth_token(username_or_token)
    if not user:
        user = AuthUser.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    return True


from stackquery.database import db_session

app.register_blueprint(dashboard.mod)
