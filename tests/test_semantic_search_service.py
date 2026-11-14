import uuid
from unittest.mock import Mock

from sqlalchemy.orm import Session

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk import RankedDocumentChunk
from app.schemas.search import SearchRequest
from app.services import semantic_search
from app.services.embedding_provider import EmbeddingProvider


def test_search_workspace_embeds_query_and_maps_results(
    monkeypatch,
):
    workspace_id = uuid.uuid4()
    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()

    query_embedding = (
        [1.0]
        + [0.0] * (EMBEDDING_DIMENSIONS - 1)
    )

    provider = Mock(spec=EmbeddingProvider)
    provider.dimensions = EMBEDDING_DIMENSIONS
    provider.embed.return_value = [query_embedding]

    session = Mock(spec=Session)

    chunk = DocumentChunk(
        id=chunk_id,
        document_id=document_id,
        chunk_index=2,
        content="Authentication uses signed tokens.",
        start_offset=100,
        end_offset=134,
        embedding=query_embedding,
    )

    repository_search = Mock(
        return_value=[
            RankedDocumentChunk(
                chunk=chunk,
                score=0.9,
            )
        ]
    )

    monkeypatch.setattr(
        semantic_search,
        "search_document_chunks",
        repository_search,
    )

    request = SearchRequest(
        query="  authentication tokens  ",
        limit=3,
    )

    results = semantic_search.search_workspace(
        session,
        workspace_id,
        request,
        provider,
    )

    provider.embed.assert_called_once_with(
        ["authentication tokens"]
    )

    repository_search.assert_called_once_with(
        session,
        workspace_id,
        query_embedding=query_embedding,
        limit=request.limit,
    )

    assert len(results) == 1

    result = results[0]

    assert result.chunk_id == chunk_id
    assert result.document_id == document_id
    assert result.chunk_index == 2
    assert result.content == "Authentication uses signed tokens."
    assert result.start_offset == 100
    assert result.end_offset == 134
    assert result.score == 0.9