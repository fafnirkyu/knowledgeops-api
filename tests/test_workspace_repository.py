import uuid

from sqlalchemy.orm import Session

from app.repositories.workspace import (
    create_workspace,
    get_workspace,
    list_workspaces,
    update_workspace
)
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def test_create_workspace_persists_workspace(db_session: Session):
    data = WorkspaceCreate(
        name="Research",
        description="Research documents",
    )

    created = create_workspace(db_session, data)
    stored = get_workspace(db_session, created.id)

    assert created.id is not None
    assert stored is not None
    assert stored.id == created.id
    assert stored.name == "Research"
    assert stored.description == "Research documents"


def test_get_workspace_returns_none_for_missing_id(db_session: Session):
    missing_id = uuid.uuid4()

    assert get_workspace(db_session, missing_id) is None


def test_list_workspaces_returns_alphabetical_order(db_session: Session):
    create_workspace(
        db_session,
        WorkspaceCreate(name="Zulu"),
    )
    create_workspace(
        db_session,
        WorkspaceCreate(name="Alpha"),
    )

    workspaces = list_workspaces(db_session)
    names = [workspace.name for workspace in workspaces]

    assert names == ["Alpha", "Zulu"]

def test_update_workspace_changes_only_supplied_fields(
    db_session: Session,
):
    workspace = create_workspace(
    db_session,
    WorkspaceCreate(
        name="Research",
        description="Original description",
    ),
)

    workspace_id = workspace.id
    updated_workspace = update_workspace(
    db_session,
    workspace,
    WorkspaceUpdate(description="Updated description"),
)
    workspace_id = workspace.id
    assert updated_workspace.id == workspace_id
    assert updated_workspace.name == "Research"
    assert updated_workspace.description == "Updated description"
    saved_workspace = get_workspace(
    db_session,
    workspace_id,
)

    assert saved_workspace is not None
    assert saved_workspace.description == "Updated description"