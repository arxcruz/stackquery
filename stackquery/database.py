from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from stackquery import app

engine = create_engine(app.config['DATABASE_URI'],
                       convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


def init_db(fill_table=False):
    # Creating tables
    from stackquery.models.report import RedHatBugzillaReport
    from stackquery.models.team import Team
    from stackquery.models.user import User

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
        from stackquery.models.release import Release

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
    from stackquery.common import utils
    from stackquery.common import gerrit
    from stackquery.models.project import Project

    filename = app.config['DATA_JSON']
    openstack_projects = gerrit.get_all_gerrit_projects()
    for openstack_project in openstack_projects.keys():
        project = Project()
        project.name = openstack_project
        repos = utils.get_repos_by_module(filename, openstack_project)
        project.git_url = repos['uri']
        db_session.add(project)

    db_session.commit()

Base = declarative_base(name='Base')
Base.query = db_session.query_property()
