"""
Contract tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.core.security import create_access_token


@pytest.mark.asyncio
class TestAuthContract:
    """Contract tests for authentication endpoints"""

    async def test_login_successful(self, client: AsyncClient, test_user: User):
        """Test successful user login returns access and refresh tokens"""
        login_data = {
            "username": test_user.username,
            "password": "testpass123"  # This should match the test user password
        }

        response = await client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        # Verify tokens are strings and not empty
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials returns 401"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }

        response = await client.post("/api/v1/auth/login", json=login_data)

        # Debug: print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
        assert "Incorrect username or password" in data["detail"]

    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing required fields returns 422"""
        # Missing password
        login_data = {"username": "testuser"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 422

        # Missing username
        login_data = {"password": "testpass"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 422

    async def test_refresh_token_successful(self, client: AsyncClient, test_user: User):
        """Test successful token refresh"""
        # First login to get tokens
        login_data = {"username": test_user.username, "password": "testpass123"}
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]

        # Now refresh the token
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        # Verify new access token is different from original
        original_token = login_response.json()["access_token"]
        assert data["access_token"] != original_token

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token returns 401"""
        refresh_data = {"refresh_token": "invalid_token"}

        response = await client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 401

        data = response.json()
        assert "detail" in data

    async def test_refresh_token_missing(self, client: AsyncClient):
        """Test refresh with missing token returns 422"""
        refresh_data = {}

        response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == 422

    async def test_protected_endpoint_requires_auth(self, client: AsyncClient):
        """Test that protected endpoints require authentication"""
        response = await client.get("/api/v1/patients/")

        assert response.status_code == 401

        data = response.json()
        assert "detail" in data

    async def test_protected_endpoint_with_valid_token(self, client: AsyncClient, test_user: User, auth_headers: dict):
        """Test that protected endpoints work with valid authentication"""
        response = await client.get("/api/v1/patients/", headers=auth_headers)

        # Should return 200 (even if no patients exist)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)  # Should return a list of patients