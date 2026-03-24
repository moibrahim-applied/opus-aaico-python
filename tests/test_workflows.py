"""Tests for the Workflows resource."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico.resources.jobs import SyncJobs
from opus_aaico.resources.workflows import SyncWorkflows
from opus_aaico.types.workflows import (
    GenerateWorkflowResponse,
    PrivateWorkflowsResponse,
    PublicWorkflowsResponse,
    Workflow,
    WorkflowRunResult,
)


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def jobs(client: SyncHTTPClient) -> SyncJobs:
    return SyncJobs(client)


@pytest.fixture
def workflows(client: SyncHTTPClient, jobs: SyncJobs) -> SyncWorkflows:
    return SyncWorkflows(client, jobs)


class TestGet:
    def test_get_workflow(
        self, workflows: SyncWorkflows, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/workflow/wf-1",
            method="GET",
            json={
                "workflowId": "wf-1",
                "name": "Test Workflow",
                "description": "A test",
                "active": True,
            },
        )
        result = workflows.get("wf-1")
        assert isinstance(result, Workflow)
        assert result.workflow_id == "wf-1"
        assert result.name == "Test Workflow"
        assert result.active is True


class TestList:
    def test_list_private_workflows(
        self, workflows: SyncWorkflows, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            json={
                "totalCount": 2,
                "workflows": [
                    {"name": "WF 1", "workflowId": "wf-1"},
                    {"name": "WF 2", "workflowId": "wf-2"},
                ],
            },
        )
        result = workflows.list()
        assert isinstance(result, PrivateWorkflowsResponse)
        assert result.total_count == 2
        assert len(result.workflows) == 2


class TestListPublic:
    def test_list_public_workflows(
        self, workflows: SyncWorkflows, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            json={
                "totalCount": 1,
                "workflows": [
                    {"name": "Public WF", "generationId": "gen-1"},
                ],
            },
        )
        result = workflows.list_public(industry="finance")
        assert isinstance(result, PublicWorkflowsResponse)
        assert result.total_count == 1


class TestGenerate:
    def test_generate_workflow(
        self, workflows: SyncWorkflows, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/workflow/generate",
            method="POST",
            json={"generationId": "gen-abc"},
        )
        result = workflows.generate("Automate invoice processing")
        assert isinstance(result, GenerateWorkflowResponse)
        assert result.generation_id == "gen-abc"

    def test_generate_sends_correct_body(
        self, workflows: SyncWorkflows, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/workflow/generate",
            method="POST",
            json={"generationId": "gen-1"},
        )
        workflows.generate(
            "Do something",
            user_id="u-1",
            make_private=True,
            include_policies=True,
        )
        import json

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["userQuery"] == "Do something"
        assert body["userId"] == "u-1"
        assert body["makePrivate"] is True
        assert body["includePolicies"] is True


class TestRun:
    """Test the full run() orchestration flow."""

    def test_run_happy_path(
        self, workflows: SyncWorkflows, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        # 1. POST /job/initiate
        httpx_mock.add_response(
            url=f"{base_url}/job/initiate",
            method="POST",
            json={"jobExecutionId": "j-1"},
        )
        # 2. POST /job/execute
        httpx_mock.add_response(
            url=f"{base_url}/job/execute",
            method="POST",
            json={"success": True},
        )
        # 3. GET /job/j-1/status (poll returns COMPLETED immediately)
        httpx_mock.add_response(
            url=f"{base_url}/job/j-1/status",
            method="GET",
            json={"status": "COMPLETED"},
        )
        # 4. GET /job/j-1/results
        httpx_mock.add_response(
            url=f"{base_url}/job/j-1/results",
            method="GET",
            json={"jobResultsPayloadSchema": {"output": "result"}},
        )
        # 5. GET /job/j-1/audit
        httpx_mock.add_response(
            url=f"{base_url}/job/j-1/audit",
            method="GET",
            json={
                "nb_nodes": 1,
                "nb_executed_nodes": 1,
                "nb_failed_nodes": 0,
                "executed_nodes": ["node1"],
                "failed_nodes": [],
                "remaining_nodes_to_execute": [],
                "running_node": None,
                "next_node_to_execute": None,
                "audit": {"nodes_execution_data": {}},
            },
        )

        result = workflows.run(
            "wf-1",
            {"input": "hello"},
            title="Test Run",
            description="Testing",
            poll_interval=0.01,
            timeout=5.0,
        )

        assert isinstance(result, WorkflowRunResult)
        assert result.status == "COMPLETED"
        assert result.job_id == "j-1"
        assert result.outputs == {"output": "result"}
        assert result.execution_time is not None
        assert result.execution_time >= 0
        assert result.audit is not None
        assert result.audit.nb_nodes == 1

    def test_run_failed_job(
        self, workflows: SyncWorkflows, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        # Initiate
        httpx_mock.add_response(
            url=f"{base_url}/job/initiate",
            method="POST",
            json={"jobExecutionId": "j-2"},
        )
        # Execute
        httpx_mock.add_response(
            url=f"{base_url}/job/execute",
            method="POST",
            json={"success": True},
        )
        # Poll returns FAILED
        httpx_mock.add_response(
            url=f"{base_url}/job/j-2/status",
            method="GET",
            json={"status": "FAILED"},
        )

        result = workflows.run(
            "wf-1",
            {"input": "hello"},
            poll_interval=0.01,
            timeout=5.0,
        )

        assert result.status == "FAILED"
        assert result.job_id == "j-2"
        assert result.outputs is None
        assert result.audit is None

    def test_run_calls_on_status_change(
        self, workflows: SyncWorkflows, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/initiate",
            method="POST",
            json={"jobExecutionId": "j-3"},
        )
        httpx_mock.add_response(
            url=f"{base_url}/job/execute",
            method="POST",
            json={"success": True},
        )
        httpx_mock.add_response(
            url=f"{base_url}/job/j-3/status",
            method="GET",
            json={"status": "COMPLETED"},
        )
        httpx_mock.add_response(
            url=f"{base_url}/job/j-3/results",
            method="GET",
            json={"jobResultsPayloadSchema": {}},
        )
        httpx_mock.add_response(
            url=f"{base_url}/job/j-3/audit",
            method="GET",
            json={
                "nb_nodes": 0,
                "executed_nodes": [],
                "failed_nodes": [],
                "remaining_nodes_to_execute": [],
                "audit": {"nodes_execution_data": {}},
            },
        )

        statuses_seen: list[str] = []
        workflows.run(
            "wf-1",
            {},
            poll_interval=0.01,
            timeout=5.0,
            on_status_change=lambda s: statuses_seen.append(s),
        )
        assert "COMPLETED" in statuses_seen
