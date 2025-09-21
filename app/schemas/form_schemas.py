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
    # Preparation details
    preparation_time: Optional[str] = None
    injection_time: Optional[str] = None
    injection_site: Optional[str] = None
    ctd1vol: Optional[Decimal] = None
    dlp: Optional[Decimal] = None
    uses_contrast: Optional[str] = None
    kidney_function_value: Optional[Decimal] = None
    
    # Study information
    is_first_time: Optional[str] = None
    is_comparison: Optional[str] = None
    previous_study_code: Optional[str] = None
    requires_report: Optional[str] = None
    requires_cd: Optional[str] = None
    
    # Clinical information
    diagnosis: Optional[str] = None
    reason_for_study: Optional[str] = None
    
    # Assessment content
    findings: Optional[str] = None
    impression: Optional[str] = None
    recommendations: Optional[str] = None
    
    # Technical details
    modality: Optional[str] = None
    body_region: Optional[str] = None
    contrast_used: Optional[str] = None
    
    # Treatment history
    has_chemotherapy: Optional[bool] = None
    chemo_type: Optional[str] = None
    chemo_details: Optional[str] = None
    chemo_sessions: Optional[int] = None
    chemo_last_date: Optional[date] = None
    has_radiotherapy: Optional[bool] = None
    radiotherapy_site: Optional[str] = None
    radiotherapy_sessions: Optional[int] = None
    radiotherapy_last_date: Optional[date] = None
    has_hormonal_treatment: Optional[bool] = None
    hormonal_last_dose_date: Optional[date] = None
    other_treatments: Optional[str] = None
    
    # Previous imaging history
    has_operations: Optional[bool] = None
    has_endoscopy: Optional[bool] = None
    has_biopsies: Optional[bool] = None
    has_tc_dtpa_kidney_scan: Optional[bool] = None
    has_tc_mdp_bone_scan: Optional[bool] = None
    has_mri: Optional[bool] = None
    has_mammography: Optional[bool] = None
    has_ct: Optional[bool] = None
    has_xray: Optional[bool] = None
    has_ultrasound: Optional[bool] = None
    has_other_imaging: Optional[bool] = None
    other_imaging_desc: Optional[str] = None
    
    # General sheet additional fields
    mas: Optional[Decimal] = None
    kv: Optional[Decimal] = None
    has_gypsum_splint: Optional[bool] = None
    has_chronic_disease: Optional[bool] = None
    chronic_disease_desc: Optional[str] = None
    has_pacemaker: Optional[bool] = None
    has_slats_screws_joints: Optional[bool] = None
    is_pregnant: Optional[bool] = None
    has_pain_numbness: Optional[bool] = None
    pain_numbness_desc: Optional[str] = None
    has_spinal_deformities: Optional[bool] = None
    has_swelling: Optional[bool] = None
    swelling_desc: Optional[str] = None
    has_headache: Optional[bool] = None
    has_fever: Optional[bool] = None
    has_tumor_history: Optional[bool] = None
    tumor_location: Optional[str] = None
    tumor_type: Optional[str] = None
    operation_date: Optional[date] = None
    operation_reason: Optional[str] = None
    previous_investigation_type: Optional[str] = None
    previous_investigation_date: Optional[date] = None
    has_disc_slip: Optional[bool] = None
    medications_fall_risk: Optional[str] = None
    current_medications: Optional[str] = None
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