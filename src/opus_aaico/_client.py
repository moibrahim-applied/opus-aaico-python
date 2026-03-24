"""Core HTTP client layer for the OPUS SDK."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

from opus_aaico._constants import (
    BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    USER_AGENT,
)
from opus_aaico._exceptions import (
    AuthenticationError,
    ConnectionError,
    OpusError,
    TimeoutError,
    raise_for_status,
)

logger = logging.getLogger("opus_aaico")


class BaseClient:
    """Shared HTTP client configuration and request logic."""

    api_key: str
    base_url: str
    workspace_id: str | None
    timeout: float
    max_retries: int

    def __init__(
        self,
        api_key: str | None = None,
        workspace_id: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        bearer_token: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPUS_API_KEY", "")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass api_key= or set OPUS_API_KEY environment variable."
            )

        self.workspace_id = workspace_id or os.environ.get("OPUS_WORKSPACE_ID")
        self.base_url = (base_url or os.environ.get("OPUS_BASE_URL") or BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._bearer_token = bearer_token

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "x-service-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"
        if self.workspace_id:
            headers["x-workspace-id"] = self.workspace_id
        return headers

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _should_retry(self, status_code: int, attempt: int) -> bool:
        if attempt >= self.max_retries:
            return False
        return status_code in (429, 500, 502, 503, 504)

    def _retry_delay(self, attempt: int, retry_after: float | None = None) -> float:
        if retry_after is not None:
            return retry_after
        return min(2**attempt, 30)  # 1, 2, 4, 8, ... max 30s


class SyncHTTPClient(BaseClient):
    """Synchronous HTTP client using httpx."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._http = httpx.Client(
            timeout=httpx.Timeout(self.timeout),
            headers=self._build_headers(),
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> SyncHTTPClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def request(
        self,
        method: str,
        path: str,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = self._build_url(path)
        merged_headers = {**self._build_headers(), **(headers or {})}

        # Remove Content-Type for multipart uploads
        if files is not None:
            merged_headers.pop("Content-Type", None)

        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"{method} {url} (attempt {attempt + 1})")
                response = self._http.request(
                    method=method,
                    url=url,
                    json=json,
                    params=_clean_params(params),
                    data=data,
                    files=files,
                    headers=merged_headers,
                )

                logger.debug(
                    f"Response: {response.status_code} ({response.elapsed.total_seconds():.2f}s)"
                )

                if self._should_retry(response.status_code, attempt):
                    retry_after = _parse_retry_after(response.headers)
                    delay = self._retry_delay(attempt, retry_after)
                    logger.info(f"Retrying in {delay:.1f}s (status={response.status_code})")
                    time.sleep(delay)
                    continue

                if response.status_code >= 400:
                    body = _safe_json(response)
                    request_id = response.headers.get("x-request-id")
                    raise_for_status(response.status_code, body, request_id)

                if response.status_code == 204:
                    return None

                return response.json()

            except httpx.TimeoutException as e:
                last_error = TimeoutError(message=f"Request timed out: {e}")
                if attempt < self.max_retries:
                    time.sleep(self._retry_delay(attempt))
                    continue
                raise last_error from e
            except httpx.ConnectError as e:
                last_error = ConnectionError(message=f"Connection failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self._retry_delay(attempt))
                    continue
                raise last_error from e
            except OpusError:
                raise

        raise last_error or OpusError(message="Request failed after retries")


class AsyncHTTPClient(BaseClient):
    """Asynchronous HTTP client using httpx."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers=self._build_headers(),
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncHTTPClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def request(
        self,
        method: str,
        path: str,
        json: Any | None = None,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        import asyncio

        url = self._build_url(path)
        merged_headers = {**self._build_headers(), **(headers or {})}

        if files is not None:
            merged_headers.pop("Content-Type", None)

        last_error: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"{method} {url} (attempt {attempt + 1})")
                response = await self._http.request(
                    method=method,
                    url=url,
                    json=json,
                    params=_clean_params(params),
                    data=data,
                    files=files,
                    headers=merged_headers,
                )

                logger.debug(f"Response: {response.status_code}")

                if self._should_retry(response.status_code, attempt):
                    retry_after = _parse_retry_after(response.headers)
                    delay = self._retry_delay(attempt, retry_after)
                    logger.info(f"Retrying in {delay:.1f}s (status={response.status_code})")
                    await asyncio.sleep(delay)
                    continue

                if response.status_code >= 400:
                    body = _safe_json(response)
                    request_id = response.headers.get("x-request-id")
                    raise_for_status(response.status_code, body, request_id)

                if response.status_code == 204:
                    return None

                return response.json()

            except httpx.TimeoutException as e:
                last_error = TimeoutError(message=f"Request timed out: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(self._retry_delay(attempt))
                    continue
                raise last_error from e
            except httpx.ConnectError as e:
                last_error = ConnectionError(message=f"Connection failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(self._retry_delay(attempt))
                    continue
                raise last_error from e
            except OpusError:
                raise

        raise last_error or OpusError(message="Request failed after retries")


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove None values from query params."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}


def _parse_retry_after(headers: httpx.Headers) -> float | None:
    """Parse Retry-After header."""
    value = headers.get("retry-after")
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _safe_json(response: httpx.Response) -> Any:
    """Try to parse JSON body, fall back to text."""
    try:
        return response.json()
    except Exception:
        return response.text
