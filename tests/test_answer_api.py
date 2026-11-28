import uuid
from unittest.mock import Mock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.workspace import create_workspace
from app.routers import answers as answer_router
from app.schemas.answer import (
    AnswerCitation,
    AnswerRequest,
    AnswerResponse,
)
from app.schemas.workspace import WorkspaceCreate
from app.services.answer_provider import AnswerProvider
from app.services.embedding_provider import EmbeddingProvider
from app.services.grounded_answer import InvalidGeneratedAnswer


def test_answer_workspace_endpoint(
    api_client: TestClient,
    db_session: Session,
    embedding_provider: EmbeddingProvider,
    answer_provider: AnswerProvider,
    monkeypatch,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Answer Workspace",
            description=None,
        ),
    )

    chunk_id = uuid.uuid4()
    document_id = uuid.uuid4()

    expected_response = AnswerResponse(
        answer="The system uses cosine similarity.",
        citations=[
            AnswerCitation(
                source_id="S1",
                chunk_id=chunk_id,
                document_id=document_id,
                chunk_index=0,
                content="Semantic search uses cosine similarity.",
                score=0.91,
            )
        ],
        insufficient_context=False,
    )

    answer_service = Mock(
        return_value=expected_response,
    )

    monkeypatch.setattr(
        answer_router,
        "answer_workspace",
        answer_service,
    )

    response = api_client.post(
        f"/workspaces/{workspace.id}/answer",
        json={
            "query": "How does semantic search work?",
            "limit": 3,
        },
    )

    assert response.status_code == 200

    answer_service.assert_called_once_with(
        db_session,
        workspace.id,
        AnswerRequest(
            query="How does semantic search work?",
            limit=3,
        ),
        embedding_provider, 
        answer_provider,
    )

    assert response.json() == expected_response.model_dump(
        mode="json",
    )

def test_answer_missing_workspace_returns_404(
    api_client: TestClient,
    monkeypatch,
):
    answer_service = Mock()

    monkeypatch.setattr(
        answer_router,
        "answer_workspace",
        answer_service,
    )

    missing_workspace_id = uuid.uuid4()

    response = api_client.post(
        f"/workspaces/{missing_workspace_id}/answer",
        json={
            "query": "How does semantic search work?",
            "limit": 3,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workspace not found"
    }

    answer_service.assert_not_called()


def test_invalid_generated_answer_returns_502(
    api_client: TestClient,
    db_session: Session,
    monkeypatch,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Invalid Answer Workspace",
            description=None,
        ),
    )

    answer_service = Mock(
        side_effect=InvalidGeneratedAnswer(
            "unknown citation IDs: S99"
        ),
    )

    monkeypatch.setattr(
        answer_router,
        "answer_workspace",
        answer_service,
    )

    response = api_client.post(
        f"/workspaces/{workspace.id}/answer",
        json={
            "query": "How does semantic search work?",
            "limit": 3,
        },
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Answer provider returned an invalid response"
    }