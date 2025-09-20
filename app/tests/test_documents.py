"""
Tests for document management functionality
"""

import pytest
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from app.models.document import Document, DocumentType
from app.schemas.document import DocumentCreate
from app.services.document_service import DocumentService
from app.utils.file_handler import FileHandler


class TestFileHandler:
    """Test file handling utilities"""

    def test_validate_file_valid(self):
        """Test file validation with valid file"""
        # Create mock file
        file_content = b"test file content"
        file = type('MockFile', (), {
            'filename': 'test.pdf',
            'content_type': 'application/pdf',
            'size': len(file_content),
            'file': BytesIO(file_content)
        })()

        is_valid, error = FileHandler.validate_file(file)
        assert is_valid is True
        assert error == "File is valid"

    def test_validate_file_too_large(self):
        """Test file validation with file too large"""
        file_content = b"x" * (11 * 1024 * 1024)  # 11MB
        file = type('MockFile', (), {
            'filename': 'large.pdf',
            'content_type': 'application/pdf',
            'size': len(file_content),
            'file': BytesIO(file_content)
        })()

        is_valid, error = FileHandler.validate_file(file)
        assert is_valid is False
        assert "exceeds maximum" in error

    def test_validate_file_invalid_type(self):
        """Test file validation with invalid MIME type"""
        file_content = b"test file content"
        file = type('MockFile', (), {
            'filename': 'test.exe',
            'content_type': 'application/x-msdownload',
            'size': len(file_content),
            'file': BytesIO(file_content)
        })()

        is_valid, error = FileHandler.validate_file(file)
        assert is_valid is False
        assert "not allowed" in error

    def test_generate_secure_filename(self):
        """Test secure filename generation"""
        original = "test document.pdf"
        secure = FileHandler.generate_secure_filename(original)

        assert secure != original
        assert secure.endswith(".pdf")
        assert len(secure) > len(original)

    def test_is_safe_filename(self):
        """Test filename safety validation"""
        assert FileHandler._is_safe_filename("safe_file.pdf") is True
        assert FileHandler._is_safe_filename("../../../etc/passwd") is False
        assert FileHandler._is_safe_filename("file<>.txt") is False
        assert FileHandler._is_safe_filename("") is False

    def test_get_file_path(self):
        """Test file path generation"""
        filename = "test.pdf"
        visit_id = "123e4567-e89b-12d3-a456-426614174000"

        path = FileHandler.get_file_path(filename, visit_id)
        assert str(path).endswith(f"visits/{visit_id}/{filename}")

    def test_is_image_file(self):
        """Test image file detection"""
        assert FileHandler.is_image_file("image/jpeg") is True
        assert FileHandler.is_image_file("image/png") is True
        assert FileHandler.is_image_file("application/pdf") is False

    def test_is_pdf_file(self):
        """Test PDF file detection"""
        assert FileHandler.is_pdf_file("application/pdf") is True
        assert FileHandler.is_pdf_file("image/jpeg") is False

    def test_get_file_extension(self):
        """Test file extension extraction"""
        assert FileHandler.get_file_extension("document.pdf") == ".pdf"
        assert FileHandler.get_file_extension("image.jpeg") == ".jpeg"
        assert FileHandler.get_file_extension("file") == ""


class TestDocumentModel:
    """Test Document model"""

    def test_document_creation(self):
        """Test document model creation"""
        doc_data = {
            "visit_id": uuid4(),
            "document_type": DocumentType.lab_result,
            "filename": "test.pdf",
            "original_filename": "original.pdf",
            "file_path": "/path/to/file.pdf",
            "mime_type": "application/pdf",
            "file_size": 1024,
            "uploaded_by": uuid4()
        }

        document = Document(**doc_data)
        assert document.visit_id == doc_data["visit_id"]
        assert document.document_type == DocumentType.lab_result
        assert document.filename == "test.pdf"
        assert document.is_encrypted is False  # Default value

    def test_validate_mime_type(self):
        """Test MIME type validation"""
        assert Document.validate_mime_type("application/pdf") is True
        assert Document.validate_mime_type("image/jpeg") is True
        assert Document.validate_mime_type("application/x-msdownload") is False

    def test_get_file_size_mb(self):
        """Test file size conversion to MB"""
        document = Document(
            visit_id=uuid4(),
            document_type=DocumentType.lab_result,
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/path",
            mime_type="application/pdf",
            file_size=2 * 1024 * 1024,  # 2MB
            uploaded_by=uuid4()
        )

        assert document.file_size_mb == 2.0

    def test_display_name(self):
        """Test display name property"""
        # With title
        document = Document(
            visit_id=uuid4(),
            document_type=DocumentType.lab_result,
            title="Lab Results",
            filename="test.pdf",
            original_filename="original.pdf",
            file_path="/path",
            mime_type="application/pdf",
            file_size=1024,
            uploaded_by=uuid4()
        )
        assert document.display_name == "Lab Results"

        # Without title
        document.title = None
        assert document.display_name == "original.pdf"


