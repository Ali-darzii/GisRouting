from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config._config import SETTING
from src.routes import all_routers


app = FastAPI(root_path=SETTING.ROUTES_PREFIX)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
for router in all_routers:
    app.include_router(router)