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


class Document(Base):
    """
    Document model for secure file storage and metadata
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.id"), nullable=False, index=True)

    # File metadata
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_hash = Column(String(128), nullable=True)  # SHA-256 hash for integrity

    # Document classification
    document_type = Column(String(50), nullable=False)  # Will validate in application logic
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Security and compliance
    is_encrypted = Column(Boolean, default=False, nullable=False)
    encryption_key_id = Column(String(100), nullable=True)

    # Audit fields
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    visit = relationship("PatientVisit", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, type={self.document_type.value})>"

    @staticmethod
    def validate_file_size(size_bytes: int, max_size_mb: int = 10) -> bool:
        """Validate file size (default max 10MB)"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return size_bytes <= max_size_bytes

    @staticmethod
    def validate_mime_type(mime_type: str) -> bool:
        """Validate allowed MIME types for medical documents"""
        allowed_types = {
            # Images
            'image/jpeg', 'image/png', 'image/gif', 'image/tiff', 'image/bmp',
            # Documents
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            # Text
            'text/plain', 'text/csv',
            # Archives (for multiple files)
            'application/zip', 'application/x-zip-compressed'
        }
        return mime_type.lower() in allowed_types

    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def is_image(self) -> bool:
        """Check if document is an image"""
        return self.mime_type.startswith('image/')

    @property
    def is_pdf(self) -> bool:
        """Check if document is a PDF"""
        return self.mime_type == 'application/pdf'

    @property
    def file_extension(self) -> str:
        """Get file extension from filename"""
        if '.' in self.filename:
            return self.filename.split('.')[-1].lower()
        return ''

    @property
    def display_name(self) -> str:
        """Get display name (title or filename)"""
        return self.title if self.title else self.original_filename