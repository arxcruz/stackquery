import os.path

from flask import Flask
from oslo.config import cfg

from stackquery.dashboard.api.rest_api import rest_api
import config
from dashboard import dashboard
from gerritreport.gerrit_reports import gerrit_report
from rhbzreports.rest_api import report_rest_api
from rhbzreports.redhat_bugzilla_report import redhat_bugzilla_report
import filters


def create_app():
    from database import init_db
    init_db(not os.path.isfile('dashboard.db'))

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stackquery.db'
    app.secret_key = 'why would I tell you my secret key?'

    filters.init_app(app)
    app.register_blueprint(dashboard)
    app.register_blueprint(rest_api)
    app.register_blueprint(report_rest_api)
    app.register_blueprint(redhat_bugzilla_report)
    app.register_blueprint(gerrit_report)

    conf = cfg.CONF
    conf.register_opts(config.OPTS)

    conf_file = os.getenv('STACKQUERY_CONF')
    if conf_file and os.path.isfile(conf_file):
        conf(default_config_files=[conf_file])

    app.config['DEBUG'] = cfg.CONF.debug
    return app

app = create_app()

if __name__ == '__main__':
    app.run(cfg.CONF.listen_host, cfg.CONF.listen_port)
