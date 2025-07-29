from fastapi.routing import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import status
from typing import List

from src.core.db import get_db
from src.schema.gis import GisSchema, GisNode
from src.crud.gis import GisCrud
from src.models.gis import GisModel

router = APIRouter(prefix="/gis")
crud = GisCrud(GisModel)

@router.get("/{color}", response_model=List[GisNode], status_code=status.HTTP_200_OK, response_model_by_alias=False)
def get_5_best_by_color(
    color:str,
    params: GisSchema = Depends(),
    db: Session = Depends(get_db)
    
) -> List[GisNode]:
    color = "#" + color
    return crud.find_best_5_route_by_color(
        db,
        params,
        color
    )
@router.get("best/{color}", response_model=List[GisNode], status_code=status.HTTP_200_OK, response_model_by_alias=False)
def get_5_best_by_color(
    color:str,
    params: GisSchema = Depends(),
    db: Session = Depends(get_db)
    
) -> List[GisNode]:
    color = "#" + color
    return crud.find_shortest_route_by_color(
        db,
        params,
        color
    )