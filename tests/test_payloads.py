"""Tests for the payload input helpers."""

from __future__ import annotations

import opus_aaico
from opus_aaico.payloads import file_array_input, file_input


def test_file_input_shape() -> None:
    assert file_input("https://files.opus.com/a.pdf") == {
        "value": "https://files.opus.com/a.pdf",
        "type": "file",
    }


def test_file_array_input_shape() -> None:
    urls = ["https://files.opus.com/a.pdf", "https://files.opus.com/b.pdf"]
    result = file_array_input(urls)

    assert result["value"] == urls
    assert result["type"] == "array"
    # The load-bearing part: item type is declared as file.
    assert result["typeDefinition"] == {
        "id": "file",
        "variable_name": "file",
        "allowed_types": [{"type": "file"}],
    }


def test_file_array_input_copies_input_list() -> None:
    urls = ["https://files.opus.com/a.pdf"]
    result = file_array_input(urls)
    urls.append("https://files.opus.com/b.pdf")
    # Mutating the caller's list must not change the built payload.
    assert result["value"] == ["https://files.opus.com/a.pdf"]


def test_file_array_input_accepts_any_sequence() -> None:
    result = file_array_input(("https://files.opus.com/a.pdf",))
    assert result["value"] == ["https://files.opus.com/a.pdf"]


def test_helpers_exported_from_package() -> None:
    assert opus_aaico.file_input is file_input
    assert opus_aaico.file_array_input is file_array_input
