"""Files resource — upload, download, search, generate, and multipart upload."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from opus_aaico._exceptions import ValidationError
from opus_aaico._utils.files import (
    get_file_extension,
    upload_bytes_to_presigned_url_async,
    upload_bytes_to_presigned_url_sync,
    upload_to_presigned_url_async,
    upload_to_presigned_url_sync,
)
from opus_aaico.resources._base import AsyncResource, SyncResource
from opus_aaico.types.files import (
    AbortUploadResponse,
    CompleteUploadResponse,
    FileGenerateResponse,
    FileSearchResponse,
    MultipartInitiateResponse,
)
from opus_aaico.types.jobs import JobFileDownloadResponse, JobFileUploadResponse

if TYPE_CHECKING:
    from opus_aaico._client import AsyncHTTPClient, SyncHTTPClient


def _upload_scope_fields(
    client: SyncHTTPClient | AsyncHTTPClient,
    workflow_id: str | None,
    workspace_id: str | None,
) -> dict[str, str]:
    """Resolve the scope field required by ``/job/file/upload``.

    The endpoint now requires one of ``workflowId`` or ``workspaceId``. Prefer an
    explicit ``workflow_id``, then an explicit ``workspace_id``, then fall back to
    the client's configured workspace. Raise ``ValidationError`` if none is found.
    """
    if workflow_id:
        return {"workflowId": workflow_id}
    if workspace_id:
        return {"workspaceId": workspace_id}
    if client.workspace_id:
        return {"workspaceId": client.workspace_id}
    raise ValidationError(
        message=(
            "File upload requires a scope: pass workflow_id= or workspace_id= to "
            "upload(), or configure a default workspace via OpusClient(workspace_id=...) "
            "or the OPUS_WORKSPACE_ID environment variable. The /job/file/upload endpoint "
            "no longer accepts requests without one of workflowId or workspaceId."
        ),
        status_code=400,
    )


class SyncFiles(SyncResource):
    """Synchronous files resource."""

    # ---- upload via presigned URL ----------------------------------------

    def upload(
        self,
        file_path: str,
        access_scope: str = "organization",
        workflow_id: str | None = None,
        workspace_id: str | None = None,
    ) -> str:
        """Upload a local file and return its permanent URL.

        The ``/job/file/upload`` endpoint requires one of ``workflow_id`` or
        ``workspace_id``. If neither is passed, the client's configured workspace
        is used; a ``ValidationError`` is raised when none can be resolved.
        """
        ext = get_file_extension(file_path)
        body: dict[str, Any] = {
            "fileExtension": ext,
            "accessScope": access_scope,
            **_upload_scope_fields(self._client, workflow_id, workspace_id),
        }
        data = self._client.request("POST", "/job/file/upload", json=body)
        resp = JobFileUploadResponse(**data)
        upload_to_presigned_url_sync(resp.presigned_url, file_path)
        return resp.file_url  # type: ignore[return-value]

    def upload_bytes(
        self,
        data: bytes,
        file_extension: str,
        access_scope: str = "organization",
        workflow_id: str | None = None,
        workspace_id: str | None = None,
    ) -> str:
        """Upload raw bytes and return the permanent URL.

        Requires one of ``workflow_id`` or ``workspace_id`` (see :meth:`upload`).
        """
        body: dict[str, Any] = {
            "fileExtension": file_extension,
            "accessScope": access_scope,
            **_upload_scope_fields(self._client, workflow_id, workspace_id),
        }
        resp_data = self._client.request("POST", "/job/file/upload", json=body)
        resp = JobFileUploadResponse(**resp_data)
        upload_bytes_to_presigned_url_sync(resp.presigned_url, data)
        return resp.file_url  # type: ignore[return-value]

    # ---- download --------------------------------------------------------

    def download(
        self,
        file_url: str,
        custom_expiry: int | None = None,
    ) -> JobFileDownloadResponse:
        body: dict[str, Any] = {"fileUrl": file_url}
        if custom_expiry is not None:
            body["customExpiry"] = custom_expiry
        data = self._client.request("POST", "/job/file/download", json=body)
        return JobFileDownloadResponse(**data)

    # ---- search ----------------------------------------------------------

    def search(
        self,
        query: str,
        media_type: str | None = None,
        country: str | None = None,
        language: str | None = None,
        max_results: int = 25,
    ) -> FileSearchResponse:
        params: dict[str, Any] = {
            "query": query,
            "maxResults": max_results,
        }
        if media_type is not None:
            params["mediaType"] = media_type
        if country is not None:
            params["country"] = country
        if language is not None:
            params["language"] = language
        data = self._client.request("GET", "/file/search", params=params)
        return FileSearchResponse(**data)

    # ---- generate --------------------------------------------------------

    def generate(
        self,
        user_query: str,
        mime_type: str,
        file_extension: str,
        country: str | None = None,
    ) -> FileGenerateResponse:
        body: dict[str, Any] = {
            "userQuery": user_query,
            "mimeType": mime_type,
            "fileExtension": file_extension,
        }
        if country is not None:
            body["country"] = country
        data = self._client.request("POST", "/file/generate", json=body)
        return FileGenerateResponse(**data)

    # ---- multipart upload ------------------------------------------------

    def multipart_upload(
        self,
        file_path: str,
        content_type: str,
        job_id: str | None = None,
        use_public_bucket: bool = False,
    ) -> str:
        """Initiate, complete (stub), and return the file URL."""
        file_name = os.path.basename(file_path)
        init_body: dict[str, Any] = {
            "fileName": file_name,
            "contentType": content_type,
            "usePublicBucket": use_public_bucket,
        }
        if job_id is not None:
            init_body["jobId"] = job_id

        init_data = self._client.request("POST", "/file/multipart/initiate", json=init_body)
        init_resp = MultipartInitiateResponse(**init_data)

        try:
            complete_body: dict[str, Any] = {
                "fileKey": init_resp.file_key,
                "uploadId": init_resp.upload_id,
                "parts": [],
            }
            complete_data = self._client.request(
                "POST", "/file/multipart/complete", json=complete_body
            )
            complete_resp = CompleteUploadResponse(**complete_data)
            return complete_resp.data.file_url  # type: ignore[union-attr]
        except Exception:
            self.multipart_abort(init_resp.file_key, init_resp.upload_id)  # type: ignore[arg-type]
            raise

    def multipart_abort(
        self,
        file_key: str,
        upload_id: str,
    ) -> AbortUploadResponse:
        body: dict[str, Any] = {
            "fileKey": file_key,
            "uploadId": upload_id,
        }
        data = self._client.request("POST", "/file/multipart/abort", json=body)
        return AbortUploadResponse(**data)


class AsyncFiles(AsyncResource):
    """Asynchronous files resource."""

    # ---- upload via presigned URL ----------------------------------------

    async def upload(
        self,
        file_path: str,
        access_scope: str = "organization",
        workflow_id: str | None = None,
        workspace_id: str | None = None,
    ) -> str:
        """Upload a local file and return its permanent URL.

        Requires one of ``workflow_id`` or ``workspace_id`` (see
        :meth:`SyncFiles.upload`).
        """
        ext = get_file_extension(file_path)
        body: dict[str, Any] = {
            "fileExtension": ext,
            "accessScope": access_scope,
            **_upload_scope_fields(self._client, workflow_id, workspace_id),
        }
        data = await self._client.request("POST", "/job/file/upload", json=body)
        resp = JobFileUploadResponse(**data)
        await upload_to_presigned_url_async(resp.presigned_url, file_path)
        return resp.file_url  # type: ignore[return-value]

    async def upload_bytes(
        self,
        data: bytes,
        file_extension: str,
        access_scope: str = "organization",
        workflow_id: str | None = None,
        workspace_id: str | None = None,
    ) -> str:
        """Upload raw bytes and return the permanent URL.

        Requires one of ``workflow_id`` or ``workspace_id``.
        """
        body: dict[str, Any] = {
            "fileExtension": file_extension,
            "accessScope": access_scope,
            **_upload_scope_fields(self._client, workflow_id, workspace_id),
        }
        resp_data = await self._client.request("POST", "/job/file/upload", json=body)
        resp = JobFileUploadResponse(**resp_data)
        await upload_bytes_to_presigned_url_async(resp.presigned_url, data)
        return resp.file_url  # type: ignore[return-value]

    # ---- download --------------------------------------------------------

    async def download(
        self,
        file_url: str,
        custom_expiry: int | None = None,
    ) -> JobFileDownloadResponse:
        body: dict[str, Any] = {"fileUrl": file_url}
        if custom_expiry is not None:
            body["customExpiry"] = custom_expiry
        data = await self._client.request("POST", "/job/file/download", json=body)
        return JobFileDownloadResponse(**data)

    # ---- search ----------------------------------------------------------

    async def search(
        self,
        query: str,
        media_type: str | None = None,
        country: str | None = None,
        language: str | None = None,
        max_results: int = 25,
    ) -> FileSearchResponse:
        params: dict[str, Any] = {
            "query": query,
            "maxResults": max_results,
        }
        if media_type is not None:
            params["mediaType"] = media_type
        if country is not None:
            params["country"] = country
        if language is not None:
            params["language"] = language
        data = await self._client.request("GET", "/file/search", params=params)
        return FileSearchResponse(**data)

    # ---- generate --------------------------------------------------------

    async def generate(
        self,
        user_query: str,
        mime_type: str,
        file_extension: str,
        country: str | None = None,
    ) -> FileGenerateResponse:
        body: dict[str, Any] = {
            "userQuery": user_query,
            "mimeType": mime_type,
            "fileExtension": file_extension,
        }
        if country is not None:
            body["country"] = country
        data = await self._client.request("POST", "/file/generate", json=body)
        return FileGenerateResponse(**data)

    # ---- multipart upload ------------------------------------------------

    async def multipart_upload(
        self,
        file_path: str,
        content_type: str,
        job_id: str | None = None,
        use_public_bucket: bool = False,
    ) -> str:
        file_name = os.path.basename(file_path)
        init_body: dict[str, Any] = {
            "fileName": file_name,
            "contentType": content_type,
            "usePublicBucket": use_public_bucket,
        }
        if job_id is not None:
            init_body["jobId"] = job_id

        init_data = await self._client.request("POST", "/file/multipart/initiate", json=init_body)
        init_resp = MultipartInitiateResponse(**init_data)

        try:
            complete_body: dict[str, Any] = {
                "fileKey": init_resp.file_key,
                "uploadId": init_resp.upload_id,
                "parts": [],
            }
            complete_data = await self._client.request(
                "POST", "/file/multipart/complete", json=complete_body
            )
            complete_resp = CompleteUploadResponse(**complete_data)
            return complete_resp.data.file_url  # type: ignore[union-attr]
        except Exception:
            await self.multipart_abort(init_resp.file_key, init_resp.upload_id)  # type: ignore[arg-type]
            raise

    async def multipart_abort(
        self,
        file_key: str,
        upload_id: str,
    ) -> AbortUploadResponse:
        body: dict[str, Any] = {
            "fileKey": file_key,
            "uploadId": upload_id,
        }
        data = await self._client.request("POST", "/file/multipart/abort", json=body)
        return AbortUploadResponse(**data)
