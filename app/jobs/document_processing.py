import uuid

from app.core.config import Settings
from app.db.session import (
    create_db_engine,
    create_session_factory,
)
from app.repositories.document import get_document
from app.services.dependencies import get_embedding_provider
from app.services.document_processor import process_document


def process_document_job(
    document_id: str,
) -> str:
    settings = Settings()
    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            document = get_document(
                session,
                uuid.UUID(document_id),
            )

            if document is None:
                raise ValueError(
                    f"Document {document_id} not found"
                )

            processed_document = process_document(
                session,
                document,
                embedding_provider=get_embedding_provider(),
            )

            return str(processed_document.id)
    finally:
        engine.dispose()