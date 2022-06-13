from typing import Union

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(
    prefix="/character_master",
    tags=["character_master"],
)


class CreateCharacterMaster(BaseModel):
    name: str
    kind: str


class UpdateCharacterMaster(BaseModel):
    name: Union[str, None]
    kind: Union[str, None]


@router.get("/{character_id}", tags=["character_master"])
def read_character_master(character_id: int) -> JSONResponse:
    """
    Get character master
    """
    # TODO: get character master from Cloud Spanner
    return JSONResponse(content=jsonable_encoder([{"username": "Rick"}, {"username": "Morty"}]))


@router.post("/", tags=["character_master"])
def create_character_master(character_master: CreateCharacterMaster) -> JSONResponse:
    """
    Create character master
    """
    # TODO: create character master and store it to Cloud Spanner
    return JSONResponse(status_code=201, content=jsonable_encoder(character_master))


@router.put("/", tags=["character_master"])
def update_character_master(updates: UpdateCharacterMaster) -> JSONResponse:
    """
    Update character master
    """
    # TODO: update character master and store it to Cloud Spanner
    return JSONResponse(content=jsonable_encoder(updates))
