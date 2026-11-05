from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.repositories.document import transition_document_status
from app.repositories.document_chunk import create_document_chunks
from app.services.text_chunker import chunk_text


def process_document(
    session: Session,
    document: Document,
    *,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> Document:
    transition_document_status(
        session,
        document,
        DocumentStatus.PROCESSING,
    )

    try:
        chunks = chunk_text(
            document.content,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        create_document_chunks(
            session,
            document,
            chunks,
        )

    except Exception as error:
        session.rollback()

        error_message = (
            str(error).strip()
            or type(error).__name__
        )

        transition_document_status(
            session,
            document,
            DocumentStatus.FAILED,
            processing_error=error_message,
        )

        raise

    return transition_document_status(
        session,
        document,
        DocumentStatus.READY,
    )