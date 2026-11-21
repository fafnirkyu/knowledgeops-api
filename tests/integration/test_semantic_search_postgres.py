import pytest
from sqlalchemy.orm import Session

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.repositories.document import create_document
from app.repositories.document_chunk import (
    create_document_chunks,
    search_document_chunks,
)
from app.repositories.workspace import create_workspace
from app.schemas.document import DocumentCreate
from app.schemas.workspace import WorkspaceCreate
from app.services.text_chunker import TextChunk


def unit_vector(index: int) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSIONS
    vector[index] = 1.0
    return vector


def test_semantic_search_ranks_and_filters_by_workspace(
    postgres_session: Session,
):
    workspace_a = create_workspace(
        postgres_session,
        WorkspaceCreate(
            name="Search Workspace A",
            description=None,
        ),
    )

    workspace_b = create_workspace(
        postgres_session,
        WorkspaceCreate(
            name="Search Workspace B",
            description=None,
        ),
    )

    document_a = create_document(
        postgres_session,
        workspace_a.id,
        DocumentCreate(
            title="Visible Document",
            content="Visible semantic-search content",
            source_url=None,
        ),
    )

    document_b = create_document(
        postgres_session,
        workspace_b.id,
        DocumentCreate(
            title="Hidden Document",
            content="Content from another workspace",
            source_url=None,
        ),
    )

    try:
        create_document_chunks(
            postgres_session,
            document_a,
            [
                TextChunk(
                    chunk_index=0,
                    content="Exact match",
                    start_offset=0,
                    end_offset=11,
                ),
                TextChunk(
                    chunk_index=1,
                    content="Different topic",
                    start_offset=12,
                    end_offset=27,
                ),
            ],
            [
                unit_vector(0),
                unit_vector(1),
            ],
        )

        create_document_chunks(
            postgres_session,
            document_b,
            [
                TextChunk(
                    chunk_index=0,
                    content="Hidden exact match",
                    start_offset=0,
                    end_offset=18,
                ),
            ],
            [
                unit_vector(0),
            ],
        )

        results = search_document_chunks(
            postgres_session,
            workspace_a.id,
            query_embedding=unit_vector(0),
            limit=2,
        )

        assert len(results) == 2

        assert [
            result.chunk.content
            for result in results
        ] == [
            "Exact match",
            "Different topic",
        ]

        assert results[0].score == pytest.approx(1)
        assert results[1].score == pytest.approx(0)

        assert all(
            result.chunk.document_id == document_a.id
            for result in results
        )

    finally:
        postgres_session.delete(workspace_a)
        postgres_session.delete(workspace_b)
        postgres_session.commit()