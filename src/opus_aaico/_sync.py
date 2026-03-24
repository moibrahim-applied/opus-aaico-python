"""Synchronous OPUS client."""

from __future__ import annotations

from typing import Any

from opus_aaico._client import SyncHTTPClient
from opus_aaico.resources.files import SyncFiles
from opus_aaico.resources.jobs import SyncJobs
from opus_aaico.resources.workflows import SyncWorkflows


class OpusClient:
    """Synchronous client for the OPUS API.

    Usage:
        client = OpusClient(api_key="sk-...")
        workflow = client.workflows.get("wf-123")

        # Or with context manager:
        with OpusClient(api_key="sk-...") as client:
            result = client.workflows.run("wf-123", payload={...})
    """

    def __init__(self, **kwargs: Any) -> None:
        self._http = SyncHTTPClient(**kwargs)
        self.jobs = SyncJobs(self._http)
        self.workflows = SyncWorkflows(self._http, self.jobs)
        self.files = SyncFiles(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> OpusClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
