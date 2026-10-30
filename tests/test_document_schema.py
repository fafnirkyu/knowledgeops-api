import uuid

import pytest
from pydantic import ValidationError

from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentRead


def test_document_creation():
    document = DocumentCreate(title= "MyDocument", content= "Document contents")
    assert document.title == "MyDocument"
    assert document.content == "Document contents"
    assert document.source_url is None

@pytest.mark.parametrize(
    "payload",
    [
        {
            "title": "   ",
            "content": "Valid content",
        },
        {
            "title": "x" * 201,
            "content": "Valid content",
        },
        {
            "title": "Valid title",
            "content": "   ",
        },
        {
            "title": "Valid title",
            "content": "Valid content",
            "source_url": "mysitewrong",
        },
        {
            "id": uuid.uuid4(),
            "title": "Valid title",
            "content": "Valid content",
        },
        {
            "workspace_id": uuid.uuid4(),
            "title": "Valid title",
            "content": "Valid content",
        },
        {
            "title": "Valid title",
            "content": "Valid content",
            "status": "ready",
        },
    ],
)
def test_document_create_rejects_invalid_payload(payload):
    with pytest.raises(ValidationError):
        DocumentCreate.model_validate(payload)

def test_document_read_accepts_orm_object():
    document_id = uuid.uuid4()
    workspace_id = uuid.uuid4()

    document = Document(
        id=document_id,
        workspace_id=workspace_id,
        title="FastAPI Notes",
        content="Document contents",
        source_url="https://example.com/document",
        status=DocumentStatus.READY,
        processing_error=None,
    )

    result = DocumentRead.model_validate(document)

    assert result.id == document_id
    assert result.workspace_id == workspace_id
    assert result.title == "FastAPI Notes"
    assert result.content == "Document contents"
    assert str(result.source_url) == "https://example.com/document"
    assert result.status is DocumentStatus.READY
    assert result.processing_error is None
    assert result.model_dump(mode="json")["status"] == "ready"
