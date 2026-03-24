"""Job-related types."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from opus_aaico.types.enums import JobStatus
from opus_aaico.types.shared import (
    ExecutionEstimation,
    UserDetails,
    WorkspaceDetails,
    _BaseModel,
)


class JobInitiateResponse(_BaseModel):
    job_execution_id: str = Field(..., alias="jobExecutionId")


class JobExecuteResponse(_BaseModel):
    success: bool | None = None
    job_execution_id: str | None = Field(None, alias="jobExecutionId")
    message: str | None = None


class JobStatusResponse(_BaseModel):
    status: JobStatus


class JobResultsResponse(_BaseModel):
    job_results_payload_schema: dict[str, Any] | None = Field(None, alias="jobResultsPayloadSchema")


class NodeExecutionData(_BaseModel):
    execution_status: str | None = Field(None, alias="execution_status")
    execution_time: int | None = Field(None, alias="execution_time")
    execution_start_time: int | None = Field(None, alias="execution_start_time")
    execution_index: int | None = Field(None, alias="execution_index")


class JobAudit(_BaseModel):
    """Flattened from API response (API nests nodes_execution_data inside audit.audit)."""

    nb_nodes: int | None = None
    nb_executed_nodes: int | None = None
    nb_failed_nodes: int | None = None
    executed_nodes: list[str] = []
    failed_nodes: list[str] = []
    remaining_nodes_to_execute: list[str] = []
    running_node: str | None = None
    next_node_to_execute: str | None = None
    nodes_execution_data: dict[str, NodeExecutionData] = {}

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> JobAudit:
        """Parse the nested API response into a flat JobAudit."""
        audit_inner = data.get("audit", {})
        nodes_data_raw = audit_inner.get("nodes_execution_data", {})
        nodes_data = {
            k: NodeExecutionData(**v) if isinstance(v, dict) else v
            for k, v in nodes_data_raw.items()
        }
        return cls(
            nb_nodes=data.get("nb_nodes"),
            nb_executed_nodes=data.get("nb_executed_nodes"),
            nb_failed_nodes=data.get("nb_failed_nodes"),
            executed_nodes=data.get("executed_nodes", []),
            failed_nodes=data.get("failed_nodes", []),
            remaining_nodes_to_execute=data.get("remaining_nodes_to_execute", []),
            running_node=data.get("running_node"),
            next_node_to_execute=data.get("next_node_to_execute"),
            nodes_execution_data=nodes_data,
        )


class JobSearchWorkflowDetails(_BaseModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None
    industry: str | None = None
    execution_estimation: ExecutionEstimation | None = Field(None, alias="executionEstimation")


class JobSearchItem(_BaseModel):
    title: str | None = None
    description: str | None = None
    job_execution_id: str | None = Field(None, alias="jobExecutionId")
    workflow_id: str | None = Field(None, alias="workflowId")
    status: JobStatus | None = None
    audit: dict[str, Any] | None = None
    user: UserDetails | None = None
    created_at: str | None = Field(None, alias="createdAt")
    workflow: JobSearchWorkflowDetails | None = None
    workspace: WorkspaceDetails | None = None


class JobSearchResponse(_BaseModel):
    total_count: int = Field(0, alias="totalCount")
    jobs: list[JobSearchItem] = []


class JobFileUploadResponse(_BaseModel):
    presigned_url: str | None = Field(None, alias="presignedUrl")
    file_url: str | None = Field(None, alias="fileUrl")


class JobFileDownloadResponse(_BaseModel):
    presigned_url: str | None = Field(None, alias="presignedUrl")
    file_url: str | None = Field(None, alias="fileUrl")
    content_type: str | None = Field(None, alias="contentType")
    content_length: int | None = Field(None, alias="contentLength")
