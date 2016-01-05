from stackquery.database import Base
from stackquery.models import DictSerializable

from sqlalchemy import Column, Integer, String


class ScenarioFilter(Base, DictSerializable):
    __tablename__ = 'scenario_filter'
    id = Column(Integer, primary_key=True)
    filter_desc = Column('filter_desc', String(200))
    name = Column('name', String(100))
