# Patient Visit Management System - Backend API Documentation

## Overview

This document provides comprehensive API documentation for the Patient Visit Management System backend. The API is built with FastAPI and provides endpoints for user management, patient records, visit tracking, form submissions, and reporting.

**Base URL:** `http://localhost:8000/api/v1`

**Authentication:** JWT Bearer tokens required for all protected endpoints

---

## Authentication

### Login
**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `422 Unprocessable Entity`: Invalid request format

### Register User (Admin Only)
**Endpoint:** `POST /auth/register`

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "full_name": "string",
  "role": "nurse|physician|admin",
  "password": "string"
}
```

**Response:** Same as login

**Requirements:**
- Admin role required
- Unique username and email

### Get Current User Info
**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": true
}
```

---

## User Management

### Get Users (Admin Only)
**Endpoint:** `GET /users/`

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
[
  {
    "user_id": "uuid",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "role": "string",
    "is_active": true,
    "created_at": "datetime",
    "last_login": "datetime"
  }
]
```

### Create User (Admin Only)
**Endpoint:** `POST /users/`

**Request Body:** Same as register

### Get User by ID
**Endpoint:** `GET /users/{user_id}`

**Permissions:** Admin or own account

### Update User
**Endpoint:** `PUT /users/{user_id}`

**Request Body:**
```json
{
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": boolean
}
```

---

## Patient Management

### Get Patients
**Endpoint:** `GET /patients/`

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
[
  {
    "ssn": "string (14 digits)",
    "mobile_number": "string",
    "full_name": "string",
    "date_of_birth": "date",
    "gender": "male|female|other",
    "address": "string",
    "created_at": "datetime",
    "updated_at": "datetime",
    "is_active": true
  }
]
```

### Create Patient
**Endpoint:** `POST /patients/`

**Request Body:**
```json
{
  "ssn": "string (14 digits, Egyptian format)",
  "mobile_number": "string (Egyptian format: 01XXXXXXXXX)",
  "full_name": "string",
  "date_of_birth": "YYYY-MM-DD",
  "gender": "male|female|other",
  "address": "string"
}
```

**Validation Rules:**
- SSN: 14 digits, unique
- Mobile: Egyptian format starting with 01
- Full name: Required

### Get Patient by SSN
**Endpoint:** `GET /patients/{ssn}`

### Update Patient
**Endpoint:** `PUT /patients/{ssn}`

**Request Body:** Same as create (all fields optional)

---

## Visit Management

