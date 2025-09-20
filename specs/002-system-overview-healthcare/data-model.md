# Data Model

## Patient
- **Fields**:
  - id: UUID (primary key)
  - ssn: str (unique, regex validation)
  - mobile_number: str (regex validation)
  - phone_number: Optional[str]
  - medical_number: Optional[str] (unique)
  - full_name: str
  - date_of_birth: Optional[date]
  - gender: Optional[enum: male, female, other]
  - created_at: datetime
  - updated_at: datetime
- **Relationships**:
  - visits: One-to-many with PatientVisit
- **Validation Rules**:
  - SSN: 14 digits
  - Mobile: Egyptian format (01[0-2] followed by 8 digits)
  - Full name: 2-255 characters

## User
- **Fields**:
  - id: UUID (primary key)
  - username: str (unique)
  - email: str (unique)
  - hashed_password: str
  - role: enum (nurse, physician, admin)
  - is_active: bool
  - created_at: datetime
  - updated_at: datetime
- **Relationships**:
  - None direct (audit log references)
- **Validation Rules**:
  - Username: alphanumeric, 3-50 chars
  - Email: valid email format
  - Role: required

## PatientVisit
- **Fields**:
  - id: UUID (primary key)
  - patient_id: UUID (foreign key to Patient)
  - visit_date: datetime
  - status: enum (open, completed, cancelled)
  - created_by: UUID (foreign key to User)
  - created_at: datetime
  - updated_at: datetime
- **Relationships**:
  - patient: Many-to-one with Patient
  - nursing_assessment: One-to-one with NursingAssessment
  - radiology_assessment: One-to-one with RadiologyAssessment
  - documents: One-to-many with Document
- **Validation Rules**:
  - Visit date: not in future
  - Status: required

## NursingAssessment
- **Fields**:
  - id: UUID (primary key)
  - visit_id: UUID (foreign key to PatientVisit)
  - temperature_celsius: Optional[float]
  - pulse_bpm: Optional[int]
  - blood_pressure_systolic: Optional[int]
  - blood_pressure_diastolic: Optional[int]
  - respiratory_rate_per_min: Optional[int]
  - oxygen_saturation_percent: Optional[float]
  - pain_assessment: Optional[dict] (JSON)
  - fall_risk_assessment: Optional[dict] (JSON)
  - notes: Optional[str]
  - assessed_by: UUID (foreign key to User)
  - assessed_at: datetime
- **Relationships**:
  - visit: One-to-one with PatientVisit
- **Validation Rules**:
  - Temperature: 30.0-45.0°C
  - Pulse: 30-200 bpm
  - BP systolic: 70-250 mmHg
  - BP diastolic: 40-150 mmHg
  - Respiratory rate: 8-60/min
  - O2 saturation: 70.0-100.0%

## RadiologyAssessment
- **Fields**:
  - id: UUID (primary key)
  - visit_id: UUID (foreign key to PatientVisit)
  - findings: str
  - diagnosis: Optional[str]
  - recommendations: Optional[str]
  - assessed_by: UUID (foreign key to User)
  - assessed_at: datetime
- **Relationships**:
  - visit: One-to-one with PatientVisit
- **Validation Rules**:
  - Findings: required, 10-1000 chars
  - Diagnosis: optional, 10-500 chars

## Document
- **Fields**:
  - id: UUID (primary key)
  - visit_id: UUID (foreign key to PatientVisit)
  - filename: str
  - file_path: str
  - mime_type: str
  - file_size: int
  - uploaded_by: UUID (foreign key to User)
  - uploaded_at: datetime
- **Relationships**:
  - visit: Many-to-one with PatientVisit
- **Validation Rules**:
  - Filename: 1-255 chars
  - File size: max 10MB
  - MIME type: allowed types only

## AuditLog
- **Fields**:
  - id: UUID (primary key)
  - user_id: UUID (foreign key to User)
  - action: str
  - resource_type: str
  - resource_id: UUID
  - details: dict (JSON)
  - ip_address: str
  - user_agent: str
  - timestamp: datetime
- **Relationships**:
  - user: Many-to-one with User
- **Validation Rules**:
  - Action: required
  - Resource type: required
  - Timestamp: auto-generated

## State Transitions

### PatientVisit Status
- open → completed (when assessments done)
- open → cancelled (by authorized user)
- completed → open (for corrections, admin only)

### Assessment Workflow
- Visit created → Nursing assessment can be started
- Nursing assessment completed → Radiology assessment can be started
- Radiology assessment completed → Visit can be completed
- Documents can be uploaded at any time during open visit