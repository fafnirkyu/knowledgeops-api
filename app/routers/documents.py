from io import BytesIO
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from redis.exceptions import RedisError
from rq import Queue
from sqlalchemy.orm import Session

from app.db.dependencies import get_db_session
from app.jobs.document_processing import process_document_job
from app.jobs.queue import get_document_queue
from app.repositories.document import (
    InvalidDocumentStatusTransition,
    create_document,
    delete_document,
    get_document,
    list_documents,
)
from app.repositories.workspace import get_workspace
from app.schemas.document import DocumentCreate, DocumentRead
from app.services.dependencies import get_embedding_provider
from app.services.document_processor import process_document
from app.services.embedding_provider import EmbeddingProvider
from app.services.pdf_extractor import (
    PdfExtractionError,
    extract_pdf_text,
)

router = APIRouter(tags=["documents"])

DbSession = Annotated[Session, Depends(get_db_session)]

DocumentQueue = Annotated[
    Queue,
    Depends(get_document_queue),
]

MAX_PDF_SIZE = 10 * 1024 * 1024

EmbeddingProviderDependency = Annotated[
    EmbeddingProvider,
    Depends(get_embedding_provider),
]

@router.post(
    "/workspaces/{workspace_id}/documents/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document_endpoint(
    workspace_id: UUID,
    session: DbSession,
    queue: DocumentQueue,
    file: Annotated[UploadFile, File()],
    title: Annotated[
        str | None,
        Form(min_length=1, max_length=200),
    ] = None,
):
    workspace = get_workspace(
        session,
        workspace_id,
    )

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    if (
        file.content_type != "application/pdf"
        or Path(file.filename or "").suffix.lower() != ".pdf"
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported",
        )

    contents = await file.read(
        MAX_PDF_SIZE + 1
    )

    if len(contents) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="PDF file exceeds the 10 MiB limit",
        )

    try:
        extracted_text = extract_pdf_text(
            BytesIO(contents),
        )
    except PdfExtractionError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    document_title = (
        title
        or Path(file.filename or "document.pdf").stem
    )

    document = create_document(
        session,
        workspace_id,
        DocumentCreate(
            title=document_title,
            content=extracted_text,
            source_url=None,
        ),
    )

    try:
        queue.enqueue(
            process_document_job,
            str(document.id),
        )
    except RedisError as error:
        delete_document(
            session,
            document,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document queue unavailable",
        ) from error

    return document

@router.post(
    "/workspaces/{workspace_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document_endpoint(
    workspace_id: UUID,
    document_data: DocumentCreate,
    session: DbSession,
):
    workspace = get_workspace(session, workspace_id)

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    return create_document(
        session,
        workspace_id,
        document_data,
    )


@router.get(
    "/workspaces/{workspace_id}/documents",
    response_model=list[DocumentRead],
)
def read_documents(
    workspace_id: UUID,
    session: DbSession,
):
    workspace = get_workspace(session, workspace_id)

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    return list_documents(
        session,
        workspace_id,
    )


@router.post(
    "/documents/{document_id}/process",
    response_model=DocumentRead,
)
def process_document_endpoint(
    document_id: UUID,
    session: DbSession,
    embedding_provider: EmbeddingProviderDependency,
):
    document = get_document(session, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        return process_document(
            session,
            document,
            embedding_provider=embedding_provider,
        )

    except InvalidDocumentStatusTransition as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "/documents/{document_id}",
    response_model=DocumentRead,
)
def read_document(
    document_id: UUID,
    session: DbSession,
):
    document = get_document(session, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document