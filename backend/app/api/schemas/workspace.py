from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(
        min_length=3,
        max_length=63,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Workspace name cannot be empty")
        return normalized


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    plan: str
    owner_user_id: UUID
    created_at: datetime
    updated_at: datetime
