"""Unit tests for individual opportunity workflow tasks."""

from datetime import datetime
import pytest

from src.models import ApplicationStatus, RiskFlag, RiskLevel
from src.workflow import OpportunityWorkflowManager


def test_viewing_opportunities(
    workflow_manager: OpportunityWorkflowManager,
    fixed_now: datetime,
) -> None:
    """Test viewing opportunities and verifying list and filter output."""
    # 1. View all opportunities without filter
    all_opps = workflow_manager.view_opportunities(current_time=fixed_now)
    assert len(all_opps) == 3

    # 2. Filter by keyword in title
    hackathon_opps = workflow_manager.view_opportunities(
        keyword="Hackathon",
        current_time=fixed_now,
    )
    assert len(hackathon_opps) == 1
    assert hackathon_opps[0].id == "opp_urgent_02"
    assert "Hackathon" in hackathon_opps[0].title

    # 3. Filter by keyword in company or description
    tech_opps = workflow_manager.view_opportunities(
        keyword="TechCorp",
        current_time=fixed_now,
    )
    assert len(tech_opps) == 1
    assert tech_opps[0].company == "TechCorp Global"

    # 4. Filter by active deadline only (should exclude the expired opportunity)
    active_opps = workflow_manager.view_opportunities(
        active_only=True,
        current_time=fixed_now,
    )
    assert len(active_opps) == 2
    active_ids = {opp.id for opp in active_opps}
    assert "opp_upcoming_01" in active_ids
    assert "opp_urgent_02" in active_ids
    assert "opp_expired_03" not in active_ids

    # 5. Combined filter: keyword + active_only
    matching_active = workflow_manager.view_opportunities(
        keyword="Internship",
        active_only=True,
        current_time=fixed_now,
    )
    assert len(matching_active) == 1
    assert matching_active[0].id == "opp_upcoming_01"


def test_saving_opportunity(
    workflow_manager: OpportunityWorkflowManager,
    sample_student: dict,
) -> None:
    """Test saving an opportunity to tracker and preventing duplicate entries."""
    student_id = sample_student["student_id"]
    target_opp_id = "opp_upcoming_01"

    # 1. Save an opportunity successfully
    app = workflow_manager.save_opportunity(
        student_id=student_id,
        opportunity_id=target_opp_id,
    )
    assert app.id is not None
    assert app.student_id == student_id
    assert app.opportunity_id == target_opp_id
    assert app.status == ApplicationStatus.SAVED
    assert app.submitted_documents == []

    # 2. Prevent duplicate bookmark/save
    with pytest.raises(ValueError) as exc_info:
        workflow_manager.save_opportunity(
            student_id=student_id,
            opportunity_id=target_opp_id,
        )
    assert "already been saved" in str(exc_info.value)

    # 3. Verify saving non-existent opportunity raises ValueError
    with pytest.raises(ValueError) as exc_info:
        workflow_manager.save_opportunity(
            student_id=student_id,
            opportunity_id="non_existent_opp",
        )
    assert "not found" in str(exc_info.value)


def test_application_status_updates(
    workflow_manager: OpportunityWorkflowManager,
    sample_student: dict,
) -> None:
    """Test application status transitions and error handling on invalid transitions."""
    student_id = sample_student["student_id"]
    app = workflow_manager.save_opportunity(student_id, "opp_upcoming_01")
    assert app.status == ApplicationStatus.SAVED

    # 1. Valid transition: SAVED -> IN_PROGRESS
    app = workflow_manager.update_application_status(
        app.id,
        ApplicationStatus.IN_PROGRESS,
    )
    assert app.status == ApplicationStatus.IN_PROGRESS

    # 2. Valid transition: IN_PROGRESS -> SUBMITTED
    app = workflow_manager.update_application_status(
        app.id,
        ApplicationStatus.SUBMITTED,
    )
    assert app.status == ApplicationStatus.SUBMITTED

    # 3. Valid transition: SUBMITTED -> ACCEPTED
    app = workflow_manager.update_application_status(
        app.id,
        ApplicationStatus.ACCEPTED,
    )
    assert app.status == ApplicationStatus.ACCEPTED

    # 4. Invalid transition: ACCEPTED -> IN_PROGRESS (Terminal state)
    with pytest.raises(ValueError) as exc_info:
        workflow_manager.update_application_status(app.id, ApplicationStatus.IN_PROGRESS)
    assert "Invalid status transition" in str(exc_info.value)

    # 5. Invalid transition: Direct skip from SAVED -> SUBMITTED
    app2 = workflow_manager.save_opportunity(student_id, "opp_urgent_02")
    with pytest.raises(ValueError) as exc_info:
        workflow_manager.update_application_status(app2.id, ApplicationStatus.SUBMITTED)
    assert "Invalid status transition" in str(exc_info.value)

    # 6. Invalid transition: Backward from SUBMITTED -> SAVED
    app_to_submit = workflow_manager.update_application_status(
        app2.id,
        ApplicationStatus.IN_PROGRESS,
    )
    app_submitted = workflow_manager.update_application_status(
        app_to_submit.id,
        ApplicationStatus.SUBMITTED,
    )
    with pytest.raises(ValueError) as exc_info:
        workflow_manager.update_application_status(app_submitted.id, ApplicationStatus.SAVED)
    assert "Invalid status transition" in str(exc_info.value)

    # 7. Invalid string status
    with pytest.raises(ValueError) as exc_info:
        workflow_manager.update_application_status(app_submitted.id, "NOT_A_REAL_STATUS")
    assert "Unknown application status" in str(exc_info.value)


