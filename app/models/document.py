"""
Document model for file attachments and medical records
"""

from uuid import uuid4
from typing import Optional
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class DocumentType(str, Enum):
    """Document type enumeration"""
    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    PRESCRIPTION = "prescription"
    DISCHARGE_SUMMARY = "discharge_summary"
    PROGRESS_NOTE = "progress_note"
    CONSENT_FORM = "consent_form"
    OTHER = "other"


# class Document(Base):  # Temporarily disabled
class Document(Base):
    """
    Document model for secure file storage and metadata
    """
    __tablename__ = "visit_documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.visit_id"), nullable=False, index=True)

    # File metadata
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_path = Column(Text, nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)

    # Document classification
    description = Column(Text, nullable=True)

    # Security and compliance
    is_active = Column(Boolean, default=True, nullable=False)

    # Audit fields
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    # visit = relationship("PatientVisit", back_populates="documents")  # Temporarily disabled

    def __repr__(self):
        return f"<Document(document_id={self.document_id}, document_name={self.document_name}, type={self.document_type})>"