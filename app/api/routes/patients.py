from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.init_db import get_db
from app.models import Patient, User
from app.schemas.patient_schemas import PatientCreate, PatientUpdate, PatientResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/search", response_model=List[PatientResponse])
async def search_patients(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search patients by SSN or name."""
    result = await db.execute(
        select(Patient).where(
            (Patient.ssn.contains(q)) | (Patient.full_name.ilike(f"%{q}%"))
        ).limit(10)
    )
    patients = result.scalars().all()
    return patients

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new patient record with SSN, name, contact info, etc."""
    # Check if patient exists
    result = await db.execute(select(Patient).where(Patient.ssn == patient_data.ssn))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Patient with this SSN already exists")
    
    # Create patient
    patient = Patient(
        ssn=patient_data.ssn,
        mobile_number=patient_data.mobile_number,
        full_name=patient_data.full_name,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        address=patient_data.address,
        created_by=current_user.user_id
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient

@router.get("/{ssn}", response_model=PatientResponse)
async def get_patient(
    ssn: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve a specific patient by SSN."""
    result = await db.execute(select(Patient).where(Patient.ssn == ssn))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{ssn}", response_model=PatientResponse)
async def update_patient(
    ssn: str,
    patient_data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update patient information."""
    result = await db.execute(select(Patient).where(Patient.ssn == ssn))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update fields
    for field, value in patient_data.dict(exclude_unset=True).items():
        setattr(patient, field, value)
    
    await db.commit()
    await db.refresh(patient)
    return patient