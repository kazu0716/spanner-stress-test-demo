from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from pydantic import BaseModel

from .utils import get_db, get_uuid

TABLE: str = "Characters"
CHARACTER_LIMIT = 300

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
def read_rondom_characters(db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get random 300 characters for checking test status
    """
    with db.snapshot() as snapshot:
        query = f"""SELECT Id, Users.Name,CharacterMasters.Name, Kind, {TABLE}.Name, Level, Experience, Strength FROM {TABLE} TABLESAMPLE RESERVOIR (300 ROWS)
                  INNER JOIN Users ON Characters.UserId=Users.UserId
                  INNER JOIN CharacterMasters ON Characters.CharacterId=CharacterMasters.CharacterId"""
        results = list(snapshot.execute_sql(query))
    return JSONResponse(content=jsonable_encoder([CharacterResponse(**dict(zip(CharacterResponse.__fields__.keys(), result))).dict() for result in results]))


@router.get("/{user_id}", tags=["characters"])
def read_character(user_id: int, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get characters of the user
    """
    with db.snapshot() as snapshot:
        query = f"""SELECT Id, Users.Name,CharacterMasters.Name, Kind, {TABLE}.Name, Level, Experience, Strength FROM {TABLE}
                  INNER JOIN Users ON Characters.UserId=Users.UserId
                  INNER JOIN CharacterMasters ON Characters.CharacterId=CharacterMasters.CharacterId WHERE {TABLE}.UserId={user_id}"""
        results = list(snapshot.execute_sql(query))
    if not results:
        raise HTTPException(status_code=404, detail="This user does not have any characters")
    return JSONResponse(content=jsonable_encoder([CharacterResponse(**dict(zip(CharacterResponse.__fields__.keys(), result))).dict() for result in results]))


@ router.post("/", tags=["characters"])
def create_characters(characters: Character, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Create character such as getting a monster 
    """
    with db.snapshot() as snapshot:
        cnt: int = list(snapshot.execute_sql(f"SELECT COUNT(*) FROM {TABLE} WHERE UserId={characters.user_id}"))[0][0]
    # NOTE: avoid to get characters more over CHARACTER_LIMIT, because it become difficult to handle a lot of characters in this game
    if cnt >= CHARACTER_LIMIT:
        return JSONResponse(content=jsonable_encoder({}))
    with db.batch() as batch:
        batch.insert(table=TABLE, columns=("Id", "UserId", "CharacterId", "Name", "Level", "Experience", "Strength", "CreatedAt", "UpdatedAt"),
                     values=[(get_uuid(), characters.user_id, characters.character_id, characters.name, characters.level,
                              characters.experience, characters.experience, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)])
    return JSONResponse(status_code=201, content=jsonable_encoder(characters))
