from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from google.cloud import spanner
from google.cloud.spanner_v1.database import Database
from pydantic import BaseModel, EmailStr, Field, SecretStr

from .utils import get_db, get_password_hash, get_uuid

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class User(BaseModel):
    name: str
    mail: EmailStr
    password: SecretStr = Field(min_length=8, max_length=16)


@router.get("/{user_id}", tags=["users"])
def read_user(user_id: int, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Get user info
    """
    # TODO: get user info from Cloud Spanner
    return JSONResponse(content=jsonable_encoder([{"username": "Rick"}, {"username": "Morty"}]))


@router.post("/", tags=["users"])
def create_user(user: User, db: Database = Depends(get_db)) -> JSONResponse:
    """
    Create user
    """
    hashed_password = get_password_hash(user.password.get_secret_value())
    with db.batch() as batch:
        batch.insert(
            table="Users",
            columns=("UserId", "Name", "Mail", "Password", "CreatedAt", "UpdatedAt"),
            values=[(get_uuid(), user.name, user.mail, hashed_password, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)],
        )
    return JSONResponse(status_code=201, content=jsonable_encoder(user))