### Get Visits
**Endpoint:** `GET /visits/`

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
[
  {
    "visit_id": "uuid",
    "patient_ssn": "string",
    "visit_date": "datetime",
    "visit_status": "open|in_progress|completed|cancelled",
    "notes": "string",
    "created_by": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### Create Visit
**Endpoint:** `POST /visits/`

**Request Body:**
```json
{
  "patient_ssn": "string (existing patient)",
  "notes": "string"
}
```

**Requirements:**
- Patient must exist
- Auto-assigns current user as creator

### Get Visit by ID
**Endpoint:** `GET /visits/{visit_id}`

### Update Visit
**Endpoint:** `PUT /visits/{visit_id}`

**Request Body:**
```json
{
  "notes": "string"
}
```

---

## Form Management

### Check-Eval Form (Nursing Assessment)

#### Create Check-Eval
**Endpoint:** `POST /forms/check-eval`

**Request Body:**
```json
{
  "visit_id": "uuid",
  "temperature_celsius": 36.5,
  "pulse_bpm": 72,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "respiratory_rate_per_min": 16,
  "oxygen_saturation_percent": 98.0,
  "weight_kg": 70.0,
  "height_cm": 170.0,
  "chief_complaint": "string",
  "general_condition": "string",
  "consciousness_level": "string",
  "skin_condition": "string",
  "mobility_status": "string",
  "is_smoker": false,
  "has_allergies": false,
  "diet_type": "regular",
  "appetite": "good",
  "feeding_status": "independent",
  "hygiene_status": "independent",
  "toileting_status": "independent",
  "ambulation_status": "independent",
  "pain_intensity": 0,
  "fall_history_3months": false,
  "secondary_diagnosis": false,
  "iv_therapy": false,
  "needs_medication_education": false,
  "daily_activities": "independent",
  "has_signs_of_abuse": false
}
```

**Vital Signs Validation:**
- Temperature: 30.0-45.0°C
- Pulse: 30-200 bpm
- BP Systolic: 70-250 mmHg
- BP Diastolic: 40-150 mmHg
- Respiratory Rate: 8-60/min
- O2 Saturation: 70.0-100.0%
- Weight: >0 kg
- Height: >0 cm

#### Get Check-Eval
**Endpoint:** `GET /forms/check-eval/{visit_id}`

#### Update Check-Eval
**Endpoint:** `PUT /forms/check-eval/{visit_id}`

### General Sheet Form (Radiology Assessment)

#### Create General Sheet
**Endpoint:** `POST /forms/general-sheet`

**Request Body:**
```json
{
  "visit_id": "uuid",
  "diagnosis": "string",
  "reason_for_study": "string",
  "findings": "string (required)",
  "impression": "string",
  "recommendations": "string",
  "modality": "CT|MRI|X-ray|Ultrasound",
  "body_region": "string",
  "has_chronic_disease": false,
  "has_pacemaker": false,
  "is_pregnant": false,
  "has_pain_numbness": false,
  "has_spinal_deformities": false,
  "has_swelling": false,
  "has_headache": false,
  "has_fever": false,
  "has_tumor_history": false,
  "has_disc_slip": false
}
```

#### Get General Sheet
**Endpoint:** `GET /forms/general-sheet/{visit_id}`

#### Update General Sheet
**Endpoint:** `PUT /forms/general-sheet/{visit_id}`

---

## Reports

### Get Reports
**Endpoint:** `GET /reports/`

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
[
  {
    "report_id": "uuid",
    "visit_id": "uuid",
    "summary": "string",
    "doctor_notes": "string",
    "created_by": "uuid",
    "created_at": "datetime"
  }
]
```

### Create Report
**Endpoint:** `POST /reports/`

**Request Body:**
```json
{
  "visit_id": "uuid (existing visit)",
  "summary": "string",
  "doctor_notes": "string"
}
```

### Get Report by ID
**Endpoint:** `GET /reports/{report_id}`

### Update Report
**Endpoint:** `PUT /reports/{report_id}`

**Permissions:** Owner or admin only

---

## Error Handling

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing/invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Validation Errors
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

---

## Business Rules & Requirements

### User Roles & Permissions
- **Admin**: Full access to all resources
- **Physician**: Can view all patients/visits, manage assigned visits, create radiology forms
- **Nurse**: Can view patients, create/manage visits, create nursing assessment forms

### Data Validation Rules

#### Patient Data
- **SSN**: 14-digit Egyptian format, unique identifier
- **Mobile Number**: Must start with 01, followed by 8 digits
- **Gender**: male, female, other
- **Date of Birth**: Valid date, used for age calculations

#### Visit Data
- **Patient**: Must exist before creating visit
- **Status**: open → in_progress → completed
- **Created By**: Auto-assigned to current user

#### Form Submissions
- **Visit**: Must exist
- **Role-based Access**:
  - Nursing forms (SH.MR.FRM.05): Nurses only
  - Radiology forms (SH.MR.FRM.04): Physicians only
- **One form per type per visit**

#### Vital Signs Ranges
- Temperature: 30-45°C
- Pulse: 30-200 bpm
- Blood Pressure: 70-250/40-150 mmHg
- Respiratory Rate: 8-60 breaths/min
- O2 Saturation: 70-100%
- Weight: >0 kg
- Height: >0 cm

### Workflow

1. **Patient Registration**: Create patient record with SSN
2. **Visit Creation**: Nurse creates visit for patient
3. **Assessment Forms**:
   - Nurse fills Check-Eval (nursing assessment)
   - Physician fills General Sheet (radiology assessment)
4. **Report Generation**: Physician creates final report
5. **Visit Completion**: Mark visit as completed

### Security Considerations

- All sensitive data (PHI) should be encrypted
- JWT tokens expire in 30 minutes
- Passwords hashed with bcrypt
- Role-based access control
- Audit logging for all changes

---

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Docker (optional, for containerized database)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -c "from app.db.init_db import create_tables; import asyncio; asyncio.run(create_tables())"

# Start server
uvicorn app.main:app --reload
```

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

---

## Frontend Integration Notes

### Authentication Flow
1. Login → Receive JWT token
2. Store token in localStorage
3. Include token in Authorization header for all requests
4. Handle 401 responses by redirecting to login

### Error Handling
- Check response status codes
- Parse error messages from response body
- Handle network errors gracefully
- Show user-friendly error messages

### Data Fetching
- Use pagination for large lists
- Implement loading states
- Cache data when appropriate
- Handle concurrent requests properly

### Form Validation
- Validate data on frontend before submission
- Show field-level error messages
- Use the same validation rules as backend
- Handle async validation for unique constraints

### Real-time Updates
- Consider WebSocket connection for real-time updates
- Poll for status changes on long-running operations
- Implement optimistic updates for better UX

This documentation should provide everything needed for frontend developers to integrate with the backend API effectively.