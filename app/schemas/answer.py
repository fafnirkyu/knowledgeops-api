import uuid
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

SourceId = Annotated[
    str,
    Field(pattern=r"^S[1-9][0-9]*$"),
]


class AnswerRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    query: str = Field(
        min_length=1,
        max_length=500,
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class GeneratedAnswer(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    answer: str = Field(
        min_length=1,
        max_length=2000,
    )
    citation_ids: list[SourceId] = Field(
        max_length=20,
    )
    insufficient_context: bool


class AnswerCitation(BaseModel):
    source_id: SourceId
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int = Field(ge=0)
    content: str = Field(min_length=1)
    score: float


class AnswerResponse(BaseModel):
    answer: str = Field(
        min_length=1,
        max_length=2000,
    )
    citations: list[AnswerCitation]
    insufficient_context: bool