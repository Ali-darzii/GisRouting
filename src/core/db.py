from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config._config import SETTING
from src.utils.postgres import prepare_connection_string

conn_str = prepare_connection_string(
    SETTING.POSTGRE_HOST,
    SETTING.POSTGRE_PORT,
    SETTING.POSTGRE_USER,
    SETTING.POSTGRE_PASS,
    SETTING.POSTGRE_DB,
)

engine = create_engine(conn_str)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db() -> Generator[Any, Any, None]:
    """Function to inject database as dependency via fastapi functionalities.

    Yields:
        Generator[Any, Any, None]: database session.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()