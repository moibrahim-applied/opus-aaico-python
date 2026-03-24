"""Tests for the base HTTP client layer."""

from unittest.mock import patch

import pytest

from opus_aaico._client import AsyncHTTPClient, SyncHTTPClient
from opus_aaico._constants import BASE_URL, USER_AGENT
from opus_aaico._exceptions import AuthenticationError


class TestBaseClientInit:
    """Test client initialization and configuration."""

    def test_requires_api_key(self) -> None:
        """Client raises AuthenticationError when no API key is provided."""
        with patch.dict("os.environ", {}, clear=True):
            # Ensure env vars are cleared
            with patch("os.environ.get", return_value=""):
                with pytest.raises(AuthenticationError, match="API key is required"):
                    SyncHTTPClient()

    def test_accepts_api_key_param(self, api_key: str) -> None:
        """Client accepts api_key as a constructor parameter."""
        client = SyncHTTPClient(api_key=api_key)
        assert client.api_key == api_key
        client.close()

    def test_reads_api_key_from_env(self) -> None:
        """Client reads API key from OPUS_API_KEY environment variable."""
        with patch.dict("os.environ", {"OPUS_API_KEY": "env-key-456"}):
            client = SyncHTTPClient()
            assert client.api_key == "env-key-456"
            client.close()

    def test_default_base_url(self, api_key: str) -> None:
        """Client uses the default base URL when none is provided."""
        client = SyncHTTPClient(api_key=api_key)
        assert client.base_url == BASE_URL
        client.close()

    def test_custom_base_url(self, api_key: str, base_url: str) -> None:
        """Client accepts a custom base URL."""
        client = SyncHTTPClient(api_key=api_key, base_url=base_url)
        assert client.base_url == base_url
        client.close()

    def test_base_url_from_env(self, api_key: str) -> None:
        """Client reads base URL from OPUS_BASE_URL environment variable."""
        with patch.dict("os.environ", {"OPUS_BASE_URL": "https://custom.opus.com"}):
            client = SyncHTTPClient(api_key=api_key)
            assert client.base_url == "https://custom.opus.com"
            client.close()

    def test_base_url_strips_trailing_slash(self, api_key: str) -> None:
        """Client strips trailing slash from base URL."""
        client = SyncHTTPClient(api_key=api_key, base_url="https://test.opus.com/")
        assert client.base_url == "https://test.opus.com"
        client.close()


class TestClientHeaders:
    """Test header construction."""

    def test_builds_correct_headers(self, api_key: str) -> None:
        """Client builds headers with x-service-key and User-Agent."""
        client = SyncHTTPClient(api_key=api_key, workspace_id="ws-123")
        headers = client._build_headers()
        assert headers["x-service-key"] == api_key
        assert headers["x-workspace-id"] == "ws-123"
        assert headers["User-Agent"] == USER_AGENT
        assert headers["Content-Type"] == "application/json"
        client.close()

    def test_omits_workspace_id_when_not_set(self, api_key: str) -> None:
        """Client omits x-workspace-id header when workspace_id is not set."""
        client = SyncHTTPClient(api_key=api_key)
        headers = client._build_headers()
        assert "x-workspace-id" not in headers
        client.close()

    def test_includes_bearer_token(self, api_key: str) -> None:
        """Client includes Authorization header when bearer_token is set."""
        client = SyncHTTPClient(api_key=api_key, bearer_token="my-token")
        headers = client._build_headers()
        assert headers["Authorization"] == "Bearer my-token"
        client.close()


class TestClientContextManager:
    """Test context manager support."""

    def test_sync_context_manager(self, api_key: str) -> None:
        """SyncHTTPClient supports context manager protocol."""
        with SyncHTTPClient(api_key=api_key) as client:
            assert isinstance(client, SyncHTTPClient)

    @pytest.mark.asyncio
    async def test_async_context_manager(self, api_key: str) -> None:
        """AsyncHTTPClient supports async context manager protocol."""
        async with AsyncHTTPClient(api_key=api_key) as client:
            assert isinstance(client, AsyncHTTPClient)


class TestClientRetryLogic:
    """Test retry decision logic."""

    def test_should_retry_on_429(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._should_retry(429, 0) is True
        client.close()

    def test_should_retry_on_500(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._should_retry(500, 0) is True
        client.close()

    def test_should_not_retry_on_400(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._should_retry(400, 0) is False
        client.close()

    def test_should_not_retry_on_401(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._should_retry(401, 0) is False
        client.close()

    def test_should_not_retry_on_403(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._should_retry(403, 0) is False
        client.close()

    def test_should_not_retry_on_404(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._should_retry(404, 0) is False
        client.close()

    def test_should_not_retry_when_max_reached(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key, max_retries=2)
        assert client._should_retry(500, 2) is False
        client.close()

    def test_retry_delay_exponential(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._retry_delay(0) == 1
        assert client._retry_delay(1) == 2
        assert client._retry_delay(2) == 4
        assert client._retry_delay(3) == 8
        client.close()

    def test_retry_delay_capped_at_30(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._retry_delay(10) == 30
        client.close()

    def test_retry_delay_respects_retry_after(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._retry_delay(0, retry_after=5.0) == 5.0
        client.close()


class TestBuildUrl:
    """Test URL construction."""

    def test_build_url(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        assert client._build_url("/api/v1/jobs") == f"{BASE_URL}/api/v1/jobs"
        client.close()

    def test_build_url_strips_leading_slash(self, api_key: str) -> None:
        client = SyncHTTPClient(api_key=api_key)
        url = client._build_url("api/v1/jobs")
        assert url == f"{BASE_URL}/api/v1/jobs"
        client.close()
