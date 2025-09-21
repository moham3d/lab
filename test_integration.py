import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.init_db import Base
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost/test_db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
async def test_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(test_db):
    """Test client."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest.mark.asyncio
async def test_register_and_login(client):
    """Test user registration and login."""
    # Register
    response = await client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "nurse",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    # Login
    response = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]

    return token

@pytest.mark.asyncio
async def test_create_patient(client):
    """Test creating a patient."""
    token = await test_register_and_login(client)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/api/v1/patients/", json={
        "ssn": "12345678901234",
        "mobile_number": "01234567890",
        "full_name": "John Doe",
        "date_of_birth": "1980-01-01",
        "gender": "male",
        "address": "123 Main St"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ssn"] == "12345678901234"

@pytest.mark.asyncio
async def test_create_visit(client):
    """Test creating a visit."""
    token = await test_register_and_login(client)
    
    # First create patient
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/v1/patients/", json={
        "ssn": "12345678901234",
        "mobile_number": "01234567890",
        "full_name": "John Doe"
    }, headers=headers)
    
    # Create visit
    response = await client.post("/api/v1/visits/", json={
        "patient_ssn": "12345678901234",
        "notes": "Initial visit"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["patient_ssn"] == "12345678901234"

@pytest.mark.asyncio
async def test_create_form(client):
    """Test creating a form."""
    token = await test_register_and_login(client)
    
    headers = {"Authorization": f"Bearer {token}"}
    # Create patient and visit first
    await client.post("/api/v1/patients/", json={
        "ssn": "12345678901234",
        "mobile_number": "01234567890",
        "full_name": "John Doe"
    }, headers=headers)
    
    visit_response = await client.post("/api/v1/visits/", json={
        "patient_ssn": "12345678901234"
    }, headers=headers)
    visit_id = visit_response.json()["visit_id"]
    
    # Create check-eval form
    response = await client.post("/api/v1/forms/check-eval", json={
        "visit_id": visit_id,
        "temperature_celsius": 36.5,
        "pulse_bpm": 72
    }, headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_report(client):
    """Test creating a report."""
    token = await test_register_and_login(client)
    
    headers = {"Authorization": f"Bearer {token}"}
    # Create patient and visit
    await client.post("/api/v1/patients/", json={
        "ssn": "12345678901234",
        "mobile_number": "01234567890",
        "full_name": "John Doe"
    }, headers=headers)
    
    visit_response = await client.post("/api/v1/visits/", json={
        "patient_ssn": "12345678901234"
    }, headers=headers)
    visit_id = visit_response.json()["visit_id"]
    
    # Create report
    response = await client.post("/api/v1/reports/", json={
        "visit_id": visit_id,
        "summary": "Patient stable",
        "doctor_notes": "Follow up"
    }, headers=headers)
    assert response.status_code == 200