"""
Patient API routes
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.services.patient_service import PatientService

router = APIRouter()


@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new patient"""
    service = PatientService(db)
    try:
        db_patient = await service.create_patient(patient, current_user.id)
        return PatientResponse.model_validate(db_patient)
    except ValueError as e:
        # Check if it's a duplicate error
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient by ID"""
    service = PatientService(db)
    db_patient = await service.get_patient(patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.model_validate(db_patient)


@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None, min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patients with optional search"""
    service = PatientService(db)
    if search:
        patients = await service.search_patients(search, skip, limit)
    else:
        # For now, return recent patients if no search
        patients = await service.get_recent_patients(limit)

    return [PatientResponse.model_validate(patient) for patient in patients]


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    patient_update: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update patient information"""
    service = PatientService(db)
    try:
        db_patient = await service.update_patient(patient_id, patient_update, current_user.id)
        if not db_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return PatientResponse.model_validate(db_patient)
    except ValueError as e:
        # Check if it's a duplicate error
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{patient_id}")
async def deactivate_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deactivate a patient (soft delete)"""
    service = PatientService(db)
    success = await service.deactivate_patient(patient_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deactivated successfully"}


@router.get("/search/ssn/{ssn}", response_model=PatientResponse)
async def get_patient_by_ssn(
    ssn: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient by SSN"""
    service = PatientService(db)
    db_patient = await service.get_patient_by_ssn(ssn)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.model_validate(db_patient)


@router.get("/search/mobile/{mobile}", response_model=PatientResponse)
async def get_patient_by_mobile(
    mobile: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get patient by mobile number"""
    service = PatientService(db)
    db_patient = await service.get_patient_by_mobile(mobile)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse.model_validate(db_patient)


@router.get("/stats/count", response_model=dict)
async def get_patients_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get total count of active patients"""
    service = PatientService(db)
    count = await service.get_patients_count()
    return {"total_patients": count}