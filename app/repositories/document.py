import uuid

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