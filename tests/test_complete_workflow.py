"""End-to-end integration test for the student opportunity workflow."""

from datetime import datetime, timedelta

from src.models import ApplicationStatus, RiskFlag, RiskLevel
from src.workflow import OpportunityWorkflowManager


def test_end_to_end_student_workflow(
    workflow_manager: OpportunityWorkflowManager,
    sample_student: dict,
    fixed_now: datetime,
) -> None:
    """Test the complete student workflow from opportunity discovery to final application submission.

    Workflow stages:
    1. Discover and view available opportunities.
    2. Save a target opportunity to the student tracker.
    3. Check deadline tracking metrics for the saved opportunity.
    4. Simulate an approaching deadline or missing document to trigger risk detection.
    5. Fetch recommended actions and resolve the flagged issue (attach required documents).
    6. Update the application status from SAVED to IN_PROGRESS and finally to SUBMITTED.
    7. Assert that the final state is SUBMITTED with zero active risk flags and no unhandled errors.
    """
    student_id = sample_student["student_id"]

    # -------------------------------------------------------------------------
    # Step 1: Discover and view available opportunities
    # -------------------------------------------------------------------------
    available_opportunities = workflow_manager.view_opportunities(
        active_only=True,
        current_time=fixed_now,
    )
    assert len(available_opportunities) >= 1
    # Pick the upcoming internship as our target opportunity
    target_opp = next(opp for opp in available_opportunities if opp.id == "opp_upcoming_01")
    assert target_opp is not None
    assert "TechCorp" in target_opp.company
    assert len(target_opp.required_documents) > 0

    # -------------------------------------------------------------------------
    # Step 2: Save target opportunity to the student tracker
    # -------------------------------------------------------------------------
    app = workflow_manager.save_opportunity(
        student_id=student_id,
        opportunity_id=target_opp.id,
    )
    assert app.id is not None
    assert app.status == ApplicationStatus.SAVED
    assert app.opportunity_id == target_opp.id
    assert app.student_id == student_id

    # -------------------------------------------------------------------------
    # Step 3: Check deadline tracking metrics for the saved opportunity
    # -------------------------------------------------------------------------
    initial_metrics = workflow_manager.get_deadline_metrics(
        target_opp.id,
        current_time=fixed_now,
    )
    assert initial_metrics.is_expired is False
    assert initial_metrics.days_remaining > 0
    assert initial_metrics.hours_remaining > 48.0
    assert initial_metrics.is_urgent is False

    # -------------------------------------------------------------------------
    # Step 4: Simulate an approaching deadline & missing documents to trigger risk detection
    # -------------------------------------------------------------------------
    # Transition application to IN_PROGRESS
    app = workflow_manager.update_application_status(app.id, ApplicationStatus.IN_PROGRESS)
    assert app.status == ApplicationStatus.IN_PROGRESS

    # Fast forward time to 36 hours before deadline (triggering approaching deadline risk)
    approaching_time = target_opp.deadline - timedelta(hours=36)
    urgent_metrics = workflow_manager.get_deadline_metrics(
        target_opp.id,
        current_time=approaching_time,
    )
    assert urgent_metrics.is_urgent is True
    assert urgent_metrics.hours_remaining <= 48.0

    # Detect risks with missing documents and approaching deadline
    active_risk_assessment = workflow_manager.detect_risks(
        app.id,
        current_time=approaching_time,
    )
    assert active_risk_assessment.has_risk is True
    assert RiskFlag.MISSING_DOCUMENTS.value in active_risk_assessment.flags
    assert RiskFlag.DEADLINE_APPROACHING.value in active_risk_assessment.flags
    assert active_risk_assessment.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    # -------------------------------------------------------------------------
    # Step 5: Fetch recommended actions and resolve the flagged issues
    # -------------------------------------------------------------------------
    recommended_actions = workflow_manager.get_recommended_actions(
        app.id,
        current_time=approaching_time,
    )
    assert any("Upload missing required documents:" in action for action in recommended_actions)
    assert any("Urgent: Submit application within 48 hours" in action for action in recommended_actions)

    # Resolve missing documents risk by attaching all required documents
    for doc in target_opp.required_documents:
        workflow_manager.upload_document(app.id, doc)

    # Verify documents are now recorded
    refreshed_app = workflow_manager.get_application(app.id)
    assert set(refreshed_app.submitted_documents) == set(target_opp.required_documents)

    # Missing documents risk is now resolved
    post_upload_assessment = workflow_manager.detect_risks(
        app.id,
        current_time=approaching_time,
    )
    assert RiskFlag.MISSING_DOCUMENTS.value not in post_upload_assessment.flags

    # -------------------------------------------------------------------------
    # Step 6: Update application status to SUBMITTED
    # -------------------------------------------------------------------------
    submitted_app = workflow_manager.update_application_status(
        app.id,
        ApplicationStatus.SUBMITTED,
    )
    assert submitted_app.status == ApplicationStatus.SUBMITTED

    # -------------------------------------------------------------------------
    # Step 7: Assert final state is SUBMITTED with zero active risk flags
    # -------------------------------------------------------------------------
    final_assessment = workflow_manager.detect_risks(
        app.id,
        current_time=approaching_time,
    )
    assert final_assessment.flags == []
    assert final_assessment.has_risk is False
    assert final_assessment.risk_level == RiskLevel.NONE
    assert "Application submitted. Awaiting review result." in final_assessment.recommended_actions

    # Verify no unhandled errors when fetching recommended actions
    final_actions = workflow_manager.get_recommended_actions(
        app.id,
        current_time=approaching_time,
    )
    assert final_actions == ["Application submitted. Awaiting review result."]


def load_tests(loader, standard_tests, pattern):
    """Enable discovery when running python -m unittest discover."""
    import unittest
    from tests.conftest import (
        get_fixed_now,
        get_sample_student,
        get_workflow_manager,
    )

    class UnittestCompleteWorkflow(unittest.TestCase):
        def test_end_to_end_student_workflow(self):
            test_end_to_end_student_workflow(
                get_workflow_manager(),
                get_sample_student(),
                get_fixed_now(),
            )

    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(UnittestCompleteWorkflow))
    return suite
