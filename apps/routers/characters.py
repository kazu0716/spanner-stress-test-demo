from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from pydantic import BaseModel

from .utils import get_db, get_password_hash, get_uuid

TABLE: str = "Characters"

router = APIRouter(
    prefix="/characters",
    tags=["characters"],
)


class Character(BaseModel):
    user_id: int
    character_id: int
    name: str
    level: int
    experience: int
    strength: int


class CharacterResponse(BaseModel):
    id: int
    user_name: str
    character_name: str
    kind: str
    nick_name: str
    level: int
    experience: int
    strength: int


@router.get("/", tags=["characters"])
def read_all_characters(db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get all characters
    """
    with db.snapshot() as snapshot:
        query = f"SELECT Id, Users.Name,CharacterMasters.Name, Kind, {TABLE}.Name, Level, Experience, Strength FROM {TABLE}\
                  INNER JOIN Users ON Characters.UserId=Users.UserId\
                  INNER JOIN CharacterMasters ON Characters.CharacterId=CharacterMasters.CharacterId"
        results = list(snapshot.execute_sql(query))
    return JSONResponse(content=jsonable_encoder([CharacterResponse(**dict(zip(CharacterResponse.__fields__.keys(), result))).dict() for result in results]))


@router.get("/{character_id}", tags=["characters"])
def read_character(character_id: int, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get a character
    """
    with db.snapshot() as snapshot:
        query = f"SELECT Id, Users.Name,CharacterMasters.Name, Kind, {TABLE}.Name, Level, Experience, Strength FROM {TABLE}\
                  INNER JOIN Users ON Characters.UserId=Users.UserId\
                  INNER JOIN CharacterMasters ON Characters.CharacterId=CharacterMasters.CharacterId WHERE Id={character_id}"
        results = list(snapshot.execute_sql(query))
    if not results:
        return JSONResponse(content=jsonable_encoder({}))
    return JSONResponse(content=jsonable_encoder(CharacterResponse(**dict(zip(CharacterResponse.__fields__.keys(), results[0])))))


@ router.post("/", tags=["characters"])
def create_characters(characters: Character, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Create character status
    """
    with db.batch() as batch:
        batch.insert(table=TABLE, columns=("Id", "UserId", "CharacterId", "Name", "Level", "Experience", "Strength", "CreatedAt", "UpdatedAt"),
                     values=[(get_uuid(), characters.user_id, characters.character_id, characters.name, characters.level,
                              characters.experience, characters.experience, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)])
    return JSONResponse(status_code=201, content=jsonable_encoder(characters))
