"""Workflows resource — list, generate, and run workflows end-to-end."""

from __future__ import annotations

import builtins
import time
from typing import TYPE_CHECKING, Any, Callable

from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.enums import JobStatus
from opus_aaico.types.workflows import (
    GenerateWorkflowResponse,
    PrivateWorkflowsResponse,
    PublicWorkflowsResponse,
    Workflow,
    WorkflowRunResult,
)

if TYPE_CHECKING:
    from opus_aaico.resources.jobs import AsyncJobs, SyncJobs


class SyncWorkflows(SyncResource):
    """Synchronous workflows resource."""

    def __init__(self, client: Any, jobs_resource: SyncJobs) -> None:
        super().__init__(client)
        self._jobs = jobs_resource

    # ---- single workflow -------------------------------------------------

    def get(self, workflow_id: str) -> Workflow:
        data = self._client.request("GET", f"/workflow/{workflow_id}")
        return Workflow(**data)

    # ---- listing ---------------------------------------------------------

    def list(
        self,
        query: str | None = None,
        industry: str | None = None,
        workspace_ids: builtins.list[str] | None = None,
        active: bool | None = None,
        has_jobs: bool | None = None,
        offset: int = 0,
        max_results: int = 25,
    ) -> PrivateWorkflowsResponse:
        params: dict[str, Any] = {
            "offset": offset,
            "maxResults": max_results,
        }
        if query is not None:
            params["query"] = query
        if industry is not None:
            params["industry"] = industry
        if workspace_ids is not None:
            params["workspaceIds"] = ",".join(workspace_ids)
        if active is not None:
            params["active"] = active
        if has_jobs is not None:
            params["hasJobs"] = has_jobs

        data = self._client.request("GET", "/workflow/private", params=params)
        return PrivateWorkflowsResponse(**data)

    def list_public(
        self,
        query: str | None = None,
        industry: str | None = None,
        country: str | None = None,
        source: str | None = None,
        offset: int = 0,
        max_results: int = 25,
    ) -> PublicWorkflowsResponse:
        params: dict[str, Any] = {
            "offset": offset,
            "maxResults": max_results,
        }
        if query is not None:
            params["query"] = query
        if industry is not None:
            params["industry"] = industry
        if country is not None:
            params["country"] = country
        if source is not None:
            params["source"] = source

        data = self._client.request("GET", "/workflow/public", params=params)
        return PublicWorkflowsResponse(**data)

    def get_public(self, generation_id: str) -> Any:
        return self._client.request("GET", f"/workflow/public/{generation_id}")

    # ---- generation ------------------------------------------------------

    def generate(
        self,
        user_query: str,
        user_id: str | None = None,
        make_private: bool = False,
        include_policies: bool = False,
        settings: dict[str, Any] | None = None,
    ) -> GenerateWorkflowResponse:
        body: dict[str, Any] = {
            "userQuery": user_query,
            "makePrivate": make_private,
            "includePolicies": include_policies,
        }
        if user_id is not None:
            body["userId"] = user_id
        if settings is not None:
            body["settings"] = settings

        data = self._client.request("POST", "/workflow/generate", json=body)
        return GenerateWorkflowResponse(**data)

    # ---- feed ------------------------------------------------------------

    def feed(self, workflow_id: str, private: bool = False) -> Any:
        return self._client.request(
            "POST",
            f"/workflow/{workflow_id}/feed",
            params={"private": private},
        )

    def feed_external(
        self,
        workflow_object: Any,
        user_query: str,
        blueprint: Any,
    ) -> Any:
        body: dict[str, Any] = {
            "workflowObject": workflow_object,
            "userQuery": user_query,
            "blueprint": blueprint,
        }
        return self._client.request("POST", "/workflow/generate/external/feed", json=body)

    # ---- sharing ---------------------------------------------------------

    def share(self, workflow_id: str) -> Any:
        return self._client.request("POST", f"/workflow/share/{workflow_id}")

    def get_shared(self, workflow_id: str) -> Any:
        return self._client.request("GET", f"/workflow/share/{workflow_id}")

    # ---- email -----------------------------------------------------------

    def send_email(
        self,
        workflow_id: str,
        recipients: builtins.list[str],
        subject: str,
        body: str,
        attachments: builtins.list[dict[str, Any]] | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "recipients": recipients,
            "subject": subject,
            "body": body,
        }
        if attachments is not None:
            payload["attachments"] = attachments
        self._client.request("POST", f"/workflow/{workflow_id}/email", json=payload)

    # ---- industries ------------------------------------------------------

    def list_industries(self) -> Any:
        return self._client.request("GET", "/workflow/industries")

    # ---- flagship: run() -------------------------------------------------

    def run(
        self,
        workflow_id: str,
        payload: dict[str, Any],
        title: str = "SDK Job",
        description: str = "",
        poll_interval: float = 2.0,
        timeout: float = 300.0,
        on_status_change: Callable[[str], None] | None = None,
    ) -> WorkflowRunResult:
        """Initiate, execute, poll, and return results in one call."""
        # 1. Initiate
        job = self._jobs.initiate(workflow_id, title, description)

        # 2. Execute
        self._jobs.execute(job.job_execution_id, payload)

        # 3. Poll
        start = time.monotonic()
        status_resp = self._jobs.poll(
            job.job_execution_id,
            poll_interval=poll_interval,
            timeout=timeout,
            on_status_change=on_status_change,
        )
        elapsed = time.monotonic() - start

        # 4. Gather results if completed
        outputs = None
        audit = None
        status_val = (
            status_resp.status.value
            if isinstance(status_resp.status, JobStatus)
            else status_resp.status
        )
        if status_val == JobStatus.COMPLETED.value:
            results = self._jobs.get_results(job.job_execution_id)
            outputs = results.job_results_payload_schema
            audit = self._jobs.get_audit(job.job_execution_id)

        return WorkflowRunResult(
            status=status_val,
            job_id=job.job_execution_id,
            outputs=outputs,
            execution_time=elapsed,
            audit=audit,
        )


