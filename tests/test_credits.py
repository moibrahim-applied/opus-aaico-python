"""Tests for the Credits resource (v2)."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico._exceptions import NotSupportedError
from opus_aaico.resources.credits import SyncCredits
from opus_aaico.types.credits import CreditHistoryEntry


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def credits_res(client: SyncHTTPClient) -> SyncCredits:
    return SyncCredits(client)


class TestHistory:
    def test_history_parses_string_numbers(
        self, credits_res: SyncCredits, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        # Live API returns numbers as strings; we coerce to floats
        httpx_mock.add_response(
            url=f"{base_url}/credits/history?offset=0&max_results=100",
            method="GET",
            json=[
                {
                    "date": "2026-05-04T12:00:00Z",
                    "balance_after": "1081.581600",
                    "credits_used": "-1.912000",
                    "description": "Workflow run",
                },
                {
                    "date": "2026-05-04T11:00:00Z",
                    "balance_after": "1083.493600",
                    "credits_used": "-2.000000",
                    "description": "Workflow run",
                },
            ],
        )
        result = credits_res.history()
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], CreditHistoryEntry)
        assert result[0].balance_after == 1081.5816
        assert result[0].credits_used == -1.912

    def test_current_balance_uses_latest_entry(
        self, credits_res: SyncCredits, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/credits/history?offset=0&max_results=1",
            method="GET",
            json=[{"balance_after": "500.0", "credits_used": "-1.0"}],
        )
        balance = credits_res.current_balance()
        assert balance == 500.0


class TestRemovedMethodsRaiseClearly:
    def test_get_balance_raises_not_supported(
        self, credits_res: SyncCredits
    ) -> None:
        with pytest.raises(NotSupportedError) as exc_info:
            credits_res.get_balance()
        msg = str(exc_info.value)
        assert "no longer available" in msg
        assert "credits.history()" in msg

    def test_get_usage_raises_not_supported(
        self, credits_res: SyncCredits
    ) -> None:
        with pytest.raises(NotSupportedError):
            credits_res.get_usage()

    def test_record_usage_raises_not_supported(
        self, credits_res: SyncCredits
    ) -> None:
        with pytest.raises(NotSupportedError):
            credits_res.record_usage(usage_type="nodeExecution")

    def test_get_workflow_usage_raises_not_supported(
        self, credits_res: SyncCredits
    ) -> None:
        with pytest.raises(NotSupportedError):
            credits_res.get_workflow_usage("wf-1")

    def test_create_balance_raises_not_supported(
        self, credits_res: SyncCredits
    ) -> None:
        with pytest.raises(NotSupportedError):
            credits_res.create_balance("u-new", "org-1")
