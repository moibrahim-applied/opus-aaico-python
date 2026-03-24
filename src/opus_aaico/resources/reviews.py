"""Reviews resource — initiate, list, pick, release, submit results."""

from __future__ import annotations

from typing import Any

from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.reviews import ReviewInitiateResponse, ReviewSubmitResponse


class SyncReviews(SyncResource):
    """Synchronous reviews resource."""

    def initiate(
        self,
        job_execution_id: str,
        type: str,
        node_id: str,
        node_name: str,
        workflow_id: str,
        review_payload: dict[str, Any],
        input_definition_schema: dict[str, Any],
        output_definition_schema: dict[str, Any],
        webhook_callback: str,
        assignee_id: str | None = None,
        max_duration: int = 24,
    ) -> ReviewInitiateResponse:
        body: dict[str, Any] = {
            "jobExecutionId": job_execution_id,
            "type": type,
            "nodeId": node_id,
            "nodeName": node_name,
            "workflowId": workflow_id,
            "reviewPayload": review_payload,
            "inputDefinitionSchema": input_definition_schema,
            "outputDefinitionSchema": output_definition_schema,
            "webhookCallback": webhook_callback,
            "maxDuration": max_duration,
        }
        if assignee_id is not None:
            body["assigneeId"] = assignee_id
        data = self._client.request("POST", "/review/initiate", json=body)
        return ReviewInitiateResponse(**data)

    def list(
        self,
        type: str | None = None,
        status: str | None = None,
        offset: int = 0,
        max_results: int = 25,
    ) -> Any:
        params: dict[str, Any] = {
            "offset": offset,
            "maxResults": max_results,
        }
        if type is not None:
            params["type"] = type
        if status is not None:
            params["status"] = status
        return self._client.request("GET", "/review", params=params)

    def get(self, review_id: str, type: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        return self._client.request("GET", f"/review/{review_id}", params=params or None)

    def pick(self, review_id: str) -> Any:
        return self._client.request("PUT", f"/review/{review_id}", json={"action": "pick"})

    def release(self, review_id: str) -> Any:
        return self._client.request("PUT", f"/review/{review_id}", json={"action": "release"})

    def submit_result(
        self,
        review_id: str,
        status: str,
        review_result: dict[str, Any],
    ) -> ReviewSubmitResponse:
        body: dict[str, Any] = {
            "reviewId": review_id,
            "status": status,
            "reviewResult": review_result,
        }
        data = self._client.request("POST", "/review/results", json=body)
        return ReviewSubmitResponse(**data)

    def submit_output(
        self,
        review_id: str,
        accept: bool,
        updated: dict[str, Any],
        comment: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {
            "accept": accept,
            "updated": updated,
        }
        if comment is not None:
            body["comment"] = comment
        return self._client.request("PUT", f"/review/{review_id}/output", json=body)

    def submit_human_task_output(
        self,
        review_id: str,
        updated: dict[str, Any],
    ) -> Any:
        body: dict[str, Any] = {"updated": updated}
        return self._client.request("PUT", f"/review/{review_id}/humanOutput", json=body)

    def check_status(self, job_id: str) -> Any:
        return self._client.request("GET", f"/review/check/{job_id}")


class AsyncReviews(AsyncResource):
    """Asynchronous reviews resource."""

    async def initiate(
        self,
        job_execution_id: str,
        type: str,
        node_id: str,
        node_name: str,
        workflow_id: str,
        review_payload: dict[str, Any],
        input_definition_schema: dict[str, Any],
        output_definition_schema: dict[str, Any],
        webhook_callback: str,
        assignee_id: str | None = None,
        max_duration: int = 24,
    ) -> ReviewInitiateResponse:
        body: dict[str, Any] = {
            "jobExecutionId": job_execution_id,
            "type": type,
            "nodeId": node_id,
            "nodeName": node_name,
            "workflowId": workflow_id,
            "reviewPayload": review_payload,
            "inputDefinitionSchema": input_definition_schema,
            "outputDefinitionSchema": output_definition_schema,
            "webhookCallback": webhook_callback,
            "maxDuration": max_duration,
        }
        if assignee_id is not None:
            body["assigneeId"] = assignee_id
        data = await self._client.request("POST", "/review/initiate", json=body)
        return ReviewInitiateResponse(**data)

    async def list(
        self,
        type: str | None = None,
        status: str | None = None,
        offset: int = 0,
        max_results: int = 25,
    ) -> Any:
        params: dict[str, Any] = {
            "offset": offset,
            "maxResults": max_results,
        }
        if type is not None:
            params["type"] = type
        if status is not None:
            params["status"] = status
        return await self._client.request("GET", "/review", params=params)

    async def get(self, review_id: str, type: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        return await self._client.request("GET", f"/review/{review_id}", params=params or None)

    async def pick(self, review_id: str) -> Any:
        return await self._client.request("PUT", f"/review/{review_id}", json={"action": "pick"})

    async def release(self, review_id: str) -> Any:
        return await self._client.request("PUT", f"/review/{review_id}", json={"action": "release"})

    async def submit_result(
        self,
        review_id: str,
        status: str,
        review_result: dict[str, Any],
    ) -> ReviewSubmitResponse:
        body: dict[str, Any] = {
            "reviewId": review_id,
            "status": status,
            "reviewResult": review_result,
        }
        data = await self._client.request("POST", "/review/results", json=body)
        return ReviewSubmitResponse(**data)

    async def submit_output(
        self,
        review_id: str,
        accept: bool,
        updated: dict[str, Any],
        comment: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {
            "accept": accept,
            "updated": updated,
        }
        if comment is not None:
            body["comment"] = comment
        return await self._client.request("PUT", f"/review/{review_id}/output", json=body)

    async def submit_human_task_output(
        self,
        review_id: str,
        updated: dict[str, Any],
    ) -> Any:
        body: dict[str, Any] = {"updated": updated}
        return await self._client.request("PUT", f"/review/{review_id}/humanOutput", json=body)

    async def check_status(self, job_id: str) -> Any:
        return await self._client.request("GET", f"/review/check/{job_id}")
