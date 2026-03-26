"""Policies resource — upload, list, summarize, and manage policies."""

from __future__ import annotations

import mimetypes
import os
from typing import Any

from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.policies import Policy, PolicyListResponse, PolicySummary


class SyncPolicies(SyncResource):
    """Synchronous policies resource."""

    def list_types(self) -> Any:
        return self._client.request("GET", "/policy/list")

    def upload(self, file_path: str, policy_type: str) -> Policy:
        file_name = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, content_type)}
            data_fields = {"policyType": policy_type}
            resp = self._client.request("POST", "/policy/upload", data=data_fields, files=files)
        return Policy(**resp)

    def list(
        self,
        page: int = 1,
        limit: int = 25,
        sort: str = "DESC",
        policy_type: str | None = None,
        title: str | None = None,
        keyword: str | None = None,
    ) -> PolicyListResponse:
        params: dict[str, Any] = {
            "page": page,
            "limit": limit,
            "sort": sort,
        }
        if policy_type is not None:
            params["policyType"] = policy_type
        if title is not None:
            params["title"] = title
        if keyword is not None:
            params["keyword"] = keyword
        data = self._client.request("GET", "/policy", params=params)
        return PolicyListResponse(**data)

    def get(self, policy_id: str) -> Policy:
        data = self._client.request("GET", f"/policy/{policy_id}")
        return Policy(**data)

    def download(self, policy_id: str) -> Any:
        return self._client.request("GET", f"/policy/download/{policy_id}")

    def get_summary(self, policy_id: str) -> PolicySummary:
        data = self._client.request("GET", f"/policy/summary/{policy_id}")
        return PolicySummary(**data)

    def update_summary(
        self,
        policy_id: str,
        summary: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {}
        if summary is not None:
            body["summary"] = summary
        return self._client.request("PATCH", f"/policy/summary/{policy_id}", json=body)

    def get_organization_summary(self) -> Any:
        return self._client.request("GET", "/policy/organization/summary")

    def regenerate_blueprint(self) -> Any:
        return self._client.request("POST", "/policy/policy/regenerate-blueprint")

    def set_active(self, policy_id: str, active: bool) -> Any:
        body: dict[str, Any] = {"status": active}
        return self._client.request("PATCH", f"/policy/status/{policy_id}", json=body)

    def delete(self, policy_id: str) -> None:
        self._client.request("DELETE", f"/policy/{policy_id}")


class AsyncPolicies(AsyncResource):
    """Asynchronous policies resource."""

    async def list_types(self) -> Any:
        return await self._client.request("GET", "/policy/list")

    async def upload(self, file_path: str, policy_type: str) -> Policy:
        file_name = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, content_type)}
            data_fields = {"policyType": policy_type}
            resp = await self._client.request(
                "POST", "/policy/upload", data=data_fields, files=files
            )
        return Policy(**resp)

    async def list(
        self,
        page: int = 1,
        limit: int = 25,
        sort: str = "DESC",
        policy_type: str | None = None,
        title: str | None = None,
        keyword: str | None = None,
    ) -> PolicyListResponse:
        params: dict[str, Any] = {
            "page": page,
            "limit": limit,
            "sort": sort,
        }
        if policy_type is not None:
            params["policyType"] = policy_type
        if title is not None:
            params["title"] = title
        if keyword is not None:
            params["keyword"] = keyword
        data = await self._client.request("GET", "/policy", params=params)
        return PolicyListResponse(**data)

    async def get(self, policy_id: str) -> Policy:
        data = await self._client.request("GET", f"/policy/{policy_id}")
        return Policy(**data)

    async def download(self, policy_id: str) -> Any:
        return await self._client.request("GET", f"/policy/download/{policy_id}")

    async def get_summary(self, policy_id: str) -> PolicySummary:
        data = await self._client.request("GET", f"/policy/summary/{policy_id}")
        return PolicySummary(**data)

    async def update_summary(
        self,
        policy_id: str,
        summary: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {}
        if summary is not None:
            body["summary"] = summary
        return await self._client.request("PATCH", f"/policy/summary/{policy_id}", json=body)

    async def get_organization_summary(self) -> Any:
        return await self._client.request("GET", "/policy/organization/summary")

    async def regenerate_blueprint(self) -> Any:
        return await self._client.request("POST", "/policy/policy/regenerate-blueprint")

    async def set_active(self, policy_id: str, active: bool) -> Any:
        body: dict[str, Any] = {"status": active}
        return await self._client.request("PATCH", f"/policy/status/{policy_id}", json=body)

    async def delete(self, policy_id: str) -> None:
        await self._client.request("DELETE", f"/policy/{policy_id}")
