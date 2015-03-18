from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///dashboard.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db(fill_table=False):
    # Creating tables
    Base.metadata.create_all(bind=engine)

    if fill_table:
        import models

        # Populating Release table
        release = models.Release()
        release.name = 'All'
        db_session.add(release)

        release = models.Release()
        release.name = 'Kilo'
        db_session.add(release)

        release = models.Release()
        release.name = 'Juno'
        db_session.add(release)

        release = models.Release()
        release.name = 'Icehouse'
        db_session.add(release)

        release = models.Release()
        release.name = 'Havana'
        db_session.add(release)

        release = models.Release()
        release.name = 'Grizzly'
        db_session.add(release)

        release = models.Release()
        release.name = 'Folsom'
        db_session.add(release)

        release = models.Release()
        release.name = 'Essex'
        db_session.add(release)

        release = models.Release()
        release.name = 'Diablo'
        db_session.add(release)

        release = models.Release()
        release.name = 'Cactus'
        db_session.add(release)

        release = models.Release()
        release.name = 'Bexar'
        db_session.add(release)

        release = models.Release()
        release.name = 'Austin'
        db_session.add(release)
        db_session.commit()

        # Populating User table
        user1 = models.User()
        user1.name = 'Arx Cruz'
        user1.email = 'arxcruz@test.com'
        user1.user_id = 'arxcruz'
        db_session.add(user1)

        user2 = models.User()
        user2.name = 'David Kranz'
        user2.email = 'david@test.com'
        user2.user_id = 'david-kranz'
        db_session.add(user2)

        user3 = models.User()
        user3.name = 'Arx Cruz Delete'
        user3.email = 'arxcruz@test.com'
        user3.user_id = 'arxcruz'
        db_session.add(user3)
        db_session.commit()

        # Populating team
        team = models.Team()
        team.name = 'Demo team 1'
        team.users.append(user1)
        team.users.append(user2)
        db_session.add(team)

        team = models.Team()
        team.name = 'Demo team 2'
        team.users.append(user1)
        team.users.append(user2)
        db_session.add(team)
        db_session.commit()

        report = models.RedHatBugzillaReport()
        report.name = 'Test'
        report.description = 'Test description'
        report.url = 'http://www.redhat.com'
        db_session.add(report)

        report = models.RedHatBugzillaReport()
        report.name = 'Test'
        report.description = 'Test description'
        report.url = ('http://www.thisisaverybigurl.com/?withalotofinformation'
                      'topassthroughblablablaaasfasfdasfdasfasfdasdfasdfasdfasdf')
        db_session.add(report)
        db_session.commit()
