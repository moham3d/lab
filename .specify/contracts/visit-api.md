# Visit Management API Contract

## Overview
The visit API manages patient visits, linking patients to healthcare interactions and forms.

## Endpoints

### GET /api/v1/visits
Retrieve paginated list of visits.

**Query Parameters:**
- `skip`: number
- `limit`: number
- `status`: open|in_progress|completed|cancelled
- `patient_ssn`: string

**Response (200):**
```json
[
  {
    "visit_id": "uuid",
    "patient_ssn": "string",
    "visit_date": "datetime",
    "visit_status": "string",
    "visit_type": "outpatient|inpatient|emergency",
    "department": "string",
    "notes": "string",
    "created_by": "uuid",
    "created_at": "datetime"
  }
]
```

### POST /api/v1/visits
Create a new patient visit.

**Request:**
```json
{
  "patient_ssn": "string",
  "notes": "string (optional)"
}
```

**Response (200):** Visit object

**Error Responses:**
- 404: Patient not found

### GET /api/v1/visits/{visit_id}
Retrieve specific visit.

**Response (200):** Visit object

### PUT /api/v1/visits/{visit_id}
Update visit information.

**Request:** Partial Visit object

**Response (200):** Updated Visit object

## Frontend Integration
- Visit creation from patient context
- Status tracking and updates
- Form association display
- Timeline visualization</content>
<parameter name="filePath">/home/mohamed/lab/.specify/contracts/visit-api.md