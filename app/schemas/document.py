import uuid

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.document import DocumentStatus


class DocumentCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    source_url: HttpUrl | None = None


class DocumentRead(DocumentCreate):
    id: uuid.UUID
    workspace_id: uuid.UUID
    status: DocumentStatus
    processing_error: str | None = None

    model_config = ConfigDict(from_attributes=True)
