"""API key types."""

from __future__ import annotations

from pydantic import Field

from opus_aaico.types.shared import _BaseModel


class ApiKey(_BaseModel):
    id: str | None = None
    name: str | None = None
    key: str | None = None  # Only returned on creation
    scopes: list[str] = []
    created_at: str | None = Field(None, alias="createdAt")
    expires_at: str | None = Field(None, alias="expiresAt")
    is_active: bool | None = Field(None, alias="isActive")
    last_used_at: str | None = Field(None, alias="lastUsedAt")
    total_lifetime_calls: int | None = Field(None, alias="totalLifetimeCalls")
    owner: str | None = None


class ScopeDetails(_BaseModel):
    scope: str | None = None
    permissions: list[str] | None = None
    description: str | None = None


class ScopesResponse(_BaseModel):
    scopes: list[ScopeDetails] = []
    total_scopes: int | None = Field(None, alias="totalScopes")
