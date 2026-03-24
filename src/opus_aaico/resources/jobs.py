"""Jobs resource — initiate, execute, poll, search, and manage jobs."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Callable

from opus_aaico._utils.polling import poll_async, poll_sync
from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.enums import JobStatus
from opus_aaico.types.jobs import (
    JobAudit,
    JobExecuteResponse,
    JobInitiateResponse,
    JobResultsResponse,
    JobSearchResponse,
    JobStatusResponse,
)

_DEFAULT_TERMINAL = (
    JobStatus.COMPLETED.value,
    JobStatus.FAILED.value,
    JobStatus.CANCELLED.value,
)


class SyncJobs(SyncResource):
    """Synchronous jobs resource."""

    # ---- core lifecycle --------------------------------------------------

    def initiate(
        self,
        workflow_id: str,
        title: str,
        description: str,
        ref_user_id: str | None = None,
    ) -> JobInitiateResponse:
        body: dict[str, Any] = {
            "workflowId": workflow_id,
            "title": title,
            "description": description,
        }
        if ref_user_id is not None:
            body["refUserId"] = ref_user_id
        data = self._client.request("POST", "/job/initiate", json=body)
        return JobInitiateResponse(**data)

    def execute(
        self,
        job_execution_id: str,
        payload: dict[str, Any],
        callback_url: str | None = None,
    ) -> JobExecuteResponse:
        body: dict[str, Any] = {
            "jobExecutionId": job_execution_id,
            "jobPayloadSchemaInstance": payload,
        }
        if callback_url is not None:
            body["callbackUrl"] = callback_url
        data = self._client.request("POST", "/job/execute", json=body)
        return JobExecuteResponse(**data)

    # ---- status / detail -------------------------------------------------

    def get_status(self, job_id: str) -> JobStatusResponse:
        data = self._client.request("GET", f"/job/{job_id}/status")
        return JobStatusResponse(**data)

    def get(self, job_id: str) -> Any:
        return self._client.request("GET", f"/job/{job_id}")

    def get_results(self, job_id: str) -> JobResultsResponse:
        data = self._client.request("GET", f"/job/{job_id}/results")
        return JobResultsResponse(**data)

    def get_audit(self, job_id: str) -> JobAudit:
        data = self._client.request("GET", f"/job/{job_id}/audit")
        return JobAudit.from_api_response(data)

    # ---- search ----------------------------------------------------------

    def search(
        self,
        workflow_id: str | None = None,
        workspace_ids: list[str] | None = None,
        status: list[str] | None = None,
        query: str | None = None,
        archive_status: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        offset: int = 0,
        max_results: int = 25,
    ) -> JobSearchResponse:
        params: dict[str, Any] = {
            "offset": offset,
            "maxResults": max_results,
        }
        if workflow_id is not None:
            params["workflowId"] = workflow_id
        if workspace_ids is not None:
            params["workspaceIds"] = ",".join(workspace_ids)
        if status is not None:
            params["status"] = ",".join(status)
        if query is not None:
            params["query"] = query
        if archive_status is not None:
            params["archiveStatus"] = archive_status
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date

        data = self._client.request("GET", "/job/search", params=params)
        return JobSearchResponse(**data)

    # ---- archive / duplicate / delete ------------------------------------

    def archive(self, job_id: str) -> None:
        self._client.request("POST", f"/job/{job_id}/archive")

    def unarchive(self, job_id: str) -> None:
        self._client.request("DELETE", f"/job/{job_id}/archive")

    def duplicate(self, job_id: str) -> Any:
        return self._client.request("GET", f"/job/{job_id}/duplicate")

    def delete(self, job_id: str) -> None:
        self._client.request("DELETE", f"/job/{job_id}/delete")

    # ---- polling ---------------------------------------------------------

    def poll(
        self,
        job_execution_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
        terminal_statuses: Sequence[str] | None = None,
        on_status_change: Callable[[str], None] | None = None,
    ) -> JobStatusResponse:
        terminals = terminal_statuses or _DEFAULT_TERMINAL
        return poll_sync(
            fn=lambda: self.get_status(job_execution_id),
            terminal_values=terminals,
            extract_value=lambda r: r.status.value if isinstance(r.status, JobStatus) else r.status,
            poll_interval=poll_interval,
            timeout=timeout,
            on_change=on_status_change,
        )


class AsyncJobs(AsyncResource):
    """Asynchronous jobs resource."""

    # ---- core lifecycle --------------------------------------------------

    async def initiate(
        self,
        workflow_id: str,
        title: str,
        description: str,
        ref_user_id: str | None = None,
    ) -> JobInitiateResponse:
        body: dict[str, Any] = {
            "workflowId": workflow_id,
            "title": title,
            "description": description,
        }
        if ref_user_id is not None:
            body["refUserId"] = ref_user_id
        data = await self._client.request("POST", "/job/initiate", json=body)
        return JobInitiateResponse(**data)

    async def execute(
        self,
        job_execution_id: str,
        payload: dict[str, Any],
        callback_url: str | None = None,
    ) -> JobExecuteResponse:
        body: dict[str, Any] = {
            "jobExecutionId": job_execution_id,
            "jobPayloadSchemaInstance": payload,
        }
        if callback_url is not None:
            body["callbackUrl"] = callback_url
        data = await self._client.request("POST", "/job/execute", json=body)
        return JobExecuteResponse(**data)

    # ---- status / detail -------------------------------------------------

    async def get_status(self, job_id: str) -> JobStatusResponse:
        data = await self._client.request("GET", f"/job/{job_id}/status")
        return JobStatusResponse(**data)

    async def get(self, job_id: str) -> Any:
        return await self._client.request("GET", f"/job/{job_id}")

    async def get_results(self, job_id: str) -> JobResultsResponse:
        data = await self._client.request("GET", f"/job/{job_id}/results")
        return JobResultsResponse(**data)

    async def get_audit(self, job_id: str) -> JobAudit:
        data = await self._client.request("GET", f"/job/{job_id}/audit")
        return JobAudit.from_api_response(data)

    # ---- search ----------------------------------------------------------

    async def search(
        self,
        workflow_id: str | None = None,
        workspace_ids: list[str] | None = None,
        status: list[str] | None = None,
        query: str | None = None,
        archive_status: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        offset: int = 0,
        max_results: int = 25,
    ) -> JobSearchResponse:
        params: dict[str, Any] = {
            "offset": offset,
            "maxResults": max_results,
        }
        if workflow_id is not None:
            params["workflowId"] = workflow_id
        if workspace_ids is not None:
            params["workspaceIds"] = ",".join(workspace_ids)
        if status is not None:
            params["status"] = ",".join(status)
        if query is not None:
            params["query"] = query
        if archive_status is not None:
            params["archiveStatus"] = archive_status
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date

        data = await self._client.request("GET", "/job/search", params=params)
        return JobSearchResponse(**data)

    # ---- archive / duplicate / delete ------------------------------------

    async def archive(self, job_id: str) -> None:
        await self._client.request("POST", f"/job/{job_id}/archive")

    async def unarchive(self, job_id: str) -> None:
        await self._client.request("DELETE", f"/job/{job_id}/archive")

    async def duplicate(self, job_id: str) -> Any:
        return await self._client.request("GET", f"/job/{job_id}/duplicate")

    async def delete(self, job_id: str) -> None:
        await self._client.request("DELETE", f"/job/{job_id}/delete")

    # ---- polling ---------------------------------------------------------

    async def poll(
        self,
        job_execution_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
        terminal_statuses: Sequence[str] | None = None,
        on_status_change: Callable[[str], None] | None = None,
    ) -> JobStatusResponse:
        terminals = terminal_statuses or _DEFAULT_TERMINAL
        return await poll_async(
            fn=lambda: self.get_status(job_execution_id),
            terminal_values=terminals,
            extract_value=lambda r: r.status.value if isinstance(r.status, JobStatus) else r.status,
            poll_interval=poll_interval,
            timeout=timeout,
            on_change=on_status_change,
        )
