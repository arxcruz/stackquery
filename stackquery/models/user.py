from stackquery.database import Base
from stackquery.models import DictSerializable

from sqlalchemy import Column, DateTime, Integer, String

from datetime import datetime


class User(Base, DictSerializable):
    '''User database representation'''
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    name = Column('name', String(200))
    email = Column('email', String(100))
    user_id = Column('user_id', String(20))
