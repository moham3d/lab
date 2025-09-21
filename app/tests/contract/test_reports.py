"""
Contract tests for reports endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.main import app


@pytest.mark.asyncio
class TestReportsContract:
    """Contract tests for reports endpoints"""

    async def test_get_dashboard_stats_successful(self, client: AsyncClient, auth_headers: dict):
        """Test getting dashboard statistics"""
        response = await client.get("/api/v1/reports/dashboard", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "total_patients" in data
        assert "total_visits" in data
        assert "active_visits" in data
        assert "total_documents" in data
        assert "visit_trends" in data
        assert "assessment_stats" in data

        # Check data types
        assert isinstance(data["total_patients"], int)
        assert isinstance(data["total_visits"], int)
        assert isinstance(data["active_visits"], int)
        assert isinstance(data["total_documents"], int)
        assert isinstance(data["visit_trends"], list)
        assert isinstance(data["assessment_stats"], dict)

    async def test_get_patient_statistics_successful(self, client: AsyncClient, auth_headers: dict):
        """Test getting patient statistics"""
        response = await client.get("/api/v1/reports/patients", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "age_distribution" in data
        assert "gender_distribution" in data
        assert "visit_frequency" in data
        assert "top_conditions" in data

        # Check data types
        assert isinstance(data["age_distribution"], list)
        assert isinstance(data["gender_distribution"], list)
        assert isinstance(data["visit_frequency"], list)
        assert isinstance(data["top_conditions"], list)

    async def test_get_visit_volume_report_successful(self, client: AsyncClient, auth_headers: dict):
        """Test getting visit volume report"""
        # Test with default date range
        response = await client.get("/api/v1/reports/visits/volume", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "daily_visits" in data
        assert "weekly_visits" in data
        assert "monthly_visits" in data
        assert "department_distribution" in data

        # Check data types
        assert isinstance(data["daily_visits"], list)
        assert isinstance(data["weekly_visits"], list)
        assert isinstance(data["monthly_visits"], list)
        assert isinstance(data["department_distribution"], list)

    async def test_get_visit_volume_report_with_date_range(self, client: AsyncClient, auth_headers: dict):
        """Test getting visit volume report with custom date range"""
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        response = await client.get(
            f"/api/v1/reports/visits/volume?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "daily_visits" in data
        assert "weekly_visits" in data
        assert "monthly_visits" in data

    async def test_get_visit_volume_report_invalid_date_range(self, client: AsyncClient, auth_headers: dict):
        """Test visit volume report with invalid date range returns 400"""
        response = await client.get(
            "/api/v1/reports/visits/volume?start_date=2024-12-31&end_date=2024-01-01",
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_get_clinical_assessment_report_successful(self, client: AsyncClient, auth_headers: dict):
        """Test getting clinical assessment report"""
        response = await client.get("/api/v1/reports/assessments/clinical", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "nursing_assessments" in data
        assert "radiology_assessments" in data
        assert "common_findings" in data
        assert "assessment_trends" in data

        # Check data types
        assert isinstance(data["nursing_assessments"], list)
        assert isinstance(data["radiology_assessments"], list)
        assert isinstance(data["common_findings"], list)
        assert isinstance(data["assessment_trends"], list)

    async def test_get_audit_log_report_successful(self, client: AsyncClient, auth_headers: dict):
        """Test getting audit log report"""
        response = await client.get("/api/v1/reports/audit", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "logs" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data

        # Check data types
        assert isinstance(data["logs"], list)
        assert isinstance(data["total_count"], int)
        assert isinstance(data["page"], int)
        assert isinstance(data["page_size"], int)

    async def test_get_audit_log_report_with_filters(self, client: AsyncClient, auth_headers: dict):
        """Test getting audit log report with filters"""
        response = await client.get(
            "/api/v1/reports/audit?action=CREATE_PATIENT&user_id=test-user",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "logs" in data
        assert "total_count" in data

    async def test_get_audit_log_report_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test audit log report pagination"""
        response = await client.get(
            "/api/v1/reports/audit?page=1&page_size=10",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "logs" in data
        assert "total_count" in data
        assert data["page"] == 1
        assert data["page_size"] == 10

    async def test_get_document_report_successful(self, client: AsyncClient, auth_headers: dict):
        """Test getting document report"""
        response = await client.get("/api/v1/reports/documents", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert "total_documents" in data
        assert "document_types" in data
        assert "storage_usage" in data
        assert "recent_uploads" in data

        # Check data types
        assert isinstance(data["total_documents"], int)
        assert isinstance(data["document_types"], list)
        assert isinstance(data["storage_usage"], dict)
        assert isinstance(data["recent_uploads"], list)

    async def test_export_patient_data_successful(self, client: AsyncClient, auth_headers: dict):
        """Test successful patient data export"""
        response = await client.get("/api/v1/reports/export/patients", headers=auth_headers)

        assert response.status_code == 200

        # Check that response has file headers for CSV export
        assert "content-type" in response.headers
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers.get("content-disposition", "")

    async def test_export_visit_data_successful(self, client: AsyncClient, auth_headers: dict):
        """Test successful visit data export"""
        response = await client.get("/api/v1/reports/export/visits", headers=auth_headers)

        assert response.status_code == 200

        # Check that response has file headers for CSV export
        assert "content-type" in response.headers
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers.get("content-disposition", "")

    async def test_export_audit_log_successful(self, client: AsyncClient, auth_headers: dict):
        """Test successful audit log export"""
        response = await client.get("/api/v1/reports/export/audit", headers=auth_headers)

        assert response.status_code == 200

        # Check that response has file headers for CSV export
        assert "content-type" in response.headers
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers.get("content-disposition", "")

    async def test_reports_access_denied_for_non_admin(self, client: AsyncClient, nurse_auth_headers: dict):
        """Test that non-admin users cannot access reports"""
        response = await client.get("/api/v1/reports/dashboard", headers=nurse_auth_headers)

        assert response.status_code == 403

    async def test_export_access_denied_for_non_admin(self, client: AsyncClient, nurse_auth_headers: dict):
        """Test that non-admin users cannot export data"""
        response = await client.get("/api/v1/reports/export/patients", headers=nurse_auth_headers)

        assert response.status_code == 403