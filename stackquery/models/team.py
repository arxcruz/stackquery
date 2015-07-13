from stackquery.database import Base
from stackquery.models import DictSerializable


from sqlalchemy import Column, DateTime, Integer, String, Table
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

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


class Team(Base, DictSerializable):
    '''Team database representation'''
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    name = Column('name', String(200))
    users = relationship('User', secondary=user_team_association)
    projects = relationship('Project', secondary=project_team_association)
