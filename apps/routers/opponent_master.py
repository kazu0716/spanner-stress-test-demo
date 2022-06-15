from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from pydantic import BaseModel

from .utils import get_db, get_uuid

TABLE: str = "OpponentMasters"

router = APIRouter(
    prefix="/opponent_master",
    tags=["opponent_master"],
)


class OpponentMaster(BaseModel):
    name: str
    kind: str
    strength: int
    experience: int


class OpponentMasterResponse(BaseModel):
    opponent_id: int
    name: str
    kind: str
    strength: int
    experience: int


@router.get("/", tags=["opponent_master"])
def read_all_opponent_masters(db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get all opponent masters
    """
    with db.snapshot() as snapshot:
        keyset = spanner.KeySet(all_=True)
        results = snapshot.read(table=TABLE, columns=("OpponentId", "Name", "Kind", "Strength", "Experience"), keyset=keyset)
    return JSONResponse(content=jsonable_encoder([OpponentMasterResponse(opponent_id=result[0], name=result[1], kind=result[2], strength=result[3], experience=result[4]).dict() for result in results]))


@router.get("/{opponent_id}", tags=["opponent_master"])
def read_opponent_master(opponent_id: int, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get a opponent master
    """
    with db.snapshot() as snapshot:
        query = f"SELECT OpponentId, Name, Kind, Strength, Experience From {TABLE} WHERE OpponentId={opponent_id}"
        results = list(snapshot.execute_sql(query))
    if not results:
        return JSONResponse(content=jsonable_encoder({}))
    return JSONResponse(content=jsonable_encoder(OpponentMasterResponse(opponent_id=results[0][0], name=results[0][1], kind=results[0][2], strength=results[0][3], experience=results[0][4])))


@ router.post("/", tags=["opponent_master"])
def create_opponent_master(opponent_master: OpponentMaster, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Create opponent master
    """
    with db.batch() as batch:
        batch.insert(
            table=TABLE,
            columns=("OpponentId", "Name", "Kind", "Strength", "Experience", "CreatedAt", "UpdatedAt"),
            values=[(get_uuid(), opponent_master.name, opponent_master.kind, opponent_master.strength,
                     opponent_master.experience, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)])
    return JSONResponse(status_code=201, content=jsonable_encoder(opponent_master))


@router.delete("/", tags=["opponent_master"])
def delete_opponent_master(db: Database = Depends(get_db)) -> JSONResponse:
    db.execute_partitioned_dml(f"DELETE FROM {TABLE} WHERE OpponentId > 0")
    return JSONResponse(content=jsonable_encoder({}))
