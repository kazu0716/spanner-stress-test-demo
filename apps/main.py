from fastapi import FastAPI

from routers.characters import router as characters_router
from routers.users import router as user_router

app = FastAPI()
app.include_router(user_router, prefix="/api/v1")
app.include_router(characters_router, prefix="/api/v1")
