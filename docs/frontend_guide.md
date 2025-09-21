# Frontend Developer Guide: Patient Visit Management System

## Overview

This guide provides comprehensive documentation for frontend developers to build forms and interfaces for the Patient Visit Management System using HTMX. The backend is a FastAPI application with PostgreSQL database, providing RESTful APIs for managing patients, visits, assessments, and reports.

### Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **Frontend Integration**: HTMX for dynamic interactions
- **API Documentation**: Automatic OpenAPI/Swagger at `/docs`

### Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints except authentication require a JWT token in the `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

### Login
**Endpoint**: `POST /api/v1/auth/login`

**Request Body**:
```json
{
  "username": "nurse1",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**HTMX Example**:
```html
<form hx-post="/api/v1/auth/login" hx-target="#result" hx-swap="innerHTML">
  <input name="username" type="text" placeholder="Username" required>
  <input name="password" type="password" placeholder="Password" required>
  <button type="submit">Login</button>
</form>
<div id="result"></div>
```

### Register (Admin Only)
**Endpoint**: `POST /api/v1/auth/register`

**Request Body**:
```json
{
  "username": "nurse1",
  "email": "nurse1@hospital.com",
  "full_name": "Jane Nurse",
  "role": "nurse",
  "password": "password123"
}
```

## Core Entities

### Users
- **Roles**: `nurse`, `physician`, `admin`
- **Permissions**: Admins can manage users; others can view/update their own profile

### Patients
- **SSN**: 14-digit Egyptian format
- **Mobile**: 01[0-2] followed by 8 digits

### Visits
- Each patient visit creates a new record
- Forms are associated with visits

### Forms
- **Check-Eval**: Nursing assessment form (vital signs)
- **General Sheet**: Radiology assessment form (comprehensive patient history and imaging)

## API Endpoints

### Users

#### List Users (Admin Only)
**GET** `/api/v1/users/`

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

**Response**: Array of UserResponse objects

#### Create User (Admin Only)
**POST** `/api/v1/users/`

**Request Body**: UserCreate schema

#### Get User
**GET** `/api/v1/users/{user_id}`

#### Update User
**PUT** `/api/v1/users/{user_id}`

**Request Body**: UserUpdate schema

### Patients

#### List Patients
**GET** `/api/v1/patients/`

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

**Response**:
```json
[
  {
    "ssn": "12345678901234",
    "mobile_number": "01234567890",
    "full_name": "John Doe",
    "date_of_birth": "1980-01-01",
    "gender": "male",
    "address": "123 Main St",
    "created_at": "2023-01-01",
    "updated_at": "2023-01-01",
    "is_active": true
  }
]
```

#### Create Patient
**POST** `/api/v1/patients/`

**Request Body**:
```json
{
  "ssn": "12345678901234",
  "mobile_number": "01234567890",
  "full_name": "John Doe",
  "date_of_birth": "1980-01-01",
  "gender": "male",
  "address": "123 Main St"
}
```

#### Get Patient
**GET** `/api/v1/patients/{ssn}`

#### Update Patient
**PUT** `/api/v1/patients/{ssn}`

**Request Body**: PatientUpdate schema

### Visits

#### List Visits
**GET** `/api/v1/visits/`

#### Create Visit
**POST** `/api/v1/visits/`

**Request Body**:
```json
{
  "patient_ssn": "12345678901234",
  "notes": "Initial consultation"
}
```

#### Get Visit
**GET** `/api/v1/visits/{visit_id}`

#### Update Visit
**PUT** `/api/v1/visits/{visit_id}`

### Forms

#### Check-Eval (Nursing Assessment)

##### Create Check-Eval Form
**POST** `/api/v1/forms/check-eval`

**Request Body**:
```json
{
  "visit_id": "123e4567-e89b-12d3-a456-426614174000",
  "temperature_celsius": 36.5,
  "pulse_bpm": 72,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "respiratory_rate_per_min": 16,
  "oxygen_saturation_percent": 98.0
}
```

##### Get Check-Eval Form
**GET** `/api/v1/forms/check-eval/{visit_id}`

##### Update Check-Eval Form
**PUT** `/api/v1/forms/check-eval/{visit_id}`

#### General Sheet (Radiology Assessment)

The General Sheet form includes comprehensive patient history, treatment details, imaging history, and radiology-specific information.

##### Create General Sheet Form
**POST** `/api/v1/forms/general-sheet`

**Request Body** (partial example - all fields are optional):
```json
{
  "visit_id": "123e4567-e89b-12d3-a456-426614174000",
  "modality": "X-ray",
  "body_region": "Chest",
  "findings": "Normal chest X-ray findings",
  "diagnosis": "No acute abnormalities detected",
  "recommendations": "Follow up as clinically indicated",
  "has_chronic_disease": false,
  "has_pacemaker": false,
  "is_pregnant": false,
  "has_operations": true,
  "has_ct": true,
  "mas": 10.5,
  "kv": 120.0,
  "patient_signature": "Patient Name",
  "physician_signature": "Dr. Smith"
}
```

##### Get General Sheet Form
**GET** `/api/v1/forms/general-sheet/{visit_id}`

##### Update General Sheet Form
**PUT** `/api/v1/forms/general-sheet/{visit_id}`

### Reports

#### List Reports
**GET** `/api/v1/reports/`

#### Create Report
**POST** `/api/v1/reports/`

**Request Body**:
```json
{
  "visit_id": "123e4567-e89b-12d3-a456-426614174000",
  "summary": "Patient presented with chest pain",
  "doctor_notes": "ECG normal, prescribed rest"
}
```

#### Get Report
**GET** `/api/v1/reports/{report_id}`

#### Update Report
**PUT** `/api/v1/reports/{report_id}`

## HTMX Integration Examples

### Authentication Form
```html
<div id="auth-section">
  <h2>Login</h2>
  <form hx-post="/api/v1/auth/login" 
        hx-target="#auth-result" 
        hx-swap="innerHTML"
        hx-headers='{"Content-Type": "application/json"}'>
    <input name="username" type="text" placeholder="Username" required>
    <input name="password" type="password" placeholder="Password" required>
    <button type="submit">Login</button>
  </form>
  <div id="auth-result"></div>
