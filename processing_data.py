import stackquery.libs.gerrit as gerrit
import stackquery.libs.utils as utils

import logging

LOG = logging.getLogger(__name__)

def main():
    projects = utils.get_projects_being_used()
    LOG.debug('Projects being used: %s' % projects)
    for project in projects:
        gerrit.process_reviews(project)

if __name__ == '__main__':
    main()
