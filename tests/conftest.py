from collections.abc import Generator, Sequence

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models
from app.core.embedding import EMBEDDING_DIMENSIONS
from app.db.base import Base
from app.db.dependencies import get_db_session
from app.db.session import create_session_factory
from app.main import app
from app.services.dependencies import get_embedding_provider
from app.services.embedding_provider import EmbeddingProvider


class DeterministicEmbeddingProvider:
    dimensions = EMBEDDING_DIMENSIONS

    def embed(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        return [
            [
                float(len(text)),
            ] + [
                0.0
            ] * (self.dimensions - 1)
            for text in texts
        ]


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    session_factory = create_session_factory(engine)

    with session_factory() as session:
        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def api_client(
    db_session: Session,
    embedding_provider: EmbeddingProvider,
) -> Generator[TestClient, None, None]:
    def override_get_db_session():
        yield db_session
    def override_get_embedding_provider():
        return embedding_provider

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_embedding_provider] = override_get_embedding_provider

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_db_session, None)
    app.dependency_overrides.pop(get_embedding_provider, None)

@pytest.fixture
def embedding_provider() -> EmbeddingProvider:
    return DeterministicEmbeddingProvider()