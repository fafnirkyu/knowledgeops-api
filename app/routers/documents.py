from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db_session
from app.repositories.document import (
    create_document,
    get_document,
    list_documents,
)
from app.repositories.workspace import get_workspace
from app.schemas.document import DocumentCreate, DocumentRead

router = APIRouter(tags=["documents"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/workspaces/{workspace_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document_endpoint(
    workspace_id: UUID,
    document_data: DocumentCreate,
    session: DbSession,
):
    workspace = get_workspace(session, workspace_id)

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    return create_document(
        session,
        workspace_id,
        document_data,
    )


@router.get(
    "/workspaces/{workspace_id}/documents",
    response_model=list[DocumentRead],
)
def read_documents(
    workspace_id: UUID,
    session: DbSession,
):
    workspace = get_workspace(session, workspace_id)

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    return list_documents(
        session,
        workspace_id,
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentRead,
)
def read_document(
    document_id: UUID,
    session: DbSession,
):
    document = get_document(session, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document