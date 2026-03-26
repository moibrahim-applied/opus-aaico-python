"""Tests for the Credits resource."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico.resources.credits import SyncCredits
from opus_aaico.types.credits import CreditBalance


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def credits_res(client: SyncHTTPClient) -> SyncCredits:
    return SyncCredits(client)


class TestGetBalance:
    def test_get_balance_returns_credit_balance(
        self, credits_res: SyncCredits, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/credits/balance",
            method="GET",
            json={
                "userId": "u-1",
                "organizationId": "org-1",
                "credits": 100.0,
                "creditsLeft": 75.5,
            },
        )
        result = credits_res.get_balance()
        assert isinstance(result, CreditBalance)
        assert result.user_id == "u-1"
        assert result.credits == 100.0
        assert result.credits_left == 75.5


class TestCreateBalance:
    def test_create_balance(
        self, credits_res: SyncCredits, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/credits/create-balance",
            method="POST",
            json={
                "userId": "u-new",
                "organizationId": "org-1",
                "credits": 0,
                "creditsLeft": 0,
            },
        )
        result = credits_res.create_balance("u-new", "org-1")
        assert isinstance(result, CreditBalance)
        assert result.user_id == "u-new"

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["userId"] == "u-new"
        assert body["organizationId"] == "org-1"


class TestGetUsage:
    def test_get_usage(
        self, credits_res: SyncCredits, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/credits/usage",
            method="GET",
            json={"usages": [{"creditsUsed": 10.0}]},
        )
        result = credits_res.get_usage()
        assert result["usages"][0]["creditsUsed"] == 10.0


class TestGetWorkflowUsage:
    def test_get_workflow_usage(
        self, credits_res: SyncCredits, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/credits/usage/workflow/wf-1",
            method="GET",
            json={"totalCreditsUsed": 50.0},
        )
        result = credits_res.get_workflow_usage("wf-1")
        assert result["totalCreditsUsed"] == 50.0


class TestRecordUsage:
    def test_record_usage_sends_body(
        self, credits_res: SyncCredits, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/credits/usage",
            method="POST",
            json={"success": True},
        )
        credits_res.record_usage(
            usage_type="nodeExecution",
            workflow_id="wf-1",
            node_id="n-1",
            node_type="llm",
            node_name="GPT Node",
            credits_used=5.0,
            description="LLM call",
            generation_id="gen-1",
        )
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["usageType"] == "nodeExecution"
        assert body["workflowId"] == "wf-1"
        assert body["creditsUsed"] == 5.0
        assert body["generationId"] == "gen-1"

    def test_record_usage_minimal(
        self, credits_res: SyncCredits, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/credits/usage",
            method="POST",
            json={"success": True},
        )
        credits_res.record_usage(usage_type="workflowGeneration")
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["usageType"] == "workflowGeneration"
        assert body["creditsUsed"] == 0
        assert "workflowId" not in body
