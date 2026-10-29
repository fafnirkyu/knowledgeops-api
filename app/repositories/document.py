import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate


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