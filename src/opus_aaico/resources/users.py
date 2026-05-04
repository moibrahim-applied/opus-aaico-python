"""Users resource — list users and projects."""

from __future__ import annotations

from typing import Any

from opus_aaico.resources._base import AsyncResource, SyncResource


class SyncUsers(SyncResource):
    """Synchronous users resource."""

    def list(self, workspace_id: str | None = None) -> Any:
        headers: dict[str, str] | None = None
        if workspace_id is not None:
            headers = {"x-workspace-id": workspace_id}
        return self._client.request("GET", "/users", headers=headers)

    def list_projects(self, workspace_id: str | None = None) -> Any:
        params: dict[str, Any] | None = None
        if workspace_id is not None:
            params = {"workspaceId": workspace_id}
        return self._client.request("GET", "/users/projects", params=params)

    # alias for ergonomics
    projects = list_projects

    def get_projects(self, workspace_id: str | None = None) -> Any:
        params: dict[str, Any] | None = None
        if workspace_id is not None:
            params = {"workspaceId": workspace_id}
        return self._client.request("GET", "/projects", params=params)


class AsyncUsers(AsyncResource):
    """Asynchronous users resource."""

    async def list(self, workspace_id: str | None = None) -> Any:
        headers: dict[str, str] | None = None
        if workspace_id is not None:
            headers = {"x-workspace-id": workspace_id}
        return await self._client.request("GET", "/users", headers=headers)

    async def list_projects(self, workspace_id: str | None = None) -> Any:
        params: dict[str, Any] | None = None
        if workspace_id is not None:
            params = {"workspaceId": workspace_id}
        return await self._client.request("GET", "/users/projects", params=params)

    async def projects(self, workspace_id: str | None = None) -> Any:
        return await self.list_projects(workspace_id)

    async def get_projects(self, workspace_id: str | None = None) -> Any:
        params: dict[str, Any] | None = None
        if workspace_id is not None:
            params = {"workspaceId": workspace_id}
        return await self._client.request("GET", "/projects", params=params)
