from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    CheckConstraint,
    Integer,
    Text,
    UniqueConstraint,
)

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.db.base import Base
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


def test_document_chunk_registers_expected_table():
    assert DocumentChunk.__tablename__ == "document_chunks"
    assert "document_chunks" in Base.metadata.tables

    assert set(DocumentChunk.__table__.columns.keys()) == {
        "id",
        "document_id",
        "chunk_index",
        "content",
        "start_offset",
        "end_offset",
        "embedding",
    }


def test_document_chunk_column_constraints():
    columns = DocumentChunk.__table__.columns

    assert columns["id"].primary_key is True
    assert columns["id"].nullable is False
    assert columns["id"].default is not None
    assert columns["id"].default.is_callable is True
    assert columns["document_id"].nullable is False
    assert columns["chunk_index"].nullable is False
    assert isinstance(columns["chunk_index"].type, Integer)
    assert columns["content"].nullable is False
    assert isinstance(columns["content"].type, Text)
    assert columns["start_offset"].nullable is False
    assert isinstance(columns["start_offset"].type, Integer)
    assert columns["end_offset"].nullable is False
    assert isinstance(columns["end_offset"].type, Integer)
    assert columns["embedding"].nullable is True
    assert isinstance(
        columns["embedding"].type,
        VECTOR,
    )
    assert columns["embedding"].type.dim == EMBEDDING_DIMENSIONS


def test_document_chunk_document_foreign_key():
    foreign_keys = (
        DocumentChunk.__table__
        .columns["document_id"]
        .foreign_keys
    )

    assert len(foreign_keys) == 1

    foreign_key = next(iter(foreign_keys))

    assert foreign_key.target_fullname == "documents.id"
    assert foreign_key.ondelete == "CASCADE"


def test_document_chunk_table_constraints():
    constraints = {
        constraint.name: constraint
        for constraint in DocumentChunk.__table__.constraints
        if constraint.name
    }

    assert set(constraints) == {
        "uq_document_chunks_document_id_chunk_index",
        "ck_document_chunks_chunk_index_nonnegative",
        "ck_document_chunks_start_offset_nonnegative",
        "ck_document_chunks_valid_offsets",
    }

    unique_constraint = constraints[
        "uq_document_chunks_document_id_chunk_index"
    ]

    assert isinstance(
        unique_constraint,
        UniqueConstraint,
    )
    assert tuple(unique_constraint.columns.keys()) == (
        "document_id",
        "chunk_index",
    )

    expected_checks = {
        "ck_document_chunks_chunk_index_nonnegative":
            "chunk_index >= 0",
        "ck_document_chunks_start_offset_nonnegative":
            "start_offset >= 0",
        "ck_document_chunks_valid_offsets":
            "end_offset > start_offset",
    }

    for name, expected_expression in expected_checks.items():
        constraint = constraints[name]

        assert isinstance(constraint, CheckConstraint)
        assert str(constraint.sqltext) == expected_expression


def test_document_chunk_relationship():
    chunk_relationship = DocumentChunk.document.property
    document_relationship = Document.chunks.property

    assert chunk_relationship.back_populates == "chunks"
    assert document_relationship.back_populates == "document"

    assert document_relationship.passive_deletes is True
    assert "delete-orphan" in document_relationship.cascade

    assert tuple(document_relationship.order_by) == (
        DocumentChunk.__table__.columns["chunk_index"],
    )
