from sqlalchemy import URL, Engine, create_engine

from app.core.config import Settings


def build_database_url(settings: Settings) -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
    )


def create_db_engine(settings: Settings) -> Engine:
    engine_url = build_database_url(settings)
    engine = create_engine(engine_url, pool_pre_ping=True)
    return engine
