import stackquery.libs.gerrit as gerrit
import stackquery.libs.utils as utils

import logging
import argparse

LOG = logging.getLogger(__name__)


def init_argparse():
    parser = argparse.ArgumentParser(description='Processing gerrit changes')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug message', default=False)
    return parser.parse_args()


def main():
    args = init_argparse()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    projects = utils.get_projects_being_used()
    LOG.debug('Projects being used: %s' % projects)
    for project in projects:
        gerrit.process_reviews(project)

if __name__ == '__main__':
    main()
