import os
from collections.abc import Generator, Sequence
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from rq import Queue
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models
from app.core.embedding import EMBEDDING_DIMENSIONS
from app.db.base import Base
from app.db.dependencies import get_db_session
from app.db.session import create_session_factory
from app.jobs.queue import get_document_queue
from app.main import app
from app.services.answer_provider import AnswerProvider
from app.services.dependencies import (
    get_answer_provider,
    get_embedding_provider,
)
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
            ]
            + [0.0] * (self.dimensions - 1)
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
def postgres_session() -> Generator[Session, None, None]:
    if os.getenv("RUN_POSTGRES_TESTS") != "1":
        pytest.skip(
            "PostgreSQL integration tests are disabled"
        )

    dependency = get_db_session()
    session = next(dependency)

    try:
        yield session
    finally:
        dependency.close()


@pytest.fixture
def embedding_provider() -> EmbeddingProvider:
    return DeterministicEmbeddingProvider()


@pytest.fixture
def answer_provider() -> AnswerProvider:
    return Mock(spec=AnswerProvider)


@pytest.fixture
def document_queue() -> Queue:
    return Mock(spec=Queue)


@pytest.fixture
def api_client(
    db_session: Session,
    embedding_provider: EmbeddingProvider,
    answer_provider: AnswerProvider,
    document_queue: Queue,
) -> Generator[TestClient, None, None]:
    def override_get_db_session():
        yield db_session

    def override_get_embedding_provider():
        return embedding_provider

    def override_get_answer_provider():
        return answer_provider

    def override_get_document_queue():
        return document_queue

    app.dependency_overrides[get_db_session] = (
        override_get_db_session
    )
    app.dependency_overrides[get_embedding_provider] = (
        override_get_embedding_provider
    )
    app.dependency_overrides[get_answer_provider] = (
        override_get_answer_provider
    )
    app.dependency_overrides[get_document_queue] = (
        override_get_document_queue
    )

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(
        get_db_session,
        None,
    )
    app.dependency_overrides.pop(
        get_embedding_provider,
        None,
    )
    app.dependency_overrides.pop(
        get_answer_provider,
        None,
    )
    app.dependency_overrides.pop(
        get_document_queue,
        None,
    )