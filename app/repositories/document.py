import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentCreate


class InvalidDocumentStatusTransition(ValueError):
    pass


ALLOWED_STATUS_TRANSITIONS = {
    DocumentStatus.PENDING: frozenset({
        DocumentStatus.PROCESSING,
    }),
    DocumentStatus.PROCESSING: frozenset({
        DocumentStatus.READY,
        DocumentStatus.FAILED,
    }),
    DocumentStatus.FAILED: frozenset({
        DocumentStatus.PROCESSING,
    }),
    DocumentStatus.READY: frozenset(),
}


def create_document(
    session: Session,
    workspace_id: uuid.UUID,
    document_data: DocumentCreate,
) -> Document:
    data = document_data.model_dump(mode="json")

    document = Document(
        workspace_id=workspace_id,
        **data,
    )
    session.add(document)
    session.commit()
    session.refresh(document)

    return document


def list_documents(
    session: Session,
    workspace_id: uuid.UUID,
) -> Sequence[Document]:
    statement = (
        select(Document)
        .where(Document.workspace_id == workspace_id)
        .order_by(
            Document.title.asc(),
            Document.id.asc(),
        )
    )

    return session.scalars(statement).all()


def get_document(
    session: Session,
    document_id: uuid.UUID,
) -> Document | None:
    return session.get(Document, document_id)


def transition_document_status(
    session: Session,
    document: Document,
    new_status: DocumentStatus,
    *,
    processing_error: str | None = None,
) -> Document:
    allowed_statuses = ALLOWED_STATUS_TRANSITIONS[
        document.status
    ]

    if new_status not in allowed_statuses:
        raise InvalidDocumentStatusTransition(
            f"Cannot transition document from "
            f"{document.status.value} to "
            f"{new_status.value}"
        )

    normalized_error = (
        processing_error.strip()
        if processing_error
        else None
    )

    if (
        new_status is DocumentStatus.FAILED
        and not normalized_error
    ):
        raise ValueError(
            "processing_error is required for failed documents"
        )

    document.status = new_status
    document.processing_error = (
        normalized_error
        if new_status is DocumentStatus.FAILED
        else None
    )

    session.commit()
    session.refresh(document)

    return document