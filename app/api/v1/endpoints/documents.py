"""
Document API routes for file upload and management
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentType,
    DocumentUpdate,
    DocumentUploadResponse,
    FileValidationRequest,
    FileValidationResponse
)
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/upload/{visit_id}", response_model=DocumentUploadResponse)
async def upload_document(
    visit_id: UUID,
    file: UploadFile = File(...),
    document_type: DocumentType = Query(..., description="Type of medical document"),
    title: str = Query(None, description="Document title"),
    description: str = Query(None, description="Document description"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a medical document for a patient visit
    """
    try:
        # Upload file and create document record
        document = await DocumentService.upload_and_create_document(
            db=db,
            file=file,
            visit_id=visit_id,
            document_type=document_type,
            user_id=current_user.id,
            title=title,
            description=description
        )

        # Convert to response
        document_response = DocumentService.document_to_response(document)

        return DocumentUploadResponse(
            document=document_response,
            upload_url=f"/api/v1/documents/download/{document.id}",
            message="Document uploaded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/validate-upload/{visit_id}", response_model=FileValidationResponse)
async def validate_file_upload(
    visit_id: UUID,
    validation_request: FileValidationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate file before upload
    """
    try:
        validation_result = await DocumentService.validate_file_upload(
            db=db,
            validation_request=validation_request,
            visit_id=visit_id,
            user_id=current_user.id
        )

        return FileValidationResponse(**validation_result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get document metadata by ID
    """
    try:
        document = await DocumentService.get_document_by_id(
            db=db,
            document_id=document_id,
            user_id=current_user.id
        )

        return DocumentService.document_to_response(document)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")


@router.get("/visit/{visit_id}", response_model=DocumentListResponse)
async def get_visit_documents(
    visit_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all documents for a patient visit
    """
    try:
        documents = await DocumentService.get_documents_by_visit(
            db=db,
            visit_id=visit_id,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )

        document_responses = [
            DocumentService.document_to_response(doc) for doc in documents
        ]

        return DocumentListResponse(
            documents=document_responses,
            total_count=len(document_responses),
            page=skip // limit + 1,
            page_size=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    update_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update document metadata
    """
    try:
        document = await DocumentService.update_document(
            db=db,
            document_id=document_id,
            update_data=update_data,
            user_id=current_user.id
        )

        return DocumentService.document_to_response(document)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update document: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete document and associated file
    """
    try:
        success = await DocumentService.delete_document(
            db=db,
            document_id=document_id,
            user_id=current_user.id
        )

        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/download/{document_id}")
async def download_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download document file
    """
    try:
        from fastapi.responses import FileResponse

        # Get file path
        file_path = await DocumentService.get_document_file_path(
            db=db,
            document_id=document_id,
            user_id=current_user.id
        )

        # Get document for filename
        document = await DocumentService.get_document_by_id(
            db=db,
            document_id=document_id,
            user_id=current_user.id
        )

        return FileResponse(
            path=file_path,
            filename=document.original_filename,
            media_type=document.mime_type
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download document: {str(e)}")