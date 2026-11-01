import uuid

import pytest
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.repositories.document import (
    InvalidDocumentStatusTransition,
    create_document,
    get_document,
    list_documents,
    transition_document_status,
)
from app.repositories.workspace import create_workspace
from app.schemas.document import DocumentCreate
from app.schemas.workspace import WorkspaceCreate


def _create_processing_test_document(
    db_session: Session,
) -> Document:
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Processing Workspace",
            description=None,
        ),
    )

    return create_document(
        db_session,
        workspace.id,
        DocumentCreate(
            title="Processing Test",
            content="Content that will be processed",
            source_url=None,
        ),
    )


def test_create_document_persists_document(
    db_session: Session,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Research",
            description="Research workspace",
        ),
    )

    document_data = DocumentCreate(
        title="FastAPI Notes",
        content="Notes about request validation",
        source_url="https://fastapi.tiangolo.com/",
    )

    document = create_document(
        db_session,
        workspace.id,
        document_data,
    )

    assert document.id is not None
    assert document.workspace_id == workspace.id
    assert document.title == "FastAPI Notes"
    assert document.content == "Notes about request validation"
    assert document.source_url == "https://fastapi.tiangolo.com/"
    assert document.status is DocumentStatus.PENDING
    assert document.processing_error is None

    stored_document = db_session.get(
        Document,
        document.id,
    )

    assert stored_document is not None
    assert stored_document.id == document.id


def test_list_documents_filters_by_workspace_and_orders_by_title(
    db_session: Session,
):
    workspace_a = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Workspace A",
            description=None,
        ),
    )

    workspace_b = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Workspace B",
            description=None,
        ),
    )

    create_document(
        db_session,
        workspace_a.id,
        DocumentCreate(
            title="Zulu",
            content="Test content",
            source_url=None,
        ),
    )

    create_document(
        db_session,
        workspace_a.id,
        DocumentCreate(
            title="Alpha",
            content="Test content",
            source_url=None,
        ),
    )

    create_document(
        db_session,
        workspace_b.id,
        DocumentCreate(
            title="Hidden",
            content="Test content",
            source_url=None,
        ),
    )

    documents = list_documents(
        db_session,
        workspace_a.id,
    )

    titles = [
        document.title
        for document in documents
    ]

    assert titles == ["Alpha", "Zulu"]
    assert all(
        document.workspace_id == workspace_a.id
        for document in documents
    )


def test_get_document_returns_document_or_none(
    db_session: Session,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Workspace",
            description=None,
        ),
    )

    created_document = create_document(
        db_session,
        workspace.id,
        DocumentCreate(
            title="Retrieval Test",
            content="Test content",
            source_url=None,
        ),
    )

    found_document = get_document(
        db_session,
        created_document.id,
    )

    missing_document = get_document(
        db_session,
        uuid.uuid4(),
    )

    assert found_document is not None
    assert found_document.id == created_document.id
    assert found_document.title == "Retrieval Test"

    assert missing_document is None


def test_transition_document_through_successful_lifecycle(
    db_session: Session,
):
    document = _create_processing_test_document(
        db_session
    )

    assert document.status is DocumentStatus.PENDING
    assert document.processing_error is None

    processing_document = transition_document_status(
        db_session,
        document,
        DocumentStatus.PROCESSING,
    )

    assert (
        processing_document.status
        is DocumentStatus.PROCESSING
    )
    assert processing_document.processing_error is None

    ready_document = transition_document_status(
        db_session,
        processing_document,
        DocumentStatus.READY,
    )

    assert ready_document.status is DocumentStatus.READY
    assert ready_document.processing_error is None

    stored_document = db_session.get(
        Document,
        document.id,
    )

    assert stored_document is not None
    assert stored_document.status is DocumentStatus.READY
    assert stored_document.processing_error is None


def test_failed_document_can_be_retried(
    db_session: Session,
):
    document = _create_processing_test_document(
        db_session
    )

    transition_document_status(
        db_session,
        document,
        DocumentStatus.PROCESSING,
    )

    failed_document = transition_document_status(
        db_session,
        document,
        DocumentStatus.FAILED,
        processing_error="  Chunking failed  ",
    )

    assert failed_document.status is DocumentStatus.FAILED
    assert (
        failed_document.processing_error
        == "Chunking failed"
    )

    retried_document = transition_document_status(
        db_session,
        failed_document,
        DocumentStatus.PROCESSING,
    )

    assert (
        retried_document.status
        is DocumentStatus.PROCESSING
    )
    assert retried_document.processing_error is None


def test_pending_document_cannot_become_ready(
    db_session: Session,
):
    document = _create_processing_test_document(
        db_session
    )

    with pytest.raises(
        InvalidDocumentStatusTransition,
        match=(
            "Cannot transition document "
            "from pending to ready"
        ),
    ):
        transition_document_status(
            db_session,
            document,
            DocumentStatus.READY,
        )

    db_session.refresh(document)

    assert document.status is DocumentStatus.PENDING
    assert document.processing_error is None


@pytest.mark.parametrize(
    "processing_error",
    [None, "", "   "],
)
def test_failed_document_requires_error_message(
    db_session: Session,
    processing_error: str | None,
):
    document = _create_processing_test_document(
        db_session
    )

    transition_document_status(
        db_session,
        document,
        DocumentStatus.PROCESSING,
    )

    assert document.status is DocumentStatus.PROCESSING
    assert document.processing_error is None

    with pytest.raises(
        ValueError,
        match="processing_error is required",
    ):
        transition_document_status(
            db_session,
            document,
            DocumentStatus.FAILED,
            processing_error=processing_error,
        )

    db_session.refresh(document)

    assert document.status is DocumentStatus.PROCESSING
    assert document.processing_error is None