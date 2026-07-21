"""Tests for the Files resource."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from opus_aaico._client import SyncHTTPClient
from opus_aaico._exceptions import ValidationError
from opus_aaico.resources.files import SyncFiles
from opus_aaico.types.files import AbortUploadResponse, FileGenerateResponse, FileSearchResponse
from opus_aaico.types.jobs import JobFileDownloadResponse


@pytest.fixture
def client(api_key: str, base_url: str) -> SyncHTTPClient:
    c = SyncHTTPClient(api_key=api_key, base_url=base_url, max_retries=0)
    yield c
    c.close()


@pytest.fixture
def files(client: SyncHTTPClient) -> SyncFiles:
    return SyncFiles(client)


class TestUpload:
    def test_upload_returns_file_url(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str, tmp_path
    ) -> None:
        # Create a temp file
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")

        # Mock the presigned URL request
        httpx_mock.add_response(
            url=f"{base_url}/job/file/upload",
            method="POST",
            json={
                "presignedUrl": "https://s3.example.com/upload?sig=abc",
                "fileUrl": "https://cdn.example.com/files/test.pdf",
            },
        )
        # Mock the presigned URL upload (PUT to S3)
        httpx_mock.add_response(
            url="https://s3.example.com/upload?sig=abc",
            method="PUT",
            status_code=200,
        )

        result = files.upload(str(test_file), workspace_id="ws-1")
        assert result == "https://cdn.example.com/files/test.pdf"

        # Verify the POST body
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["fileExtension"] == ".pdf"
        assert body["accessScope"] == "organization"
        assert body["workspaceId"] == "ws-1"

    def test_upload_sends_workflow_id_scope(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str, tmp_path
    ) -> None:
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")
        httpx_mock.add_response(
            url=f"{base_url}/job/file/upload",
            method="POST",
            json={
                "presignedUrl": "https://s3.example.com/upload?sig=abc",
                "fileUrl": "https://cdn.example.com/files/test.pdf",
            },
        )
        httpx_mock.add_response(
            url="https://s3.example.com/upload?sig=abc", method="PUT", status_code=200
        )

        files.upload(str(test_file), workflow_id="wf-uuid")
        body = json.loads(httpx_mock.get_requests()[0].content)
        assert body["workflowId"] == "wf-uuid"
        assert "workspaceId" not in body

    def test_upload_falls_back_to_client_workspace(
        self, httpx_mock: HTTPXMock, api_key: str, base_url: str, tmp_path
    ) -> None:
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")
        client = SyncHTTPClient(
            api_key=api_key, base_url=base_url, workspace_id="ws-default", max_retries=0
        )
        httpx_mock.add_response(
            url=f"{base_url}/job/file/upload",
            method="POST",
            json={
                "presignedUrl": "https://s3.example.com/upload?sig=abc",
                "fileUrl": "https://cdn.example.com/files/test.pdf",
            },
        )
        httpx_mock.add_response(
            url="https://s3.example.com/upload?sig=abc", method="PUT", status_code=200
        )

        SyncFiles(client).upload(str(test_file))
        body = json.loads(httpx_mock.get_requests()[0].content)
        assert body["workspaceId"] == "ws-default"
        client.close()

    def test_upload_without_scope_raises(
        self, files: SyncFiles, httpx_mock: HTTPXMock, tmp_path
    ) -> None:
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")
        with pytest.raises(ValidationError, match="requires a scope"):
            files.upload(str(test_file))
        # No HTTP request should have been made.
        assert httpx_mock.get_requests() == []

    def test_upload_bytes_returns_file_url(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/file/upload",
            method="POST",
            json={
                "presignedUrl": "https://s3.example.com/upload?sig=xyz",
                "fileUrl": "https://cdn.example.com/files/data.bin",
            },
        )
        httpx_mock.add_response(
            url="https://s3.example.com/upload?sig=xyz",
            method="PUT",
            status_code=200,
        )

        result = files.upload_bytes(b"raw data", ".bin", workspace_id="ws-1")
        assert result == "https://cdn.example.com/files/data.bin"
        body = json.loads(httpx_mock.get_requests()[0].content)
        assert body["workspaceId"] == "ws-1"


class TestDownload:
    def test_download_returns_response(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/file/download",
            method="POST",
            json={
                "presignedUrl": "https://s3.example.com/download?sig=abc",
                "fileUrl": "https://cdn.example.com/files/test.pdf",
                "contentType": "application/pdf",
                "contentLength": 12345,
            },
        )
        result = files.download("https://cdn.example.com/files/test.pdf")
        assert isinstance(result, JobFileDownloadResponse)
        assert result.content_type == "application/pdf"
        assert result.content_length == 12345

    def test_download_with_custom_expiry(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/job/file/download",
            method="POST",
            json={
                "presignedUrl": "https://s3.example.com/dl",
                "fileUrl": "https://cdn.example.com/f.pdf",
            },
        )
        files.download("https://cdn.example.com/f.pdf", custom_expiry=3600)
        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["customExpiry"] == 3600


class TestSearch:
    def test_search_returns_results(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            json={
                "totalCount": 2,
                "files": [
                    {"fileId": "f-1", "fileName": "image1.png"},
                    {"fileId": "f-2", "fileName": "image2.png"},
                ],
            },
        )
        result = files.search("landscape photos", media_type="image")
        assert isinstance(result, FileSearchResponse)
        assert result.total_count == 2
        assert len(result.files) == 2

    def test_search_sends_params(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            method="GET",
            json={"totalCount": 0, "files": []},
        )
        files.search("test", media_type="document", country="US", language="en", max_results=10)
        request = httpx_mock.get_requests()[0]
        assert "query=test" in str(request.url)
        assert "mediaType=document" in str(request.url)
        assert "country=US" in str(request.url)
        assert "language=en" in str(request.url)
        assert "maxResults=10" in str(request.url)


class TestGenerate:
    def test_generate_returns_response(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str
    ) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/file/generate",
            method="POST",
            json={
                "totalCount": 1,
                "files": [{"fileId": "gen-1", "fileName": "generated.png"}],
            },
        )
        result = files.generate("a sunset", "image/png", ".png")
        assert isinstance(result, FileGenerateResponse)
        assert result.total_count == 1


class TestMultipartUpload:
    def test_multipart_upload_returns_url(
        self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str, tmp_path
    ) -> None:
        test_file = tmp_path / "big.mp4"
        test_file.write_bytes(b"video content")

        httpx_mock.add_response(
            url=f"{base_url}/file/multipart/initiate",
            method="POST",
            json={"uploadId": "up-123", "fileKey": "key-abc"},
        )
        httpx_mock.add_response(
            url=f"{base_url}/file/multipart/complete",
            method="POST",
            json={
                "message": "Upload completed",
                "data": {"fileUrl": "https://cdn.example.com/big.mp4"},
            },
        )

        result = files.multipart_upload(str(test_file), "video/mp4")
        assert result == "https://cdn.example.com/big.mp4"

    def test_multipart_abort(self, files: SyncFiles, httpx_mock: HTTPXMock, base_url: str) -> None:
        httpx_mock.add_response(
            url=f"{base_url}/file/multipart/abort",
            method="POST",
            json={"message": "Upload aborted"},
        )
        result = files.multipart_abort("key-1", "up-1")
        assert isinstance(result, AbortUploadResponse)
        assert result.message == "Upload aborted"
