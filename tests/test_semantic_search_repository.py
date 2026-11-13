import uuid
from unittest.mock import Mock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk import search_document_chunks


def test_search_document_chunks_converts_distance_to_similarity():
    workspace_id = uuid.uuid4()

    chunk = DocumentChunk(
        document_id=uuid.uuid4(),
        chunk_index=0,
        content="Relevant passage",
        start_offset=0,
        end_offset=16,
        embedding=[0.0] * EMBEDDING_DIMENSIONS,
    )

    session = Mock(spec=Session)
    session.execute.return_value.all.return_value = [
        (chunk, 0.25),
    ]

    results = search_document_chunks(
        session,
        workspace_id,
        [0.0] * EMBEDDING_DIMENSIONS,
        limit=5,
    )

    assert len(results) == 1

    result = results[0]

    assert result.chunk is chunk
    assert result.score == pytest.approx(0.75)


def test_search_document_chunks_builds_pgvector_query():
    session = Mock(spec=Session)
    session.execute.return_value.all.return_value = []

    search_document_chunks(
        session,
        uuid.uuid4(),
        [0.0] * EMBEDDING_DIMENSIONS,
        limit=5,
    )

    statement = session.execute.call_args.args[0]

    compiled_sql = str(
        statement.compile(
            dialect=postgresql.dialect(),
        )
    )
    assert "document_chunks.embedding <=> " in compiled_sql
    assert "JOIN documents" in compiled_sql
    assert "documents.workspace_id" in compiled_sql
    assert "document_chunks.embedding IS NOT NULL" in compiled_sql
    assert "ORDER BY distance ASC" in compiled_sql
    assert "LIMIT" in compiled_sql