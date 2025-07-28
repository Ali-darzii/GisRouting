from fastapi.routing import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from shapely.geometry import Point
from geoalchemy2.shape import from_shape

from src.core.db import get_db
from src.schema.gis import GisByColorSchema
from src.crud.gis import GisCrud
from src.models.gis import GisModel


router = APIRouter(prefix="/gis")
crud = GisCrud(GisModel)

@router.get("/{color}")
def get_by_color(
    color:str,
    GisSchema:GisByColorSchema,
    db: Session = Depends(get_db)
    
) -> list:
    return crud.find_route(
        db,
        GisSchema,
        color
    )