class TestDocumentSchemas:
    """Test document Pydantic schemas"""

    def test_document_create_validation(self):
        """Test DocumentCreate schema validation"""
        valid_data = {
            "visit_id": str(uuid4()),
            "document_type": "lab_result",
            "filename": "test.pdf",
            "original_filename": "original.pdf",
            "mime_type": "application/pdf",
            "file_size": 1024
        }

        schema = DocumentCreate(**valid_data)
        assert schema.visit_id == valid_data["visit_id"]
        assert schema.document_type == DocumentType.lab_result

    def test_document_create_file_size_validation(self):
        """Test file size validation in DocumentCreate"""
        # Valid size
        DocumentCreate(
            visit_id=str(uuid4()),
            document_type="lab_result",
            filename="test.pdf",
            original_filename="test.pdf",
            mime_type="application/pdf",
            file_size=5 * 1024 * 1024  # 5MB
        )

        # Invalid size
        with pytest.raises(ValueError, match="File size must not exceed 10MB"):
            DocumentCreate(
                visit_id=str(uuid4()),
                document_type="lab_result",
                filename="test.pdf",
                original_filename="test.pdf",
                mime_type="application/pdf",
                file_size=15 * 1024 * 1024  # 15MB
            )

    def test_document_create_mime_type_validation(self):
        """Test MIME type validation in DocumentCreate"""
        # Valid MIME type
        DocumentCreate(
            visit_id=str(uuid4()),
            document_type="lab_result",
            filename="test.pdf",
            original_filename="test.pdf",
            mime_type="application/pdf",
            file_size=1024
        )

        # Invalid MIME type
        with pytest.raises(ValueError, match="File type not allowed"):
            DocumentCreate(
                visit_id=str(uuid4()),
                document_type="lab_result",
                filename="test.exe",
                original_filename="test.exe",
                mime_type="application/x-msdownload",
                file_size=1024
            )


class TestDocumentService:
    """Test document service methods"""

    @pytest.mark.asyncio
    async def test_document_to_response(self):
        """Test document to response conversion"""
        document = Document(
            id=uuid4(),
            visit_id=uuid4(),
            document_type=DocumentType.lab_result,
            title="Test Document",
            filename="test.pdf",
            original_filename="original.pdf",
            file_path="/path/to/file.pdf",
            mime_type="application/pdf",
            file_size=1024,
            uploaded_by=uuid4(),
            uploaded_at=None
        )

        response = DocumentService.document_to_response(document)

        assert response.id == document.id
        assert response.title == "Test Document"
        assert response.file_size_mb == 1024 / (1024 * 1024)
        assert response.is_image is False
        assert response.is_pdf is True
        assert response.file_extension == ".pdf"
        assert response.display_name == "Test Document"

    def test_validate_file_upload_request(self):
        """Test file upload validation"""
        from app.schemas.document import FileValidationRequest

        # Valid request
        valid_request = FileValidationRequest(
            filename="test.pdf",
            mime_type="application/pdf",
            file_size=1024
        )
        assert valid_request.filename == "test.pdf"

        # Invalid size
        with pytest.raises(ValueError, match="File size must not exceed 10MB"):
            FileValidationRequest(
                filename="test.pdf",
                mime_type="application/pdf",
                file_size=15 * 1024 * 1024
            )

        # Invalid MIME type
        with pytest.raises(ValueError, match="File type not allowed"):
            FileValidationRequest(
                filename="test.exe",
                mime_type="application/x-msdownload",
                file_size=1024
            )