</div>
```

### Patient Registration Form
```html
<div id="patient-form">
  <h2>Register New Patient</h2>
  <form hx-post="/api/v1/patients/" 
        hx-target="#patient-result" 
        hx-swap="innerHTML"
        hx-headers='{"Content-Type": "application/json", "Authorization": "Bearer ' + token + '"}'>
    <input name="ssn" type="text" placeholder="SSN (14 digits)" pattern="\d{14}" required>
    <input name="mobile_number" type="tel" placeholder="Mobile (01xxxxxxxxx)" pattern="01[0-2]\d{8}" required>
    <input name="full_name" type="text" placeholder="Full Name" required>
    <input name="date_of_birth" type="date">
    <select name="gender">
      <option value="">Select Gender</option>
      <option value="male">Male</option>
      <option value="female">Female</option>
      <option value="other">Other</option>
    </select>
    <textarea name="address" placeholder="Address"></textarea>
    <button type="submit">Register Patient</button>
  </form>
  <div id="patient-result"></div>
</div>
```

### Dynamic Patient List
```html
<div id="patient-list">
  <h2>Patients</h2>
  <button hx-get="/api/v1/patients/" 
          hx-target="#patient-list" 
          hx-swap="innerHTML"
          hx-headers='{"Authorization": "Bearer ' + token + '"}'>
    Load Patients
  </button>
  <div id="patients"></div>
</div>
```

### Check-Eval Form (Vital Signs)
```html
<div id="check-eval-form">
  <h2>Nursing Assessment (Check-Eval)</h2>
  <form hx-post="/api/v1/forms/check-eval" 
        hx-target="#check-eval-result" 
        hx-swap="innerHTML"
        hx-headers='{"Content-Type": "application/json", "Authorization": "Bearer ' + token + '"}'>
    <input name="visit_id" type="hidden" value="current-visit-id">
    
    <label>Temperature (°C):</label>
    <input name="temperature_celsius" type="number" step="0.1" min="30" max="45">
    
    <label>Pulse (bpm):</label>
    <input name="pulse_bpm" type="number" min="30" max="200">
    
    <label>Blood Pressure:</label>
    <input name="blood_pressure_systolic" type="number" placeholder="Systolic">
    <input name="blood_pressure_diastolic" type="number" placeholder="Diastolic">
    
    <label>Respiratory Rate (per min):</label>
    <input name="respiratory_rate_per_min" type="number" min="8" max="60">
    
    <label>Oxygen Saturation (%):</label>
    <input name="oxygen_saturation_percent" type="number" step="0.1" min="0" max="100">
    
    <button type="submit">Save Assessment</button>
  </form>
  <div id="check-eval-result"></div>
</div>
```

### General Sheet Form (Radiology Assessment)
```html
<div id="general-sheet-form">
  <h2>Radiology Assessment (General Sheet)</h2>
  <form hx-post="/api/v1/forms/general-sheet" 
        hx-target="#general-sheet-result" 
        hx-swap="innerHTML"
        hx-headers='{"Content-Type": "application/json", "Authorization": "Bearer ' + token + '"}'>
    <input name="visit_id" type="hidden" value="current-visit-id">
    
    <!-- Technical Details -->
    <fieldset>
      <legend>Technical Details</legend>
      <select name="modality">
        <option value="">Select Modality</option>
        <option value="X-ray">X-ray</option>
        <option value="CT">CT</option>
        <option value="MRI">MRI</option>
        <option value="Ultrasound">Ultrasound</option>
      </select>
      <input name="body_region" type="text" placeholder="Body Region">
      <input name="mas" type="number" step="0.1" placeholder="mAs">
      <input name="kv" type="number" step="0.1" placeholder="kV">
    </fieldset>
    
    <!-- Patient History -->
    <fieldset>
      <legend>Patient History</legend>
      <label><input name="has_chronic_disease" type="checkbox"> Chronic Disease</label>
      <textarea name="chronic_disease_desc" placeholder="Chronic disease description"></textarea>
      
      <label><input name="has_pacemaker" type="checkbox"> Pacemaker</label>
      <label><input name="is_pregnant" type="checkbox"> Pregnant</label>
      
      <label><input name="has_operations" type="checkbox"> Previous Operations</label>
      <label><input name="has_ct" type="checkbox"> Previous CT</label>
      <label><input name="has_mri" type="checkbox"> Previous MRI</label>
    </fieldset>
    
    <!-- Assessment -->
    <fieldset>
      <legend>Assessment</legend>
      <textarea name="findings" rows="4" placeholder="Findings" required></textarea>
      <textarea name="diagnosis" rows="4" placeholder="Diagnosis"></textarea>
      <textarea name="recommendations" rows="4" placeholder="Recommendations"></textarea>
    </fieldset>
    
    <!-- Signatures -->
    <fieldset>
      <legend>Signatures</legend>
      <input name="patient_signature" type="text" placeholder="Patient Signature">
      <input name="physician_signature" type="text" placeholder="Physician Signature">
    </fieldset>
    
    <button type="submit">Save Assessment</button>
  </form>
  <div id="general-sheet-result"></div>
