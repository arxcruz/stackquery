from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from stackquery import app

engine = create_engine(app.config['DATABASE_URI'],
                       convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


user1 = None
user2 = None


def init_db(args=None):
    Base.metadata.create_all(bind=engine)

    if args:
        if args.all or args.projects:
            _populate_project_table()
        if args.all or args.release:
            _populate_release_table()
        if args.all or args.user:
            _populate_user_table()
        if args.all or args.team:
            _populate_team_table()
        if args.all or args.report:
            _populate_report_table()
        if args.all or args.filters:
            _populate_filters_table()


def _populate_team_table():
    from stackquery.models.team import Team
    _drop_and_recreate_tables('user_team_association')
    _drop_and_recreate_tables('project_team_association')
    _drop_and_recreate_tables('team')

    _populate_user_table()

    team = Team()
    team.name = 'Demo team 1'
    if user1 and user2:
        team.users.append(user1)
        team.users.append(user2)
    db_session.add(team)

    team = Team()
    team.name = 'Demo team 2'
    if user1 and user2:
        team.users.append(user1)
        team.users.append(user2)

    db_session.add(team)
    db_session.commit()


def _populate_user_table():
    from stackquery.models.user import User

    _drop_and_recreate_tables('user')

    global user1
    user1 = User()
    user1.name = 'Arx Cruz'
    user1.email = 'arxcruz@test.com'
    user1.user_id = 'arxcruz'
    db_session.add(user1)

    global user2
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


def _populate_report_table():
    from stackquery.models.report import RedHatBugzillaReport

    _drop_and_recreate_tables('redhat_bugzilla_report')

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

        _drop_and_recreate_tables('releases')

        release = Release()
        release.name = 'All'
        db_session.add(release)

        release = Release()
        release.name = 'Liberty'
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
    from stackquery.models.project import Project
    _drop_and_recreate_tables('projects')

    project = Project()
    project.name = 'openstack/tempest'
    project.git_url = 'git.openstack.org/openstack/tempest.git'
    project.gerrit_server = 'https://review.openstack.org'
    db_session.add(project)

    project = Project()
    project.name = 'openstack/rally'
    project.git_url = 'git://git.openstack.org/openstack/rally.git'
    project.gerrit_server = 'https://review.openstack.org'
    db_session.add(project)

    project = Project()
    project.name = 'redhat-openstack/khaleesi'
    project.git_url = 'git@github.com:redhat-openstack/khaleesi.git'
    project.gerrit_server = 'https://review.gerrithub.io'
    db_session.add(project)

    db_session.commit()


def _populate_filters_table():
    from stackquery.models.filter import ScenarioFilter

    _drop_and_recreate_tables('scenario_filter')

    filters = ScenarioFilter()
    filters.name = 'Tempest scenario'
    filters.filter_desc = 'file:tempest/scenario.*'
    db_session.add(filters)

    filters = ScenarioFilter()
    filters.name = 'Rally scenario'
    filters.filter_desc = 'file:rally/benchmark/scenarios.*'
    db_session.add(filters)

    db_session.commit()


def _drop_and_recreate_tables(table_name):
    table = Base.metadata.tables[table_name]
    Base.metadata.drop_all(bind=engine, tables=[table])
    Base.metadata.create_all(bind=engine)

Base = declarative_base(name='Base')
Base.query = db_session.query_property()
