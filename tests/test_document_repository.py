import uuid

from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.document import (
    create_document,
    get_document,
    list_documents,
)
from app.repositories.workspace import create_workspace
from app.schemas.document import DocumentCreate
from app.schemas.workspace import WorkspaceCreate


def test_create_document_persists_document(db_session: Session):
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

    stored_document = db_session.get(Document, document.id)

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

    # Act:
    documents = list_documents(db_session, workspace_a.id)

    # Assert:
    titles = [document.title for document in documents]

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