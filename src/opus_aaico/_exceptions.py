"""OPUS SDK error hierarchy."""

from __future__ import annotations

from typing import Any


class OpusError(Exception):
    """Base error for all OPUS SDK exceptions."""

    message: str
    status_code: int | None
    body: Any | None
    request_id: str | None

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        body: Any | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.body = body
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"(status={self.status_code})")
        if self.request_id is not None:
            parts.append(f"[request_id={self.request_id}]")
        return " ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code!r})"
        )


class AuthenticationError(OpusError):
    """401 — Invalid or missing API key."""


class PermissionDeniedError(OpusError):
    """403 — Insufficient permissions."""


class NotFoundError(OpusError):
    """404 — Resource not found."""


class ValidationError(OpusError):
    """400 — Invalid request parameters."""


class RateLimitError(OpusError):
    """429 — Too many requests."""

    retry_after: float | None

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        body: Any | None = None,
        request_id: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code, body, request_id)
        self.retry_after = retry_after


class APIError(OpusError):
    """5xx — Server-side error."""


class TimeoutError(OpusError):
    """Request or polling timeout."""


class ConnectionError(OpusError):
    """Network connection failure."""


# Map HTTP status codes to error classes
STATUS_CODE_MAP: dict[int, type[OpusError]] = {
    400: ValidationError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    429: RateLimitError,
}


def raise_for_status(status_code: int, body: Any, request_id: str | None = None) -> None:
    """Raise the appropriate OpusError for an HTTP error response."""
    if status_code < 400:
        return

    message = "API request failed"
    if isinstance(body, dict):
        message = body.get("message", body.get("error", message))
    elif isinstance(body, str):
        message = body
    elif isinstance(body, list):
        message = "; ".join(str(item) for item in body)

    error_cls = STATUS_CODE_MAP.get(status_code, APIError)

    if error_cls is RateLimitError:
        raise RateLimitError(
            message=message,
            status_code=status_code,
            body=body,
            request_id=request_id,
            retry_after=None,
        )

    raise error_cls(
        message=message,
        status_code=status_code,
        body=body,
        request_id=request_id,
    )