</div>
```

## Form Field Specifications

### Check-Eval Form Fields
- **temperature_celsius**: Decimal (30.0 - 45.0 °C)
- **pulse_bpm**: Integer (30 - 200 bpm)
- **blood_pressure_systolic**: Integer (70 - 250 mmHg)
- **blood_pressure_diastolic**: Integer (40 - 150 mmHg)
- **respiratory_rate_per_min**: Integer (8 - 60 breaths/min)
- **oxygen_saturation_percent**: Decimal (0.0 - 100.0 %)

### General Sheet Form Fields (Extended)
The General Sheet includes the following field categories:

#### Preparation & Technical Details
- `preparation_time`, `injection_time`, `injection_site`
- `ctd1vol` (CTDI volume), `dlp` (Dose length product)
- `uses_contrast`, `kidney_function_value`
- `mas` (milliampere-seconds), `kv` (kilovoltage)

#### Study Information
- `is_first_time`, `is_comparison`, `previous_study_code`
- `requires_report`, `requires_cd`
- `modality` (CT, MRI, X-ray), `body_region`, `contrast_used`

#### Clinical Information
- `diagnosis`, `reason_for_study`

#### Assessment Content
- `findings`, `impression`, `recommendations`

#### Treatment History
- Chemotherapy: `has_chemotherapy`, `chemo_type`, `chemo_details`, `chemo_sessions`, `chemo_last_date`
- Radiotherapy: `has_radiotherapy`, `radiotherapy_site`, `radiotherapy_sessions`, `radiotherapy_last_date`
- Hormonal: `has_hormonal_treatment`, `hormonal_last_dose_date`
- `other_treatments`

#### Previous Imaging History
- `has_operations`, `has_endoscopy`, `has_biopsies`
- `has_tc_dtpa_kidney_scan`, `has_tc_mdp_bone_scan`
- `has_mri`, `has_mammography`, `has_ct`, `has_xray`, `has_ultrasound`
- `has_other_imaging`, `other_imaging_desc`

#### Patient Conditions
- `has_chronic_disease`, `chronic_disease_desc`
- `has_pacemaker`, `has_slats_screws_joints`
- `is_pregnant`, `has_pain_numbness`, `pain_numbness_desc`
- `has_spinal_deformities`, `has_swelling`, `swelling_desc`
- `has_headache`, `has_fever`
- `has_tumor_history`, `tumor_location`, `tumor_type`
- `has_disc_slip`, `medications_fall_risk`, `current_medications`

#### Signatures
- `patient_signature`, `physician_signature`

## Error Handling

### Common HTTP Status Codes
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (invalid/missing token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found (resource doesn't exist)
- **422**: Unprocessable Entity (business logic validation)

### HTMX Error Handling
```html
<div hx-target="#error-message" hx-swap="innerHTML">
  <!-- Form content -->
</div>
<div id="error-message" class="error"></div>
```

## Best Practices

1. **Store JWT Token**: Save the token in localStorage/sessionStorage after login
2. **Include Authorization Header**: Add `Authorization: Bearer <token>` to all authenticated requests
3. **Handle Token Expiry**: Implement token refresh or re-login on 401 responses
4. **Form Validation**: Use HTML5 validation and server-side validation
5. **Loading States**: Use HTMX indicators for better UX
6. **Error Display**: Show user-friendly error messages
7. **Pagination**: Implement pagination for large lists
8. **Real-time Updates**: Use HTMX polling for dynamic data

## Development Setup

1. Start the backend: `docker-compose up --build`
2. Access API docs: `http://localhost:8000/docs`
3. Health check: `http://localhost:8000/health`

## Security Notes

- All patient data is PHI (Protected Health Information)
- Implement proper session management
- Use HTTPS in production
- Validate all input data
- Log all user actions for audit trails</content>
<parameter name="filePath">/home/mohamed/lab/docs/frontend_guide.md