from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ReportBase(BaseModel):
    summary: Optional[str] = None
    doctor_notes: Optional[str] = None

class ReportCreate(ReportBase):
    visit_id: UUID

class ReportUpdate(ReportBase):
    pass

class ReportResponse(ReportBase):
    report_id: UUID
    visit_id: UUID
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "report_id": "123e4567-e89b-12d3-a456-426614174000",
                "visit_id": "123e4567-e89b-12d3-a456-426614174000",
                "summary": "Patient stable",
                "doctor_notes": "Follow up in 2 weeks",
                "created_by": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2023-09-21T10:00:00Z"
            }
        }