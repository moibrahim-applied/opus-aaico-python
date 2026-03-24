"""Policy types."""

from __future__ import annotations

from pydantic import Field

from opus_aaico.types.shared import UserDetails, _BaseModel


class PolicyType(_BaseModel):
    name: str | None = None
    display_name: str | None = Field(None, alias="displayName")
    documentation_url: str | None = Field(None, alias="documentationUrl")


class Policy(_BaseModel):
    id: str | None = None
    organization_id: str | None = Field(None, alias="organizationId")
    user_id: str | None = Field(None, alias="userId")
    user: UserDetails | None = None
    s3_uri: str | None = Field(None, alias="s3Uri")
    file_name: str | None = Field(None, alias="fileName")
    file_type: str | None = Field(None, alias="fileType")
    policy_type: str | None = Field(None, alias="policyType")
    summary: str | None = None
    summary_status: str | None = Field(None, alias="summaryStatus")
    policy_enabled: bool | None = Field(None, alias="policyEnabled")
    policy_title: str | None = Field(None, alias="policyTitle")
    policy_categories: list[str] | None = Field(None, alias="policyCategories")
    summary_text: str | None = Field(None, alias="summaryText")
    created_at: str | None = Field(None, alias="createdAt")
    updated_at: str | None = Field(None, alias="updatedAt")
    deleted_at: str | None = Field(None, alias="deletedAt")


class PolicyPaginationMeta(_BaseModel):
    current_page: int | None = Field(None, alias="currentPage")
    items_per_page: int | None = Field(None, alias="itemsPerPage")
    total_items: int | None = Field(None, alias="totalItems")
    total_pages: int | None = Field(None, alias="totalPages")


class PolicyListResponse(_BaseModel):
    data: list[Policy] = []
    meta: PolicyPaginationMeta | None = None


class PolicySummary(_BaseModel):
    id: str | None = None
    organization_id: str | None = Field(None, alias="organizationId")
    summary: str | None = None
    summary_status: str | None = Field(None, alias="summaryStatus")
    created_at: str | None = Field(None, alias="createdAt")
    updated_at: str | None = Field(None, alias="updatedAt")
    deleted_at: str | None = Field(None, alias="deletedAt")
