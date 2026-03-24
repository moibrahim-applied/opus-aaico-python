"""Credits resource — balance, usage, and recording."""

from __future__ import annotations

from typing import Any

from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.credits import CreditBalance


class SyncCredits(SyncResource):
    """Synchronous credits resource."""

    def get_balance(self) -> CreditBalance:
        data = self._client.request("GET", "/credits/balance")
        return CreditBalance(**data)

    def create_balance(self, user_id: str, organization_id: str) -> CreditBalance:
        body: dict[str, Any] = {
            "userId": user_id,
            "organizationId": organization_id,
        }
        data = self._client.request("POST", "/credits/create-balance", json=body)
        return CreditBalance(**data)

    def get_usage(self) -> Any:
        return self._client.request("GET", "/credits/usage")

    def get_workflow_usage(self, workflow_id: str) -> Any:
        return self._client.request("GET", f"/credits/usage/workflow/{workflow_id}")

    def record_usage(
        self,
        usage_type: str,
        workflow_id: str | None = None,
        node_id: str | None = None,
        node_type: str | None = None,
        node_name: str | None = None,
        credits_used: float = 0,
        description: str | None = None,
        generation_id: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {
            "usageType": usage_type,
            "creditsUsed": credits_used,
        }
        if workflow_id is not None:
            body["workflowId"] = workflow_id
        if node_id is not None:
            body["nodeId"] = node_id
        if node_type is not None:
            body["nodeType"] = node_type
        if node_name is not None:
            body["nodeName"] = node_name
        if description is not None:
            body["description"] = description
        if generation_id is not None:
            body["generationId"] = generation_id
        return self._client.request("POST", "/credits/usage", json=body)


class AsyncCredits(AsyncResource):
    """Asynchronous credits resource."""

    async def get_balance(self) -> CreditBalance:
        data = await self._client.request("GET", "/credits/balance")
        return CreditBalance(**data)

    async def create_balance(self, user_id: str, organization_id: str) -> CreditBalance:
        body: dict[str, Any] = {
            "userId": user_id,
            "organizationId": organization_id,
        }
        data = await self._client.request("POST", "/credits/create-balance", json=body)
        return CreditBalance(**data)

    async def get_usage(self) -> Any:
        return await self._client.request("GET", "/credits/usage")

    async def get_workflow_usage(self, workflow_id: str) -> Any:
        return await self._client.request("GET", f"/credits/usage/workflow/{workflow_id}")

    async def record_usage(
        self,
        usage_type: str,
        workflow_id: str | None = None,
        node_id: str | None = None,
        node_type: str | None = None,
        node_name: str | None = None,
        credits_used: float = 0,
        description: str | None = None,
        generation_id: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {
            "usageType": usage_type,
            "creditsUsed": credits_used,
        }
        if workflow_id is not None:
            body["workflowId"] = workflow_id
        if node_id is not None:
            body["nodeId"] = node_id
        if node_type is not None:
            body["nodeType"] = node_type
        if node_name is not None:
            body["nodeName"] = node_name
        if description is not None:
            body["description"] = description
        if generation_id is not None:
            body["generationId"] = generation_id
        return await self._client.request("POST", "/credits/usage", json=body)
