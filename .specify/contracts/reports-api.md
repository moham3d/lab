# Reports API Contract

## Overview
The reports API provides endpoints for generating and managing patient visit reports.

## Endpoints

### GET /api/v1/reports
Retrieve paginated list of reports.

**Query Parameters:**
- `skip`: number
- `limit`: number
- `visit_id`: uuid (optional)

**Response (200):**
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

### POST /api/v1/reports
Create a new report.

**Request:**
```json
{
  "visit_id": "uuid",
  "summary": "string",
  "doctor_notes": "string"
}
```

**Response (200):** Report object

**Error Responses:**
- 404: Visit not found

### GET /api/v1/reports/{report_id}
Retrieve specific report.

**Response (200):** Report object

### PUT /api/v1/reports/{report_id}
Update report (owner or admin only).

**Request:** Partial Report object

**Response (200):** Updated Report object

**Error Responses:**
- 403: Insufficient permissions

## Frontend Integration
- Report generation from visit data
- PDF/Excel export functionality
- Print-friendly formatting
- Role-based access control</content>
<parameter name="filePath">/home/mohamed/lab/.specify/contracts/reports-api.md