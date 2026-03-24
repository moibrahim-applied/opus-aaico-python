"""File upload helpers for presigned URL flows."""

from __future__ import annotations

import os

import httpx


def upload_to_presigned_url_sync(presigned_url: str, file_path: str) -> None:
    """Upload a local file to an S3 presigned URL (sync)."""
    with open(file_path, "rb") as f:
        response = httpx.put(presigned_url, content=f.read())
        response.raise_for_status()


async def upload_to_presigned_url_async(presigned_url: str, file_path: str) -> None:
    """Upload a local file to an S3 presigned URL (async)."""
    with open(file_path, "rb") as f:
        data = f.read()
    async with httpx.AsyncClient() as client:
        response = await client.put(presigned_url, content=data)
        response.raise_for_status()


def upload_bytes_to_presigned_url_sync(presigned_url: str, data: bytes) -> None:
    """Upload bytes to an S3 presigned URL (sync)."""
    response = httpx.put(presigned_url, content=data)
    response.raise_for_status()


async def upload_bytes_to_presigned_url_async(presigned_url: str, data: bytes) -> None:
    """Upload bytes to an S3 presigned URL (async)."""
    async with httpx.AsyncClient() as client:
        response = await client.put(presigned_url, content=data)
        response.raise_for_status()


def get_file_extension(file_path: str) -> str:
    """Extract file extension from path."""
    _, ext = os.path.splitext(file_path)
    return ext or ".bin"
