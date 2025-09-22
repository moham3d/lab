<!-- Sync Impact Report
Version change: 1.2.0 → 1.3.0
List of modified principles: Principle 1 updated for admin role access control
Added sections: Principle 13 (Admin Dashboard and Access Control), Principle 14 (Data Import and Export)
Removed sections: None
Templates requiring updates: None (no templates exist)
Follow-up TODOs: None
-->

# Project Constitution

**Project Name:** Patient Visit Management System

**Constitution Version:** 1.3.0

**Ratification Date:** TODO(RATIFICATION_DATE): Original adoption date not specified

**Last Amended Date:** 2025-09-23

## Principles

### Principle 1: Users & Authentication
The system MUST support user management with defined roles (nurse, physician, admin). Authentication MUST use JWT tokens with endpoints for login and register. Routers MUST include /auth for login and refresh, and /users for CRUD operations and role management. Admin role MUST have exclusive access to reports, user management, and administrative functions.

Rationale: Ensures secure, role-based access control essential for HIPAA compliance and protecting patient data, with administrative oversight capabilities.

### Principle 2: Patients
Patients MUST have a unique ID, a 14-digit SSN, and demographic information. A router /patients MUST be provided for patient management.

Rationale: Provides a foundation for linking all medical data to individual patients securely and uniquely.

### Principle 3: Visits
Visits MUST be linked to a patient, created by a user, and include a timestamp. A router /visits MUST be provided.

Rationale: Tracks patient interactions over time, enabling chronological medical history.

### Principle 4: Forms / Evaluations
The system MUST support multiple form types: Check-Eval for nursing screening, vitals, and risk assessments; General Sheet for radiology info, chronic diseases, surgeries, and history; CT Form for detailed diagnostic info, chemo, radiotherapy, and diagnosis. Each form MUST be linked to a visit and support handwritten signatures for tablet/stylus input. A router /forms MUST provide separate endpoints for each form type.

Rationale: Captures comprehensive medical evaluations and assessments critical for patient care and compliance, with secure signature capture.

### Principle 5: Reports
Reports MUST be linked to a patient and visit, containing summary and doctor notes. A router /reports MUST be provided.

Rationale: Enables documentation of visit outcomes and facilitates communication among healthcare providers.

### Principle 6: Frontend Technology Stack
The frontend MUST use HTMX for dynamic content loading, Alpine.js for client-side interactivity, and Tailwind CSS for styling. No heavy frameworks like React or Vue MUST be used. The application MUST be a single-page application with partial updates.

Rationale: Ensures lightweight, fast, and maintainable frontend that integrates seamlessly with the FastAPI backend.

### Principle 7: User Interface Design
The UI MUST be clean, medical-grade with accessibility compliance, role-based navigation, and responsive design for tablets and desktop. Arabic/English language support MUST be included. Toast notifications and loading indicators MUST be provided.

Rationale: Provides professional, accessible interface suitable for healthcare environments and multilingual users.

### Principle 8: Form Management
Forms MUST support multi-section tabbed interfaces, auto-save with debounced HTMX requests, real-time validation, progress indicators, and print-ready layouts. Conditional field display and rich text editors MUST be supported where appropriate.

Rationale: Enables efficient data entry with user-friendly interfaces that prevent data loss and ensure completeness.

### Principle 9: Data Management Interfaces
Patient and visit management MUST include real-time search capabilities, advanced filtering, bulk operations, and CRUD interfaces. Data grids with sorting, pagination, and export functionality MUST be provided.

Rationale: Allows efficient management of large datasets with professional administrative tools.

### Principle 10: Reporting and Analytics
Role-based dashboards with statistics, activity feeds, and quick actions MUST be provided. Reports MUST support date ranges, export to PDF/Excel, and real-time data updates.

Rationale: Enables data-driven decision making and operational oversight.

### Principle 12: Visit Workflow
The system MUST follow a structured patient visit process: reception initiates new visits by searching patients by SSN; if patient data exists, it loads into nursing assessment forms (Check-Eval); the visit is saved with nursing data; then the patient proceeds to physician evaluation using General Sheet forms. All forms MUST support handwritten signatures captured via tablet and stylus.

Rationale: Ensures standardized, compliant patient visit management with proper sequential documentation and signature authentication.

### Principle 13: Admin Dashboard and Access Control
The system MUST provide an admin dashboard accessible only to users with admin role. Reports and new user creation forms MUST be restricted to admin access only. Admin dashboard MUST include system overview, user management, audit logs, and administrative controls.

Rationale: Provides centralized administrative oversight and ensures sensitive functions are properly secured and monitored.

### Principle 14: Data Import and Export
The system MUST support data import and export functionality for admins. Import MUST support massive CSV file uploads for bulk data operations (patients, users, etc.). Export MUST provide data in multiple formats (CSV, Excel, PDF) with proper filtering and date range selection.

Rationale: Enables efficient data management, migration, and reporting capabilities essential for healthcare administration and compliance.

## Governance

**Amendment Procedure:** Amendments to this constitution require approval from the admin role or consensus among all user roles. Changes MUST be documented with version updates.

**Versioning Policy:** Follows semantic versioning: MAJOR for backward-incompatible changes (e.g., removing principles), MINOR for additions (e.g., new principles), PATCH for clarifications.

**Compliance Review Expectations:** Annual reviews MUST be conducted to ensure alignment with HIPAA and other regulations. All changes MUST maintain compliance.