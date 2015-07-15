from stackquery.database import Base
from stackquery.models import DictSerializable

from sqlalchemy import Column, Integer, String, Text


class Harvester(Base, DictSerializable):
    '''List of projects from openstack'''
    __tablename__ = 'harvester'
    id = Column(Integer, primary_key=True)
    name = Column('name', String(200))
    url = Column('url', String(400))
    description = Column('description', Text)
