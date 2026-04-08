"""Review-related types."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from opus_aaico.types.enums import ReviewStatus, ReviewType
from opus_aaico.types.shared import _BaseModel


class ReviewInitiateResponse(_BaseModel):
    review_execution_id: str | None = Field(None, alias="reviewExecutionId")


class ReviewResult(_BaseModel):
    variable_name: str | None = Field(None, alias="variableName")
    value: Any | None = None


class ReviewSubmitResponse(_BaseModel):
    review_id: str | None = Field(None, alias="reviewId")
    status: str | None = None
    review_result: list[ReviewResult] | ReviewResult | None = Field(None, alias="reviewResult")


class ReviewItem(_BaseModel):
    id: str | None = None
    job_execution_id: str | None = Field(None, alias="jobExecutionId")
    type: ReviewType | None = None
    status: ReviewStatus | None = None
    node_id: str | None = Field(None, alias="nodeId")
    node_name: str | None = Field(None, alias="nodeName")
    workflow_id: str | None = Field(None, alias="workflowId")
    assignee_id: str | None = Field(None, alias="assigneeId")
    created_at: str | None = Field(None, alias="createdAt")


class ReviewListResponse(_BaseModel):
    total_count: int = Field(0, alias="totalCount")
    reviews: list[ReviewItem] = []
