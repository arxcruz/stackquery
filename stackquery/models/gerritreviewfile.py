from stackquery.database import Base
from stackquery.models import DictSerializable

from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import ForeignKey


class GerritReviewFile(Base, DictSerializable):
    __tablename__ = 'gerrit_review_file'
    id = Column(Integer, primary_key=True)
    filename = Column('project', String(500))
    gerrit_review_id = Column(Integer, ForeignKey('gerrit_review.id'))
