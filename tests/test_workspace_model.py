from app.db.base import Base
from app.models.workspace import Workspace


def test_workspace_registers_expected_table():
    assert Workspace.__tablename__ == "workspaces"
    assert "workspaces" in Base.metadata.tables
    assert set(Workspace.__table__.columns.keys()) == {
        "id",
        "name",
        "description",
    }

def test_workspace_column_constraints():
    columns = Workspace.__table__.columns

    assert columns["id"].primary_key is True
    assert columns["id"].nullable is False
    assert columns["id"].default is not None
    assert columns["id"].default.is_callable is True

    assert columns["name"].nullable is False
    assert columns["name"].type.length == 100

    assert columns["description"].nullable is True
    assert columns["description"].type.length == 500
