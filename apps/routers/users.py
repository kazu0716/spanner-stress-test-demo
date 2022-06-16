from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from pydantic import BaseModel, EmailStr, Field, SecretStr

from .utils import get_db, get_password_hash, get_uuid

TABLE: str = "Users"

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class User(BaseModel):
    name: str
    mail: EmailStr
    password: SecretStr = Field(min_length=8, max_length=16)


class UserResponse(BaseModel):
    user_id: str
    name: str
    mail: EmailStr


@router.get("/", tags=["users"])
def read_all_users(db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get all users
    """
    with db.snapshot() as snapshot:
        keyset = spanner.KeySet(all_=True)
        results = snapshot.read(table=TABLE, columns=("UserId", "Name", "Mail"), keyset=keyset, limit=10000)
    return JSONResponse(content=jsonable_encoder([UserResponse(user_id=result[0], name=result[1], mail=result[2]).dict() for result in results]))


@router.get("/{user_id}", tags=["users"])
def read_user(user_id: str, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get a user
    """
    with db.snapshot() as snapshot:
        query = f"SELECT UserId, Name, Mail From {TABLE} WHERE UserId={user_id}"
        results = list(snapshot.execute_sql(query))
    if not results:
        return JSONResponse(content=jsonable_encoder({}))
    return JSONResponse(content=jsonable_encoder(UserResponse(user_id=results[0][0], name=results[0][1], mail=results[0][2])))


@router.post("/", tags=["users"])
def create_user(user: User, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Create user
    """
    hashed_password = get_password_hash(user.password.get_secret_value())
    with db.batch() as batch:
        batch.insert(
            table=TABLE,
            columns=("UserId", "Name", "Mail", "Password", "CreatedAt", "UpdatedAt"),
            values=[(get_uuid(), user.name, user.mail, hashed_password, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)],
        )
    return JSONResponse(status_code=201, content=jsonable_encoder(user))


@router.delete("/", tags=["users"])
def delete_all_users(db: Database = Depends(get_db)) -> JSONResponse:
    db.execute_partitioned_dml(f"DELETE FROM {TABLE} WHERE UserId > 0")
    return JSONResponse(content=jsonable_encoder({}))
