"""Polling utility with exponential backoff."""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, Callable

from opus_aaico._constants import DEFAULT_POLL_INTERVAL, DEFAULT_POLL_TIMEOUT
from opus_aaico._exceptions import TimeoutError


def poll_sync(
    fn: Callable[[], Any],
    terminal_values: Sequence[str],
    extract_value: Callable[[Any], str],
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    timeout: float = DEFAULT_POLL_TIMEOUT,
    on_change: Callable[[str], None] | None = None,
) -> Any:
    """Poll a function until the extracted value is in terminal_values."""
    start = time.monotonic()
    last_value: str | None = None

    while True:
        result = fn()
        current_value = extract_value(result)

        if on_change and current_value != last_value:
            on_change(current_value)
            last_value = current_value

        if current_value in terminal_values:
            return result

        elapsed = time.monotonic() - start
        if elapsed + poll_interval > timeout:
            raise TimeoutError(
                message=f"Polling timed out after {timeout}s. Last status: {current_value}"
            )

        time.sleep(poll_interval)


async def poll_async(
    fn: Callable[[], Any],
    terminal_values: Sequence[str],
    extract_value: Callable[[Any], str],
    poll_interval: float = DEFAULT_POLL_INTERVAL,
    timeout: float = DEFAULT_POLL_TIMEOUT,
    on_change: Callable[[str], None] | None = None,
) -> Any:
    """Async version of poll."""
    import asyncio

    start = time.monotonic()
    last_value: str | None = None

    while True:
        result = await fn()
        current_value = extract_value(result)

        if on_change and current_value != last_value:
            on_change(current_value)
            last_value = current_value

        if current_value in terminal_values:
            return result

        elapsed = time.monotonic() - start
        if elapsed + poll_interval > timeout:
            raise TimeoutError(
                message=f"Polling timed out after {timeout}s. Last status: {current_value}"
            )

        await asyncio.sleep(poll_interval)
