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


# ---- v2 workflow object (from /reference-workflow/v2/workflow-object/{id}) ----


class WorkflowNode(_BaseModel):
    """A node in a v2 workflow's graph."""

    id: str
    type: str | None = None
    name: str | None = None
    description: str | None = None
    label: str | None = None
    handler_id: str | None = None
    handler_version_id: str | None = None
    handler_active_id: str | None = None
    handler_active_version_id: str | None = None
    handler_class: str | None = None
    handler_status: str | None = None
    workflow_version_id: str | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    routes: dict[str, Any] | None = None
    mappings: dict[str, Any] | None = None
    set_values: dict[str, Any] | None = None
    properties: list[Any] | None = None
    position: dict[str, Any] | None = None


class WorkflowEdge(_BaseModel):
    """An edge connecting two nodes in a v2 workflow."""

    id: str
    from_node_id: str
    to_node_id: str
    label: str | None = None
    route_id: str | None = None
    route_complement: bool | None = None


class WorkflowObject(_BaseModel):
    """Full v2 workflow object: graph, schemas, settings.

    Returned by ``workflows.get(workflow_uuid)``.
    """

    workflow_id: str
    name: str | None = None
    description: str | None = None
    version: int | None = None
    major_version: int | None = None
    minor_version: int | None = None
    validity_status: str | None = None
    active_status: str | None = None
    workspace_id: str | None = None
    workflow_input_node_id: str | None = None
    workflow_output_node_id: str | None = None
    starting_nodes_ids: list[str] = []
    ending_nodes_ids: list[str] = []
    action_items: list[Any] = []
    public_execution_settings: dict[str, Any] | None = None
    environment_variables: dict[str, Any] | None = None
    environment_variables_set_values: dict[str, Any] | None = None
    nodes: dict[str, WorkflowNode] = {}
    edges: dict[str, WorkflowEdge] = {}
    parent_adjacency: dict[str, list[str]] = {}
    child_adjacency: dict[str, list[str]] = {}
    routing_masks: Any | None = None

    @property
    def input_variables(self) -> dict[str, Any]:
        """Convenience: input variables defined on the workflow_input node."""
        if not self.workflow_input_node_id:
            return {}
        node = self.nodes.get(self.workflow_input_node_id)
        if not node or not node.input_schema:
            return {}
        return node.input_schema.get("schema", {})

    def find_sub_workflows(self) -> list[dict[str, Any]]:
        """Return every Execute-Workflow style node and the workflow it points to.

        A node is considered a sub-workflow call when its handler_class hints at
        execute_workflow / sub-workflow OR its type contains 'execute' / 'workflow'.
        """
        out: list[dict[str, Any]] = []
        for node in self.nodes.values():
            t = (node.type or "").lower()
            cls = (node.handler_class or "").lower()
            is_sub = (
                "execute_workflow" in t
                or "execute_workflow" in cls
                or "sub_workflow" in t
                or "sub_workflow" in cls
            )
            if is_sub:
                out.append(
                    {
                        "node_id": node.id,
                        "node_name": node.name,
                        "node_type": node.type,
                        "handler_id": node.handler_id,
                        "handler_active_id": node.handler_active_id,
                        "handler_class": node.handler_class,
                    }
                )
        return out


class WorkflowVersionItem(_BaseModel):
    """One version entry from /executor/workflow/{id}/versions."""

    workflow_version_id: str
    version: int
    status: str | None = None
    change_description: str | None = None
    created_at: str | None = None
    major_version: int | None = None
    minor_version: int | None = None
    version_label: str | None = None


class WorkflowVersionsResponse(_BaseModel):
    workflow_id: str
    name: str | None = None
    latest_version: int | None = None
    versions: list[WorkflowVersionItem] = []


class NodeHealthStats(_BaseModel):
    """Per-node health statistics."""

    name: str
    total_executions: int = 0
    failures: int = 0
    failure_rate: float = 0.0
    avg_execution_time_ms: float = 0.0
    max_execution_time_ms: float = 0.0


class WorkflowHealthReport(_BaseModel):
    """Health report for a workflow over a time period."""

    workflow_id: str
    workflow_name: str | None = None
    days_analyzed: int = 7
    total_runs: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    in_progress: int = 0
    success_rate: float = 0.0
    avg_execution_time_seconds: float = 0.0
    slowest_node: str | None = None
    slowest_node_avg_ms: float = 0.0
    most_failing_node: str | None = None
    most_failing_node_count: int = 0
    node_stats: list[NodeHealthStats] = []
    stuck_jobs: list[str] = []


class RetryResult(_BaseModel):
    """Result of retrying a failed job."""

    original_job_id: str
    new_job_id: str | None = None
    status: str = "pending"
    error: str | None = None


class RetryReport(_BaseModel):
    """Report from retry_failed operation."""

    workflow_id: str
    total_failed: int = 0
    retried: int = 0
    skipped: int = 0
    results: list[RetryResult] = []
