from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from uuid import UUID

# Check-Eval schema
class CheckEvalBase(BaseModel):
    temperature_celsius: Optional[Decimal] = None
    pulse_bpm: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    respiratory_rate_per_min: Optional[int] = None
    oxygen_saturation_percent: Optional[Decimal] = None

class CheckEvalCreate(CheckEvalBase):
    visit_id: UUID

class CheckEvalUpdate(CheckEvalBase):
    pass

class CheckEvalResponse(CheckEvalBase):
    assessment_id: UUID
    submission_id: UUID
    assessed_by: UUID
    assessed_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
                "submission_id": "123e4567-e89b-12d3-a456-426614174000",
                "temperature_celsius": 36.5,
                "pulse_bpm": 72,
                "blood_pressure_systolic": 120,
                "blood_pressure_diastolic": 80,
                "respiratory_rate_per_min": 16,
                "oxygen_saturation_percent": 98.0,
                "assessed_by": "123e4567-e89b-12d3-a456-426614174000",
                "assessed_at": "2023-09-21T10:00:00Z"
            }
        }

# General Sheet schema
class GeneralSheetBase(BaseModel):
    findings: Optional[str] = None
    diagnosis: Optional[str] = None
    recommendations: Optional[str] = None

class GeneralSheetCreate(GeneralSheetBase):
    visit_id: UUID

class GeneralSheetUpdate(GeneralSheetBase):
    pass

class GeneralSheetResponse(GeneralSheetBase):
    radiology_id: UUID
    submission_id: UUID
    assessed_by: UUID
    assessed_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "radiology_id": "123e4567-e89b-12d3-a456-426614174000",
                "submission_id": "123e4567-e89b-12d3-a456-426614174000",
                "findings": "Normal findings",
                "diagnosis": "No abnormalities",
                "recommendations": "Follow up as needed",
                "assessed_by": "123e4567-e89b-12d3-a456-426614174000",
                "assessed_at": "2023-09-21T10:00:00Z"
            }
        }