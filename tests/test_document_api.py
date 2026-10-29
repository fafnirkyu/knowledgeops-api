from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.document import create_document, get_document
from app.repositories.workspace import create_workspace
from app.schemas.workspace import WorkspaceCreate
from app.schemas.document import DocumentCreate


def test_create_document(
    api_client: TestClient,
    db_session: Session,
):

    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Research",
            description="Research documents",
        ),
    )

    response = api_client.post(
        f"/workspaces/{workspace.id}/documents",
        json={
            "title": "FastAPI Notes",
            "content": "Notes about request validation",
            "source_url": None,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "FastAPI Notes"
    assert data["content"] == "Notes about request validation"
    assert data["source_url"] is None
    assert data["workspace_id"] == str(workspace.id)

    document_id = UUID(data["id"])
    saved_document = get_document(db_session, document_id)

    assert saved_document is not None
    assert saved_document.workspace_id == workspace.id
    assert saved_document.title == "FastAPI Notes"

def test_create_document_returns_404_for_missing_workspace(
    api_client: TestClient,
):
    missing_workspace_id = uuid4()

    response = api_client.post(
        f"/workspaces/{missing_workspace_id}/documents",
        json={
            "title": "Orphan Document",
            "content": "This document has no workspace",
            "source_url": None,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workspace not found",
    }

def test_list_documents_returns_only_requested_workspace(
    api_client: TestClient,
    db_session: Session,
):
    workspace_a = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Research",
            description="Research documents",
        ),
    )

    workspace_b = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Research",
            description="Research documents",
        ),
    )
    created_document = create_document(
        db_session,
        workspace_a.id,
        DocumentCreate(
            title="Visible",
            content="Visible content",
            source_url=None,
        ),
    )

    response = api_client.get(
        f"/workspaces/{workspace_a.id}/documents"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Visible"
    assert data[0]["workspace_id"] == str(workspace_a.id)

def test_get_document_returns_document(
    api_client: TestClient,
    db_session: Session,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Research",
            description="Research documents",
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

    response = api_client.get(
        f"/documents/{created_document.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(created_document.id)
    assert data["workspace_id"] == str(workspace.id)
    assert data["title"] == "Retrieval Test"
    assert data["content"] == "Test content"

def test_get_document_returns_404_when_missing(
    api_client: TestClient,
):
    missing_document_id = uuid4()

    response = api_client.get(
        f"/documents/{missing_document_id}"
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found",
    }