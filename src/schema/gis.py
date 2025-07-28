from pydantic import BaseModel, field_validator, model_validator


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
        
    
class GisByColorSchema(GisSchema):
    color:str
    