from stackquery.database import Base
from stackquery.models import DictSerializable
from stackquery.models.user import User
from stackquery.models.gerritreviewfile import GerritReviewFile

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from datetime import datetime


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
