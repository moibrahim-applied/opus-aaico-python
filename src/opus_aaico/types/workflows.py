"""Workflow-related types."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from opus_aaico.types.enums import ReviewSettingType
from opus_aaico.types.shared import (
    ExecutionEstimation,
    PayloadVariable,
    _BaseModel,
)


class WorkflowGenerateSettings(_BaseModel):
    is_user_in_core_plan: bool | None = None
    organization_policy_count: int | None = None
    enable_workflow_caching: bool | None = None
    enable_workflow_policies: bool | None = None
    enable_input_variables: bool | None = None
    enable_code_generation: bool | None = None
    review_intensity: str | None = None
    review_type: ReviewSettingType | None = None


class WorkflowBlueprint(_BaseModel):
    id: str | None = None
    name: str | None = None
    objective: str | None = None
    description: str | None = None
    industry: str | None = None
    country: str | None = None


class Workflow(_BaseModel):
    workflow_id: str | None = Field(None, alias="workflowId")
    name: str | None = None
    description: str | None = None
    industry: str | None = None
    active: bool | None = None
    workflow_blueprint: WorkflowBlueprint | None = Field(None, alias="workflowBlueprint")
    execution_estimation: ExecutionEstimation | None = Field(None, alias="executionEstimation")
    workflow_image: str | None = Field(None, alias="workflowImage")
    job_payload_schema: dict[str, PayloadVariable] | None = Field(None, alias="jobPayloadSchema")
    job_results_payload_schema: dict[str, Any] | None = Field(None, alias="jobResultsPayloadSchema")
    created_at: str | None = Field(None, alias="createdAt")


class PublicWorkflowItem(_BaseModel):
    name: str | None = None
    description: str | None = None
    workflow_blueprint: WorkflowBlueprint | None = Field(None, alias="workflowBlueprint")
    execution_estimation: ExecutionEstimation | None = Field(None, alias="executionEstimation")
    redirect_url: str | None = Field(None, alias="redirectUrl")
    created_at: str | None = Field(None, alias="createdAt")
    generation_id: str | None = Field(None, alias="generationId")
    industry: str | None = None
    source: str | None = None


class PublicWorkflowsResponse(_BaseModel):
    total_count: int = Field(0, alias="totalCount")
    workflows: list[PublicWorkflowItem] = []


class PrivateWorkflowItem(_BaseModel):
    name: str | None = None
    description: str | None = None
    workflow_blueprint: WorkflowBlueprint | None = Field(None, alias="workflowBlueprint")
    execution_estimation: ExecutionEstimation | None = Field(None, alias="executionEstimation")
    redirect_url: str | None = Field(None, alias="redirectUrl")
    workflow_id: str | None = Field(None, alias="workflowId")
    workspace_name: str | None = Field(None, alias="workspaceName")
    created_at: str | None = Field(None, alias="createdAt")


class PrivateWorkflowsResponse(_BaseModel):
    total_count: int = Field(0, alias="totalCount")
    workflows: list[PrivateWorkflowItem] = []


class GenerateWorkflowResponse(_BaseModel):
    generation_id: str | None = Field(None, alias="generationId")


class IndustryItem(_BaseModel):
    display_value: str | None = Field(None, alias="displayValue")
    search_value: str | None = Field(None, alias="searchValue")


class IndustriesResponse(_BaseModel):
    industries: list[IndustryItem] = []


class EmailAttachment(_BaseModel):
    content: str
    filename: str
    mime_type: str = Field(..., alias="mimeType")


class WorkflowRunResult(_BaseModel):
    """High-level result from workflows.run()."""

    status: str
    job_id: str
    outputs: dict[str, Any] | None = None
    execution_time: float | None = None
    audit: Any | None = None
