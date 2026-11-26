from unittest.mock import Mock

from app.schemas.answer import GeneratedAnswer
from app.services.outlines_answer_provider import (
    OutlinesAnswerProvider,
)


def test_outlines_answer_provider_generates_validated_answer():
    generator = Mock(
        return_value=(
            '{"answer":"The system uses retrieval.",'
            '"citation_ids":["S1"],'
            '"insufficient_context":false}'
        )
    )

    provider = OutlinesAnswerProvider(
        generator,
        max_tokens=256,
    )

    result = provider.generate(
        "Use source S1 to answer the question."
    )

    assert isinstance(result, GeneratedAnswer)
    assert result.answer == "The system uses retrieval."
    assert result.citation_ids == ["S1"]
    assert result.insufficient_context is False

    generator.assert_called_once_with(
        "Use source S1 to answer the question.",
        max_tokens=256,
        temperature=0.0,
        seed=42,
    )