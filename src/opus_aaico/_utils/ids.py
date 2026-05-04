"""ID validation helpers."""

from __future__ import annotations

import re

from opus_aaico._exceptions import ValidationError

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def is_uuid(value: str) -> bool:
    """Return True if value is a canonical 36-char UUID."""
    return bool(UUID_RE.match(value))


def require_uuid(value: str, *, name: str = "id") -> str:
    """Raise ValidationError if value is not a UUID.

    Used to give a clear error to users still passing 16-char short IDs from
    the legacy v1 OPUS interface.
    """
    if not isinstance(value, str) or not is_uuid(value):
        raise ValidationError(
            message=(
                f"{name!r} must be a UUID. OPUS v2 uses UUIDs for workflow IDs. "
                f"The legacy 16-char short IDs from the URL bar are no longer accepted. "
                f"Open your workflow at https://app.opus.com to copy its UUID. "
                f"Got: {value!r}"
            ),
            status_code=400,
        )
    return value
