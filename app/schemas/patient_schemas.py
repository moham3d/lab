from pydantic import BaseModel
from typing import Optional
from datetime import date
from uuid import UUID

class PatientBase(BaseModel):
    ssn: str
    mobile_number: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None  # male, female, other
    address: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    mobile_number: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class PatientResponse(PatientBase):
    created_at: date
    updated_at: date
    created_by: Optional[UUID] = None
    is_active: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "ssn": "12345678901234",
                "mobile_number": "01234567890",
                "full_name": "John Doe",
                "date_of_birth": "1980-01-01",
                "gender": "male",
                "address": "123 Main St",
                "created_at": "2023-01-01",
                "updated_at": "2023-01-01",
                "is_active": True
            }
        }