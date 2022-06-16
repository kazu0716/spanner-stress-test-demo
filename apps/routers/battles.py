from random import randint, random

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from pydantic import BaseModel

from .utils import get_db, get_entry_shard_id, get_uuid

OpponentMasters: str = "OpponentMasters"
Characters: str = "Characters"
BattleHistory: str = "BattleHistory"

router = APIRouter(
    prefix="/battles",
    tags=["battles"],
)


class Battles(BaseModel):
    character_id: int


class BattleHistoryResponse(BaseModel):
    user_id: int
    character_id: int
    opponent_id: int
    result: bool
    created_at: str
    updated_at: str


class Opponent(BaseModel):
    opponent_id: int
    kind: str
    strength: int
    experience: int


class Character(BaseModel):
    id: int
    user_id: int
    level: int
    experience: int
    strength: int


@router.post("/", tags=["battles"])
def battles(battles: Battles, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Battles against opponents
    """
    with db.snapshot(multi_use=True) as snapshot:
        query = f"SELECT Id, UserId, Level, Experience, Strength FROM {Characters} WHERE Id={battles.character_id}"
        characters = list(snapshot.execute_sql(query))
        key_set = spanner.KeySet(all_=True)
        opponents = list(snapshot.read(table=OpponentMasters, columns=("OpponentId", "Kind", "Strength", "Experience"), keyset=key_set))
    opponent = Opponent(**dict(zip(Opponent.__fields__.keys(), opponents[randint(0, len(opponents) - 1)])))
    if not characters:
        raise HTTPException(status_code=404, detail="The character did not found")
    character = Character(**dict(zip(Character.__fields__.keys(), characters[0])))
    # NOTE: battle simple logic
    result: bool = random() <= (character.strength + randint(1, character.strength * randint(1, 10)) / opponent.strength)
    with db.batch() as batch:
        if result:
            # TODO: process then win
            pass
        entry_shard_id = get_entry_shard_id(character.user_id)
        batch.insert(table=BattleHistory, columns=("BattleHistoryId", "UserId", "Id", "OpponentId", "Result", "EntryShardId", "CreatedAt", "UpdatedAt"),
                     values=[(get_uuid(), character.user_id, character.id, opponent.opponent_id, result, entry_shard_id, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)])
    return JSONResponse(content=jsonable_encoder({"result": result}))


# @ router.get("/history", tags=["battles"])
# def battle_history(user_id: int, since: int, until: int) -> JSONResponse:
#     """
#     Append battle history
#     """
#     # TODO: create battle history and store it to Cloud Spanner by stale read
#     return JSONResponse(content=jsonable_encoder())
