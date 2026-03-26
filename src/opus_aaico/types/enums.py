"""Enumerations for the OPUS API."""

from __future__ import annotations

from enum import Enum


class JobStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING = "WAITING"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


class ReviewType(str, Enum):
    AGENT = "AGENT"
    HUMAN = "HUMAN"
    HUMAN_TASK = "HUMAN_TASK"


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    OVERDUE = "OVERDUE"
    DISPATCHED = "DISPATCHED"
    NODE_DISPATCHED = "NODE_DISPATCHED"
    NODE_DISPATCH_FAILED = "NODE_DISPATCH_FAILED"


class MediaType(str, Enum):
    IMAGE = "image"
    DOCUMENT = "document"


class CreditUsageType(str, Enum):
    WORKFLOW_GENERATION = "workflowGeneration"
    NODE_EXECUTION = "nodeExecution"


class ArchiveStatus(str, Enum):
    ALL = "all"
    ARCHIVED_ONLY = "archivedOnly"
    NON_ARCHIVED_ONLY = "nonArchivedOnly"


class WorkflowSource(str, Enum):
    WKG = "WKG"
    USER_GENERATED = "USER_GENERATED"


class ReviewSettingType(str, Enum):
    HUMAN_REVIEW = "humanReview"
    AGENTIC_REVIEW = "agenticReview"