class AsyncWorkflows(AsyncResource):
    """Asynchronous workflows resource."""

    def __init__(self, client: Any, jobs_resource: AsyncJobs) -> None:
        super().__init__(client)
        self._jobs = jobs_resource

    # ---- single workflow -------------------------------------------------

    async def get(self, workflow_id: str) -> Workflow:
        data = await self._client.request("GET", f"/workflow/{workflow_id}")
        return Workflow(**data)

    # ---- listing ---------------------------------------------------------

    async def list(
        self,
        query: str | None = None,
        industry: str | None = None,
        workspace_ids: builtins.list[str] | None = None,
        active: bool | None = None,
        has_jobs: bool | None = None,
        offset: int = 0,
        max_results: int = 25,
    ) -> PrivateWorkflowsResponse:
        params: dict[str, Any] = {
            "offset": offset,
            "maxResults": max_results,
        }
        if query is not None:
            params["query"] = query
        if industry is not None:
            params["industry"] = industry
        if workspace_ids is not None:
            params["workspaceIds"] = ",".join(workspace_ids)
        if active is not None:
            params["active"] = active
        if has_jobs is not None:
            params["hasJobs"] = has_jobs

        data = await self._client.request("GET", "/workflow/private", params=params)
        return PrivateWorkflowsResponse(**data)

    async def list_public(
        self,
        query: str | None = None,
        industry: str | None = None,
        country: str | None = None,
        source: str | None = None,
        offset: int = 0,
        max_results: int = 25,
    ) -> PublicWorkflowsResponse:
        params: dict[str, Any] = {
            "offset": offset,
            "maxResults": max_results,
        }
        if query is not None:
            params["query"] = query
        if industry is not None:
            params["industry"] = industry
        if country is not None:
            params["country"] = country
        if source is not None:
            params["source"] = source

        data = await self._client.request("GET", "/workflow/public", params=params)
        return PublicWorkflowsResponse(**data)

    async def get_public(self, generation_id: str) -> Any:
        return await self._client.request("GET", f"/workflow/public/{generation_id}")

    # ---- generation ------------------------------------------------------

    async def generate(
        self,
        user_query: str,
        user_id: str | None = None,
        make_private: bool = False,
        include_policies: bool = False,
        settings: dict[str, Any] | None = None,
    ) -> GenerateWorkflowResponse:
        body: dict[str, Any] = {
            "userQuery": user_query,
            "makePrivate": make_private,
            "includePolicies": include_policies,
        }
        if user_id is not None:
            body["userId"] = user_id
        if settings is not None:
            body["settings"] = settings

        data = await self._client.request("POST", "/workflow/generate", json=body)
        return GenerateWorkflowResponse(**data)

    # ---- feed ------------------------------------------------------------

    async def feed(self, workflow_id: str, private: bool = False) -> Any:
        return await self._client.request(
            "POST",
            f"/workflow/{workflow_id}/feed",
            params={"private": private},
        )

    async def feed_external(
        self,
        workflow_object: Any,
        user_query: str,
        blueprint: Any,
    ) -> Any:
        body: dict[str, Any] = {
            "workflowObject": workflow_object,
            "userQuery": user_query,
            "blueprint": blueprint,
        }
        return await self._client.request("POST", "/workflow/generate/external/feed", json=body)

    # ---- sharing ---------------------------------------------------------

    async def share(self, workflow_id: str) -> Any:
        return await self._client.request("POST", f"/workflow/share/{workflow_id}")

    async def get_shared(self, workflow_id: str) -> Any:
        return await self._client.request("GET", f"/workflow/share/{workflow_id}")

    # ---- email -----------------------------------------------------------

    async def send_email(
        self,
        workflow_id: str,
        recipients: builtins.list[str],
        subject: str,
        body: str,
        attachments: builtins.list[dict[str, Any]] | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "recipients": recipients,
            "subject": subject,
            "body": body,
        }
        if attachments is not None:
            payload["attachments"] = attachments
        await self._client.request("POST", f"/workflow/{workflow_id}/email", json=payload)

    # ---- industries ------------------------------------------------------

    async def list_industries(self) -> Any:
        return await self._client.request("GET", "/workflow/industries")

    # ---- flagship: run() -------------------------------------------------

    async def run(
        self,
        workflow_id: str,
        payload: dict[str, Any],
        title: str = "SDK Job",
        description: str = "",
        poll_interval: float = 2.0,
        timeout: float = 300.0,
        on_status_change: Callable[[str], None] | None = None,
    ) -> WorkflowRunResult:
        """Initiate, execute, poll, and return results in one call."""

        # 1. Initiate
        job = await self._jobs.initiate(workflow_id, title, description)

        # 2. Execute
        await self._jobs.execute(job.job_execution_id, payload)

        # 3. Poll
        start = time.monotonic()
        status_resp = await self._jobs.poll(
            job.job_execution_id,
            poll_interval=poll_interval,
            timeout=timeout,
            on_status_change=on_status_change,
        )
        elapsed = time.monotonic() - start

        # 4. Gather results if completed
        outputs = None
        audit = None
        status_val = (
            status_resp.status.value
            if isinstance(status_resp.status, JobStatus)
            else status_resp.status
        )
        if status_val == JobStatus.COMPLETED.value:
            results = await self._jobs.get_results(job.job_execution_id)
            outputs = results.job_results_payload_schema
            audit = await self._jobs.get_audit(job.job_execution_id)

        return WorkflowRunResult(
            status=status_val,
            job_id=job.job_execution_id,
            outputs=outputs,
            execution_time=elapsed,
            audit=audit,
        )
