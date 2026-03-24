"""User and project types."""

from __future__ import annotations

from pydantic import Field

from opus_aaico.types.shared import _BaseModel


class User(_BaseModel):
    id: str | None = None
    name: str | None = None
    email: str | None = None


class Project(_BaseModel):
    id: str | None = None
    name: str | None = None
    workspace_id: str | None = Field(None, alias="workspaceId")