def test_deadline_tracking(
    workflow_manager: OpportunityWorkflowManager,
    sample_student: dict,
    fixed_now: datetime,
) -> None:
    """Test deadline tracking metrics accuracy for upcoming, urgent, and expired opportunities."""
    # 1. Check upcoming opportunity (14 days remaining)
    m_upcoming = workflow_manager.get_deadline_metrics("opp_upcoming_01", current_time=fixed_now)
    assert m_upcoming.opportunity_id == "opp_upcoming_01"
    assert m_upcoming.is_expired is False
    assert m_upcoming.is_urgent is False
    assert pytest.approx(m_upcoming.days_remaining, 0.01) == 14.0
    assert pytest.approx(m_upcoming.hours_remaining, 0.1) == 336.0

    # 2. Check urgent opportunity (< 24 hours remaining, specifically 20 hours)
    m_urgent = workflow_manager.get_deadline_metrics("opp_urgent_02", current_time=fixed_now)
    assert m_urgent.opportunity_id == "opp_urgent_02"
    assert m_urgent.is_expired is False
    assert m_urgent.is_urgent is True
    assert pytest.approx(m_urgent.hours_remaining, 0.1) == 20.0
    assert m_urgent.hours_remaining < 24.0

    # 3. Check expired opportunity (2 days expired)
    m_expired = workflow_manager.get_deadline_metrics("opp_expired_03", current_time=fixed_now)
    assert m_expired.opportunity_id == "opp_expired_03"
    assert m_expired.is_expired is True
    assert m_expired.is_urgent is False
    assert m_expired.days_remaining < 0
    assert m_expired.hours_remaining < 0

    # 4. Check sorting saved opportunities by urgency
    student_id = sample_student["student_id"]
    workflow_manager.save_opportunity(student_id, "opp_upcoming_01")
    workflow_manager.save_opportunity(student_id, "opp_expired_03")
    workflow_manager.save_opportunity(student_id, "opp_urgent_02")

    sorted_apps = workflow_manager.sort_saved_by_urgency(student_id, current_time=fixed_now)
    # The active nearest deadline (opp_urgent_02) should come first, then opp_upcoming_01, then expired
    assert sorted_apps[0].opportunity_id == "opp_urgent_02"
    assert sorted_apps[1].opportunity_id == "opp_upcoming_01"
    assert sorted_apps[2].opportunity_id == "opp_expired_03"


