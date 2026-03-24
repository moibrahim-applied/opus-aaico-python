import pytest

from opus_aaico._exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    OpusError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
    raise_for_status,
)
from opus_aaico._exceptions import (
    ConnectionError as OpusConnectionError,
)
from opus_aaico._exceptions import (
    TimeoutError as OpusTimeoutError,
)


def test_error_hierarchy():
    assert issubclass(AuthenticationError, OpusError)
    assert issubclass(PermissionDeniedError, OpusError)
    assert issubclass(NotFoundError, OpusError)
    assert issubclass(ValidationError, OpusError)
    assert issubclass(RateLimitError, OpusError)
    assert issubclass(APIError, OpusError)
    assert issubclass(OpusTimeoutError, OpusError)
    assert issubclass(OpusConnectionError, OpusError)


def test_error_attributes():
    err = APIError(message="Server error", status_code=500, body={"detail": "fail"})
    assert err.message == "Server error"
    assert err.status_code == 500
    assert err.body == {"detail": "fail"}
    assert "Server error" in str(err)


def test_rate_limit_error_retry_after():
    err = RateLimitError(message="Too many requests", status_code=429, retry_after=5.0)
    assert err.retry_after == 5.0


def test_error_without_status_code():
    err = OpusTimeoutError(message="Request timed out")
    assert err.message == "Request timed out"
    assert err.status_code is None


def test_raise_for_status_400():
    with pytest.raises(ValidationError):
        raise_for_status(400, {"message": "Bad request"})


def test_raise_for_status_401():
    with pytest.raises(AuthenticationError):
        raise_for_status(401, {"message": "Unauthorized"})


def test_raise_for_status_404():
    with pytest.raises(NotFoundError):
        raise_for_status(404, {"message": "Not found"})


def test_raise_for_status_429():
    with pytest.raises(RateLimitError):
        raise_for_status(429, {"message": "Rate limited"})


def test_raise_for_status_500():
    with pytest.raises(APIError):
        raise_for_status(500, {"message": "Internal error"})


def test_raise_for_status_ok():
    raise_for_status(200, {})  # Should not raise
