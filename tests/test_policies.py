"""Tests for the Policies resource."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico.resources.policies import SyncPolicies
from opus_aaico.types.policies import Policy, PolicyListResponse, PolicySummary


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def policies(client: SyncHTTPClient) -> SyncPolicies:
    return SyncPolicies(client)


class TestListTypes:
    def test_list_types(self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/list",
            method="GET",
            json=[{"name": "hr", "displayName": "HR Policy"}],
        )
        result = policies.list_types()
        assert len(result) == 1
        assert result[0]["name"] == "hr"


class TestUpload:
    def test_upload_returns_policy(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str, tmp_path
    ) -> None:
        test_file = tmp_path / "policy.pdf"
        test_file.write_bytes(b"policy content")

        httpx_mock.add_response(
            url=f"{base_url}/policy/upload",
            method="POST",
            json={
                "id": "pol-1",
                "policyType": "hr",
                "fileName": "policy.pdf",
            },
        )
        result = policies.upload(str(test_file), "hr")
        assert isinstance(result, Policy)
        assert result.id == "pol-1"
        assert result.policy_type == "hr"


class TestList:
    def test_list_policies(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            json={
                "data": [{"id": "pol-1", "policyType": "hr"}],
                "meta": {"currentPage": 1, "totalItems": 1, "totalPages": 1, "itemsPerPage": 25},
            },
        )
        result = policies.list(page=1, limit=25, policy_type="hr")
        assert isinstance(result, PolicyListResponse)
        assert len(result.data) == 1
        assert result.meta.total_items == 1

    def test_list_sends_params(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(method="GET", json={"data": [], "meta": {}})
        policies.list(page=2, limit=10, sort="ASC", title="Test", keyword="compliance")
        request = httpx_mock.get_requests()[0]
        url_str = str(request.url)
        assert "page=2" in url_str
        assert "limit=10" in url_str
        assert "sort=ASC" in url_str
        assert "title=Test" in url_str
        assert "keyword=compliance" in url_str


class TestGet:
    def test_get_policy(self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/pol-1",
            method="GET",
            json={"id": "pol-1", "policyType": "hr", "fileName": "policy.pdf"},
        )
        result = policies.get("pol-1")
        assert isinstance(result, Policy)
        assert result.id == "pol-1"


class TestDownload:
    def test_download_policy(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/download/pol-1",
            method="GET",
            json={"url": "https://s3.example.com/policy.pdf"},
        )
        result = policies.download("pol-1")
        assert result["url"] == "https://s3.example.com/policy.pdf"


class TestGetSummary:
    def test_get_summary(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/summary/pol-1",
            method="GET",
            json={"id": "pol-1", "summary": "This policy covers HR guidelines."},
        )
        result = policies.get_summary("pol-1")
        assert isinstance(result, PolicySummary)
        assert result.summary == "This policy covers HR guidelines."


class TestUpdateSummary:
    def test_update_summary(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/summary/pol-1",
            method="PATCH",
            json={"success": True},
        )
        result = policies.update_summary("pol-1", summary="Updated summary")
        assert result["success"] is True

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["summary"] == "Updated summary"


class TestSetActive:
    def test_set_active(self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/status/pol-1",
            method="PATCH",
            json={"policyEnabled": True},
        )
        result = policies.set_active("pol-1", True)
        assert result["policyEnabled"] is True

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["status"] is True


class TestDelete:
    def test_delete_policy(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/pol-1",
            method="DELETE",
            status_code=204,
        )
        policies.delete("pol-1")  # Should not raise


class TestOrganizationSummary:
    def test_get_organization_summary(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/organization/summary",
            method="GET",
            json={"summary": "Org-wide policy summary"},
        )
        result = policies.get_organization_summary()
        assert result["summary"] == "Org-wide policy summary"


class TestRegenerateBlueprint:
    def test_regenerate_blueprint(
        self, policies: SyncPolicies, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/policy/policy/regenerate-blueprint",
            method="POST",
            json={"success": True},
        )
        result = policies.regenerate_blueprint()
        assert result["success"] is True
