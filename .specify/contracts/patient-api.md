# Patient Management API Contract

## Overview
The patient API provides comprehensive patient data management including search, registration, and profile updates.

## Endpoints

### GET /api/v1/patients
Retrieve paginated list of patients with optional search.

**Query Parameters:**
- `skip`: number (default: 0)
- `limit`: number (default: 100)
- `search`: string (searches name, SSN, mobile)

**Response (200):**
```json
[
  {
    "ssn": "string",
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

**HTMX Usage:**
```html
<div hx-get="/api/v1/patients" hx-trigger="load">
  <!-- Patient list rendered here -->
</div>
```

### POST /api/v1/patients
Create a new patient record.

**Request:**
```json
{
  "ssn": "string (14 digits)",
  "mobile_number": "string (Egyptian format)",
  "full_name": "string",
  "date_of_birth": "date (optional)",
  "gender": "male|female|other (optional)",
  "address": "string (optional)"
}
```

**Response (200):** Patient object

**Error Responses:**
- 400: Invalid SSN or mobile format
- 409: Patient with SSN already exists

### GET /api/v1/patients/{ssn}
Retrieve specific patient by SSN.

**Response (200):** Patient object

**Error Responses:**
- 404: Patient not found

### PUT /api/v1/patients/{ssn}
Update patient information.

**Request:** Partial Patient object

**Response (200):** Updated Patient object

## Validation Rules
- SSN: Exactly 14 digits, Egyptian format
- Mobile: Starts with 01, followed by 0-2, then 8 digits
- Full name: Required, 2-255 characters
- Date of birth: Must be in past, reasonable age range

## Frontend Integration
- Real-time search with debouncing
- Form validation with immediate feedback
- Emergency contact management
- Patient history integration</content>
<parameter name="filePath">/home/mohamed/lab/.specify/contracts/patient-api.md