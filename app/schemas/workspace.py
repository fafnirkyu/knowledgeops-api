import uuid

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    model_config = ConfigDict(
    str_strip_whitespace=True,
    extra="forbid",
)
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class WorkspaceRead(WorkspaceCreate):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
