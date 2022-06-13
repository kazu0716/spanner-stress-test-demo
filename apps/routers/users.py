from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, SecretStr

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class User(BaseModel):
    name: str
    mail: EmailStr
    password: SecretStr = Field(min_length=8, max_length=16)


@router.get("/{user_id}", tags=["users"])
def read_user(id: int) -> JSONResponse:
    """
    Get user info
    """
    # TODO: get user info from Cloud Spanner
    return JSONResponse(content=jsonable_encoder([{"username": "Rick"}, {"username": "Morty"}]))


@router.post("/", tags=["users"])
def create_user(user: User) -> JSONResponse:
    """
    Create user
    """
    # TODO: create user and store it to Cloud Spanner
    return JSONResponse(status_code=201, content=jsonable_encoder(user))
