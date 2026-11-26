import uuid

from app.schemas.search import SearchResult
from app.services.answer_prompt import (
    build_grounded_answer_prompt,
)


def test_build_grounded_answer_prompt_labels_sources():
    sources = [
        SearchResult(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk_index=0,
            content="RAG retrieves relevant document passages.",
            start_offset=0,
            end_offset=41,
            score=0.90,
        ),
        SearchResult(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk_index=1,
            content="Generated answers must cite their evidence.",
            start_offset=42,
            end_offset=87,
            score=0.80,
        ),
    ]

    prompt = build_grounded_answer_prompt(
        "How does the system answer questions?",
        sources,
    )

    assert "How does the system answer questions?" in prompt
    assert '"source_id": "S1"' in prompt
    assert '"source_id": "S2"' in prompt
    assert sources[0].content in prompt
    assert sources[1].content in prompt

    normalized_prompt = prompt.lower()

    assert "untrusted evidence" in normalized_prompt
    assert "do not guess" in normalized_prompt