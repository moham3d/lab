<!-- Sync Impact Report
Version change: 0.0.0 → 1.0.0
List of modified principles: None (new)
Added sections: Principles 1-5, Governance
Removed sections: None
Templates requiring updates: None (no templates exist)
Follow-up TODOs: RATIFICATION_DATE needs to be set
-->

# Project Constitution

**Project Name:** Patient Visit Management System

**Constitution Version:** 1.0.0

**Ratification Date:** TODO(RATIFICATION_DATE): Original adoption date not specified

**Last Amended Date:** 2025-09-21

## Principles

### Principle 1: Users & Authentication
The system MUST support user management with defined roles (nurse, physician, admin). Authentication MUST use JWT tokens with endpoints for login and register. Routers MUST include /auth for login and refresh, and /users for CRUD operations and role management.

Rationale: Ensures secure, role-based access control essential for HIPAA compliance and protecting patient data.

### Principle 2: Patients
Patients MUST have a unique ID, a 14-digit SSN, and demographic information. A router /patients MUST be provided for patient management.

Rationale: Provides a foundation for linking all medical data to individual patients securely and uniquely.

### Principle 3: Visits
Visits MUST be linked to a patient, created by a user, and include a timestamp. A router /visits MUST be provided.

Rationale: Tracks patient interactions over time, enabling chronological medical history.

### Principle 4: Forms / Evaluations
The system MUST support multiple form types: Check-Eval for nursing screening, vitals, and risk assessments; General Sheet for radiology info, chronic diseases, surgeries, and history; CT Form for detailed diagnostic info, chemo, radiotherapy, and diagnosis. Each form MUST be linked to a visit. A router /forms MUST provide separate endpoints for each form type.

Rationale: Captures comprehensive medical evaluations and assessments critical for patient care and compliance.

### Principle 5: Reports
Reports MUST be linked to a patient and visit, containing summary and doctor notes. A router /reports MUST be provided.

Rationale: Enables documentation of visit outcomes and facilitates communication among healthcare providers.

## Governance

**Amendment Procedure:** Amendments to this constitution require approval from the admin role or consensus among all user roles. Changes MUST be documented with version updates.

**Versioning Policy:** Follows semantic versioning: MAJOR for backward-incompatible changes (e.g., removing principles), MINOR for additions (e.g., new principles), PATCH for clarifications.

**Compliance Review Expectations:** Annual reviews MUST be conducted to ensure alignment with HIPAA and other regulations. All changes MUST maintain compliance.