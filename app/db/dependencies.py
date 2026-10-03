from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import create_db_engine, create_session_factory

settings = Settings()
engine = create_db_engine(settings)
session_factory = create_session_factory(engine)


def get_db_session() -> Generator[Session, None, None]:
    with session_factory() as session:
        yield session
