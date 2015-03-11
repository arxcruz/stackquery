from flask import Flask

from api.rest_api import rest_api
from dashboard import dashboard
from rhbzreports.rest_api import report_rest_api
from rhbzreports.redhat_bugzilla_report import redhat_bugzilla_report

import filters

import os.path


def create_app():
    if not os.path.isfile('dashboard.db'):
        from database import init_db
        init_db()

    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stackquery.db'
    app.secret_key = 'why would I tell you my secret key?'

    # db.init_app(app)
    filters.init_app(app)
    app.register_blueprint(dashboard)
    app.register_blueprint(rest_api)
    app.register_blueprint(report_rest_api)
    app.register_blueprint(redhat_bugzilla_report)

    return app

app = create_app()

if __name__ == '__main__':

    app.run()
