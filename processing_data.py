import stackquery.libs.gerrit as gerrit
from stackquery.models.project import Project

import logging
import argparse

LOG = logging.getLogger(__name__)


def init_argparse():
    parser = argparse.ArgumentParser(description='Processing gerrit changes')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug message', default=False)
    parser.add_argument('--project', help='Run for an specific project',
                        default=None)
    return parser.parse_args()


def main():
    args = init_argparse()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if args.project:
        projects = [Project.query.filter_by(name=args.project).first()]
    else:
        projects = Project.query.all()

    if len(projects) is 0:
        print 'Project not found'

    for project in projects:
        gerrit.process_reviews(project)

if __name__ == '__main__':
    main()
