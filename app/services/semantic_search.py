from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.document_chunk import search_document_chunks
from app.schemas.search import SearchRequest, SearchResult
from app.services.embedding_provider import EmbeddingProvider
from app.services.text_embedder import embed_texts


def search_workspace(
    session: Session,
    workspace_id: UUID,
    search_request: SearchRequest,
    embedding_provider: EmbeddingProvider,
) -> list[SearchResult]:
    embeddings = embed_texts(
        provider=embedding_provider,
        texts=[search_request.query],
    )

    query_embedding = embeddings[0]

    ranked_chunks = search_document_chunks(
        session,
        workspace_id,
        query_embedding=query_embedding,
        limit=search_request.limit,
    )

    return [
        SearchResult(
            chunk_id=ranked_chunk.chunk.id,
            document_id=ranked_chunk.chunk.document_id,
            chunk_index=ranked_chunk.chunk.chunk_index,
            content=ranked_chunk.chunk.content,
            start_offset=ranked_chunk.chunk.start_offset,
            end_offset=ranked_chunk.chunk.end_offset,
            score=ranked_chunk.score,
        )
        for ranked_chunk in ranked_chunks
    ]