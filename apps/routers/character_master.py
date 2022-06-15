from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from pydantic import BaseModel

from .utils import get_db, get_uuid

TABLE: str = "CharacterMasters"

router = APIRouter(
    prefix="/character_master",
    tags=["character_master"],
)


class CharacterMaster(BaseModel):
    name: str
    kind: str


class CharacterMasterRespose(BaseModel):
    character_master_id: int
    name: str
    kind: str


@router.get("/", tags=["character_master"])
def read_character_master(db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get all character masters
    """
    with db.snapshot() as snapshot:
        keyset = spanner.KeySet(all_=True)
        results = snapshot.read(table=TABLE, columns=("CharacterId", "Name", "Kind"), keyset=keyset)
    return JSONResponse(content=jsonable_encoder([CharacterMasterRespose(character_master_id=result[0], name=result[1], kind=result[2]).dict() for result in results]))


@router.get("/{character_id}", tags=["character_master"])
def read_all_character_masters(character_id: int, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get a character master
    """
    with db.snapshot() as snapshot:
        query = f"SELECT CharacterId, Name, Kind From {TABLE} WHERE CharacterId={character_id}"
        results = list(snapshot.execute_sql(query))
    if not results:
        return JSONResponse(content=jsonable_encoder({}))
    return JSONResponse(content=jsonable_encoder(CharacterMasterRespose(character_master_id=results[0][0], name=results[0][1], kind=results[0][2])))


@router.post("/", tags=["character_master"])
def create_character_master(character_master: CharacterMaster, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Create a character master
    """
    with db.batch() as batch:
        batch.insert(
            table=TABLE,
            columns=("CharacterId", "Name", "Kind", "CreatedAt", "UpdatedAt"),
            values=[(get_uuid(), character_master.name, character_master.kind, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)],
        )
    return JSONResponse(status_code=201, content=jsonable_encoder(character_master))


@router.delete("/", tags=["character_master"])
def delete_character_masters(db: Database = Depends(get_db)) -> JSONResponse:
    db.execute_partitioned_dml(f"DELETE FROM {TABLE} WHERE CharacterId > 0")
    return JSONResponse(content=jsonable_encoder({}))
