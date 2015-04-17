from stackquery.database import Base
from stackquery.models import DictSerializable

from sqlalchemy import Column, Integer, String

from datetime import datetime


class Project(Base, DictSerializable):
    '''List of projects from openstack'''
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column('name', String(200))
    git_url = Column('git_url', String(400))
