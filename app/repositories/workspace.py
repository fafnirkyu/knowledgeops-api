from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def list_workspaces(session: Session) -> Sequence[Workspace]:
    statement = select(Workspace).order_by(
        Workspace.name.asc(),
        Workspace.id.asc(),
    )
    return session.scalars(statement).all()


def get_workspace(
    session: Session,
    workspace_id: UUID,
) -> Workspace | None:
    return session.get(Workspace, workspace_id)


def create_workspace(
    session: Session,
    workspace_data: WorkspaceCreate,
) -> Workspace:
    workspace = Workspace(**workspace_data.model_dump())

    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    return workspace


def update_workspace(
    session: Session,
    workspace: Workspace,
    workspace_data: WorkspaceUpdate,
) -> Workspace:
    update_data = workspace_data.model_dump(
        exclude_unset=True
    )

    for field_name, value in update_data.items():
        setattr(workspace, field_name, value)

    session.commit()
    session.refresh(workspace)

    return workspace


def delete_workspace(
    session: Session,
    workspace: Workspace,
) -> None:
    session.delete(workspace)
    session.commit()
