import uuid
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.schemas.answer import (
    AnswerRequest,
    GeneratedAnswer,
)
from app.schemas.search import SearchResult
from app.services import grounded_answer
from app.services.answer_provider import AnswerProvider
from app.services.embedding_provider import EmbeddingProvider


def test_answer_workspace_maps_valid_citation(
    monkeypatch,
):
    sources = [
        SearchResult(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk_index=0,
            content="The first source is unrelated.",
            start_offset=0,
            end_offset=30,
            score=0.40,
        ),
        SearchResult(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk_index=1,
            content="RAG retrieves relevant document passages.",
            start_offset=31,
            end_offset=72,
            score=0.90,
        ),
    ]

    search_workspace = Mock(
        return_value=sources,
    )

    monkeypatch.setattr(
        grounded_answer,
        "search_workspace",
        search_workspace,
    )

    answer_provider = Mock(spec=AnswerProvider)
    answer_provider.generate.return_value = GeneratedAnswer(
        answer="RAG retrieves relevant passages.",
        citation_ids=["S2"],
        insufficient_context=False,
    )

    session = Mock(spec=Session)
    embedding_provider = Mock(spec=EmbeddingProvider)
    workspace_id = uuid.uuid4()

    response = grounded_answer.answer_workspace(
        session,
        workspace_id,
        AnswerRequest(
            query="How does RAG retrieve information?",
            limit=2,
        ),
        embedding_provider,
        answer_provider,
    )

    assert response.answer == (
        "RAG retrieves relevant passages."
    )
    assert response.insufficient_context is False
    assert len(response.citations) == 1

    citation = response.citations[0]

    assert citation.source_id == "S2"
    assert citation.chunk_id == sources[1].chunk_id
    assert citation.document_id == sources[1].document_id
    assert citation.chunk_index == sources[1].chunk_index
    assert citation.content == sources[1].content
    assert citation.score == sources[1].score

    answer_provider.generate.assert_called_once()

    prompt = answer_provider.generate.call_args.args[0]

    assert "How does RAG retrieve information?" in prompt
    assert '"source_id": "S1"' in prompt
    assert '"source_id": "S2"' in prompt
    assert sources[1].content in prompt


def test_answer_workspace_skips_model_when_no_sources(
    monkeypatch,
):
    search_workspace = Mock(return_value=[])

    monkeypatch.setattr(
        grounded_answer,
        "search_workspace",
        search_workspace,
    )

    session = Mock(spec=Session)
    embedding_provider = Mock(spec=EmbeddingProvider)
    answer_provider = Mock(spec=AnswerProvider)

    response = grounded_answer.answer_workspace(
        session,
        uuid.uuid4(),
        AnswerRequest(
            query="What is missing?",
        ),
        embedding_provider,
        answer_provider,
    )

    assert response.answer == (
        grounded_answer.INSUFFICIENT_CONTEXT_MESSAGE
    )
    assert response.citations == []
    assert response.insufficient_context is True

    answer_provider.generate.assert_not_called()


def test_answer_workspace_uses_fixed_refusal(
    monkeypatch,
):
    sources = [
        SearchResult(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk_index=0,
            content="This passage does not answer the question.",
            start_offset=0,
            end_offset=42,
            score=0.20,
        )
    ]

    monkeypatch.setattr(
        grounded_answer,
        "search_workspace",
        Mock(return_value=sources),
    )

    answer_provider = Mock(spec=AnswerProvider)
    answer_provider.generate.return_value = GeneratedAnswer(
        answer="Some model-written refusal.",
        citation_ids=[],
        insufficient_context=True,
    )

    response = grounded_answer.answer_workspace(
        Mock(spec=Session),
        uuid.uuid4(),
        AnswerRequest(query="What is the answer?"),
        Mock(spec=EmbeddingProvider),
        answer_provider,
    )

    assert response.answer == (
        grounded_answer.INSUFFICIENT_CONTEXT_MESSAGE
    )
    assert response.answer != "Some model-written refusal."
    assert response.citations == []
    assert response.insufficient_context is True

    answer_provider.generate.assert_called_once()


@pytest.mark.parametrize(
    ("citation_ids", "expected_message"),
    [
        (
            [],
            "supported answers require at least one citation",
        ),
        (
            ["S1", "S1"],
            "citation IDs must be unique",
        ),
        (
            ["S99"],
            "unknown citation IDs: S99",
        ),
    ],
)
def test_answer_workspace_rejects_invalid_citations(
    monkeypatch,
    citation_ids: list[str],
    expected_message: str,
):
    sources = [
        SearchResult(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk_index=0,
            content="A retrieved source.",
            start_offset=0,
            end_offset=19,
            score=0.80,
        )
    ]

    monkeypatch.setattr(
        grounded_answer,
        "search_workspace",
        Mock(return_value=sources),
    )

    answer_provider = Mock(spec=AnswerProvider)
    answer_provider.generate.return_value = GeneratedAnswer(
        answer="A supposedly supported answer.",
        citation_ids=citation_ids,
        insufficient_context=False,
    )

    with pytest.raises(
        grounded_answer.InvalidGeneratedAnswer,
        match=expected_message,
    ):
        grounded_answer.answer_workspace(
            Mock(spec=Session),
            uuid.uuid4(),
            AnswerRequest(query="What is the answer?"),
            Mock(spec=EmbeddingProvider),
            answer_provider,
        )