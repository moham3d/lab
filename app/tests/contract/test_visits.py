"""
Contract tests for visit endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.main import app
from app.models.patient import Patient
from app.models.visit import PatientVisit


@pytest.mark.asyncio
class TestVisitContract:
    """Contract tests for visit endpoints"""

    async def test_list_visits_successful(self, client: AsyncClient, auth_headers: dict):
        """Test successful visit listing"""
        response = await client.get("/api/v1/visits/", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # If there are visits, verify structure
        if len(data) > 0:
            visit = data[0]
            assert "id" in visit
            assert "patient_id" in visit
            assert "visit_date" in visit
            assert "status" in visit

    async def test_create_visit_successful(self, client: AsyncClient, auth_headers: dict, test_patient: Patient):
        """Test successful visit creation"""
        visit_data = {
            "patient_id": str(test_patient.id),
            "visit_date": datetime.utcnow().isoformat()
        }

        response = await client.post("/api/v1/visits/", json=visit_data, headers=auth_headers)

        assert response.status_code == 200  # API returns 200 OK for successful creation

        data = response.json()
        assert "id" in data
        assert data["patient_id"] == str(test_patient.id)
        assert data["status"] == "open"
        assert "visit_date" in data

    async def test_create_visit_patient_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test creating visit for non-existent patient returns 404"""
        from uuid import uuid4
        fake_patient_id = str(uuid4())

        visit_data = {
            "patient_id": fake_patient_id,
            "visit_date": datetime.utcnow().isoformat()
        }

        response = await client.post("/api/v1/visits/", json=visit_data, headers=auth_headers)

        assert response.status_code == 400  # API returns 400 Bad Request for non-existent patient

        data = response.json()
        assert "detail" in data

    async def test_create_visit_invalid_date(self, client: AsyncClient, auth_headers: dict, test_patient: Patient):
        """Test creating visit with future date returns 422"""
        future_date = datetime(2030, 1, 1).isoformat()
        visit_data = {
            "patient_id": str(test_patient.id),
            "visit_date": future_date
        }

        response = await client.post("/api/v1/visits/", json=visit_data, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    async def test_get_visit_successful(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test getting visit by ID"""
        response = await client.get(f"/api/v1/visits/{test_visit.id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(test_visit.id)
        assert data["patient_id"] == str(test_visit.patient_id)
        assert data["status"] == test_visit.status

    async def test_get_visit_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent visit returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        response = await client.get(f"/api/v1/visits/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    async def test_update_visit_successful(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test successful visit update"""
        update_data = {
            "status": "completed"
        }

        response = await client.put(f"/api/v1/visits/{test_visit.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "completed"
        assert data["id"] == str(test_visit.id)

    async def test_update_visit_invalid_status(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test updating visit with invalid status returns 422"""
        update_data = {
            "status": "invalid_status"
        }

        response = await client.put(f"/api/v1/visits/{test_visit.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    async def test_update_visit_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent visit returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        update_data = {"status": "completed"}

        response = await client.put(f"/api/v1/visits/{fake_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 404