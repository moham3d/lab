"""
Patient model with medical data validation
"""

import re
from datetime import date
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class Gender(str, Enum):
    """Patient gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Patient(Base):
    """
    Patient model with HIPAA-compliant medical data
    """
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    ssn = Column(String(20), unique=True, nullable=False, index=True)
    mobile_number = Column(String(20), nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    medical_number = Column(String(50), unique=True, nullable=True, index=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)

    # Relationships
    visits = relationship("PatientVisit", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.full_name}, ssn={self.ssn})>"

    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        """Validate Egyptian SSN format (14 digits)"""
        if not ssn:
            return False
        return bool(re.match(r'^\d{14}$', ssn))

    @staticmethod
    def validate_mobile(mobile: str) -> bool:
        """Validate Egyptian mobile number format"""
        if not mobile:
            return False
        # Egyptian mobile format: 01[0-2] followed by 8 digits
        return bool(re.match(r'^01[0-2]\d{8}$', mobile))

    @staticmethod
    def validate_full_name(name: str) -> bool:
        """Validate full name (2-255 characters)"""
        if not name:
            return False
        return 2 <= len(name.strip()) <= 255

    @property
    def age(self) -> Optional[int]:
        """Calculate patient age from date of birth"""
        if not self.date_of_birth:
            return None
        today = date.today()
        age = today.year - self.date_of_birth.year
        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age