from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/battles",
    tags=["battles"],
)


class Battles(BaseModel):
    character_id: int


class BattleHistory(BaseModel):
    user_id: int
    character_id: int
    opponent_id: int
    result: bool


@router.post("/", tags=["battles"])
def battles(battles: Battles) -> bool:
    """
    Battles opponents logic
    """
    # TODO: create battles and store it to Cloud Spanner
    print(battles)
    return {True}


@router.post("/history", tags=["battles"])
def battle_history(battle_history: BattleHistory):
    """
    Append battle history
    """
    # TODO: create battle history and store it to Cloud Spanner
    return battle_history
