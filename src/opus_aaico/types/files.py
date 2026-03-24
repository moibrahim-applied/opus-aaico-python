"""File-related types."""

from __future__ import annotations

from pydantic import Field

from opus_aaico.types.shared import _BaseModel


class FileMetadata(_BaseModel):
    file_id: str | None = Field(None, alias="fileId")
    file_uri: str | None = Field(None, alias="fileUri")
    file_thumbnail_uri: str | None = Field(None, alias="fileThumbnailUri")
    file_name: str | None = Field(None, alias="fileName")
    file_mime_type: str | None = Field(None, alias="fileMimeType")
    file_extension: str | None = Field(None, alias="fileExtension")
    description: str | None = None
    country: str | None = None


class FileSearchResponse(_BaseModel):
    total_count: int = Field(0, alias="totalCount")
    files: list[FileMetadata] = []


class FileGenerateResponse(_BaseModel):
    total_count: int = Field(0, alias="totalCount")
    files: list[FileMetadata] = []


class MultipartInitiateResponse(_BaseModel):
    upload_id: str | None = Field(None, alias="uploadId")
    file_key: str | None = Field(None, alias="fileKey")


class CompleteUploadData(_BaseModel):
    file_url: str | None = Field(None, alias="fileUrl")
    key: str | None = None
    bucket: str | None = None
    e_tag: str | None = Field(None, alias="eTag")


class CompleteUploadResponse(_BaseModel):
    message: str | None = None
    data: CompleteUploadData | None = None


class AbortUploadResponse(_BaseModel):
    message: str | None = None
