from typing import Union

from fastapi import APIRouter
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
def read_character_master(character_id: int):
    """
    Get character master
    """
    # TODO: get character master from Cloud Spanner
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.post("/", tags=["character_master"])
def create_characters(character_master: CreateCharacterMaster):
    """
    Create character master
    """
    # TODO: create character master and store it to Cloud Spanner
    return character_master


@router.put("/", tags=["character_master"])
def update_characters(updates: UpdateCharacterMaster):
    """
    Update character master
    """
    # TODO: update character master and store it to Cloud Spanner
    return updates
