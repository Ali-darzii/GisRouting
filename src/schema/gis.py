from pydantic import BaseModel, field_validator, model_validator
from typing import List, Literal

class GisSchema(BaseModel):
    lat_source:float
    lng_source:float
    lat_destination:float
    lng_destination:float
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
    
    @field_validator('lat_source', 'lng_source', 'lat_destination', 'lng_destination', mode='before')
    @classmethod
    def convert_to_float(cls, v):
        try:
            return float(v)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid float value: {v}")


class GeometrySchema(BaseModel):
    coordinates: List[List[float]]


class PropertiesSchema(BaseModel):
    id: int
    source: int
    target: int
    color: str
    cost: float
    reverse_cost: float
    seq: int
    segment_cost: float
    agg_cost: float


class GisNode(BaseModel):
    properties: PropertiesSchema
    geometry: GeometrySchema


class ConnectedLinesSchema(BaseModel):
    id: int
    color: str
    geom: dict  # <- match this to query result
    source: int
    target: int
    cost: float
    reverse_cost: float