# Student Opportunity Risk & Action Engine

A full-stack web application designed to help students discover, track, and manage internships, hackathons, scholarships, fellowships, competitions, and other career opportunities.

The system goes beyond simply listing opportunities by analysing deadlines, application progress, and student activity to identify opportunities that are at risk of being missed and recommend the appropriate next action.

---

## Features

### Authentication & User Management
- User registration and login
- JWT-based authentication
- Role-based access control
- Student, Organization, and Admin roles
- Student profile management
- Skills, interests, education, and preferred opportunity types
- Password management

### Opportunity Management
- Browse internships, hackathons, scholarships, fellowships, and competitions
- View opportunity details
- Eligibility and required skills
- Application deadline tracking
- Organization and application links
- Save/bookmark opportunities
- Search and filter opportunities
- Organization/Admin opportunity management

### Opportunity Tracking & Application Management
- Track opportunity progress through different stages:
  `Discovered → Saved → Eligibility Checked → Preparing → Application Started → Submitted → Result`
- Update application status
- Track required documents
- Manage preparation tasks
- Team formation tracking
- Add notes and deadlines
- Upcoming and ongoing opportunity dashboard

### Risk Detection & Action Engine
- Analyse deadlines, application status, and student activity
- Detect opportunities that are at risk of being missed
- Identify reasons behind the risk
- Risk levels:
  - Low
  - Medium
  - High
- Recommended actions such as:
  - Start Application
  - Form a Team
  - Complete Documents
  - Start Preparation

### Notifications & Reminders
- Deadline reminders
- Risk-based notifications
- Scheduled reminders using Spring Scheduler
- In-app notifications
- Email notification support
- Notification preferences

### Student Insights & Analytics
- Track discovered, saved, started, and submitted opportunities
- Analyse application history
- Detect missed-opportunity patterns
- Identify late application behaviour
- Personalized student insights
- Opportunity readiness overview

### Admin Dashboard & Analytics
- Manage users and organizations
- Manage opportunities
- Approve or remove opportunities
- Detect duplicate or inappropriate opportunities
- Monitor application and engagement statistics
- View popular opportunity categories
- Platform-level analytics

---

## Main USP

Traditional opportunity platforms mainly focus on **finding opportunities and showing deadlines**.

This project focuses on the **Risk & Action Layer**.

It answers three important questions:

1. **Which opportunity am I likely to miss?**
2. **Why am I at risk of missing it?**
3. **What should I do next?**

This makes the system proactive rather than just an opportunity listing platform.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React.js |
| Backend | Java, Spring Boot |
| Database | MySQL |
| ORM | Spring Data JPA / Hibernate |
| Security | Spring Security, JWT |
| API | REST APIs |
| Scheduling | Spring Scheduler |
| API Testing | Postman |
| Version Control | Git & GitHub |

---

## System Architecture

```text
User
  ↓
React.js Frontend
  ↓
Spring Boot REST APIs
  ↓
Business Logic
  ↓
Risk & Action Engine
  ↓
MySQL Database
```

---

## Core Workflow

```text
Discover Opportunity
        ↓
Save Opportunity
        ↓
Check Eligibility
        ↓
Start Preparation
        ↓
Application Started
        ↓
Risk Analysis
        ↓
Risk Detected
        ↓
Reason Identified
        ↓
Action Suggested
        ↓
Application Submitted
        ↓
Result
```

---

## Risk Detection Example

```text
Opportunity: Hackathon

Deadline: 2 Days Remaining

Application Status: Not Started

Team: Not Formed

Documents: Incomplete

Risk Level: HIGH

Recommended Actions:
→ Start Application
→ Form a Team
→ Complete Documents
```

---

## Planned API Endpoints

### Authentication

```text
POST   /api/auth/register
POST   /api/auth/login
```

### Opportunities

```text
GET    /api/opportunities
GET    /api/opportunities/{id}
POST   /api/opportunities
PUT    /api/opportunities/{id}
DELETE /api/opportunities/{id}
```

### Applications

```text
GET    /api/applications
POST   /api/applications
PUT    /api/applications/{id}
DELETE /api/applications/{id}
```

### Risk & Actions

```text
GET    /api/risks
GET    /api/risks/{opportunityId}
GET    /api/actions/{opportunityId}
```

### Notifications

```text
GET    /api/notifications
PUT    /api/notifications/{id}/read
```

> These APIs are planned and will be implemented during development.

---

## Database Design

Main entities planned for the system:

```text
User
 ├── Student Profile
 ├── Applications
 └── Notifications

Opportunity
 ├── Eligibility
 ├── Skills
 └── Deadline

Application
 ├── Status
 ├── Documents
 ├── Tasks
 └── Notes

Risk Analysis
 ├── Risk Level
 ├── Risk Reason
 └── Recommended Action
```

---

## Project Structure

```text
student-opportunity-risk-action-engine/
│
├── frontend/
│   └── React.js
│
├── backend/
│   └── Spring Boot
│
├── database/
│   └── Database Scripts
│
├── docs/
│   └── Documentation
│
└── README.md
```

---

## Security

- Spring Security
- JWT Authentication
- Role-based Authorization
- Password Hashing
- Secure REST APIs
- Input Validation
- Protected Admin Operations

---

## Future Improvements

- AI-based opportunity recommendations
- Personalized opportunity matching
- Resume-based opportunity matching
- Smart deadline prediction
- AI-generated preparation plans
- Automated opportunity collection
- Advanced behavioural analytics
- Email and push notifications
- Calendar integration
- Mobile application

---

## Project Status

🚧 **In Development**

The project is currently being developed as a full-stack web application using React.js, Spring Boot, and MySQL.

---

## Team

**PSIT-GDGOC**

---

## License

This project is licensed under the MIT License.
