# Patient Visit Management System API - Tasks

## Overview
This document outlines the actionable, dependency-ordered tasks for implementing the Patient Visit Management System API. Tasks are broken down into manageable development units based on available design artifacts (constitution.md, database.sql).

## Task Dependencies
- Setup tasks must complete before all others
- Core infrastructure (DB, Models, Schemas) before routes
- Routes can be implemented in parallel where files don't conflict
- Testing after implementation
- Polish tasks last

## Parallel Execution Guidance
Tasks marked [P] can run in parallel. Group them by running multiple in sequence within a session.

Example:
```
# Run core setup in parallel
T001, T002, T003

# Then models and schemas in parallel
T004, T005

# Routes in parallel
T007, T008, T009, T010, T011, T012
```

## Tasks

### T001: Project Setup [Setup]
**File:** /home/mohamed/lab/requirements.txt
**Description:** Install FastAPI, SQLAlchemy, Pydantic, and other dependencies. Create project structure with directories (app/, core/, db/, models/, schemas/, api/routes/).
**Dependencies:** None
**Parallel:** No

### T002: Core Module Implementation [Core]
**File:** /home/mohamed/lab/app/core/config.py, /home/mohamed/lab/app/core/security.py
**Description:** Implement settings management with Pydantic BaseSettings. Add JWT token creation/verification, password hashing functions.
**Dependencies:** T001
**Parallel:** [P] with T003

### T003: Database Module Implementation [Core]
**File:** /home/mohamed/lab/app/db/init_db.py, /home/mohamed/lab/app/db/schema.sql
**Description:** Set up async PostgreSQL engine and session. Import full schema.sql with all tables, indexes, and initial data. Execute schema on startup.
**Dependencies:** T001
**Parallel:** [P] with T002

### T004: Models Module Implementation [Core]
**File:** /home/mohamed/lab/app/models.py
**Description:** Create SQLAlchemy ORM models for all entities: User, Patient, PatientVisit, NursingAssessment, RadiologyAssessment, Report, etc. Include all fields from database.sql.
**Dependencies:** T003
**Parallel:** [P] with T005

### T005: Schemas Module Implementation [Core]
**File:** /home/mohamed/lab/app/schemas/*.py
**Description:** Define Pydantic schemas for all entities with validation, request/response models, and Swagger examples. Cover all fields from models.
**Dependencies:** T004
**Parallel:** [P] with T004

### T006: API Dependencies Implementation [Core]
**File:** /home/mohamed/lab/app/api/deps.py
**Description:** Implement get_current_user dependency with JWT verification and database user lookup.
**Dependencies:** T002, T004
**Parallel:** No

### T007: Auth Routes Implementation [Routes]
**File:** /home/mohamed/lab/app/api/routes/auth.py
**Description:** Implement /register and /login endpoints with user creation, password validation, and JWT token response.
**Dependencies:** T006
**Parallel:** [P] with other routes

### T008: Users Routes Implementation [Routes]
**File:** /home/mohamed/lab/app/api/routes/users.py
**Description:** Implement CRUD endpoints for users with role-based access control (admin checks).
**Dependencies:** T006
**Parallel:** [P] with other routes

### T009: Patients Routes Implementation [Routes]
**File:** /home/mohamed/lab/app/api/routes/patients.py
**Description:** Implement CRUD endpoints for patients using SSN as primary key.
**Dependencies:** T006
**Parallel:** [P] with other routes

### T010: Visits Routes Implementation [Routes]
**File:** /home/mohamed/lab/app/api/routes/visits.py
**Description:** Implement CRUD endpoints for patient visits linked to patients.
**Dependencies:** T006, T009
**Parallel:** [P] with other routes

### T011: Forms Routes Implementation [Routes]
**File:** /home/mohamed/lab/app/api/routes/forms.py
**Description:** Implement endpoints for check-eval and general-sheet forms with form_submissions and assessments.
**Dependencies:** T006, T010
**Parallel:** [P] with other routes

### T012: Reports Routes Implementation [Routes]
**File:** /home/mohamed/lab/app/api/routes/reports.py
**Description:** Implement CRUD endpoints for reports linked to visits.
**Dependencies:** T006, T010
**Parallel:** [P] with other routes

### T013: Main App Integration [Integration]
**File:** /home/mohamed/lab/app/main.py
**Description:** Integrate all routers, add CORS, startup schema execution, and health check endpoint.
**Dependencies:** All routes (T007-T012)
**Parallel:** No

### T014: Integration Testing [Test]
**File:** /home/mohamed/lab/test_*.py
**Description:** Create comprehensive tests: register/login, create patient/visit/forms/reports, verify JWT auth and data flow.
**Dependencies:** T013
**Parallel:** [P] with T015

### T015: Error Handling and Logging [Polish]
**File:** /home/mohamed/lab/app/main.py, /home/mohamed/lab/app/core/*.py
**Description:** Add structured logging, global error handlers, and health checks.
**Dependencies:** T013
**Parallel:** [P] with T014

### T016: Docker Deployment [Polish]
**File:** /home/mohamed/lab/Dockerfile, /home/mohamed/lab/docker-compose.yml
**Description:** Create Dockerfile for containerization and docker-compose.yml for local development with PostgreSQL.
**Dependencies:** T013
**Parallel:** No