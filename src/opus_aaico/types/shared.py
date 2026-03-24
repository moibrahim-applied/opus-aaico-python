"""Shared types used across multiple resources."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class _BaseModel(BaseModel):
    """Base for all OPUS SDK models. Converts camelCase <-> snake_case."""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    def __repr__(self) -> str:
        fields = ", ".join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
            if v is not None and not k.startswith("_")
        )
        return f"{self.__class__.__name__}({fields})"


class UserDetails(_BaseModel):
    name: str | None = None
    email: str | None = None


class ExecutionEstimation(_BaseModel):
    human_cost: float | None = None
    human_price: float | None = None
    opus_cost: float | None = None
    opus_price: float | None = None
    human_time: float | None = None
    opus_time: float | None = None
    accuracy: float | None = None


class PayloadVariable(_BaseModel):
    """Describes an expected input variable in a workflow's jobPayloadSchema."""

    id: str
    variable_name: str
    display_name: str
    type: str
    is_nullable: bool


class WorkspaceDetails(_BaseModel):
    pass


T = TypeVar("T")


class PaginatedResponse(_BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    total_count: int = 0
    items: list[T] = []
