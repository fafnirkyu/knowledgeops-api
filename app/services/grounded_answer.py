from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.answer import (
    AnswerCitation,
    AnswerRequest,
    AnswerResponse,
)
from app.schemas.search import SearchRequest
from app.services.answer_prompt import (
    build_grounded_answer_prompt,
)
from app.services.answer_provider import AnswerProvider
from app.services.embedding_provider import EmbeddingProvider
from app.services.semantic_search import search_workspace

INSUFFICIENT_CONTEXT_MESSAGE = (
    "The provided documents do not contain enough "
    "information to answer this question."
)


class InvalidGeneratedAnswer(ValueError):
    pass


def answer_workspace(
    session: Session,
    workspace_id: UUID,
    answer_request: AnswerRequest,
    embedding_provider: EmbeddingProvider,
    answer_provider: AnswerProvider,
) -> AnswerResponse:
    search_request = SearchRequest(
        query=answer_request.query,
        limit=answer_request.limit,
    )

    sources = search_workspace(
        session,
        workspace_id,
        search_request,
        embedding_provider,
    )

    if not sources:
        return AnswerResponse(
            answer=INSUFFICIENT_CONTEXT_MESSAGE,
            citations=[],
            insufficient_context=True,
        )

    prompt = build_grounded_answer_prompt(
        answer_request.query,
        sources,
    )

    generated_answer = answer_provider.generate(
        prompt,
    )

    source_map = {
        f"S{index}": source
        for index, source in enumerate(sources, start=1)
    }

    if generated_answer.insufficient_context:
        return AnswerResponse(
            answer=INSUFFICIENT_CONTEXT_MESSAGE,
            citations=[],
            insufficient_context=True,
        )

    citation_ids = generated_answer.citation_ids

    if not citation_ids:
        raise InvalidGeneratedAnswer(
            "supported answers require at least one citation"
        )

    if len(set(citation_ids)) != len(citation_ids):
        raise InvalidGeneratedAnswer(
            "citation IDs must be unique"
        )

    unknown_ids = [
        source_id
        for source_id in citation_ids
        if source_id not in source_map
    ]

    if unknown_ids:
        raise InvalidGeneratedAnswer(
            f"unknown citation IDs: {', '.join(unknown_ids)}"
        )

    citations = []

    for source_id in citation_ids:
        source = source_map[source_id]

        citations.append(
            AnswerCitation(
                source_id=source_id,
                chunk_id=source.chunk_id,
                document_id=source.document_id,
                chunk_index=source.chunk_index,
                content=source.content,
                score=source.score,
            )
        )

    return AnswerResponse(
        answer=generated_answer.answer,
        citations=citations,
        insufficient_context=False,
    )