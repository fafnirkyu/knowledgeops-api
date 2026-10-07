from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.dependencies import get_db_session
from app.main import app
from app.repositories.workspace import get_workspace, create_workspace
from app.schemas.workspace import WorkspaceCreate


def test_create_workspace(db_session: Session):
    def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)

    try:
        response = client.post(
            "/workspaces",
            json={
                "name": "Engineering",
                "description": "Engineering documentation",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Engineering"
        assert data["description"] == "Engineering documentation"
        workspace_id = UUID(data["id"])
        assert str(workspace_id) == data["id"]
        saved_workspace = get_workspace(db_session, workspace_id)
        assert saved_workspace is not None
        assert saved_workspace.name == "Engineering"
        assert saved_workspace.description == "Engineering documentation"
    finally:
        app.dependency_overrides.pop(get_db_session, None)


def test_list_workspaces(db_session: Session):
    create_workspace(
        db_session,
        WorkspaceCreate(name="Zulu", description=None),
    )
    create_workspace(
        db_session,
        WorkspaceCreate(
            name="Alpha",
            description="First workspace",
        ),
    )

    def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)

    try:
        response = client.get("/workspaces")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        names = [workspace["name"] for workspace in data]
        assert names == ["Alpha", "Zulu"]
    finally:
        app.dependency_overrides.pop(get_db_session, None)

def test_get_workspace(db_session: Session):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Research",
            description="Research documents",
        ),
    )

    def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)

    try:
        response = client.get(f"/workspaces/{workspace.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(workspace.id)
        assert data["name"] == "Research"
        assert data["description"] == "Research documents"
    finally:
        app.dependency_overrides.pop(get_db_session, None)

def test_get_missing_workspace_returns_404(db_session: Session):
    def override_get_db_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db_session
    client = TestClient(app)

    try:
        missing_workspace_id = UUID(
            "00000000-0000-0000-0000-000000000001"
        )
        response = client.get(f"/workspaces/{missing_workspace_id}")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Workspace not found"
        }
    finally:
        app.dependency_overrides.pop(get_db_session, None)

def test_create_workspace_rejects_blank_name(
    api_client: TestClient,
):
    response = api_client.post(
    "/workspaces",
    json={
        "name": "   ",
        "description": "Invalid workspace",
    },
)
    assert response.status_code == 422

def test_update_workspace(
    api_client: TestClient,
    db_session: Session,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Research",
            description="Original description",
        ),
    )

    response = api_client.patch(
        f"/workspaces/{workspace.id}",
        json={
            "description": "Updated description",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(workspace.id)
    assert data["name"] == "Research"
    assert data["description"] == "Updated description"


def test_update_missing_workspace_returns_404(
    api_client: TestClient,
):
    missing_workspace_id = UUID(
        "00000000-0000-0000-0000-000000000001"
    )

    response = api_client.patch(
        f"/workspaces/{missing_workspace_id}",
        json={
            "description": "Updated description",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workspace not found"
    }

def test_delete_workspace(
    api_client: TestClient,
    db_session: Session,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Temporary",
            description="Delete this workspace",
        ),
    )
    workspace_id = workspace.id

    response = api_client.delete(
        f"/workspaces/{workspace_id}"
    )

    assert response.status_code == 204
    assert response.content == b""

    deleted_workspace = get_workspace(
        db_session,
        workspace_id,
    )
    assert deleted_workspace is None


def test_delete_missing_workspace_returns_404(
    api_client: TestClient,
):
    missing_workspace_id = UUID(
        "00000000-0000-0000-0000-000000000001"
    )

    response = api_client.delete(
        f"/workspaces/{missing_workspace_id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Workspace not found"
    }