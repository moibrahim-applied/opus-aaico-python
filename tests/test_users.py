"""Tests for the Users resource."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico.resources.users import SyncUsers


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def users(client: SyncHTTPClient) -> SyncUsers:
    return SyncUsers(client)


class TestListUsers:
    def test_list_users(self, users: SyncUsers, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/users",
            method="GET",
            json=[{"id": "u-1", "name": "Alice"}, {"id": "u-2", "name": "Bob"}],
        )
        result = users.list()
        assert len(result) == 2
        assert result[0]["name"] == "Alice"

    def test_list_users_with_workspace_header(
        self, users: SyncUsers, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/users",
            method="GET",
            json=[{"id": "u-1"}],
        )
        users.list(workspace_id="ws-42")
        request = httpx_mock.get_requests()[0]
        assert request.headers.get("x-workspace-id") == "ws-42"


class TestListProjects:
    def test_list_projects(self, users: SyncUsers, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            method="GET",
            json=[{"id": "proj-1", "name": "Project Alpha"}],
        )
        result = users.list_projects(workspace_id="ws-1")
        assert len(result) == 1
        assert result[0]["name"] == "Project Alpha"

    def test_list_projects_sends_params(
        self, users: SyncUsers, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(method="GET", json=[])
        users.list_projects(workspace_id="ws-99")
        request = httpx_mock.get_requests()[0]
        assert "workspaceId=ws-99" in str(request.url)


class TestGetProjects:
    def test_get_projects(self, users: SyncUsers, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            method="GET",
            json=[{"id": "proj-1", "name": "Project Beta"}],
        )
        result = users.get_projects()
        assert len(result) == 1

    def test_get_projects_with_workspace(
        self, users: SyncUsers, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(method="GET", json=[])
        users.get_projects(workspace_id="ws-5")
        request = httpx_mock.get_requests()[0]
        assert "workspaceId=ws-5" in str(request.url)
