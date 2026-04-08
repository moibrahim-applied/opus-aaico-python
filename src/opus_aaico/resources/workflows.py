"""Workflows resource — list, generate, run, health check, and retry workflows."""

from __future__ import annotations

import builtins
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Callable

from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.enums import JobStatus
from opus_aaico.types.workflows import (
    GenerateWorkflowResponse,
    NodeHealthStats,
    PrivateWorkflowsResponse,
    PublicWorkflowsResponse,
    RetryReport,
    RetryResult,
    Workflow,
    WorkflowHealthReport,
    WorkflowRunResult,
)

logger = logging.getLogger("opus_aaico")

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


    # ---- compound: health() ------------------------------------------------

    def health(
        self,
        workflow_id: str,
        days: int = 7,
        sample_audits: int = 20,
    ) -> WorkflowHealthReport:
        """Instant health report: success rate, avg time, slowest/failing nodes, stuck jobs."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        wf = self.get(workflow_id)

        # Fetch jobs by status
        completed_resp = self._jobs.search(
            workflow_id=workflow_id, status=["COMPLETED"], start_date=since, max_results=100
        )
        failed_resp = self._jobs.search(
            workflow_id=workflow_id, status=["FAILED"], start_date=since, max_results=100
        )
        cancelled_resp = self._jobs.search(
            workflow_id=workflow_id, status=["CANCELLED"], start_date=since, max_results=100
        )
        in_progress_resp = self._jobs.search(
            workflow_id=workflow_id, status=["IN_PROGRESS"], start_date=since, max_results=100
        )

        n_completed = completed_resp.total_count
        n_failed = failed_resp.total_count
        n_cancelled = cancelled_resp.total_count
        n_in_progress = in_progress_resp.total_count
        total = n_completed + n_failed + n_cancelled + n_in_progress
        success_rate = (n_completed / total * 100) if total > 0 else 0.0

        # Sample audits for node-level stats
        node_times: dict[str, builtins.list[float]] = defaultdict(list)
        node_failures: dict[str, int] = defaultdict(int)
        total_execution_times: builtins.list[float] = []

        jobs_to_audit = []
        for j in completed_resp.jobs[:sample_audits]:
            jobs_to_audit.append((j.job_execution_id, "completed"))
        for j in failed_resp.jobs[:sample_audits]:
            jobs_to_audit.append((j.job_execution_id, "failed"))

        for job_id, job_status in jobs_to_audit:
            try:
                audit = self._jobs.get_audit(job_id)
                job_total_ms = 0.0
                for node_name, node_data in audit.nodes_execution_data.items():
                    t = node_data.execution_time or 0
                    node_times[node_name].append(float(t))
                    job_total_ms += t
                    if node_data.execution_status and node_data.execution_status.upper() == "FAILED":
                        node_failures[node_name] += 1
                total_execution_times.append(job_total_ms / 1000.0)
                for fn in audit.failed_nodes:
                    node_failures[fn] = node_failures.get(fn, 0) + 1
            except Exception:
                continue

        avg_time = sum(total_execution_times) / len(total_execution_times) if total_execution_times else 0.0

        # Build node stats
        node_stats = []
        for name, times in node_times.items():
            avg_ms = sum(times) / len(times) if times else 0.0
            max_ms = max(times) if times else 0.0
            failures = node_failures.get(name, 0)
            total_exec = len(times)
            node_stats.append(NodeHealthStats(
                name=name,
                total_executions=total_exec,
                failures=failures,
                failure_rate=(failures / total_exec * 100) if total_exec > 0 else 0.0,
                avg_execution_time_ms=round(avg_ms, 1),
                max_execution_time_ms=round(max_ms, 1),
            ))

        # Find slowest and most failing
        slowest = max(node_stats, key=lambda n: n.avg_execution_time_ms) if node_stats else None
        most_failing = max(node_stats, key=lambda n: n.failures) if node_stats else None

        # Detect stuck jobs (IN_PROGRESS for > 1 hour)
        stuck = []
        for j in in_progress_resp.jobs:
            if j.created_at:
                try:
                    created = datetime.fromisoformat(j.created_at.replace("Z", "+00:00"))
                    if datetime.now(timezone.utc) - created > timedelta(hours=1):
                        stuck.append(j.job_execution_id or "")
                except Exception:
                    pass

        return WorkflowHealthReport(
            workflow_id=workflow_id,
            workflow_name=wf.name,
            days_analyzed=days,
            total_runs=total,
            completed=n_completed,
            failed=n_failed,
            cancelled=n_cancelled,
            in_progress=n_in_progress,
            success_rate=round(success_rate, 1),
            avg_execution_time_seconds=round(avg_time, 1),
            slowest_node=slowest.name if slowest else None,
            slowest_node_avg_ms=slowest.avg_execution_time_ms if slowest else 0.0,
            most_failing_node=most_failing.name if most_failing and most_failing.failures > 0 else None,
            most_failing_node_count=most_failing.failures if most_failing else 0,
            node_stats=node_stats,
            stuck_jobs=stuck,
        )

    # ---- compound: retry_failed() ----------------------------------------

    def retry_failed(
        self,
        workflow_id: str,
        since_days: int = 7,
        max_retries: int = 50,
    ) -> RetryReport:
        """Find all failed jobs, re-run each with its original input payload."""
        since = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime("%Y-%m-%d")

        failed_resp = self._jobs.search(
            workflow_id=workflow_id,
            status=["FAILED"],
            start_date=since,
            max_results=max_retries,
        )

        results: builtins.list[RetryResult] = []
        retried = 0
        skipped = 0

        for job_item in failed_resp.jobs:
            job_id = job_item.job_execution_id or ""
            try:
                detail = self._jobs.get(job_id)
                if not isinstance(detail, dict) or "input" not in detail:
                    results.append(RetryResult(
                        original_job_id=job_id,
                        status="skipped",
                        error="No input payload found on original job",
                    ))
                    skipped += 1
                    continue

                original_payload = detail["input"]
                title = detail.get("title", "Retry") + " (retry)"
                description = detail.get("description", "")

                new_job = self._jobs.initiate(workflow_id, title, description)
                self._jobs.execute(new_job.job_execution_id, original_payload)

                results.append(RetryResult(
                    original_job_id=job_id,
                    new_job_id=new_job.job_execution_id,
                    status="running",
                ))
                retried += 1

            except Exception as e:
                results.append(RetryResult(
                    original_job_id=job_id,
                    status="error",
                    error=str(e),
                ))
                skipped += 1

        return RetryReport(
            workflow_id=workflow_id,
            total_failed=failed_resp.total_count,
            retried=retried,
            skipped=skipped,
            results=results,
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

    # ---- compound: health() ------------------------------------------------

    async def health(
        self,
        workflow_id: str,
        days: int = 7,
        sample_audits: int = 20,
    ) -> WorkflowHealthReport:
        """Instant health report: success rate, avg time, slowest/failing nodes, stuck jobs."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        wf = await self.get(workflow_id)

        completed_resp = await self._jobs.search(
            workflow_id=workflow_id, status=["COMPLETED"], start_date=since, max_results=100
        )
        failed_resp = await self._jobs.search(
            workflow_id=workflow_id, status=["FAILED"], start_date=since, max_results=100
        )
        cancelled_resp = await self._jobs.search(
            workflow_id=workflow_id, status=["CANCELLED"], start_date=since, max_results=100
        )
        in_progress_resp = await self._jobs.search(
            workflow_id=workflow_id, status=["IN_PROGRESS"], start_date=since, max_results=100
        )

        n_completed = completed_resp.total_count
        n_failed = failed_resp.total_count
        n_cancelled = cancelled_resp.total_count
        n_in_progress = in_progress_resp.total_count
        total = n_completed + n_failed + n_cancelled + n_in_progress
        success_rate = (n_completed / total * 100) if total > 0 else 0.0

        node_times: dict[str, builtins.list[float]] = defaultdict(list)
        node_failures: dict[str, int] = defaultdict(int)
        total_execution_times: builtins.list[float] = []

        jobs_to_audit = []
        for j in completed_resp.jobs[:sample_audits]:
            jobs_to_audit.append((j.job_execution_id, "completed"))
        for j in failed_resp.jobs[:sample_audits]:
            jobs_to_audit.append((j.job_execution_id, "failed"))

        for job_id, job_status in jobs_to_audit:
            try:
                audit = await self._jobs.get_audit(job_id)
                job_total_ms = 0.0
                for node_name, node_data in audit.nodes_execution_data.items():
                    t = node_data.execution_time or 0
                    node_times[node_name].append(float(t))
                    job_total_ms += t
                    if node_data.execution_status and node_data.execution_status.upper() == "FAILED":
                        node_failures[node_name] += 1
                total_execution_times.append(job_total_ms / 1000.0)
                for fn in audit.failed_nodes:
                    node_failures[fn] = node_failures.get(fn, 0) + 1
            except Exception:
                continue

        avg_time = sum(total_execution_times) / len(total_execution_times) if total_execution_times else 0.0

        node_stats = []
        for name, times in node_times.items():
            avg_ms = sum(times) / len(times) if times else 0.0
            max_ms = max(times) if times else 0.0
            failures = node_failures.get(name, 0)
            total_exec = len(times)
            node_stats.append(NodeHealthStats(
                name=name,
                total_executions=total_exec,
                failures=failures,
                failure_rate=(failures / total_exec * 100) if total_exec > 0 else 0.0,
                avg_execution_time_ms=round(avg_ms, 1),
                max_execution_time_ms=round(max_ms, 1),
            ))

        slowest = max(node_stats, key=lambda n: n.avg_execution_time_ms) if node_stats else None
        most_failing = max(node_stats, key=lambda n: n.failures) if node_stats else None

        stuck = []
        for j in in_progress_resp.jobs:
            if j.created_at:
                try:
                    created = datetime.fromisoformat(j.created_at.replace("Z", "+00:00"))
                    if datetime.now(timezone.utc) - created > timedelta(hours=1):
                        stuck.append(j.job_execution_id or "")
                except Exception:
                    pass

        return WorkflowHealthReport(
            workflow_id=workflow_id,
            workflow_name=wf.name,
            days_analyzed=days,
            total_runs=total,
            completed=n_completed,
            failed=n_failed,
            cancelled=n_cancelled,
            in_progress=n_in_progress,
            success_rate=round(success_rate, 1),
            avg_execution_time_seconds=round(avg_time, 1),
            slowest_node=slowest.name if slowest else None,
            slowest_node_avg_ms=slowest.avg_execution_time_ms if slowest else 0.0,
            most_failing_node=most_failing.name if most_failing and most_failing.failures > 0 else None,
            most_failing_node_count=most_failing.failures if most_failing else 0,
            node_stats=node_stats,
            stuck_jobs=stuck,
        )

    # ---- compound: retry_failed() ----------------------------------------

    async def retry_failed(
        self,
        workflow_id: str,
        since_days: int = 7,
        max_retries: int = 50,
    ) -> RetryReport:
        """Find all failed jobs, re-run each with its original input payload."""
        since = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime("%Y-%m-%d")

        failed_resp = await self._jobs.search(
            workflow_id=workflow_id,
            status=["FAILED"],
            start_date=since,
            max_results=max_retries,
        )

        results: builtins.list[RetryResult] = []
        retried = 0
        skipped = 0

        for job_item in failed_resp.jobs:
            job_id = job_item.job_execution_id or ""
            try:
                detail = await self._jobs.get(job_id)
                if not isinstance(detail, dict) or "input" not in detail:
                    results.append(RetryResult(
                        original_job_id=job_id,
                        status="skipped",
                        error="No input payload found on original job",
                    ))
                    skipped += 1
                    continue

                original_payload = detail["input"]
                title = detail.get("title", "Retry") + " (retry)"
                description = detail.get("description", "")

                new_job = await self._jobs.initiate(workflow_id, title, description)
                await self._jobs.execute(new_job.job_execution_id, original_payload)

                results.append(RetryResult(
                    original_job_id=job_id,
                    new_job_id=new_job.job_execution_id,
                    status="running",
                ))
                retried += 1

            except Exception as e:
                results.append(RetryResult(
                    original_job_id=job_id,
                    status="error",
                    error=str(e),
                ))
                skipped += 1

        return RetryReport(
            workflow_id=workflow_id,
            total_failed=failed_resp.total_count,
            retried=retried,
            skipped=skipped,
            results=results,
        )
