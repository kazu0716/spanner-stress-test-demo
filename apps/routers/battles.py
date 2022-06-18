from datetime import timedelta
from random import randint, random

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from pydantic import BaseModel

from .utils import epoch_to_datetime, get_db, get_entry_shard_id, get_uuid

OpponentMasters: str = "OpponentMasters"
Characters: str = "Characters"
# NOTE: force to use index in select
BattleHistory: str = "BattleHistory"
BattleHistoryByUserId: str = "@{FORCE_INDEX=BattleHistoryByUserId}"

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
        characters_query = f"SELECT Id, UserId, Level, Experience, Strength FROM {Characters} WHERE Id={battles.character_id}"
        characters = list(snapshot.execute_sql(characters_query))
        opponents_query = f"SELECT OpponentId, Kind, Strength, Experience FROM {OpponentMasters} TABLESAMPLE RESERVOIR (1 ROWS)"
        opponents = list(snapshot.execute_sql(opponents_query))
    if not opponents:
        raise HTTPException(status_code=503, detail="Any opponent masters does not found")
    if not characters:
        raise HTTPException(status_code=404, detail="The character did not found")
    opponent = Opponent(**dict(zip(Opponent.__fields__.keys(), opponents[0])))
    character = Character(**dict(zip(Character.__fields__.keys(), characters[0])))
    # NOTE: battle simple logic
    result: bool = random() <= (character.strength + randint(1, character.strength * randint(1, 10)) / opponent.strength)
    with db.batch() as batch:
        if result:
            batch.update(
                table=Characters,
                columns=("Id", "UserId" , "Level", "Experience", "Strength"),
                # NOTE: simple logic to make a character strong
                values=[(character.id, character.user_id, character.level + int(random() / 0.95), character.experience + opponent.experience,
                         character.strength + randint(0, opponent.experience // 100))],
            )
        entry_shard_id = get_entry_shard_id(character.user_id)
        batch.insert(table=BattleHistory, columns=("BattleHistoryId", "UserId", "Id", "OpponentId", "Result", "EntryShardId", "CreatedAt", "UpdatedAt"),
                     values=[(get_uuid(), character.user_id, character.id, opponent.opponent_id, result, entry_shard_id, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)])
    return JSONResponse(content=jsonable_encoder({"result": result}))


@router.get("/history", tags=["battles"])
def battle_history(user_id: int, since: int, until: int, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Append battle history

    stale read from history table between since and until
    """
    with db.snapshot(exact_staleness=timedelta(seconds=15)) as snapshot:
        query = f"""SELECT UserId, Id, OpponentId,  Result, CreatedAt, UpdatedAt FROM {BattleHistory+BattleHistoryByUserId}
                  WHERE UserId={user_id} AND UpdatedAt>=@Since  AND UpdatedAt<=@Until
                  ORDER BY UpdatedAt DESC LIMIT 300"""
        params = {"Since": epoch_to_datetime(since), "Until": epoch_to_datetime(until)}
        params_type = {"Since": spanner.param_types.TIMESTAMP, "Until": spanner.param_types.TIMESTAMP}
        histories = snapshot.execute_sql(query, params=params, param_types=params_type)
    res = []
    for history in histories:
        result = dict(zip(BattleHistoryResponse.__fields__.keys(), history))
        # NOTE: need datetime to string
        result["created_at"] = result["created_at"].isoformat()
        result["updated_at"] = result["updated_at"].isoformat()
        res.append(BattleHistoryResponse(**result).dict())
    return JSONResponse(content=jsonable_encoder(res))


@router.delete("/history", tags=["battles"])
def delete_all_battle_histories(db: Database = Depends(get_db)) -> JSONResponse:
    db.execute_partitioned_dml(f"DELETE FROM {BattleHistory} WHERE BattleHistoryId > 0")
    return JSONResponse(content=jsonable_encoder({}))
