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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    visit_date = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(20), default="open", nullable=False, index=True)  # Will validate in application logic
    chief_complaint = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="visits")
    nursing_assessment = relationship("NursingAssessment", back_populates="visit", uselist=False, cascade="all, delete-orphan")
    radiology_assessment = relationship("RadiologyAssessment", back_populates="visit", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="visit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PatientVisit(id={self.id}, patient_id={self.patient_id}, status={self.status.value})>"

    @staticmethod
    def validate_visit_date(visit_date: datetime) -> bool:
        """Validate that visit date is not in the future"""
        return visit_date <= datetime.now(visit_date.tzinfo) if visit_date.tzinfo else visit_date <= datetime.now()

    def can_transition_to(self, new_status: VisitStatus) -> bool:
        """Check if status transition is allowed"""
        transitions = {
            VisitStatus.OPEN: [VisitStatus.COMPLETED, VisitStatus.CANCELLED],
            VisitStatus.COMPLETED: [VisitStatus.OPEN],  # Admin only for corrections
            VisitStatus.CANCELLED: []  # Terminal state
        }
        return new_status in transitions.get(self.status, [])

    @property
    def is_open(self) -> bool:
        """Check if visit is currently open"""
        return self.status == VisitStatus.OPEN

    @property
    def is_completed(self) -> bool:
        """Check if visit is completed"""
        return self.status == VisitStatus.COMPLETED

    @property
    def duration_hours(self) -> Optional[float]:
        """Calculate visit duration in hours if completed"""
        if not self.is_completed or not self.updated_at:
            return None
        duration = self.updated_at - self.created_at
        return duration.total_seconds() / 3600