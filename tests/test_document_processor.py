import pytest
from sqlalchemy.orm import Session

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.models.document import DocumentStatus
from app.repositories.document import create_document
from app.repositories.workspace import create_workspace
from app.schemas.document import DocumentCreate
from app.schemas.workspace import WorkspaceCreate
from app.services.document_processor import process_document
from app.services.embedding_provider import EmbeddingProvider


def test_process_document_completes_successfully(
    db_session: Session,
    embedding_provider: EmbeddingProvider,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Processing Workspace",
            description=None,
        ),
    )

    document = create_document(
        db_session,
        workspace.id,
        DocumentCreate(
            title="Processing Test",
            content="ABCDEFGHIJ",
            source_url=None,
        ),
    )

    processed_document = process_document(
        db_session,
        document,
        embedding_provider=embedding_provider,
        chunk_size=4,
        overlap=1,
    )

    assert processed_document.status is DocumentStatus.READY
    assert processed_document.processing_error is None

    assert [
        chunk.content
        for chunk in processed_document.chunks
    ] == [
        "ABCD",
        "DEFG",
        "GHIJ",
    ]

    assert all(
        chunk.embedding is not None
        for chunk in processed_document.chunks
    )

    assert all(
        len(chunk.embedding) == EMBEDDING_DIMENSIONS
        for chunk in processed_document.chunks
    )

    assert [
        chunk.embedding[0]
        for chunk in processed_document.chunks
    ] == [
        4,
        4,
        4,
    ]


def test_process_document_records_failure(
    db_session: Session,
    embedding_provider: EmbeddingProvider,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Failure Workspace",
            description=None,
        ),
    )

    document = create_document(
        db_session,
        workspace.id,
        DocumentCreate(
            title="Failure Test",
            content="ABCDEFGHIJ",
            source_url=None,
        ),
    )

    expected_error = "overlap must be smaller than chunk_size"

    with pytest.raises(
        ValueError,
        match=expected_error,
    ):
        process_document(
            db_session,
            document,
            embedding_provider=embedding_provider,
            chunk_size=4,
            overlap=4,
        )

    assert document.status is DocumentStatus.FAILED
    assert document.processing_error == expected_error
    assert document.chunks == []


def test_retrying_failed_document(
    db_session: Session,
    embedding_provider: EmbeddingProvider,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Processing Workspace",
            description=None,
        ),
    )

    document = create_document(
        db_session,
        workspace.id,
        DocumentCreate(
            title="Processing Test",
            content="ABCDEFGHIJ",
            source_url=None,
        ),
    )

    with pytest.raises(ValueError):
        process_document(
            db_session,
            document,
            embedding_provider=embedding_provider,
            chunk_size=4,
            overlap=4,
        )

    assert document.status is DocumentStatus.FAILED

    retried_document = process_document(
        db_session,
        document,
        embedding_provider=embedding_provider,
        chunk_size=4,
        overlap=1,
    )

    assert retried_document.status is DocumentStatus.READY
    assert retried_document.processing_error is None
    assert len(retried_document.chunks) == 3