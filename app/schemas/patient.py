"""
Patient and Visit Pydantic schemas with validation
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.patient import Gender
from app.models.visit import VisitStatus


class PatientBase(BaseModel):
    """Base patient schema"""
    ssn: str = Field(..., min_length=14, max_length=14, description="Egyptian SSN (14 digits)")
    mobile_number: str = Field(..., min_length=11, max_length=11, description="Egyptian mobile number")
    phone_number: Optional[str] = Field(None, min_length=11, max_length=11, description="Additional phone number")
    medical_number: Optional[str] = Field(None, max_length=20, description="Medical record number")
    full_name: str = Field(..., min_length=2, max_length=255, description="Patient full name")
    date_of_birth: Optional[date] = Field(None, description="Patient date of birth")
    gender: Optional[Gender] = Field(None, description="Patient gender")

    @validator('ssn')
    def validate_ssn(cls, v):
        """Validate SSN format"""
        import re
        if not re.match(r'^\d{14}$', v):
            raise ValueError('SSN must be exactly 14 digits')
        return v

    @validator('mobile_number')
    def validate_mobile(cls, v):
        """Validate mobile number format"""
        import re
        if not re.match(r'^01[0-2]\d{8}$', v):
            raise ValueError('Mobile number must be in Egyptian format (01[0-2]xxxxxxxx)')
        return v

    @validator('phone_number')
    def validate_phone(cls, v):
        """Validate phone number format if provided"""
        if v is None:
            return v
        import re
        if not re.match(r'^01[0-2]\d{8}$', v):
            raise ValueError('Phone number must be in Egyptian format (01[0-2]xxxxxxxx)')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name"""
        if not v or not v.strip():
            raise ValueError('Full name is required')
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()


class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient"""
    mobile_number: Optional[str] = Field(None, min_length=11, max_length=11)
    phone_number: Optional[str] = Field(None, min_length=11, max_length=11)
    medical_number: Optional[str] = Field(None, max_length=20)
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None

    @validator('mobile_number')
    def validate_mobile(cls, v):
        """Validate mobile number format"""
        if v is None:
            return v
        import re
        if not re.match(r'^01[0-2]\d{8}$', v):
            raise ValueError('Mobile number must be in Egyptian format (01[0-2]xxxxxxxx)')
        return v

    @validator('phone_number')
    def validate_phone(cls, v):
        """Validate phone number format if provided"""
        if v is None:
            return v
        import re
        if not re.match(r'^01[0-2]\d{8}$', v):
            raise ValueError('Phone number must be in Egyptian format (01[0-2]xxxxxxxx)')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name"""
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()


class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: UUID
    is_active: bool
    age: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientVisitBase(BaseModel):
    """Base patient visit schema"""
    visit_date: datetime = Field(..., description="Visit date and time")
    chief_complaint: Optional[str] = Field(None, max_length=1000, description="Chief complaint")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")

    @validator('visit_date')
    def validate_visit_date(cls, v):
        """Validate that visit date is not in the future"""
        if v > datetime.now(v.tzinfo) if v.tzinfo else v > datetime.now():
            raise ValueError('Visit date cannot be in the future')
        return v


class PatientVisitCreate(PatientVisitBase):
    """Schema for creating a patient visit"""
    patient_id: UUID = Field(..., description="Patient ID")


class PatientVisitUpdate(BaseModel):
    """Schema for updating a patient visit"""
    visit_date: Optional[datetime] = None
    status: Optional[VisitStatus] = None
    chief_complaint: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)

    @validator('visit_date')
    def validate_visit_date(cls, v):
        """Validate that visit date is not in the future"""
        if v is None:
            return v
        if v > datetime.now(v.tzinfo) if v.tzinfo else v > datetime.now():
            raise ValueError('Visit date cannot be in the future')
        return v


class PatientVisitResponse(PatientVisitBase):
    """Schema for patient visit response"""
    id: UUID
    patient_id: UUID
    status: VisitStatus
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: Optional[UUID]

    class Config:
        from_attributes = True