"""Unofficial Python SDK for the OPUS workflow automation platform."""

__version__ = "0.1.0"

from opus_aaico._async import AsyncOpusClient
from opus_aaico._exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    OpusError,
    PermissionDeniedError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from opus_aaico._sync import OpusClient

__all__ = [
    "__version__",
    "OpusClient",
    "AsyncOpusClient",
    "OpusError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "APIError",
    "TimeoutError",
    "ConnectionError",
]
