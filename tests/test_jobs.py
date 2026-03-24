"""Tests for the Jobs resource."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico.resources.jobs import SyncJobs
from opus_aaico.types.enums import JobStatus
from opus_aaico.types.jobs import (
    JobExecuteResponse,
    JobInitiateResponse,
    JobSearchResponse,
    JobStatusResponse,
)


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def jobs(client: SyncHTTPClient) -> SyncJobs:
    return SyncJobs(client)


class TestInitiate:
    def test_initiate_returns_job_execution_id(
        self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/initiate",
            method="POST",
            json={"jobExecutionId": "j-abc-123"},
        )
        result = jobs.initiate("wf-1", "My Job", "A test job")
        assert isinstance(result, JobInitiateResponse)
        assert result.job_execution_id == "j-abc-123"

    def test_initiate_sends_correct_body(
        self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/initiate",
            method="POST",
            json={"jobExecutionId": "j-1"},
        )
        jobs.initiate("wf-1", "Title", "Desc", ref_user_id="user-99")
        request = httpx_mock.get_requests()[0]
        import json

        body = json.loads(request.content)
        assert body["workflowId"] == "wf-1"
        assert body["title"] == "Title"
        assert body["description"] == "Desc"
        assert body["refUserId"] == "user-99"


class TestExecute:
    def test_execute_returns_response(
        self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/execute",
            method="POST",
            json={"success": True, "jobExecutionId": "j-1"},
        )
        result = jobs.execute("j-1", {"input": "data"})
        assert isinstance(result, JobExecuteResponse)
        assert result.success is True

    def test_execute_sends_payload(
        self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/execute",
            method="POST",
            json={"success": True},
        )
        jobs.execute("j-1", {"key": "value"}, callback_url="https://cb.example.com")
        import json

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["jobExecutionId"] == "j-1"
        assert body["jobPayloadSchemaInstance"] == {"key": "value"}
        assert body["callbackUrl"] == "https://cb.example.com"


class TestGetStatus:
    def test_get_status_completed(
        self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/j-1/status",
            method="GET",
            json={"status": "COMPLETED"},
        )
        result = jobs.get_status("j-1")
        assert isinstance(result, JobStatusResponse)
        assert result.status == JobStatus.COMPLETED

    def test_get_status_in_progress(
        self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/j-2/status",
            method="GET",
            json={"status": "IN_PROGRESS"},
        )
        result = jobs.get_status("j-2")
        assert result.status == JobStatus.IN_PROGRESS


class TestSearch:
    def test_search_basic(self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            method="GET",
            json={
                "totalCount": 1,
                "jobs": [
                    {
                        "title": "Test Job",
                        "jobExecutionId": "j-1",
                        "status": "COMPLETED",
                    }
                ],
            },
        )
        result = jobs.search(workflow_id="wf-1")
        assert isinstance(result, JobSearchResponse)
        assert result.total_count == 1
        assert len(result.jobs) == 1
        assert result.jobs[0].title == "Test Job"

    def test_search_with_filters(
        self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            json={"totalCount": 0, "jobs": []},
        )
        jobs.search(
            workflow_id="wf-1",
            workspace_ids=["ws-1", "ws-2"],
            status=["COMPLETED", "FAILED"],
            query="test",
            offset=10,
            max_results=50,
        )
        request = httpx_mock.get_requests()[0]
        assert "workflowId=wf-1" in str(request.url)
        assert "workspaceIds=ws-1%2Cws-2" in str(request.url) or "workspaceIds=ws-1,ws-2" in str(
            request.url
        )
        assert "query=test" in str(request.url)


class TestGetResults:
    def test_get_results(self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/j-1/results",
            method="GET",
            json={"jobResultsPayloadSchema": {"output": "hello"}},
        )
        result = jobs.get_results("j-1")
        assert result.job_results_payload_schema == {"output": "hello"}


class TestGetAudit:
    def test_get_audit_flattens(self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/j-1/audit",
            method="GET",
            json={
                "nb_nodes": 3,
                "nb_executed_nodes": 2,
                "nb_failed_nodes": 0,
                "executed_nodes": ["node1", "node2"],
                "failed_nodes": [],
                "remaining_nodes_to_execute": ["node3"],
                "running_node": None,
                "next_node_to_execute": "node3",
                "audit": {
                    "nodes_execution_data": {
                        "node1": {
                            "execution_status": "completed",
                            "execution_time": 100,
                        }
                    }
                },
            },
        )
        result = jobs.get_audit("j-1")
        assert result.nb_nodes == 3
        assert result.executed_nodes == ["node1", "node2"]
        assert "node1" in result.nodes_execution_data


class TestPoll:
    def test_poll_returns_on_terminal_status(
        self, jobs: SyncJobs, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/j-1/status",
            method="GET",
            json={"status": "COMPLETED"},
        )
        result = jobs.poll("j-1", poll_interval=0.01, timeout=5.0)
        assert result.status == JobStatus.COMPLETED
