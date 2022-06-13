from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/characters",
    tags=["characters"],
)


class CreateCharacters(BaseModel):
    user_id: int
    character_id: int
    name: str
    level: int
    experience: int
    strength: int


class UpdateCharacters(BaseModel):
    id: int
    level: int
    experience: int


@router.get("/{character_id}", tags=["characters"])
def read_characters(character_id: int):
    """
    Get characters
    """
    # TODO: get characters from Cloud Spanner
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.post("/", tags=["characters"])
def create_characters(characters: CreateCharacters):
    """
    Create character status
    """
    # TODO: create characters and store it to Cloud Spanner
    return characters


@router.put("/", tags=["characters"])
def update_characters(updates: UpdateCharacters):
    """
    Update character status
    """
    # TODO: update characters and store it to Cloud Spanner
    return updates
