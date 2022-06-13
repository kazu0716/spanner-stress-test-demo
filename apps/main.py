from fastapi import FastAPI

from routers.character_master import router as character_master_router
from routers.characters import router as characters_router
from routers.opponent_master import router as opponent_master_router
from routers.users import router as user_router

app = FastAPI()
prefix_v1 = "/api/v1"
app.include_router(user_router, prefix=prefix_v1)
app.include_router(characters_router, prefix=prefix_v1)
app.include_router(character_master_router, prefix=prefix_v1)
app.include_router(opponent_master_router, prefix=prefix_v1)
