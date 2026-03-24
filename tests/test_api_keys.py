"""Tests for the API Keys resource."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico.resources.api_keys import SyncApiKeys
from opus_aaico.types.api_keys import ApiKey, ScopesResponse


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def api_keys(client: SyncHTTPClient) -> SyncApiKeys:
    return SyncApiKeys(client)


class TestCreate:
    def test_create_returns_api_key(
        self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys",
            method="POST",
            json={
                "id": "key-1",
                "name": "My Key",
                "key": "sk-live-abc123",
                "scopes": ["jobs:read", "jobs:write"],
                "isActive": True,
            },
        )
        result = api_keys.create("My Key", ["jobs:read", "jobs:write"])
        assert isinstance(result, ApiKey)
        assert result.id == "key-1"
        assert result.key == "sk-live-abc123"
        assert result.scopes == ["jobs:read", "jobs:write"]

    def test_create_sends_body(
        self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys",
            method="POST",
            json={"id": "key-1", "name": "K"},
        )
        api_keys.create("K", ["admin"], expires_at="2025-12-31", key_prefix="prod")
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["name"] == "K"
        assert body["scopes"] == ["admin"]
        assert body["expiresAt"] == "2025-12-31"
        assert body["keyPrefix"] == "prod"


class TestList:
    def test_list_returns_array(
        self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys",
            method="GET",
            json=[{"id": "key-1", "name": "Key 1"}, {"id": "key-2", "name": "Key 2"}],
        )
        result = api_keys.list()
        assert len(result) == 2
        assert result[0]["id"] == "key-1"


class TestListScopes:
    def test_list_scopes_returns_response(
        self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys/scopes",
            method="GET",
            json={
                "scopes": [{"scope": "jobs:read", "description": "Read jobs"}],
                "totalScopes": 1,
            },
        )
        result = api_keys.list_scopes()
        assert isinstance(result, ScopesResponse)
        assert result.total_scopes == 1
        assert len(result.scopes) == 1


class TestRotate:
    def test_rotate_key(self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys/key-1/rotate",
            method="POST",
            json={"id": "key-1", "key": "sk-live-new"},
        )
        result = api_keys.rotate("key-1")
        assert result["key"] == "sk-live-new"


class TestResetLimits:
    def test_reset_limits(
        self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys/key-1/reset-limits",
            method="POST",
            json={"success": True},
        )
        result = api_keys.reset_limits("key-1")
        assert result["success"] is True


class TestSetActive:
    def test_set_active_true(
        self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys/status/key-1/true",
            method="PATCH",
            json={"isActive": True},
        )
        result = api_keys.set_active("key-1", True)
        assert result["isActive"] is True

    def test_set_active_false(
        self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys/status/key-1/false",
            method="PATCH",
            json={"isActive": False},
        )
        result = api_keys.set_active("key-1", False)
        assert result["isActive"] is False


class TestRevoke:
    def test_revoke_key(self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys/revoke/key-1",
            method="DELETE",
            status_code=204,
        )
        api_keys.revoke("key-1")  # Should not raise


class TestDelete:
    def test_delete_key(self, api_keys: SyncApiKeys, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/api-keys/delete/key-1",
            method="DELETE",
            status_code=204,
        )
        api_keys.delete("key-1")  # Should not raise
