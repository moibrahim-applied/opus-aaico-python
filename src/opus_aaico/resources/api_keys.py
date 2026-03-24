"""API Keys resource — create, list, rotate, revoke, and delete API keys."""

from __future__ import annotations

import builtins
from typing import Any

from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.api_keys import ApiKey, ScopesResponse


class SyncApiKeys(SyncResource):
    """Synchronous API keys resource."""

    def create(
        self,
        name: str,
        scopes: builtins.list[str],
        expires_at: str | None = None,
        key_prefix: str | None = None,
    ) -> ApiKey:
        body: dict[str, Any] = {
            "name": name,
            "scopes": scopes,
        }
        if expires_at is not None:
            body["expiresAt"] = expires_at
        if key_prefix is not None:
            body["keyPrefix"] = key_prefix
        data = self._client.request("POST", "/api-keys", json=body)
        return ApiKey(**data)

    def list(self) -> builtins.list[Any]:
        data = self._client.request("GET", "/api-keys")
        if isinstance(data, list):
            return data
        return data.get("keys", data.get("data", []))

    def list_scopes(self) -> ScopesResponse:
        data = self._client.request("GET", "/api-keys/scopes")
        return ScopesResponse(**data)

    def rotate(self, key_id: str) -> Any:
        return self._client.request("POST", f"/api-keys/{key_id}/rotate")

    def reset_limits(self, key_id: str) -> Any:
        return self._client.request("POST", f"/api-keys/{key_id}/reset-limits")

    def set_active(self, key_id: str, active: bool) -> Any:
        active_str = str(active).lower()
        return self._client.request("PATCH", f"/api-keys/status/{key_id}/{active_str}")

    def revoke(self, key_id: str) -> None:
        self._client.request("DELETE", f"/api-keys/revoke/{key_id}")

    def delete(self, key_id: str) -> None:
        self._client.request("DELETE", f"/api-keys/delete/{key_id}")


class AsyncApiKeys(AsyncResource):
    """Asynchronous API keys resource."""

    async def create(
        self,
        name: str,
        scopes: builtins.list[str],
        expires_at: str | None = None,
        key_prefix: str | None = None,
    ) -> ApiKey:
        body: dict[str, Any] = {
            "name": name,
            "scopes": scopes,
        }
        if expires_at is not None:
            body["expiresAt"] = expires_at
        if key_prefix is not None:
            body["keyPrefix"] = key_prefix
        data = await self._client.request("POST", "/api-keys", json=body)
        return ApiKey(**data)

    async def list(self) -> builtins.list[Any]:
        data = await self._client.request("GET", "/api-keys")
        if isinstance(data, list):
            return data
        return data.get("keys", data.get("data", []))

    async def list_scopes(self) -> ScopesResponse:
        data = await self._client.request("GET", "/api-keys/scopes")
        return ScopesResponse(**data)

    async def rotate(self, key_id: str) -> Any:
        return await self._client.request("POST", f"/api-keys/{key_id}/rotate")

    async def reset_limits(self, key_id: str) -> Any:
        return await self._client.request("POST", f"/api-keys/{key_id}/reset-limits")

    async def set_active(self, key_id: str, active: bool) -> Any:
        active_str = str(active).lower()
        return await self._client.request("PATCH", f"/api-keys/status/{key_id}/{active_str}")

    async def revoke(self, key_id: str) -> None:
        await self._client.request("DELETE", f"/api-keys/revoke/{key_id}")

    async def delete(self, key_id: str) -> None:
        await self._client.request("DELETE", f"/api-keys/delete/{key_id}")
