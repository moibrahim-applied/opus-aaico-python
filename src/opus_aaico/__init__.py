"""Unofficial Python SDK for the OPUS workflow automation platform."""

__version__ = "0.6.0"

from opus_aaico._async import AsyncOpusClient
from opus_aaico._exceptions import (
    APIError,
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    NotSupportedError,
    OpusError,
    PermissionDeniedError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from opus_aaico._sync import OpusClient
from opus_aaico.payloads import file_array_input, file_input

__all__ = [
    "__version__",
    "OpusClient",
    "AsyncOpusClient",
    "file_input",
    "file_array_input",
    "OpusError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "NotSupportedError",
    "ValidationError",
    "RateLimitError",
    "APIError",
    "TimeoutError",
    "ConnectionError",
]
