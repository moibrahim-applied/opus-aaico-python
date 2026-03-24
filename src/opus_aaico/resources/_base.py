"""Base resource classes for sync and async resources."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opus_aaico._client import AsyncHTTPClient, SyncHTTPClient


class SyncResource:
    def __init__(self, client: SyncHTTPClient) -> None:
        self._client = client


class AsyncResource:
    def __init__(self, client: AsyncHTTPClient) -> None:
        self._client = client
