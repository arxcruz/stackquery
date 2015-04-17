import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_URI = 'sqlite:///%s' % os.path.join(_basedir, 'dashboard.db')
DATABASE_CONNECT_OPTIONS = {}

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 5000

SECRET_KEY = 'herpaderp'

DATA_JSON = '%s' % os.path.join(_basedir, 'etc/default_data.json')

del os