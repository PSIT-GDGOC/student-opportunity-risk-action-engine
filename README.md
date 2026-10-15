# Student Opportunity Risk & Action Engine

A Python workflow engine that helps students discover, track, and manage internships, hackathons, scholarships, fellowships, competitions, and other career opportunities. The system goes beyond simply listing opportunities by analysing deadlines, application progress, and student activity to identify opportunities that are at risk of being missed and recommend the appropriate next action.

> Built for [PSIT-GDGOC/student-opportunity-risk-action-engine](https://github.com/PSIT-GDGOC/student-opportunity-risk-action-engine)

---

## Project Overview

Traditional opportunity platforms mainly focus on **finding opportunities and showing deadlines**. This project focuses on the **Risk & Action Layer**, answering three important questions:

1. **Which opportunity am I likely to miss?**
2. **Why am I at risk of missing it?**
3. **What should I do next?**

The core workflow engine implements the complete student journey from opportunity discovery through application submission, with automated risk detection and recommended actions at every step.

---

## Repository Structure

```text
student-opportunity-risk-action-engine/
│
├── src/
│   ├── __init__.py              # Package exports
│   ├── models.py                # Domain models (Opportunity, StudentApplication, enums)
│   └── workflow.py              # OpportunityWorkflowManager (core business logic)
│
├── tests/
│   ├── __init__.py              # Test package
│   ├── conftest.py              # Shared fixtures and mock data
│   ├── test_opportunity_workflow.py   # Unit tests for each workflow task
│   └── test_complete_workflow.py      # End-to-end integration test
│
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
└── README.md                    # This file
```

---

## Features Covered

The following **7 workflow capabilities** are implemented and fully tested:

1. **Viewing Opportunities** — List all opportunities and filter by keyword or active deadline without mutating state.
2. **Saving an Opportunity** — Bookmark/save an opportunity to a student's tracker with explicit duplicate prevention.
3. **Application Status Updates** — Enforce valid state transitions (`DISCOVERED` → `SAVED` → `IN_PROGRESS` → `SUBMITTED` → `ACCEPTED`/`REJECTED`) and raise errors on invalid transitions.
4. **Deadline Tracking** — Calculate time/days remaining until deadlines, flag expired opportunities, and sort saved opportunities by urgency.
5. **Risk Detection** — Flag high-risk states including deadlines approaching within 48 hours, passed deadlines, and missing required documents while an application is in progress.
6. **Recommended Actions** — Dynamically generate actionable next steps based on current status and active risk flags (e.g., "Upload missing required documents: resume.pdf", "Urgent: Submit application within 48 hours").
7. **End-to-End Workflow** — Complete student journey from opportunity discovery → save → deadline check → risk detection → resolve issues → status updates → final submission with zero risk flags.

---

## Core Workflow

```text
Discover Opportunity
        ↓
Save Opportunity
        ↓
Check Deadline & Eligibility
        ↓
Start Application (IN_PROGRESS)
        ↓
Risk Analysis (deadline + documents)
        ↓
Resolve Flagged Issues
        ↓
Submit Application
        ↓
Result (ACCEPTED / REJECTED)
```

---

## Setup & Installation

### Prerequisites

- Python 3.9+

### Install Dependencies

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install required packages
pip install -r requirements.txt
```

---

## Running Tests

### Using pytest (recommended)

```bash
PYTHONPATH=. pytest -v
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH = "."; python -m pytest -v
```

### Using unittest

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH = "."; python -m unittest discover -s tests -v
```

### Expected Output

All 7 tests should pass:

```text
tests/test_complete_workflow.py::test_end_to_end_student_workflow PASSED
tests/test_opportunity_workflow.py::test_viewing_opportunities PASSED
tests/test_opportunity_workflow.py::test_saving_opportunity PASSED
tests/test_opportunity_workflow.py::test_application_status_updates PASSED
tests/test_opportunity_workflow.py::test_deadline_tracking PASSED
tests/test_opportunity_workflow.py::test_risk_detection PASSED
tests/test_opportunity_workflow.py::test_recommended_actions PASSED

7 passed
```

---

## Risk Detection Example

```text
Opportunity: Global AI Hackathon 2026

Deadline: 20 Hours Remaining
Application Status: IN_PROGRESS
Required Documents: resume.pdf, project_proposal.pdf
Submitted Documents: (none)

Risk Level: HIGH

Risk Flags:
  → DEADLINE_APPROACHING
  → MISSING_DOCUMENTS

Recommended Actions:
  → Upload missing required documents: resume.pdf, project_proposal.pdf
  → Urgent: Submit application within 48 hours
```

---

## Tech Stack

| Component       | Technology       |
|-----------------|------------------|
| Language        | Python 3.9+      |
| Testing         | pytest / unittest|
| Architecture    | Pure Python (no external dependencies beyond pytest) |

---

## License

This project is licensed under the MIT License.
