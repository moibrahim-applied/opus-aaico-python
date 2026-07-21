"""Helpers for constructing job execute payload input values.

The values returned here go into the ``payload`` dict passed to
:meth:`workflows.run` / :meth:`jobs.execute` (sent to the API as
``jobPayloadSchemaInstance``). Each helper returns the value for a single
workflow input, keyed by that input's variable name in the payload.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def file_input(url: str) -> dict[str, Any]:
    """Build a single-file workflow input value.

    Use for a workflow ``File`` input. ``url`` is the ``fileUrl`` returned by
    the upload step (not the presigned URL).

    Example::

        payload = {"document": file_input(file_url)}
    """
    return {"value": url, "type": "file"}


def file_array_input(urls: Sequence[str]) -> dict[str, Any]:
    """Build a ``File (Multiple)`` / ``array<file>`` workflow input value.

    Passing a bare list of file URLs to an ``array<file>`` input makes the
    executor forward the URLs as plain text, so a vision/extraction agent
    receives links instead of readable files. The required ``typeDefinition``
    declares the array items as files, so OPUS resolves each URL into an
    attached file the agent can read.

    ``urls`` are the ``fileUrl`` values returned by the upload step.

    Example::

        payload = {"documents": file_array_input([url1, url2])}
    """
    return {
        "value": list(urls),
        "type": "array",
        "typeDefinition": {
            "id": "file",
            "variable_name": "file",
            "allowed_types": [{"type": "file"}],
        },
    }
