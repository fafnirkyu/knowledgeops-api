from sqlalchemy import Text

from app.db.base import Base
from app.models.document import Document, DocumentStatus
from app.models.workspace import Workspace


def test_document_registers_expected_table():
    assert Document.__tablename__ == "documents"
    assert "documents" in Base.metadata.tables
    assert set(Document.__table__.columns.keys()) == {
        "id",
        "workspace_id",
        "title",
        "content",
        "source_url",
        "status",
        "processing_error",
    }


def test_document_column_constraints():
    columns = Document.__table__.columns

    assert columns["id"].primary_key is True
    assert columns["id"].nullable is False
    assert columns["id"].default is not None
    assert columns["id"].default.is_callable is True

    assert columns["workspace_id"].nullable is False
    assert columns["workspace_id"].index is True

    assert columns["title"].nullable is False
    assert columns["title"].type.length == 200

    assert columns["content"].nullable is False
    assert isinstance(columns["content"].type, Text)

    assert columns["source_url"].nullable is True
    assert columns["source_url"].type.length == 2048
    assert columns["status"].nullable is False
    assert columns["status"].type.enums == [
        status.value for status in DocumentStatus
    ]
    assert (
        columns["status"].default.arg
        is DocumentStatus.PENDING
    )
    assert (
        columns["status"].server_default.arg
        == DocumentStatus.PENDING.value
    )

    assert columns["processing_error"].nullable is True
    assert isinstance(columns["processing_error"].type, Text)


def test_document_workspace_foreign_key():
    foreign_keys = (
        Document.__table__
        .columns["workspace_id"]
        .foreign_keys
    )

    assert len(foreign_keys) == 1

    foreign_key = next(iter(foreign_keys))

    assert foreign_key.target_fullname == "workspaces.id"
    assert foreign_key.ondelete == "CASCADE"


def test_document_workspace_relationship():
    assert (
        Document.workspace.property.back_populates
        == "documents"
    )
    assert (
        Workspace.documents.property.back_populates
        == "workspace"
    )
