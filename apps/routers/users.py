from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, SecretStr, Field

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

class User(BaseModel):
    name: str
    mail: EmailStr
    password: SecretStr = Field(min_length=8, max_length=16)


@router.get("/", tags=["users"])
def read_user():
    """
    Get user info
    """
    # TODO: get user info from Cloud Spanner
    return [{"username": "Rick"}, {"username": "Morty"}]

@router.post("/", tags=["users"])
def create_user(user: User):
    """
    Create user
    """
    # TODO: create user and store it to Cloud Spanner
    return user