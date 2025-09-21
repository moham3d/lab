"""
Contract tests for patient endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.patient import Patient


@pytest.mark.asyncio
class TestPatientContract:
    """Contract tests for patient endpoints"""

    async def test_search_patients_successful(self, client: AsyncClient, auth_headers: dict, test_patient: Patient):
        """Test successful patient search"""
        # Use the correct search endpoint with query parameter
        search_params = {"search": test_patient.ssn}

        response = await client.get("/api/v1/patients/", params=search_params, headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            patient = data[0]
            assert "id" in patient
            assert "ssn" in patient
            assert "full_name" in patient
            assert "mobile_number" in patient

    async def test_search_patients_no_results(self, client: AsyncClient, auth_headers: dict):
        """Test patient search with no results"""
        search_params = {"search": "nonexistent"}

        response = await client.get("/api/v1/patients/", params=search_params, headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_create_patient_successful(self, client: AsyncClient, auth_headers: dict):
        """Test successful patient creation"""
        patient_data = {
            "ssn": "12345678901234",  # 14-digit SSN
            "mobile_number": "01112345679",
            "full_name": "Test Patient Contract",
            "date_of_birth": "1990-05-15",
            "gender": "male"
        }

        response = await client.post("/api/v1/patients/", json=patient_data, headers=auth_headers)

        assert response.status_code == 200  # API returns 200 OK for successful creation

        data = response.json()
        assert "id" in data
        assert data["ssn"] == patient_data["ssn"]
        assert data["full_name"] == patient_data["full_name"]
        assert data["mobile_number"] == patient_data["mobile_number"]

    async def test_create_patient_duplicate_ssn(self, client: AsyncClient, auth_headers: dict, test_patient: Patient):
        """Test creating patient with duplicate SSN returns conflict"""
        patient_data = {
            "ssn": test_patient.ssn,  # Duplicate SSN
            "mobile_number": "01112345679",
            "full_name": "Duplicate Patient",
            "date_of_birth": "1990-05-15",
            "gender": "female"
        }

        response = await client.post("/api/v1/patients/", json=patient_data, headers=auth_headers)

        assert response.status_code == 409  # Conflict

    async def test_create_patient_invalid_ssn(self, client: AsyncClient, auth_headers: dict):
        """Test creating patient with invalid SSN format"""
        patient_data = {
            "ssn": "12345678901abc",  # Invalid SSN (contains letters)
            "mobile_number": "01112345679",
            "full_name": "Invalid SSN Patient",
            "date_of_birth": "1990-05-15",
            "gender": "male"
        }

        response = await client.post("/api/v1/patients/", json=patient_data, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    async def test_create_patient_invalid_mobile(self, client: AsyncClient, auth_headers: dict):
        """Test creating patient with invalid mobile format"""
        patient_data = {
            "ssn": "123456789013",
            "mobile_number": "123456789",  # Invalid mobile (wrong format)
            "full_name": "Invalid Mobile Patient",
            "date_of_birth": "1990-05-15",
            "gender": "male"
        }

        response = await client.post("/api/v1/patients/", json=patient_data, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    async def test_get_patient_by_ssn_successful(self, client: AsyncClient, auth_headers: dict, test_patient: Patient):
        """Test getting patient by SSN"""
        response = await client.get(f"/api/v1/patients/search/ssn/{test_patient.ssn}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["ssn"] == test_patient.ssn
        assert data["full_name"] == test_patient.full_name
        assert data["mobile_number"] == test_patient.mobile_number

    async def test_get_patient_by_ssn_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent patient returns 404"""
        response = await client.get("/api/v1/patients/search/ssn/999999999999", headers=auth_headers)

        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    async def test_update_patient_successful(self, client: AsyncClient, auth_headers: dict, test_patient: Patient):
        """Test successful patient update"""
        update_data = {
            "full_name": "Updated Test Patient",
            "phone_number": "01212345678"  # Valid Egyptian phone format (11 characters)
        }

        response = await client.put(f"/api/v1/patients/{test_patient.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["phone_number"] == update_data["phone_number"]
        assert data["ssn"] == test_patient.ssn  # SSN should not change

    async def test_update_patient_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent patient returns 404"""
        from uuid import uuid4
        fake_id = uuid4()
        
        update_data = {"full_name": "Updated Name"}

        response = await client.put(f"/api/v1/patients/{fake_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_get_patient_history_successful(self, client: AsyncClient, auth_headers: dict, test_patient: Patient):
        """Test getting patient visit history"""
        # Use the visits endpoint with patient_id filter
        response = await client.get(f"/api/v1/visits/?patient_id={test_patient.id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # If there are visits, verify structure
        if len(data) > 0:
            visit = data[0]
            assert "id" in visit
            assert "visit_date" in visit
            assert "status" in visit
            assert "patient_id" in visit
            assert visit["patient_id"] == str(test_patient.id)

    async def test_get_patient_history_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting history for non-existent patient returns empty list"""
        from uuid import uuid4
        fake_patient_id = uuid4()
        
        response = await client.get(f"/api/v1/visits/?patient_id={fake_patient_id}", headers=auth_headers)

        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0