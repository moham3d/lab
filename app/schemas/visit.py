"""
Visit-specific schemas (imports from patient.py for consistency)
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.visit import VisitStatus


class VisitBase(BaseModel):
    """Base visit schema"""
    visit_date: datetime = Field(..., description="Visit date and time")
    chief_complaint: Optional[str] = Field(None, max_length=1000, description="Chief complaint")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")

    @validator('visit_date')
    def validate_visit_date(cls, v):
        """Validate that visit date is not in the future"""
        if v > datetime.now(v.tzinfo) if v.tzinfo else v > datetime.now():
            raise ValueError('Visit date cannot be in the future')
        return v


class VisitCreate(VisitBase):
    """Schema for creating a visit"""
    patient_id: UUID = Field(..., description="Patient ID")


class VisitUpdate(BaseModel):
    """Schema for updating a visit"""
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


class VisitResponse(VisitBase):
    """Schema for visit response"""
    id: UUID
    patient_id: UUID
    status: VisitStatus
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: Optional[UUID]

    class Config:
        from_attributes = True


class VisitSummary(BaseModel):
    """Summary view of a visit for listings"""
    id: UUID
    patient_id: UUID
    patient_name: str
    visit_date: datetime
    status: VisitStatus
    chief_complaint: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True