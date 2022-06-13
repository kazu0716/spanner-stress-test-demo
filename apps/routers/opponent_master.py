from typing import Union

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(
    prefix="/opponent_master",
    tags=["opponent_master"],
)


class CreateOpponentMaster(BaseModel):
    name: str
    kind: str
    strength: int
    experience: int


class UpdateOpponentMaster(BaseModel):
    name: Union[str, None]
    kind: Union[str, None]
    strength: Union[int, None]
    experience: Union[int, None]


@router.get("/{opponent_id}", tags=["opponent_master"])
def read_opponent_master(opponent_id: int) -> JSONResponse:
    """
    Get opponent master
    """
    # TODO: get opponent master from Cloud Spanner
    return JSONResponse(content=jsonable_encoder([{"username": "Rick"}, {"username": "Morty"}]))


@router.post("/", tags=["opponent_master"])
def create_opponent_master(opponent_master: CreateOpponentMaster) -> JSONResponse:
    """
    Create opponent master
    """
    # TODO: create opponent master and store it to Cloud Spanner
    return JSONResponse(status_code=201, content=jsonable_encoder(opponent_master))


@router.put("/", tags=["opponent_master"])
def update_opponent_master(updates: UpdateOpponentMaster) -> JSONResponse:
    """
    Update opponent master
    """
    # TODO: update opponent master and store it to Cloud Spanner
    return JSONResponse(content=jsonable_encoder(updates))
