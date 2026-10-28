from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.document import create_document
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