from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.text_chunker import TextChunk


@dataclass(frozen=True)
class RankedDocumentChunk:
    chunk: DocumentChunk
    score: float


def create_document_chunks(
    session: Session,
    document: Document,
    chunks: list[TextChunk],
    embeddings: list[list[float]],
) -> list[DocumentChunk]:
    stored_chunks = [
        DocumentChunk(
            document_id=document.id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            start_offset=chunk.start_offset,
            end_offset=chunk.end_offset,
            embedding=embedding,
        )
        for chunk, embedding in zip(
            chunks,
            embeddings,
            strict=True,
        )
    ]

    session.add_all(stored_chunks)
    session.commit()

    for stored_chunk in stored_chunks:
        session.refresh(stored_chunk)

    return stored_chunks


def search_document_chunks(
    session: Session,
    workspace_id: UUID,
    query_embedding: list[float],
    limit: int,
) -> list[RankedDocumentChunk]:
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")
    statement = (
        select(
            DocumentChunk,
            distance,
        )
        .join(
            Document,
            DocumentChunk.document_id == Document.id,
        )
        .where(
            Document.workspace_id == workspace_id,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance.asc())
        .limit(limit)
    )
    rows = session.execute(statement).all()
    return [
        RankedDocumentChunk(
            chunk=chunk,
            score=1.0 - float(distance_value),
        )
        for chunk, distance_value in rows
    ]