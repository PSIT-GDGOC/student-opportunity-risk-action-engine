"""Domain models for the Student Opportunity Risk & Action Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Union


class ApplicationStatus(str, Enum):
    """Possible lifecycle states of a student application."""

    DISCOVERED = "DISCOVERED"
    SAVED = "SAVED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"

    def __str__(self) -> str:
        return self.value


class RiskLevel(str, Enum):
    """Risk severity levels."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value


class RiskFlag(str, Enum):
    """Specific identified risk flags."""

    DEADLINE_EXPIRED = "DEADLINE_EXPIRED"
    DEADLINE_APPROACHING = "DEADLINE_APPROACHING"
    MISSING_DOCUMENTS = "MISSING_DOCUMENTS"

    def __str__(self) -> str:
        return self.value


def _ensure_datetime(val: Union[datetime, str]) -> datetime:
    """Parse or validate datetime, ensuring it is timezone-aware."""
    if isinstance(val, str):
        # Handle ISO format
        dt = datetime.fromisoformat(val)
    elif isinstance(val, datetime):
        dt = val
    else:
        raise TypeError(f"Expected datetime or ISO string, got {type(val)}")

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass
class Opportunity:
    """Represents a job, internship, hackathon, or scholarship opportunity."""

    id: str
    title: str
    company: str
    deadline: datetime
    description: str = ""
    required_documents: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.deadline = _ensure_datetime(self.deadline)
        if self.required_documents is None:
            self.required_documents = []


@dataclass
class StudentApplication:
    """Represents a student's tracked opportunity application."""

    id: str
    student_id: str
    opportunity_id: str
    status: ApplicationStatus = ApplicationStatus.SAVED
    submitted_documents: List[str] = field(default_factory=list)
    saved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if isinstance(self.status, str):
            try:
                self.status = ApplicationStatus(self.status)
            except ValueError:
                raise ValueError(f"Invalid application status: '{self.status}'")
        self.saved_at = _ensure_datetime(self.saved_at)
        self.updated_at = _ensure_datetime(self.updated_at)
        if self.submitted_documents is None:
            self.submitted_documents = []

    def add_document(self, document_name: str) -> None:
        """Add a submitted document if not already added."""
        if document_name not in self.submitted_documents:
            self.submitted_documents.append(document_name)
            self.updated_at = datetime.now(timezone.utc)


@dataclass
class DeadlineMetrics:
    """Metrics relating to an opportunity's deadline."""

    opportunity_id: str
    deadline: datetime
    time_remaining: timedelta
    days_remaining: float
    hours_remaining: float
    is_expired: bool
    is_urgent: bool


@dataclass
class RiskAssessment:
    """Risk analysis and recommended actions for an application."""

    application_id: str
    opportunity_id: str
    risk_level: RiskLevel
    flags: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)

    @property
    def has_risk(self) -> bool:
        """Check if any risk flags are present."""
        return len(self.flags) > 0

