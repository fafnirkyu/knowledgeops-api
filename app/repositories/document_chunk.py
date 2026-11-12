from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.text_chunker import TextChunk


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