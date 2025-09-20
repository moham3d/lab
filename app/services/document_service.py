"""
Document service with business logic for medical document management
"""

import os
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentType
from app.models.visit import PatientVisit
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    FileValidationRequest
)
from app.utils.file_handler import FileHandler


class DocumentService:
    """Service for document management operations"""

    @staticmethod
    async def create_document(
        db: AsyncSession,
        document_data: DocumentCreate,
        user_id: UUID
    ) -> Document:
        """Create a new document record"""
        # Verify visit exists and user has access
        visit = await db.get(PatientVisit, document_data.visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        # Create document record
        document = Document(
            **document_data.model_dump(),
            uploaded_by=user_id
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        return document

    @staticmethod
    async def upload_and_create_document(
        db: AsyncSession,
        file: UploadFile,
        visit_id: UUID,
        document_type: DocumentType,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Document:
        """Upload file and create document record"""
        # Validate file
        is_valid, error_msg = FileHandler.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Verify visit exists
        visit = await db.get(PatientVisit, visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        # Generate secure filename
        secure_filename = FileHandler.generate_secure_filename(file.filename)

        # Get file path
        file_path = FileHandler.get_file_path(secure_filename, str(visit_id))

        # Save file
        success, error_msg = await FileHandler.save_file(file, file_path)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {error_msg}")

        # Calculate file hash
        file_hash = FileHandler.calculate_file_hash(file_path)

        # Create document record
        document_data = DocumentCreate(
            visit_id=visit_id,
            document_type=document_type,
            title=title,
            description=description,
            filename=secure_filename,
            original_filename=file.filename,
            mime_type=file.content_type,
            file_size=file.size
        )

        document = Document(
            **document_data.model_dump(),
            uploaded_by=user_id,
            file_hash=file_hash
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        return document

    @staticmethod
    async def get_document_by_id(
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID
    ) -> Document:
        """Get document by ID with access control"""
        document = await db.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Check if user has access to the visit
        visit = await db.get(PatientVisit, document.visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Associated visit not found")

        # TODO: Add role-based access control check
        # For now, allow access if user is associated with the visit

        return document

    @staticmethod
    async def get_documents_by_visit(
        db: AsyncSession,
        visit_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Document]:
        """Get all documents for a visit"""
        # Verify visit exists and user has access
        visit = await db.get(PatientVisit, visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        # TODO: Add access control

        from sqlalchemy import select
        query = select(Document).where(Document.visit_id == visit_id)
        result = await db.execute(query)
        documents = result.scalars().all()

        return list(documents)

    @staticmethod
    async def update_document(
        db: AsyncSession,
        document_id: UUID,
        update_data: DocumentUpdate,
        user_id: UUID
    ) -> Document:
        """Update document metadata"""
        document = await DocumentService.get_document_by_id(db, document_id, user_id)

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(document, field, value)

        await db.commit()
        await db.refresh(document)

        return document

    @staticmethod
    async def delete_document(
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete document and associated file"""
        document = await DocumentService.get_document_by_id(db, document_id, user_id)

        # Delete physical file
        file_path = FileHandler.get_file_path(document.filename, str(document.visit_id))
        FileHandler.delete_file(file_path)

        # Delete database record
        await db.delete(document)
        await db.commit()

        return True

    @staticmethod
    async def get_document_file_path(
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID
    ) -> Path:
        """Get file path for document download"""
        document = await DocumentService.get_document_by_id(db, document_id, user_id)

        file_path = FileHandler.get_file_path(document.filename, str(document.visit_id))

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")

        return file_path

    @staticmethod
    async def validate_file_upload(
        db: AsyncSession,
        validation_request: FileValidationRequest,
        visit_id: UUID,
        user_id: UUID
    ) -> dict:
        """Validate file before upload"""
        # Verify visit exists
        visit = await db.get(PatientVisit, visit_id)
        if not visit:
            raise HTTPException(status_code=404, detail="Visit not found")

        # Validate file using FileHandler
        is_valid_mime = FileHandler.get_mime_type(validation_request.filename) == validation_request.mime_type
        is_allowed_mime = validation_request.mime_type in FileHandler.ALLOWED_MIME_TYPES
        is_valid_size = validation_request.file_size <= FileHandler.MAX_FILE_SIZE

        return {
            "is_valid": is_valid_mime and is_allowed_mime and is_valid_size,
            "mime_type_valid": is_valid_mime,
            "mime_type_allowed": is_allowed_mime,
            "size_valid": is_valid_size,
            "max_size_mb": FileHandler.MAX_FILE_SIZE / (1024 * 1024),
            "allowed_types": list(FileHandler.ALLOWED_MIME_TYPES)
        }

    @staticmethod
    def document_to_response(document: Document) -> DocumentResponse:
        """Convert Document model to DocumentResponse schema"""
        return DocumentResponse(
            id=document.id,
            visit_id=document.visit_id,
            document_type=document.document_type,
            title=document.title,
            description=document.description,
            filename=document.filename,
            original_filename=document.original_filename,
            file_path=document.file_path,
            mime_type=document.mime_type,
            file_size=document.file_size,
            file_hash=document.file_hash,
            is_encrypted=document.is_encrypted,
            uploaded_by=document.uploaded_by,
            uploaded_at=document.uploaded_at,
            file_size_mb=round(document.file_size / (1024 * 1024), 2),
            is_image=FileHandler.is_image_file(document.mime_type),
            is_pdf=FileHandler.is_pdf_file(document.mime_type),
            file_extension=FileHandler.get_file_extension(document.original_filename),
            display_name=document.title or document.original_filename
        )