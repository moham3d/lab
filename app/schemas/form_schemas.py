from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from uuid import UUID
from datetime import date

# Check-Eval schema
class CheckEvalBase(BaseModel):
    temperature_celsius: Optional[Decimal] = None
    pulse_bpm: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    respiratory_rate_per_min: Optional[int] = None
    oxygen_saturation_percent: Optional[Decimal] = None
    nurse_signature: Optional[str] = None

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
    # Study information
    study_reason: Optional[str] = None
    gypsum_splint: Optional[str] = None
    
    # Medical history
    chronic_disease: Optional[str] = None
    chronic_disease_details: Optional[str] = None
    pacemaker: Optional[str] = None
    implants: Optional[str] = None
    implants_details: Optional[str] = None
    pregnancy: Optional[str] = None
    
    # Symptoms
    pain_numbness: Optional[str] = None
    pain_location: Optional[str] = None
    pain_duration: Optional[str] = None
    spinal_deformities: Optional[str] = None
    swelling: Optional[str] = None
    swelling_location: Optional[str] = None
    headache: Optional[bool] = None
    vision_problems: Optional[bool] = None
    hearing_problems: Optional[bool] = None
    imbalance: Optional[bool] = None
    
    # Additional medical info
    fever: Optional[str] = None
    previous_operations: Optional[str] = None
    operation_date: Optional[date] = None
    operation_reason: Optional[str] = None
    tumor_history: Optional[str] = None
    tumor_location: Optional[str] = None
    tumor_type: Optional[str] = None
    previous_radiology: Optional[str] = None
    previous_radiology_type: Optional[str] = None
    previous_radiology_date: Optional[date] = None
    disc_slip: Optional[str] = None
    drowsiness_medication: Optional[str] = None
    current_medication: Optional[str] = None
    
    # Technical parameters
    dlp: Optional[str] = None
    ctd1vol: Optional[str] = None
    mas: Optional[str] = None
    kv: Optional[str] = None
    
    # Diagnosis
    diagnosis: Optional[str] = None
    
    # Signatures
    patient_signature: Optional[str] = None
    physician_signature: Optional[str] = None

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
                "findings": "Normal chest X-ray findings",
                "diagnosis": "No acute abnormalities detected",
                "recommendations": "Follow up as clinically indicated",
                "modality": "X-ray",
                "body_region": "Chest",
                "has_chronic_disease": False,
                "has_pacemaker": False,
                "is_pregnant": False,
                "assessed_by": "123e4567-e89b-12d3-a456-426614174000",
                "assessed_at": "2023-09-21T10:00:00Z"
            }
        }