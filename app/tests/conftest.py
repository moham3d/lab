"""
Test configuration and fixtures for contract tests
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import AsyncGenerator

from app.main import app
from app.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.patient import Patient
from app.models.visit import PatientVisit
from app.models.document import Document
from app.models.assessment import NursingAssessment, RadiologyAssessment
from app.core.security import create_access_token, get_password_hash


# Test database setup
test_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Event loop is handled automatically by pytest-asyncio


@pytest.fixture(scope="function")
async def test_db():
    """Create test database tables"""
    from app.models import Base
    import asyncio

    # Create a separate engine for this test to avoid connection sharing
    test_engine_local = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True
    )

    try:
        # Use a separate connection for schema operations
        async with test_engine_local.begin() as conn:
            # Drop tables first to ensure clean state
            await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
            # Create tables
            await conn.run_sync(Base.metadata.create_all, checkfirst=False)

        yield test_engine_local

    finally:
        # Clean up the engine after test
        await test_engine_local.dispose()


@pytest.fixture(scope="function")
async def db_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Get database session for tests"""
    # Create a new session for each test using the test-specific engine
    TestingSessionLocal_test = sessionmaker(
        test_db,
        class_=AsyncSession,
        expire_on_commit=False
    )

    session = TestingSessionLocal_test()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Get test client with database session"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://localhost") as client:
        yield client


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create test user"""
    from app.models.user import UserRole

    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True
    )
    user.hashed_password = get_password_hash("testpass123")

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def nurse_user(db_session: AsyncSession) -> User:
    """Create test nurse user"""
    from app.models.user import UserRole

    user = User(
        username="testnurse",
        email="nurse@example.com",
        first_name="Test",
        last_name="Nurse",
        role=UserRole.NURSE,
        is_active=True
    )
    user.hashed_password = get_password_hash("testpass123")

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Get authentication headers for admin user"""
    access_token = create_access_token(subject=test_user.username)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def nurse_auth_headers(nurse_user: User) -> dict:
    """Get authentication headers for nurse user"""
    access_token = create_access_token(subject=nurse_user.username)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def test_patient(db_session: AsyncSession) -> Patient:
    """Create test patient"""
    from app.models.patient import Gender
    from datetime import date

    patient = Patient(
        full_name="John Doe",
        ssn="12345678901234",  # 14-digit Egyptian SSN
        mobile_number="01234567890",  # Valid Egyptian mobile format (Orange)
        phone_number="01112345678",  # Valid Egyptian phone format (Etisalat)
        medical_number="MED123456",
        date_of_birth=date(1980, 1, 1),  # Use proper date object
        gender=Gender.MALE,
        is_active=True
    )

    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)

    return patient


@pytest.fixture
async def test_visit(db_session: AsyncSession, test_patient: Patient, test_user: User) -> PatientVisit:
    """Create test visit"""
    from app.models.visit import PatientVisit, VisitStatus
    from datetime import datetime

    visit = PatientVisit(
        patient_id=test_patient.id,
        visit_date=datetime.now(),
        chief_complaint="Chest pain",
        status=VisitStatus.OPEN,
        notes="Initial assessment needed",
        created_by=test_user.id,
        updated_by=test_user.id
    )

    db_session.add(visit)
    await db_session.commit()
    await db_session.refresh(visit)

    return visit


@pytest.fixture
async def test_document(db_session: AsyncSession, test_visit: PatientVisit, test_user: User) -> Document:
    """Create test document"""
    from app.models.document import DocumentType
    from app.utils.file_handler import FileHandler
    import os

    document = Document(
        visit_id=test_visit.id,
        filename="test_lab_result.pdf",
        original_filename="lab_result.pdf",
        file_path="/uploads/test_lab_result.pdf",  # Add required file_path
        mime_type="application/pdf",
        file_size=1024,
        document_type=DocumentType.LAB_RESULT,
        title="Test Lab Result",
        uploaded_by=test_user.id  # Use user ID instead of username
    )

    db_session.add(document)
    await db_session.commit()
    await db_session.refresh(document)

    # Create the actual file on disk for download tests
    file_path = FileHandler.get_file_path(document.filename, str(test_visit.id))
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write some test content to the file
    with open(file_path, "wb") as f:
        f.write(b"Test PDF content for download test")

    return document


@pytest.fixture
async def test_nursing_assessment(db_session: AsyncSession, test_visit: PatientVisit, test_user: User) -> NursingAssessment:
    """Create test nursing assessment"""
    assessment = NursingAssessment(
        visit_id=test_visit.id,
        temperature_celsius=37.5,
        pulse_bpm=80,
        blood_pressure_systolic=140,
        blood_pressure_diastolic=90,
        respiratory_rate_per_min=16,
        oxygen_saturation_percent=98.0,
        pain_assessment="Chest pain assessment",
        fall_risk_assessment="Low fall risk",
        weight_kg=75.0,
        height_cm=175.0,
        general_condition="Alert and oriented",
        consciousness_level="Conscious",
        skin_condition="Normal skin condition",
        mobility_status="Mobile",
        notes="Patient reports chest pain",
        assessed_by=test_user.id
    )

    db_session.add(assessment)
    await db_session.commit()
    await db_session.refresh(assessment)

    return assessment


@pytest.fixture
async def test_radiology_assessment(db_session: AsyncSession, test_visit: PatientVisit, test_user: User) -> RadiologyAssessment:
    """Create test radiology assessment"""
    assessment = RadiologyAssessment(
        visit_id=test_visit.id,
        findings="Normal cardiac silhouette, clear lung fields",
        diagnosis="No acute cardiopulmonary abnormality",
        recommendations="Clinical correlation recommended",
        modality="Chest X-ray",
        body_region="Chest",
        contrast_used="None",
        assessed_by=test_user.id
    )

    db_session.add(assessment)
    await db_session.commit()
    await db_session.refresh(assessment)

    return assessment