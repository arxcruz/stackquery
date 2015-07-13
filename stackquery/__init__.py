from flask import Flask

__version__ = "0.4"

app = Flask(__name__)

app.config.from_object('websiteconfig')

app.secret_key = 'why would I tell you my secret key?'

from stackquery.views import rest_api, dashboard


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()

from stackquery.database import db_session

app.register_blueprint(dashboard.mod)
app.register_blueprint(rest_api.mod)

from stackquery.helpers import filters
