import uuid

import pytest
from pydantic import ValidationError

from app.schemas.answer import (
    AnswerCitation,
    AnswerRequest,
    AnswerResponse,
    GeneratedAnswer,
)


def test_answer_request_normalizes_query():
    request = AnswerRequest(
        query="  How does semantic search work?  ",
    )

    assert request.query == "How does semantic search work?"
    assert request.limit == 5


@pytest.mark.parametrize(
    "payload",
    [
        {"query": "   "},
        {"query": "question", "limit": 0},
        {"query": "question", "limit": 21},
        {"query": "question", "unexpected": True},
    ],
)
def test_answer_request_rejects_invalid_input(
    payload: dict,
):
    with pytest.raises(ValidationError):
        AnswerRequest(**payload)


def test_generated_answer_accepts_valid_source_ids():
    answer = GeneratedAnswer(
        answer="The system uses cosine distance.",
        citation_ids=["S1", "S3"],
        insufficient_context=False,
    )

    assert answer.citation_ids == ["S1", "S3"]


def test_generated_answer_rejects_invalid_source_id():
    with pytest.raises(ValidationError):
        GeneratedAnswer(
            answer="Unsupported answer",
            citation_ids=[uuid],
            insufficient_context=False,
        )