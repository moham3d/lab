"""
Contract tests for assessment endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.visit import PatientVisit
from app.schemas.assessment import NursingAssessmentCreate, RadiologyAssessmentCreate


@pytest.mark.asyncio
class TestAssessmentContract:
    """Contract tests for assessment endpoints"""

    async def test_create_nursing_assessment_successful(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test successful nursing assessment creation"""
        assessment_data = {
            "visit_id": str(test_visit.id),
            "temperature_celsius": 37.5,
            "pulse_bpm": 80,
            "blood_pressure_systolic": 140,
            "blood_pressure_diastolic": 90,
            "respiratory_rate_per_min": 16,
            "oxygen_saturation_percent": 98.0,
            "pain_assessment": "Chest pain assessment",
            "fall_risk_assessment": "Low fall risk",
            "weight_kg": 75.0,
            "height_cm": 175.0,
            "general_condition": "Alert and oriented",
            "consciousness_level": "Conscious",
            "skin_condition": "Normal skin condition",
            "mobility_status": "Mobile",
            "notes": "Patient reports chest pain"
        }

        response = await client.post(
            "/api/v1/assessments/nursing/",
            json=assessment_data,
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert data["visit_id"] == str(test_visit.id)
        assert data["temperature_celsius"] == 37.5
        assert data["general_condition"] == "Alert and oriented"

    async def test_create_nursing_assessment_visit_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test creating nursing assessment for non-existent visit returns 404"""
        from uuid import uuid4
        fake_visit_id = uuid4()

        assessment_data = {
            "visit_id": str(fake_visit_id),
            "general_condition": "Chest pain",
            "temperature_celsius": 37.5
        }

        response = await client.post(
            "/api/v1/assessments/nursing/",
            json=assessment_data,
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_create_radiology_assessment_successful(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test successful radiology assessment creation"""
        assessment_data = {
            "visit_id": str(test_visit.id),
            "findings": "Normal cardiac silhouette, clear lung fields",
            "diagnosis": "No acute cardiopulmonary abnormality",
            "recommendations": "Clinical correlation recommended",
            "modality": "Chest X-ray",
            "body_region": "Chest",
            "contrast_used": "None"
        }

        response = await client.post(
            "/api/v1/assessments/radiology/",
            json=assessment_data,
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert data["visit_id"] == str(test_visit.id)
        assert data["modality"] == "Chest X-ray"
        assert data["findings"] == "Normal cardiac silhouette, clear lung fields"

    async def test_create_radiology_assessment_visit_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test creating radiology assessment for non-existent visit returns 422"""
        from uuid import uuid4
        fake_visit_id = uuid4()

        assessment_data = {
            "visit_id": str(fake_visit_id),
            "modality": "Chest X-ray",
            "findings": "Normal"
        }

        response = await client.post(
            "/api/v1/assessments/radiology/",
            json=assessment_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    async def test_get_nursing_assessment_successful(self, client: AsyncClient, auth_headers: dict, test_nursing_assessment):
        """Test getting nursing assessment"""
        response = await client.get(f"/api/v1/assessments/nursing/{test_nursing_assessment.id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(test_nursing_assessment.id)
        assert "general_condition" in data
        assert "temperature_celsius" in data
        assert "pulse_bpm" in data

    async def test_get_nursing_assessment_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent nursing assessment returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        response = await client.get(f"/api/v1/assessments/nursing/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    async def test_get_radiology_assessment_successful(self, client: AsyncClient, auth_headers: dict, test_radiology_assessment):
        """Test getting radiology assessment"""
        response = await client.get(f"/api/v1/assessments/radiology/{test_radiology_assessment.id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(test_radiology_assessment.id)
        assert "modality" in data
        assert "findings" in data
        assert "diagnosis" in data

    async def test_get_radiology_assessment_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent radiology assessment returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        response = await client.get(f"/api/v1/assessments/radiology/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    async def test_update_nursing_assessment_successful(self, client: AsyncClient, auth_headers: dict, test_nursing_assessment):
        """Test successful nursing assessment update"""
        update_data = {
            "general_condition": "Updated condition",
            "notes": "Updated notes"
        }

        response = await client.put(
            f"/api/v1/assessments/nursing/{test_nursing_assessment.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert data["general_condition"] == update_data["general_condition"]
        assert data["notes"] == update_data["notes"]

    async def test_update_nursing_assessment_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent nursing assessment returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        update_data = {"assessment": "Updated"}

        response = await client.put(f"/api/v1/assessments/nursing/{fake_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_update_radiology_assessment_successful(self, client: AsyncClient, auth_headers: dict, test_radiology_assessment):
        """Test successful radiology assessment update"""
        update_data = {
            "diagnosis": "Updated diagnosis",
            "recommendations": "Updated recommendations"
        }

        response = await client.put(
            f"/api/v1/assessments/radiology/{test_radiology_assessment.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert data["diagnosis"] == update_data["diagnosis"]
        assert data["recommendations"] == update_data["recommendations"]

    async def test_update_radiology_assessment_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent radiology assessment returns 404"""
        from uuid import uuid4
        fake_id = uuid4()

        update_data = {"impression": "Updated"}

        response = await client.put(f"/api/v1/assessments/radiology/{fake_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_list_visit_assessments_successful(self, client: AsyncClient, auth_headers: dict, test_visit: PatientVisit):
        """Test listing assessments for a visit"""
        response = await client.get(f"/api/v1/assessments/visit/{test_visit.id}/status", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "visit_id" in data
        assert "has_nursing_assessment" in data
        assert "has_radiology_assessment" in data
        assert "assessments_complete" in data

    async def test_list_visit_assessments_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test listing assessments for non-existent visit returns 404"""
        from uuid import uuid4
        fake_visit_id = uuid4()

        response = await client.get(f"/api/v1/assessments/visit/{fake_visit_id}/status", headers=auth_headers)

        assert response.status_code == 200  # Status endpoint returns empty status for non-existent visits