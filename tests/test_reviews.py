"""Tests for the Reviews resource."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico.resources.reviews import SyncReviews
from opus_aaico.types.reviews import ReviewInitiateResponse, ReviewSubmitResponse


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def reviews(client: SyncHTTPClient) -> SyncReviews:
    return SyncReviews(client)


class TestInitiate:
    def test_initiate_returns_response(
        self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/initiate",
            method="POST",
            json={"reviewExecutionId": "rev-123"},
        )
        result = reviews.initiate(
            job_execution_id="j-1",
            type="HUMAN",
            node_id="n-1",
            node_name="Review Node",
            workflow_id="wf-1",
            review_payload={"data": "test"},
            input_definition_schema={"type": "object"},
            output_definition_schema={"type": "object"},
            webhook_callback="https://example.com/cb",
        )
        assert isinstance(result, ReviewInitiateResponse)
        assert result.review_execution_id == "rev-123"

    def test_initiate_sends_correct_body(
        self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/initiate",
            method="POST",
            json={"reviewExecutionId": "rev-1"},
        )
        reviews.initiate(
            job_execution_id="j-1",
            type="AGENT",
            node_id="n-1",
            node_name="Agent Review",
            workflow_id="wf-1",
            review_payload={},
            input_definition_schema={},
            output_definition_schema={},
            webhook_callback="https://cb.example.com",
            assignee_id="user-42",
            max_duration=48,
        )
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["jobExecutionId"] == "j-1"
        assert body["type"] == "AGENT"
        assert body["assigneeId"] == "user-42"
        assert body["maxDuration"] == 48


class TestList:
    def test_list_reviews(self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            method="GET",
            json={"totalCount": 1, "reviews": [{"id": "rev-1"}]},
        )
        result = reviews.list(type="HUMAN", status="PENDING")
        assert result["totalCount"] == 1

    def test_list_sends_params(
        self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(method="GET", json={"totalCount": 0, "reviews": []})
        reviews.list(type="AGENT", offset=10, max_results=50)
        request = httpx_mock.get_requests()[0]
        assert "type=AGENT" in str(request.url)
        assert "offset=10" in str(request.url)
        assert "maxResults=50" in str(request.url)


class TestGet:
    def test_get_review(self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/rev-1",
            method="GET",
            json={"id": "rev-1", "status": "PENDING"},
        )
        result = reviews.get("rev-1")
        assert result["id"] == "rev-1"


class TestPickRelease:
    def test_pick_review(self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/rev-1",
            method="PUT",
            json={"id": "rev-1", "status": "DISPATCHED"},
        )
        result = reviews.pick("rev-1")
        assert result["status"] == "DISPATCHED"

    def test_release_review(
        self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/rev-1",
            method="PUT",
            json={"id": "rev-1", "status": "PENDING"},
        )
        result = reviews.release("rev-1")
        assert result["status"] == "PENDING"


class TestSubmitResult:
    def test_submit_result_returns_response(
        self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/results",
            method="POST",
            json={
                "reviewId": "rev-1",
                "status": "COMPLETED",
                "reviewResult": {"variableName": "output", "value": "done"},
            },
        )
        result = reviews.submit_result(
            "rev-1", "COMPLETED", {"variableName": "output", "value": "done"}
        )
        assert isinstance(result, ReviewSubmitResponse)
        assert result.review_id == "rev-1"
        assert result.status == "COMPLETED"


class TestSubmitOutput:
    def test_submit_output(
        self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/rev-1/output",
            method="PUT",
            json={"success": True},
        )
        result = reviews.submit_output(
            "rev-1", accept=True, updated={"key": "val"}, comment="Looks good"
        )
        assert result["success"] is True

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["accept"] is True
        assert body["comment"] == "Looks good"


class TestSubmitHumanTaskOutput:
    def test_submit_human_task_output(
        self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/rev-1/humanOutput",
            method="PUT",
            json={"success": True},
        )
        result = reviews.submit_human_task_output("rev-1", updated={"answer": "42"})
        assert result["success"] is True


class TestCheckStatus:
    def test_check_status(self, reviews: SyncReviews, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/review/check/j-1",
            method="GET",
            json={"hasPendingReviews": True},
        )
        result = reviews.check_status("j-1")
        assert result["hasPendingReviews"] is True
