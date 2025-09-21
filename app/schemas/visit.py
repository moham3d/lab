"""
Visit-specific schemas (imports from patient.py for consistency)
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class VisitStatus(str, Enum):
    """Visit status enumeration"""
    OPEN = "open"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VisitBase(BaseModel):
    """Base visit schema"""
    visit_date: datetime = Field(..., description="Visit date and time")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")

    @field_validator('visit_date')
    @classmethod
    def validate_visit_date(cls, v):
        """Validate that visit date is not in the future"""
        if v > datetime.now(v.tzinfo) if v.tzinfo else v > datetime.now():
            raise ValueError('Visit date cannot be in the future')
        return v


class VisitCreate(VisitBase):
    """Schema for creating a visit"""
    patient_id: UUID = Field(..., description="Patient UUID")


class VisitUpdate(BaseModel):
    """Schema for updating a visit"""
    visit_date: Optional[datetime] = None
    status: Optional[VisitStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)

    @field_validator('visit_date')
    @classmethod
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

    model_config = {"from_attributes": True}


class VisitSummary(BaseModel):
    """Summary view of a visit for listings"""
    id: UUID
    patient_id: UUID
    patient_name: str
    visit_date: datetime
    status: VisitStatus
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}