def test_risk_detection(
    workflow_manager: OpportunityWorkflowManager,
    sample_student: dict,
    fixed_now: datetime,
) -> None:
    """Test risk detection for approaching deadlines, expired deadlines, and missing documents."""
    student_id = sample_student["student_id"]

    # 1. Approaching deadline risk (<48 hours)
    urgent_app = workflow_manager.save_opportunity(student_id, "opp_urgent_02")
    assessment_urgent = workflow_manager.detect_risks(urgent_app, current_time=fixed_now)
    assert RiskFlag.DEADLINE_APPROACHING.value in assessment_urgent.flags
    assert assessment_urgent.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    # 2. Expired deadline risk
    expired_app = workflow_manager.save_opportunity(student_id, "opp_expired_03")
    assessment_expired = workflow_manager.detect_risks(expired_app, current_time=fixed_now)
    assert RiskFlag.DEADLINE_EXPIRED.value in assessment_expired.flags
    assert assessment_expired.risk_level == RiskLevel.CRITICAL

    # 3. Missing documents risk while in IN_PROGRESS
    app = workflow_manager.save_opportunity(student_id, "opp_upcoming_01")
    # In SAVED status, missing documents flag is not yet triggered
    assessment_saved = workflow_manager.detect_risks(app, current_time=fixed_now)
    assert RiskFlag.MISSING_DOCUMENTS.value not in assessment_saved.flags

    # Transition to IN_PROGRESS without required documents
    workflow_manager.update_application_status(app.id, ApplicationStatus.IN_PROGRESS)
    assessment_in_progress = workflow_manager.detect_risks(app, current_time=fixed_now)
    assert RiskFlag.MISSING_DOCUMENTS.value in assessment_in_progress.flags
    assert "resume.pdf" in assessment_in_progress.reasons[0]
    assert "transcript.pdf" in assessment_in_progress.reasons[0]

    # Upload only 1 of 2 required documents
    workflow_manager.upload_document(app.id, "resume.pdf")
    assessment_partial = workflow_manager.detect_risks(app, current_time=fixed_now)
    assert RiskFlag.MISSING_DOCUMENTS.value in assessment_partial.flags
    assert "transcript.pdf" in assessment_partial.reasons[0]
    assert "resume.pdf" not in assessment_partial.reasons[0]

    # Upload the remaining document -> missing documents risk is resolved
    workflow_manager.upload_document(app.id, "transcript.pdf")
    assessment_complete = workflow_manager.detect_risks(app, current_time=fixed_now)
    assert RiskFlag.MISSING_DOCUMENTS.value not in assessment_complete.flags


def test_recommended_actions(
    workflow_manager: OpportunityWorkflowManager,
    sample_student: dict,
    fixed_now: datetime,
) -> None:
    """Test recommended actions generation based on risk flags and current application state."""
    student_id = sample_student["student_id"]

    # 1. Application in SAVED status (not urgent)
    app = workflow_manager.save_opportunity(student_id, "opp_upcoming_01")
    actions_saved = workflow_manager.get_recommended_actions(app, current_time=fixed_now)
    assert "Start application draft" in actions_saved

    # 2. Application in IN_PROGRESS status with missing documents
    workflow_manager.update_application_status(app.id, ApplicationStatus.IN_PROGRESS)
    actions_in_progress = workflow_manager.get_recommended_actions(app, current_time=fixed_now)
    assert any("Upload missing required documents:" in act for act in actions_in_progress)
    assert any("resume.pdf" in act for act in actions_in_progress)

    # 3. Application with deadline approaching within 48 hours
    app_urgent = workflow_manager.save_opportunity(student_id, "opp_urgent_02")
    workflow_manager.update_application_status(app_urgent.id, ApplicationStatus.IN_PROGRESS)
    actions_urgent = workflow_manager.get_recommended_actions(app_urgent, current_time=fixed_now)
    assert "Urgent: Submit application within 48 hours" in actions_urgent

    # 4. Application fully completed and SUBMITTED
    workflow_manager.upload_documents(app.id, ["resume.pdf", "transcript.pdf"])
    workflow_manager.update_application_status(app.id, ApplicationStatus.SUBMITTED)
    actions_submitted = workflow_manager.get_recommended_actions(app, current_time=fixed_now)
    assert "Application submitted. Awaiting review result." in actions_submitted
    # Once submitted, no missing document or urgency alerts
    assert not any("Upload missing" in act for act in actions_submitted)
    assert not any("Urgent:" in act for act in actions_submitted)


def load_tests(loader, standard_tests, pattern):
    """Enable discovery when running python -m unittest discover."""
    import unittest
    from tests.conftest import (
        get_fixed_now,
        get_sample_student,
        get_workflow_manager,
    )

    class UnittestOpportunityWorkflow(unittest.TestCase):
        def test_viewing_opportunities(self):
            test_viewing_opportunities(get_workflow_manager(), get_fixed_now())

        def test_saving_opportunity(self):
            test_saving_opportunity(get_workflow_manager(), get_sample_student())

        def test_application_status_updates(self):
            test_application_status_updates(get_workflow_manager(), get_sample_student())

        def test_deadline_tracking(self):
            test_deadline_tracking(get_workflow_manager(), get_sample_student(), get_fixed_now())

        def test_risk_detection(self):
            test_risk_detection(get_workflow_manager(), get_sample_student(), get_fixed_now())

        def test_recommended_actions(self):
            test_recommended_actions(get_workflow_manager(), get_sample_student(), get_fixed_now())

    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(UnittestOpportunityWorkflow))
    return suite
