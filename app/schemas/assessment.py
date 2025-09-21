"""
Assessment Pydantic schemas with medical validation
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class NursingAssessmentBase(BaseModel):
    """Base nursing assessment schema"""
    visit_id: UUID = Field(..., description="Visit ID this assessment belongs to")

    # Vital signs
    temperature_celsius: Optional[float] = Field(None, ge=30.0, le=45.0, description="Temperature in Celsius")
    pulse_bpm: Optional[int] = Field(None, ge=30, le=200, description="Pulse rate in beats per minute")
    blood_pressure_systolic: Optional[int] = Field(None, ge=70, le=250, description="Systolic blood pressure")
    blood_pressure_diastolic: Optional[int] = Field(None, ge=40, le=150, description="Diastolic blood pressure")
    respiratory_rate_per_min: Optional[int] = Field(None, ge=8, le=60, description="Respiratory rate per minute")
    oxygen_saturation_percent: Optional[float] = Field(None, ge=70.0, le=100.0, description="Oxygen saturation percentage")

    # Assessment data
    pain_assessment: Optional[str] = Field(None, max_length=1000, description="Pain assessment details")
    fall_risk_assessment: Optional[str] = Field(None, max_length=1000, description="Fall risk assessment details")

    # Physical measurements
    weight_kg: Optional[float] = Field(None, gt=0, le=500, description="Weight in kilograms")
    height_cm: Optional[float] = Field(None, gt=0, le=300, description="Height in centimeters")

    # General assessment
    general_condition: Optional[str] = Field(None, max_length=100, description="General condition")
    consciousness_level: Optional[str] = Field(None, max_length=50, description="Level of consciousness")
    skin_condition: Optional[str] = Field(None, max_length=1000, description="Skin condition assessment")
    mobility_status: Optional[str] = Field(None, max_length=100, description="Mobility status")

    # Notes
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")

    @field_validator('blood_pressure_diastolic')
    @classmethod
    def validate_blood_pressure(cls, v, info):
        """Validate blood pressure relationship"""
        if v is None:
            return v
        systolic = info.data.get('blood_pressure_systolic')
        if systolic is not None and v >= systolic:
            raise ValueError('Diastolic pressure must be less than systolic pressure')
        return v

    @field_validator('height_cm', 'weight_kg')
    @classmethod
    def validate_physical_measurements(cls, v):
        """Validate physical measurements are reasonable"""
        if v is None:
            return v
        if v <= 0:
            raise ValueError('Measurement must be greater than 0')
        return v


class NursingAssessmentCreate(NursingAssessmentBase):
    """Schema for creating nursing assessment"""
    pass


class NursingAssessmentUpdate(BaseModel):
    """Schema for updating nursing assessment"""
    temperature_celsius: Optional[float] = Field(None, ge=30.0, le=45.0)
    pulse_bpm: Optional[int] = Field(None, ge=30, le=200)
    blood_pressure_systolic: Optional[int] = Field(None, ge=70, le=250)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=40, le=150)
    respiratory_rate_per_min: Optional[int] = Field(None, ge=8, le=60)
    oxygen_saturation_percent: Optional[float] = Field(None, ge=70.0, le=100.0)
    pain_assessment: Optional[str] = Field(None, max_length=1000)
    fall_risk_assessment: Optional[str] = Field(None, max_length=1000)
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    general_condition: Optional[str] = Field(None, max_length=100)
    consciousness_level: Optional[str] = Field(None, max_length=50)
    skin_condition: Optional[str] = Field(None, max_length=1000)
    mobility_status: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('blood_pressure_diastolic')
    @classmethod
    def validate_blood_pressure(cls, v, info):
        """Validate blood pressure relationship"""
        if v is None:
            return v
        systolic = info.data.get('blood_pressure_systolic')
        if systolic is not None and v >= systolic:
            raise ValueError('Diastolic pressure must be less than systolic pressure')
        return v


class NursingAssessmentResponse(NursingAssessmentBase):
    """Schema for nursing assessment response"""
    id: UUID
    assessed_by: int
    assessed_at: datetime
    bmi: Optional[float]

    model_config = {"from_attributes": True}


class RadiologyAssessmentBase(BaseModel):
    """Base radiology assessment schema"""
    visit_id: UUID = Field(..., description="Visit ID this assessment belongs to")
    findings: str = Field(..., min_length=10, max_length=1000, description="Radiology findings")
    diagnosis: Optional[str] = Field(None, max_length=500, description="Diagnosis")
    recommendations: Optional[str] = Field(None, max_length=1000, description="Recommendations")

    # Technical details
    modality: Optional[str] = Field(None, max_length=50, description="Imaging modality (X-ray, CT, MRI, etc.)")
    body_region: Optional[str] = Field(None, max_length=100, description="Body region examined")
    contrast_used: Optional[str] = Field(None, max_length=100, description="Contrast agents used")

    @field_validator('findings')
    @classmethod
    def validate_findings(cls, v):
        """Validate findings content"""
        if not v or not v.strip():
            raise ValueError('Findings are required')
        if len(v.strip()) < 10:
            raise ValueError('Findings must be at least 10 characters')
        return v.strip()

    @field_validator('diagnosis')
    @classmethod
    def validate_diagnosis(cls, v):
        """Validate diagnosis if provided"""
        if v is None:
            return v
        if not v.strip():
            return None
        if len(v.strip()) < 10:
            raise ValueError('Diagnosis must be at least 10 characters if provided')
        return v.strip()


class RadiologyAssessmentCreate(RadiologyAssessmentBase):
    """Schema for creating radiology assessment"""
    pass


class RadiologyAssessmentUpdate(BaseModel):
    """Schema for updating radiology assessment"""
    findings: Optional[str] = Field(None, min_length=10, max_length=1000)
    diagnosis: Optional[str] = Field(None, max_length=500)
    recommendations: Optional[str] = Field(None, max_length=1000)
    modality: Optional[str] = Field(None, max_length=50)
    body_region: Optional[str] = Field(None, max_length=100)
    contrast_used: Optional[str] = Field(None, max_length=100)

    @field_validator('findings')
    @classmethod
    def validate_findings(cls, v):
        """Validate findings content"""
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Findings cannot be empty if provided')
        if len(v.strip()) < 10:
            raise ValueError('Findings must be at least 10 characters')
        return v.strip()

    @field_validator('diagnosis')
    @classmethod
    def validate_diagnosis(cls, v):
        """Validate diagnosis if provided"""
        if v is None or not v.strip():
            return None
        if len(v.strip()) < 10:
            raise ValueError('Diagnosis must be at least 10 characters if provided')
        return v.strip()


class RadiologyAssessmentResponse(RadiologyAssessmentBase):
    """Schema for radiology assessment response"""
    id: UUID
    assessed_by: int
    assessed_at: datetime
    has_diagnosis: bool
    findings_summary: str

    model_config = {"from_attributes": True}