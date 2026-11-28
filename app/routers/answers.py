from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db_session
from app.repositories.workspace import get_workspace
from app.schemas.answer import AnswerRequest, AnswerResponse
from app.services.answer_provider import AnswerProvider
from app.services.dependencies import (
    get_answer_provider,
    get_embedding_provider,
)
from app.services.embedding_provider import EmbeddingProvider
from app.services.grounded_answer import (
    InvalidGeneratedAnswer,
    answer_workspace,
)

router = APIRouter(tags=["answers"])

DbSession = Annotated[
    Session,
    Depends(get_db_session),
]

EmbeddingProviderDependency = Annotated[
    EmbeddingProvider,
    Depends(get_embedding_provider),
]

AnswerProviderDependency = Annotated[
    AnswerProvider,
    Depends(get_answer_provider),
]


@router.post(
    "/workspaces/{workspace_id}/answer",
    response_model=AnswerResponse,
)
def answer_workspace_endpoint(
    workspace_id: UUID,
    answer_request: AnswerRequest,
    session: DbSession,
    embedding_provider: EmbeddingProviderDependency,
    answer_provider: AnswerProviderDependency,
):
    workspace = get_workspace(
        session,
        workspace_id,
    )

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    try:
        return answer_workspace(
            session,
            workspace_id,
            answer_request,
            embedding_provider,
            answer_provider,
        )
    except InvalidGeneratedAnswer as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Answer provider returned an invalid response",
        ) from error