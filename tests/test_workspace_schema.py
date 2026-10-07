import uuid

import pytest
from pydantic import ValidationError

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate


def test_workspace_create_strips_name_and_defaults_description():
    workspace = WorkspaceCreate(name="  Research  ")

    assert workspace.name == "Research"
    assert workspace.description is None


def test_workspace_create_rejects_client_provided_id():
    payload = {
        "id": uuid.uuid4(),
        "name": "Research",
    }

    with pytest.raises(ValidationError):
        WorkspaceCreate.model_validate(payload)


def test_workspace_read_accepts_orm_object():
    workspace_id = uuid.uuid4()
    workspace = Workspace(
        id=workspace_id,
        name="Research",
        description="Research documents",
    )

    result = WorkspaceRead.model_validate(workspace)

    assert result.id == workspace_id
    assert result.name == "Research"
    assert result.description == "Research documents"


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "   "},
        {"name": "x" * 101},
        {"name": "Research", "description": "x" * 501},
    ],
)
def test_workspace_create_rejects_invalid_payload(payload):
    with pytest.raises(ValidationError):
        WorkspaceCreate.model_validate(payload)


def test_workspace_update_excludes_omitted_fields():
    workspace_update = WorkspaceUpdate(
        description="Updated description"
    )

    update_data = workspace_update.model_dump(
        exclude_unset=True
    )

    assert update_data == {
        "description": "Updated description"
    }


def test_workspace_update_rejects_null_name():
    with pytest.raises(ValidationError):
        WorkspaceUpdate(name=None)
