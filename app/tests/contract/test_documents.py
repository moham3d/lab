"""
Contract tests for         upload_data = {
            "title": "Test Lab Result"
        }

        # Send document_type and title as query parameters
        params = {"document_type": DocumentType.LAB_RESULT.value, "title": "Test Lab Result"}nt endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.main import app
from app.models.visit import PatientVisit
from app.models.document import DocumentType


@pytest.mark.asyncio
class TestDocumentContract:
    """Contract tests for document endpoints"""

    async def test_upload_document_successful(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test successful document upload"""
        # Create a test file
        file_content = b"Test document content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

        upload_data = {
            "title": "Test Lab Result"
        }

        # Send document_type and title as query parameters
        params = {"document_type": DocumentType.LAB_RESULT.value, "title": "Test Lab Result"}

        response = await client.post(
            f"/api/v1/documents/upload/{test_visit.id}",
            files=files,
            data=upload_data,
            params=params,
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "document" in data
        assert "upload_url" in data
        assert "message" in data

        document = data["document"]
        assert "id" in document
        assert "filename" in document
        assert document["document_type"] == DocumentType.LAB_RESULT
        assert document["title"] == "Test Lab Result"

    async def test_upload_document_visit_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test uploading document to non-existent visit returns 404"""
        from uuid import uuid4
        fake_visit_id = uuid4()

        file_content = b"Test document content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}

        # Pass document_type as query parameter, not form data
        response = await client.post(
            f"/api/v1/documents/upload/{fake_visit_id}?document_type=lab_result",
            files=files,
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_upload_document_invalid_file_type(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test uploading document with invalid file type returns 400"""
        file_content = b"Test executable content"
        files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-msdownload")}

        # Pass document_type as query parameter
        response = await client.post(
            f"/api/v1/documents/upload/{test_visit.id}?document_type=lab_result",
            files=files,
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_get_document_successful(self, client: AsyncClient, auth_headers: dict, test_document):
        """Test getting document metadata"""
        response = await client.get(f"/api/v1/documents/{test_document.id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(test_document.id)
        assert data["filename"] == test_document.filename
        assert data["mime_type"] == test_document.mime_type

    async def test_get_document_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent document returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        response = await client.get(f"/api/v1/documents/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    async def test_list_visit_documents_successful(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test listing documents for a visit"""
        response = await client.get(f"/api/v1/documents/visit/{test_visit.id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "documents" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["documents"], list)

    async def test_list_visit_documents_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test listing documents for non-existent visit returns 404"""
        from uuid import uuid4
        fake_visit_id = uuid4()

        response = await client.get(f"/api/v1/documents/visit/{fake_visit_id}", headers=auth_headers)

        assert response.status_code == 404

    async def test_update_document_successful(self, client: AsyncClient, auth_headers: dict, test_document):
        """Test successful document metadata update"""
        update_data = {
            "title": "Updated Document Title",
            "description": "Updated description"
        }

        response = await client.put(f"/api/v1/documents/{test_document.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]

    async def test_update_document_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent document returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        update_data = {"title": "Updated Title"}

        response = await client.put(f"/api/v1/documents/{fake_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_delete_document_successful(self, client: AsyncClient, auth_headers: dict, test_document):
        """Test successful document deletion"""
        response = await client.delete(f"/api/v1/documents/{test_document.id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "deleted" in data["message"].lower()

    async def test_delete_document_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent document returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        response = await client.delete(f"/api/v1/documents/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    async def test_download_document_successful(self, client: AsyncClient, auth_headers: dict, test_document):
        """Test successful document download"""
        response = await client.get(f"/api/v1/documents/download/{test_document.id}", headers=auth_headers)

        assert response.status_code == 200

        # Check that response has file headers
        assert "content-type" in response.headers
        assert "content-disposition" in response.headers

    async def test_download_document_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test downloading non-existent document returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        response = await client.get(f"/api/v1/documents/download/{fake_id}", headers=auth_headers)

        assert response.status_code == 404