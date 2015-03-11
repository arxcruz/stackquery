from collections import OrderedDict
from datetime import datetime

from sqlalchemy import Boolean, Column
from sqlalchemy import DateTime, Integer, String, Table, Text
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class DictSerializable(object):
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

user_team_association = Table('user_team_association', Base.metadata,
                              Column('user_id', Integer,
                                     ForeignKey('user.id')),
                              Column('team_id', Integer,
                                     ForeignKey('team.id')))


class Team(Base, DictSerializable):
    '''Team database representation'''
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    name = Column('name', String(200))
    users = relationship('User', secondary=user_team_association)


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
