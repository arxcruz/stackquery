from flask import Flask


__version__ = "0.4"

app = Flask(__name__)

app.config.from_object('websiteconfig')

app.secret_key = 'why would I tell you my secret key?'

from stackquery.dashboard import dashboard
from stackquery.dashboard.api import rest_api
from stackquery.dashboard import filters

filters.init_app(app)

app.register_blueprint(dashboard.dashboard)
app.register_blueprint(rest_api.rest_api)
