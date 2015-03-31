from oslo.config import cfg

import logging

LOG = logging.getLogger(__name__)

from stackquery.common import gerrit
from stackquery.common import utils
from stackquery.db.models import Project
from stackquery.db.models import RedHatBugzillaReport
from stackquery.db.models import Release
from stackquery.db.models import Team
from stackquery.db.models import User
from stackquery.db.session import Base
from stackquery.db.session import db_session
from stackquery.db.session import engine


def init_db(fill_table=False):
    # Creating tables
    Base.metadata.create_all(bind=engine)

    if fill_table:
        _populate_project_table()
        _populate_release_table()

        # Populating User table
        user1 = User()
        user1.name = 'Arx Cruz'
        user1.email = 'arxcruz@test.com'
        user1.user_id = 'arxcruz'
        db_session.add(user1)

        user2 = User()
        user2.name = 'David Kranz'
        user2.email = 'david@test.com'
        user2.user_id = 'david-kranz'
        db_session.add(user2)

        user3 = User()
        user3.name = 'Arx Cruz Delete'
        user3.email = 'arxcruz@test.com'
        user3.user_id = 'arxcruz'
        db_session.add(user3)
        db_session.commit()

        # Populating team
        team = Team()
        team.name = 'Demo team 1'
        team.users.append(user1)
        team.users.append(user2)
        db_session.add(team)

        team = Team()
        team.name = 'Demo team 2'
        team.users.append(user1)
        team.users.append(user2)
        db_session.add(team)
        db_session.commit()

        report = RedHatBugzillaReport()
        report.name = 'Test'
        report.description = 'Test description'
        report.url = 'http://www.redhat.com'
        db_session.add(report)

        report = RedHatBugzillaReport()
        report.name = 'Test'
        report.description = 'Test description'
        report.url = ('http://www.thisisaverybigurl.com/?withalotofinformation'
                      'topassthroughblablablaaasfasfdasfdasfasfdasdfasdfasdfa')
        db_session.add(report)
        db_session.commit()


def _populate_release_table():
        # Populating Release table
        release = Release()
        release.name = 'All'
        db_session.add(release)

        release = Release()
        release.name = 'Kilo'
        db_session.add(release)

        release = Release()
        release.name = 'Juno'
        db_session.add(release)

        release = Release()
        release.name = 'Icehouse'
        db_session.add(release)

        release = Release()
        release.name = 'Havana'
        db_session.add(release)

        release = Release()
        release.name = 'Grizzly'
        db_session.add(release)

        release = Release()
        release.name = 'Folsom'
        db_session.add(release)

        release = Release()
        release.name = 'Essex'
        db_session.add(release)

        release = Release()
        release.name = 'Diablo'
        db_session.add(release)

        release = Release()
        release.name = 'Cactus'
        db_session.add(release)

        release = Release()
        release.name = 'Bexar'
        db_session.add(release)

        release = Release()
        release.name = 'Austin'
        db_session.add(release)

        db_session.commit()


def _populate_project_table():

    filename = cfg.CONF.data_json

    openstack_projects = gerrit.get_all_gerrit_projects()
    for openstack_project in openstack_projects.keys():
        LOG.debug('Creating project: %s' % openstack_project)
        project = Project()
        project.name = openstack_project
        repos = utils.get_repos_by_module(filename, openstack_project)
        project.git_url = repos['uri']
        db_session.add(project)

    db_session.commit()
