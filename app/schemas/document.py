"""
Document Pydantic schemas with file validation
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator

# Define enum locally for Pydantic compatibility
class DocumentType(str, Enum):
    """Document type enumeration"""
    LAB_RESULT = "lab_result"
    IMAGING = "imaging"
    PRESCRIPTION = "prescription"
    DISCHARGE_SUMMARY = "discharge_summary"
    PROGRESS_NOTE = "progress_note"
    CONSENT_FORM = "consent_form"
    OTHER = "other"


class DocumentBase(BaseModel):
    """Base document schema"""
    visit_id: UUID = Field(..., description="Visit ID this document belongs to")
    document_type: DocumentType = Field(..., description="Type of medical document")
    title: Optional[str] = Field(None, max_length=255, description="Document title")
    description: Optional[str] = Field(None, max_length=1000, description="Document description")


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    filename: str = Field(..., max_length=255, description="Generated filename")
    original_filename: str = Field(..., max_length=255, description="Original uploaded filename")
    mime_type: str = Field(..., max_length=100, description="MIME type of the file")
    file_size: int = Field(..., gt=0, description="File size in bytes")

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        """Validate file size (max 10MB)"""
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError('File size must not exceed 10MB')
        return v

    @field_validator('mime_type')
    @classmethod
    def validate_mime_type(cls, v):
        """Validate allowed MIME types"""
        from app.models.document import Document
        if not Document.validate_mime_type(v):
            raise ValueError('File type not allowed for medical documents')
        return v


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    document_type: Optional[DocumentType] = None


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: UUID
    filename: str
    original_filename: str
    file_path: str
    mime_type: str
    file_size: int
    file_hash: Optional[str]
    is_encrypted: bool
    uploaded_by: int
    uploaded_at: datetime
    file_size_mb: float
    is_image: bool
    is_pdf: bool
    file_extension: str
    display_name: str

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """Response after successful file upload"""
    document: DocumentResponse
    upload_url: str
    message: str = "Document uploaded successfully"


class DocumentListResponse(BaseModel):
    """Response for document listing"""
    documents: list[DocumentResponse]
    total_count: int
    page: int
    page_size: int


class FileValidationRequest(BaseModel):
    """Request to validate file before upload"""
    filename: str = Field(..., max_length=255)
    mime_type: str = Field(..., max_length=100)
    file_size: int = Field(..., gt=0)

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        """Validate file size"""
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError('File size must not exceed 10MB')
        return v

    @field_validator('mime_type')
    @classmethod
    def validate_mime_type(cls, v):
        """Validate MIME type"""
        from app.models.document import Document
        if not Document.validate_mime_type(v):
            raise ValueError('File type not allowed for medical documents')
        return v


class FileValidationResponse(BaseModel):
    """Response for file validation"""
    is_valid: bool
    message: str
    max_size_mb: int = 10
    allowed_types: list[str] = [
        "image/jpeg", "image/png", "image/gif", "image/tiff", "image/bmp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain", "text/csv",
        "application/zip", "application/x-zip-compressed"
    ]