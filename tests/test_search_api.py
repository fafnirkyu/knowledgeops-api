import uuid
from unittest.mock import Mock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.routers import search as search_router
from app.repositories.workspace import create_workspace
from app.schemas.search import SearchRequest, SearchResult
from app.schemas.workspace import WorkspaceCreate
from app.services.embedding_provider import EmbeddingProvider


def test_search_workspace_endpoint(
    api_client: TestClient,
    db_session: Session,
    embedding_provider: EmbeddingProvider,
    monkeypatch,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Search Workspace",
            description=None,
        ),
    )

    chunk_id = uuid.uuid4()
    document_id = uuid.uuid4()

    search_service = Mock(
        return_value=[
            SearchResult(
                chunk_id=chunk_id,
                document_id=document_id,
                chunk_index=0,
                content="Authentication uses signed tokens.",
                start_offset=0,
                end_offset=34,
                score=0.91,
            )
        ]
    )

    monkeypatch.setattr(
        search_router,
        "search_workspace",
        search_service,
    )

    response = api_client.post(
        f"/workspaces/{workspace.id}/search",
        json={
            "query": "authentication tokens",
            "limit": 3,
        },
    )

    assert response.status_code == 200

    search_service.assert_called_once_with(
        db_session,
        workspace.id,
        SearchRequest(
            query="authentication tokens",
            limit=3,
        ),
        embedding_provider,
    )

    assert response.json() == [
        {
            "chunk_id": str(chunk_id),
            "document_id": str(document_id),
            "chunk_index": 0,
            "content": "Authentication uses signed tokens.",
            "start_offset": 0,
            "end_offset": 34,
            "score": 0.91,
        }
    ]

def test_search_missing_workspace_returns_404(
    api_client: TestClient,
    monkeypatch,
):
    search_service = Mock()

    monkeypatch.setattr(
        search_router,
        "search_workspace",
        search_service,
    )

    missing_workspace_id = uuid.uuid4()

    response = api_client.post(
        f"/workspaces/{missing_workspace_id}/search",
        json={
            "query": "authentication tokens",
            "limit": 3,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workspace not found"
    }

    search_service.assert_not_called()
