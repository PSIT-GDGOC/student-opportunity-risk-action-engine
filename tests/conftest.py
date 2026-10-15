"""Pytest configuration and reusable fixtures for workflow test suite."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List
import pytest

from src.models import Opportunity
from src.workflow import OpportunityWorkflowManager


def get_fixed_now() -> datetime:
    """Return a constant reference timestamp for deterministic test evaluations."""
    return datetime(2026, 10, 14, 12, 0, 0, tzinfo=timezone.utc)


def get_sample_student() -> Dict[str, str]:
    """Return a mock student profile."""
    return {
        "student_id": "student_101",
        "name": "Jane Doe",
        "email": "jane.doe@example.edu",
        "university": "State University",
        "major": "Computer Science",
    }


def get_upcoming_opportunity(now: datetime = None) -> Opportunity:
    """Return an opportunity with plenty of time remaining (14 days)."""
    now = now or get_fixed_now()
    return Opportunity(
        id="opp_upcoming_01",
        title="Software Engineering Summer Internship",
        company="TechCorp Global",
        description="Build highly distributed backend microservices in Python and Go.",
        deadline=now + timedelta(days=14),
        required_documents=["resume.pdf", "transcript.pdf"],
    )


def get_urgent_opportunity(now: datetime = None) -> Opportunity:
    """Return an opportunity approaching its deadline in under 24 hours (20 hours)."""
    now = now or get_fixed_now()
    return Opportunity(
        id="opp_urgent_02",
        title="Global AI Hackathon 2026",
        company="InnovateAI Hub",
        description="Collaborative 48-hour buildathon creating generative AI agents.",
        deadline=now + timedelta(hours=20),
        required_documents=["resume.pdf", "project_proposal.pdf"],
    )


def get_expired_opportunity(now: datetime = None) -> Opportunity:
    """Return an opportunity whose deadline passed 2 days ago."""
    now = now or get_fixed_now()
    return Opportunity(
        id="opp_expired_03",
        title="Graduate Research Fellowship in Robotics",
        company="Robotics Foundation",
        description="Full scholarship and stipend for autonomous systems research.",
        deadline=now - timedelta(days=2),
        required_documents=["resume.pdf", "statement_of_purpose.pdf"],
    )


def get_sample_opportunities(now: datetime = None) -> List[Opportunity]:
    """Return a combined list of mock opportunities."""
    now = now or get_fixed_now()
    return [
        get_upcoming_opportunity(now),
        get_urgent_opportunity(now),
        get_expired_opportunity(now),
    ]


def get_workflow_manager(opportunities: List[Opportunity] = None) -> OpportunityWorkflowManager:
    """Return an OpportunityWorkflowManager pre-loaded with sample opportunities."""
    mgr = OpportunityWorkflowManager()
    mgr.add_opportunities(opportunities or get_sample_opportunities())
    return mgr


# Pytest fixtures
@pytest.fixture
def fixed_now() -> datetime:
    return get_fixed_now()


@pytest.fixture
def sample_student() -> Dict[str, str]:
    return get_sample_student()


@pytest.fixture
def upcoming_opportunity(fixed_now: datetime) -> Opportunity:
    return get_upcoming_opportunity(fixed_now)


@pytest.fixture
def urgent_opportunity(fixed_now: datetime) -> Opportunity:
    return get_urgent_opportunity(fixed_now)


@pytest.fixture
def expired_opportunity(fixed_now: datetime) -> Opportunity:
    return get_expired_opportunity(fixed_now)


@pytest.fixture
def sample_opportunities(fixed_now: datetime) -> List[Opportunity]:
    return get_sample_opportunities(fixed_now)


@pytest.fixture
def workflow_manager(sample_opportunities: List[Opportunity]) -> OpportunityWorkflowManager:
    return get_workflow_manager(sample_opportunities)

