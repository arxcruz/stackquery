from stackquery.database import Base
from stackquery.models import DictSerializable

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from datetime import datetime


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
