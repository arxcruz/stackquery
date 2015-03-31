from stackquery.common import gerrit
from stackquery.dashboard import config
from oslo.config import cfg

import logging


def main():
    conf = cfg.CONF
    conf.register_opts(config.OPTS)
    projects = ['openstack/nova', 'stackforge/rally', 'openstack/tempest']
    logging.basicConfig(level='DEBUG')
    for project in projects:
        gerrit.process_reviews(project)

if __name__ == '__main__':
    main()
