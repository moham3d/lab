from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class VisitBase(BaseModel):
    patient_ssn: str
    notes: Optional[str] = None

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    notes: Optional[str] = None

class VisitResponse(VisitBase):
    visit_id: UUID
    visit_date: datetime
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "visit_id": "123e4567-e89b-12d3-a456-426614174000",
                "patient_ssn": "12345678901234",
                "visit_date": "2023-09-21T10:00:00Z",
                "created_by": "123e4567-e89b-12d3-a456-426614174000",
                "notes": "Initial visit",
                "created_at": "2023-09-21T10:00:00Z",
                "updated_at": "2023-09-21T10:00:00Z"
            }
        }