"""Credit types."""

from __future__ import annotations

from pydantic import Field

from opus_aaico.types.enums import CreditUsageType
from opus_aaico.types.shared import UserDetails, _BaseModel


class CreditBalance(_BaseModel):
    user_id: str | None = Field(None, alias="userId")
    organization_id: str | None = Field(None, alias="organizationId")
    credits: float | None = None
    credits_left: float | None = Field(None, alias="creditsLeft")


class CreditUsage(_BaseModel):
    created_at: str | None = Field(None, alias="createdAt")
    usage_type: CreditUsageType | None = Field(None, alias="usageType")
    generation_id: str | None = Field(None, alias="generationId")
    workflow_id: str | None = Field(None, alias="workflowId")
    node_id: str | None = Field(None, alias="nodeId")
    node_type: str | None = Field(None, alias="nodeType")
    node_name: str | None = Field(None, alias="nodeName")
    credits_used: float | None = Field(None, alias="creditsUsed")
    description: str | None = None
    user: UserDetails | None = None


class CreditHistoryEntry(_BaseModel):
    """One row from /credits/history (v2 endpoint)."""

    date: str | None = None
    balance_after: float | None = None
    credits_used: float | None = None
    description: str | None = None
    workflow_id: str | None = None
    workflow_name: str | None = None
    user_id: str | None = None
    user_name: str | None = None
