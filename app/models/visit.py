"""
PatientVisit model for tracking patient visits
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class VisitStatus(str, Enum):
    """Visit status enumeration"""
    OPEN = "open"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PatientVisit(Base):
    """
    Patient visit tracking with status management
    """
    __tablename__ = "patient_visits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, name="visit_id")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    visit_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    status = Column(String(20), default="open", nullable=False, index=True, name="visit_status")
    primary_diagnosis = Column(Text, nullable=True, name="primary_diagnosis")
    secondary_diagnosis = Column(Text, nullable=True, name="secondary_diagnosis")
    diagnosis_code = Column(String(20), nullable=True, name="diagnosis_code")
    visit_type = Column(String(30), default="outpatient", nullable=False, name="visit_type")
    department = Column(String(100), nullable=True, name="department")
    chief_complaint = Column(Text, nullable=True, name="chief_complaint")
    notes = Column(Text, nullable=True, name="notes")

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assigned_physician = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True, name="assigned_physician")
    completed_at = Column(DateTime(timezone=True), nullable=True, name="completed_at")

    # Relationships
    patient = relationship("Patient", back_populates="visits")
    nursing_assessment = relationship("NursingAssessment", back_populates="visit", uselist=False)
    radiology_assessment = relationship("RadiologyAssessment", back_populates="visit", uselist=False)
    # documents = relationship("Document", back_populates="visit", cascade="all, delete-orphan")  # Temporarily disabled

    def __repr__(self):
        return f"<PatientVisit(id={self.id}, patient_id={self.patient_id}, status={self.status})>"

    @staticmethod
    def validate_visit_date(visit_date: datetime) -> bool:
        """Validate that visit date is not in the future"""
        return visit_date <= datetime.now(visit_date.tzinfo) if visit_date.tzinfo else visit_date <= datetime.now()

    def can_transition_to(self, new_status: str) -> bool:
        """Check if status transition is allowed"""
        transitions = {
            "open": ["completed", "cancelled"],
            "completed": ["open"],  # Admin only for corrections
            "cancelled": []  # Terminal state
        }
        return new_status in transitions.get(self.status, [])

    @property
    def is_open(self) -> bool:
        """Check if visit is currently open"""
        return self.status == "open"

    @property
    def is_completed(self) -> bool:
        """Check if visit is completed"""
        return self.status == "completed"

    @property
    def duration_hours(self) -> Optional[float]:
        """Calculate visit duration in hours if completed"""
        if not self.is_completed or not self.updated_at:
            return None
        duration = self.updated_at - self.created_at
        return duration.total_seconds() / 3600