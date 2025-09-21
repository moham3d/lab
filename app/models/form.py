"""
Form submission models for healthcare assessments
"""

from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class FormDefinition(Base):
    """
    Form definition/template
    """
    __tablename__ = "form_definitions"

    form_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    form_name = Column(String(100), nullable=False)
    form_type = Column(String(50), nullable=False)  # nursing, radiology, etc.
    form_version = Column(String(20), nullable=False, default="1.0")
    description = Column(Text, nullable=True)
    
    # Form structure (JSON)
    form_schema = Column(Text, nullable=True)  # JSON schema for the form
    
    # Status
    is_active = Column(String(10), nullable=False, default="active")
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    
    # Relationships
    submissions = relationship("FormSubmission", back_populates="form_definition")

    def __repr__(self):
        return f"<FormDefinition(form_id={self.form_id}, form_name={self.form_name}, form_type={self.form_type})>"


class FormSubmission(Base):
    """
    Form submission linking visits to assessments
    """
    __tablename__ = "form_submissions"

    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.visit_id"), nullable=False)
    form_id = Column(UUID(as_uuid=True), ForeignKey("form_definitions.form_id"), nullable=False)
    
    # Submission details
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    submission_status = Column(String(20), nullable=False, default="draft")  # draft, submitted, approved, rejected
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Approval workflow
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    visit = relationship("PatientVisit", back_populates="form_submissions")
    form_definition = relationship("FormDefinition", back_populates="submissions")
    nursing_assessment = relationship("NursingAssessment", back_populates="form_submission", uselist=False)
    radiology_assessment = relationship("RadiologyAssessment", back_populates="form_submission", uselist=False)

    def __repr__(self):
        return f"<FormSubmission(submission_id={self.submission_id}, visit_id={self.visit_id}, status={self.submission_status})>"

    @property
    def is_approved(self) -> bool:
        """Check if submission is approved"""
        return self.submission_status == "approved"

    @property
    def is_submitted(self) -> bool:
        """Check if submission is submitted (not draft)"""
        return self.submission_status in ["submitted", "approved"]