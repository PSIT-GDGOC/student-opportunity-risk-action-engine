"""Opportunity Workflow Manager implementing the core student opportunity workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Union
import uuid

from src.models import (
    ApplicationStatus,
    DeadlineMetrics,
    Opportunity,
    RiskAssessment,
    RiskFlag,
    RiskLevel,
    StudentApplication,
    _ensure_datetime,
)

# Valid status transitions
VALID_TRANSITIONS: Dict[ApplicationStatus, Set[ApplicationStatus]] = {
    ApplicationStatus.DISCOVERED: {ApplicationStatus.SAVED},
    ApplicationStatus.SAVED: {ApplicationStatus.IN_PROGRESS},
    ApplicationStatus.IN_PROGRESS: {ApplicationStatus.SUBMITTED},
    ApplicationStatus.SUBMITTED: {ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED},
    ApplicationStatus.ACCEPTED: set(),
    ApplicationStatus.REJECTED: set(),
}


class OpportunityWorkflowManager:
    """Manages opportunities, applications, deadline tracking, and risk detection."""

    def __init__(self) -> None:
        self.opportunities: Dict[str, Opportunity] = {}
        self.applications: Dict[str, StudentApplication] = {}
        # Mapping student_id -> set of opportunity_ids
        self._student_saved_opps: Dict[str, Set[str]] = {}

    # ---------------------------------------------------------
    # Opportunity Management
    # ---------------------------------------------------------

    def add_opportunity(self, opportunity: Opportunity) -> Opportunity:
        """Register a new opportunity."""
        self.opportunities[opportunity.id] = opportunity
        return opportunity

    def add_opportunities(self, opportunities: List[Opportunity]) -> None:
        """Register multiple opportunities."""
        for opp in opportunities:
            self.add_opportunity(opp)

    def get_opportunity(self, opportunity_id: str) -> Opportunity:
        """Retrieve an opportunity by ID."""
        if opportunity_id not in self.opportunities:
            raise ValueError(f"Opportunity with ID '{opportunity_id}' not found.")
        return self.opportunities[opportunity_id]

    def view_opportunities(
        self,
        keyword: Optional[str] = None,
        active_only: bool = False,
        current_time: Optional[Union[datetime, str]] = None,
    ) -> List[Opportunity]:
        """List opportunities with optional keyword and active deadline filtering."""
        ref_time = _ensure_datetime(current_time) if current_time else datetime.now(timezone.utc)
        results: List[Opportunity] = list(self.opportunities.values())

        if keyword:
            kw = keyword.strip().lower()
            results = [
                opp
                for opp in results
                if kw in opp.title.lower()
                or kw in opp.company.lower()
                or kw in opp.description.lower()
            ]

        if active_only:
            results = [opp for opp in results if opp.deadline >= ref_time]

        return results

    # Alias for convenience
    list_opportunities = view_opportunities

    # ---------------------------------------------------------
    # Saving Opportunities
    # ---------------------------------------------------------

    def save_opportunity(
        self,
        student_id: str,
        opportunity_id: str,
        application_id: Optional[str] = None,
    ) -> StudentApplication:
        """Bookmark/save an opportunity for a student, preventing duplicate saves."""
        if not student_id:
            raise ValueError("student_id must be provided.")
        if opportunity_id not in self.opportunities:
            raise ValueError(f"Opportunity with ID '{opportunity_id}' not found.")

        # Check for duplicate save
        saved_opps = self._student_saved_opps.setdefault(student_id, set())
        if opportunity_id in saved_opps:
            raise ValueError(
                f"Opportunity '{opportunity_id}' has already been saved by student '{student_id}'."
            )

        app_id = application_id or f"app_{uuid.uuid4().hex[:8]}"
        application = StudentApplication(
            id=app_id,
            student_id=student_id,
            opportunity_id=opportunity_id,
            status=ApplicationStatus.SAVED,
            submitted_documents=[],
            saved_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.applications[app_id] = application
        saved_opps.add(opportunity_id)
        return application

    def get_application(self, application_id: str) -> StudentApplication:
        """Retrieve an application by ID."""
        if application_id not in self.applications:
            raise ValueError(f"Application with ID '{application_id}' not found.")
        return self.applications[application_id]

    def get_student_applications(self, student_id: str) -> List[StudentApplication]:
        """Retrieve all applications for a specific student."""
        return [app for app in self.applications.values() if app.student_id == student_id]

    # ---------------------------------------------------------
    # Application Status Updates & Document Uploads
    # ---------------------------------------------------------

    def update_application_status(
        self,
        application_id: str,
        new_status: Union[ApplicationStatus, str],
    ) -> StudentApplication:
        """Transition an application to a new status, enforcing valid state transitions."""
        app = self.get_application(application_id)

        if isinstance(new_status, str):
            try:
                target_status = ApplicationStatus(new_status)
            except ValueError:
                raise ValueError(f"Unknown application status: '{new_status}'")
        else:
            target_status = new_status

        current_status = app.status

        # Validate transition
        allowed_next_states = VALID_TRANSITIONS.get(current_status, set())
        if target_status not in allowed_next_states:
            raise ValueError(
                f"Invalid status transition from '{current_status.value}' to '{target_status.value}'. "
                f"Allowed transitions from '{current_status.value}': {[s.value for s in allowed_next_states]}."
            )

        app.status = target_status
        app.updated_at = datetime.now(timezone.utc)
        return app

    def upload_document(self, application_id: str, document_name: str) -> StudentApplication:
        """Attach a required or supplementary document to an application."""
        app = self.get_application(application_id)
        app.add_document(document_name)
        return app

    def upload_documents(
        self,
        application_id: str,
        document_names: List[str],
    ) -> StudentApplication:
        """Attach multiple documents to an application."""
        app = self.get_application(application_id)
        for doc in document_names:
            app.add_document(doc)
        return app

    # ---------------------------------------------------------
    # Deadline Tracking
    # ---------------------------------------------------------

    def get_deadline_metrics(
        self,
        opportunity_or_id: Union[str, Opportunity],
        current_time: Optional[Union[datetime, str]] = None,
    ) -> DeadlineMetrics:
        """Calculate deadline metrics including time/days remaining and urgency/expiry."""
        if isinstance(opportunity_or_id, Opportunity):
            opp = opportunity_or_id
        else:
            opp = self.get_opportunity(opportunity_or_id)

        ref_time = _ensure_datetime(current_time) if current_time else datetime.now(timezone.utc)
        time_diff = opp.deadline - ref_time
        total_seconds = time_diff.total_seconds()

        days_remaining = total_seconds / 86400.0
        hours_remaining = total_seconds / 3600.0
        is_expired = total_seconds <= 0
        # Urgent if within 48 hours and not expired
        is_urgent = (0 < total_seconds <= 48 * 3600)

        return DeadlineMetrics(
            opportunity_id=opp.id,
            deadline=opp.deadline,
            time_remaining=time_diff,
            days_remaining=days_remaining,
            hours_remaining=hours_remaining,
            is_expired=is_expired,
            is_urgent=is_urgent,
        )

    def sort_saved_by_urgency(
        self,
        student_id: str,
        current_time: Optional[Union[datetime, str]] = None,
    ) -> List[StudentApplication]:
        """Sort saved opportunities by urgency (nearest upcoming deadline first)."""
        apps = self.get_student_applications(student_id)
        ref_time = _ensure_datetime(current_time) if current_time else datetime.now(timezone.utc)

        def urgency_key(app: StudentApplication) -> tuple:
            opp = self.opportunities.get(app.opportunity_id)
            if not opp:
                return (2, datetime.max.replace(tzinfo=timezone.utc))
            diff = opp.deadline - ref_time
            # Active (non-expired) come first sorted by nearest deadline, expired come after
            if diff.total_seconds() > 0:
                return (0, opp.deadline)
            else:
                return (1, opp.deadline)

        return sorted(apps, key=urgency_key)

    # ---------------------------------------------------------
    # Risk Detection & Action Engine
    # ---------------------------------------------------------

    def detect_risks(
        self,
        application_or_id: Union[str, StudentApplication],
        current_time: Optional[Union[datetime, str]] = None,
    ) -> RiskAssessment:
        """Analyze an application and return risk flags, reasons, and severity level.

        Flags:
        - DEADLINE_EXPIRED: If deadline has passed.
        - DEADLINE_APPROACHING: If deadline is within 48 hours.
        - MISSING_DOCUMENTS: If required documents are missing while in IN_PROGRESS status.
        """
        if isinstance(application_or_id, StudentApplication):
            app = application_or_id
        else:
            app = self.get_application(application_or_id)

        opp = self.get_opportunity(app.opportunity_id)
        metrics = self.get_deadline_metrics(opp, current_time)

        flags: List[str] = []
        reasons: List[str] = []
        actions: List[str] = []
        risk_level = RiskLevel.LOW

        # Once submitted, accepted, or rejected, application is no longer at pending risk
        if app.status in (ApplicationStatus.SUBMITTED, ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED):
            if app.status == ApplicationStatus.SUBMITTED:
                actions.append("Application submitted. Awaiting review result.")
            elif app.status == ApplicationStatus.ACCEPTED:
                actions.append("Application accepted! Prepare for onboarding.")
            else:
                actions.append("Application rejected. Explore other opportunities.")
            return RiskAssessment(
                application_id=app.id,
                opportunity_id=opp.id,
                risk_level=RiskLevel.NONE,
                flags=[],
                reasons=[],
                recommended_actions=actions,
            )

        # Check deadline status
        if metrics.is_expired:
            flags.append(RiskFlag.DEADLINE_EXPIRED.value)
            reasons.append("Deadline has passed.")
            risk_level = RiskLevel.CRITICAL
            actions.append("Deadline has passed. Archive or remove application.")
        elif metrics.is_urgent:
            flags.append(RiskFlag.DEADLINE_APPROACHING.value)
            reasons.append(
                f"Deadline is approaching in {round(metrics.hours_remaining, 1)} hours (within 48 hours)."
            )
            risk_level = RiskLevel.HIGH

        # Check document completion if IN_PROGRESS
        missing_docs = [
            doc for doc in opp.required_documents if doc not in app.submitted_documents
        ]
        if app.status == ApplicationStatus.IN_PROGRESS:
            if missing_docs:
                flags.append(RiskFlag.MISSING_DOCUMENTS.value)
                missing_str = ", ".join(missing_docs)
                reasons.append(f"Missing required documents: {missing_str}")
                if risk_level != RiskLevel.CRITICAL:
                    risk_level = RiskLevel.HIGH if metrics.is_urgent else RiskLevel.MEDIUM
                actions.append(f"Upload missing required documents: {missing_str}")
            else:
                if not metrics.is_expired:
                    actions.append("Review and submit application")

            if metrics.is_urgent and not metrics.is_expired:
                actions.append("Urgent: Submit application within 48 hours")

        elif app.status == ApplicationStatus.SAVED:
            if not metrics.is_expired:
                actions.append("Start application draft")
                if metrics.is_urgent:
                    actions.append("Urgent: Submit application within 48 hours")

        # Deduplicate actions while preserving order
        unique_actions = list(dict.fromkeys(actions))

        return RiskAssessment(
            application_id=app.id,
            opportunity_id=opp.id,
            risk_level=risk_level,
            flags=flags,
            reasons=reasons,
            recommended_actions=unique_actions,
        )

    def get_recommended_actions(
        self,
        application_or_id: Union[str, StudentApplication],
        current_time: Optional[Union[datetime, str]] = None,
    ) -> List[str]:
        """Return actionable next-step strings based on application status and detected risks."""
        assessment = self.detect_risks(application_or_id, current_time)
        return assessment.recommended_actions

