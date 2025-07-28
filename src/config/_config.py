import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    DOTENV_PATH: str = os.path.join(os.path.dirname(__file__), ".env")

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        env_file_encoding="utf-8",
    )
    
    POSTGRE_HOST: str
    POSTGRE_PORT: str
    POSTGRE_USER: str
    POSTGRE_PASS: str
    POSTGRE_DB: str
    
    ROUTES_PREFIX:str = "/api"
    
SETTING = Setting()