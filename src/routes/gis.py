from fastapi.routing import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import status
from typing import Dict, List
from shapely.geometry import LineString

from src.core.db import get_db
from src.schema.gis import ConnectedLinesSchema, GisSchema, GisNode
from src.crud.gis import GisCrud
from src.models.gis import GisModel

router = APIRouter(prefix="/gis")
crud = GisCrud(GisModel)


@router.post(
    "",
    response_model=GisModel,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
def create_gis(body: GisSchema, db: Session = Depends(get_db)) -> GisModel:
    color = "#" + color
    return crud.crete_gis(
        db,
        LineString(
            [
                (body.lng_source,body.lat_source),
                (body.lng_destination, body.lat_destination),
            ]
        ),
        body.color
    )


@router.get(
    "/{color}",
    response_model=List[GisNode],
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
def get_5_best_by_color(
    color: str, params: GisSchema = Depends(), db: Session = Depends(get_db)
) -> List[GisNode]:
    color = "#" + color
    return crud.find_best_5_route_by_color(db, params, color)


@router.get(
    "/best/{color}",
    response_model=List[GisNode],
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
def get_5_best_by_color(
    color: str, params: GisSchema = Depends(), db: Session = Depends(get_db)
) -> List[GisNode]:
    color = "#" + color
    return crud.find_shortest_route_by_color(db, params, color)


@router.get(
    "/connected-lines/",
    response_model=Dict[int, List[ConnectedLinesSchema]],
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
def get_all_connected_lines(
    db: Session = Depends(get_db),
) -> Dict[int, List[ConnectedLinesSchema]]:
    return crud.get_all_connected_lines(db)


@router.get(
    "/connected-lines/{color}",
    response_model=Dict[int, List[ConnectedLinesSchema]],
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
def get_all_connected_lines_by_color(
    color: str, db: Session = Depends(get_db)
) -> Dict[int, List[ConnectedLinesSchema]]:
    color = "#" + color
    return crud.get_all_connected_lines_by_color(db, color)
