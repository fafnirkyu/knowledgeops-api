import uuid

import pytest
from pydantic import ValidationError

from app.schemas.search import SearchRequest, SearchResult


def test_search_request_normalizes_query_and_uses_default_limit():
    request = SearchRequest(query="  semantic search  ")

    assert request.query == "semantic search"
    assert request.limit == 5


@pytest.mark.parametrize(
    "payload",
    [
        {"query": "    "},                         # blank after stripping
        {"query": "valid", "limit": 0},      # below minimum
        {"query": "valid", "limit": 21},      # above maximum
        {"query": "valid", "unexpected": True},   # forbidden extra field
    ],
)
def test_search_request_rejects_invalid_payloads(payload):
    with pytest.raises(ValidationError):
        SearchRequest(**payload)


def test_search_result_represents_ranked_chunk():
    chunk_id = uuid.uuid4()
    document_id = uuid.uuid4()

    result = SearchResult(
        chunk_id=chunk_id,
        document_id=document_id,
        chunk_index=2,
        content="Relevant document passage",
        start_offset=100,
        end_offset=126,
        score=0.87,
    )

    assert result.chunk_id == chunk_id
    assert result.document_id == document_id
    assert result.chunk_index == 2
    assert result.score == 0.87