from stackquery.database import Base
from stackquery.models import DictSerializable

from sqlalchemy import Column, DateTime, Integer, String

from datetime import datetime


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
