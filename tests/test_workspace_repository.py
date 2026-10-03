import uuid

from sqlalchemy.orm import Session

from app.repositories.workspace import (
    create_workspace,
    get_workspace,
    list_workspaces,
)
from app.schemas.workspace import WorkspaceCreate


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
