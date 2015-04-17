from collections import OrderedDict
from datetime import datetime

from sqlalchemy import Boolean, Column
from sqlalchemy import DateTime, Integer, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

from stackquery.db.database import Base


user_team_association = Table('user_team_association', Base.metadata,
                              Column('user_id', Integer,
                                     ForeignKey('user.id')),
                              Column('team_id', Integer,
                                     ForeignKey('team.id')))

project_team_association = Table('project_team_association', Base.metadata,
                                 Column('project_id', Integer,
                                        ForeignKey('projects.id')),
                                 Column('team_id', Integer,
                                        ForeignKey('team.id')))


class DictSerializable(object):
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result


class Team(Base, DictSerializable):
    '''Team database representation'''
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    name = Column('name', String(200))
    users = relationship('User', secondary=user_team_association)
    projects = relationship('Project', secondary=project_team_association)


class Release(Base, DictSerializable):
    '''Release database representation'''
    __tablename__ = 'release'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    name = Column('name', String(200))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class User(Base, DictSerializable):
    '''User database representation'''
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    name = Column('name', String(200))
    email = Column('email', String(100))
    user_id = Column('user_id', String(20))


class Project(Base, DictSerializable):
    '''List of projects from openstack'''
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column('name', String(200))
    git_url = Column('git_url', String(400))


class RedHatBugzillaReport(Base, DictSerializable):
    '''Custom report representation in database'''
    __tablename__ = 'redhat_bugzilla_report'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    name = Column('name', String(200))
    url = Column('url', Text)
    require_authentication = Column(Boolean, default=False)
    description = Column('description', Text)


class GerritReviewFile(Base, DictSerializable):
    __tablename__ = 'gerrit_review_file'
    id = Column(Integer, primary_key=True)
    filename = Column('project', String(500))
    gerrit_review_id = Column(Integer, ForeignKey('gerrit_review.id'))


class GerritReview(Base, DictSerializable):
    __tablename__ = 'gerrit_review'
    id = Column(Integer, primary_key=True)
    commit_id = Column('commit_id', String(40))
    change_id = Column('change_id', String(40))
    version = Column('version', String(30))
    project = Column('project', String(200))
    sortkey = Column('sortkey', String(50))
    status = Column('status', String(20))
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship('User')
    files = relationship('GerritReviewFile', backref='gerrit_review',
                         lazy='dynamic')
