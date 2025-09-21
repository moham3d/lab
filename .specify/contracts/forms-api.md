# Forms API Contract

## Overview
The forms API provides endpoints for nursing assessments (Check-Eval) and radiology assessments (General Sheet).

## Check-Eval Endpoints

### POST /api/v1/forms/check-eval
Create nursing assessment for a visit.

**Request:**
```json
{
  "visit_id": "uuid",
  "temperature_celsius": 36.5,
  "pulse_bpm": 72,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "respiratory_rate_per_min": 16,
  "oxygen_saturation_percent": 98.0
  // ... other fields
}
```

**Response (200):** NursingAssessment object

### GET /api/v1/forms/check-eval/{visit_id}
Retrieve nursing assessment for a visit.

**Response (200):** NursingAssessment object or 404

### PUT /api/v1/forms/check-eval/{visit_id}
Update nursing assessment.

**Request:** Partial NursingAssessment object

**Response (200):** Updated NursingAssessment object

## General Sheet Endpoints

### POST /api/v1/forms/general-sheet
Create radiology assessment for a visit.

**Request:**
```json
{
  "visit_id": "uuid",
  "modality": "X-ray",
  "body_region": "Chest",
  "findings": "Normal findings",
  "diagnosis": "No abnormalities",
  "recommendations": "Follow up as needed"
  // ... extensive fields
}
```

**Response (200):** RadiologyAssessment object

### GET /api/v1/forms/general-sheet/{visit_id}
Retrieve radiology assessment for a visit.

**Response (200):** RadiologyAssessment object or 404

### PUT /api/v1/forms/general-sheet/{visit_id}
Update radiology assessment.

**Request:** Partial RadiologyAssessment object

**Response (200):** Updated RadiologyAssessment object

## Frontend Integration
- Auto-save with debounced HTMX requests
- Real-time validation feedback
- Progress indicators for completion
- Conditional field display logic
- Rich text editing for findings
- Digital signature capture</content>
<parameter name="filePath">/home/mohamed/lab/.specify/contracts/forms-api.md