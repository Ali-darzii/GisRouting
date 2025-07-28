from sqlalchemy import Column, Integer, String, Float
from geoalchemy2 import Geometry

from src.models.base import Base


class GisModel(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    color = Column(String(50), default="#000000")
    geom = Column(Geometry(geometry_type="LINESTRING", srid=4326))
    # for pgRouting
    source = Column(Integer, nullable=True)     
    target = Column(Integer, nullable=True)     
    cost = Column(Float, nullable=True)         
    reverse_cost = Column(Float, nullable=True) 
