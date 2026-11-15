from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db_session
from app.repositories.workspace import get_workspace
from app.schemas.search import SearchRequest, SearchResult
from app.services.dependencies import get_embedding_provider
from app.services.embedding_provider import EmbeddingProvider
from app.services.semantic_search import search_workspace

router = APIRouter(tags=["search"])

DbSession = Annotated[
    Session,
    Depends(get_db_session),
]

EmbeddingProviderDependency = Annotated[
    EmbeddingProvider,
    Depends(get_embedding_provider),
]


@router.post(
    "/workspaces/{workspace_id}/search",
    response_model=list[SearchResult],
)
def search_workspace_endpoint(
    workspace_id: UUID,
    search_request: SearchRequest,
    session: DbSession,
    embedding_provider: EmbeddingProviderDependency,
):
    workspace = get_workspace(session, workspace_id)

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    return search_workspace(
        session,
        workspace_id,
        search_request,
        embedding_provider,
    )
