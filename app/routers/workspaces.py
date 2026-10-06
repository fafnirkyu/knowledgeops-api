from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db_session
from app.repositories.workspace import (
    create_workspace,
    get_workspace,
    list_workspaces,
)
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead

router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"],
)

DbSession = Annotated[Session, Depends(get_db_session)]

@router.get("", response_model=list[WorkspaceRead])
def read_workspaces(session: DbSession):
    return list_workspaces(session)

@router.get("/{workspace_id}", response_model=WorkspaceRead)
def read_workspace(workspace_id: UUID, session: DbSession):
    workspace = get_workspace(session, workspace_id)
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return workspace

@router.post(
    "",
    response_model=WorkspaceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_workspace_endpoint(
    workspace_data: WorkspaceCreate,
    session: DbSession,
):
    workspace = create_workspace(session, workspace_data)
    return workspace