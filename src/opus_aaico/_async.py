"""Asynchronous OPUS client."""

from __future__ import annotations

from typing import Any

from opus_aaico._client import AsyncHTTPClient
from opus_aaico.resources.api_keys import AsyncApiKeys
from opus_aaico.resources.credits import AsyncCredits
from opus_aaico.resources.files import AsyncFiles
from opus_aaico.resources.jobs import AsyncJobs
from opus_aaico.resources.policies import AsyncPolicies
from opus_aaico.resources.reviews import AsyncReviews
from opus_aaico.resources.users import AsyncUsers
from opus_aaico.resources.workflows import AsyncWorkflows


class AsyncOpusClient:
    """Asynchronous client for the OPUS API.

    Usage:
        async with AsyncOpusClient(api_key="sk-...") as client:
            result = await client.workflows.run("wf-123", payload={...})
    """

    def __init__(self, **kwargs: Any) -> None:
        self._http = AsyncHTTPClient(**kwargs)
        self.jobs = AsyncJobs(self._http)
        self.workflows = AsyncWorkflows(self._http, self.jobs)
        self.files = AsyncFiles(self._http)
        self.reviews = AsyncReviews(self._http)
        self.api_keys = AsyncApiKeys(self._http)
        self.credits = AsyncCredits(self._http)
        self.policies = AsyncPolicies(self._http)
        self.users = AsyncUsers(self._http)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> AsyncOpusClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
