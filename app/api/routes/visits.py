from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.init_db import get_db
from app.models import PatientVisit, User
from app.schemas.visit_schemas import VisitCreate, VisitUpdate, VisitResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[VisitResponse])
async def get_visits(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all visits."""
    result = await db.execute(select(PatientVisit).offset(skip).limit(limit))
    visits = result.scalars().all()
    return visits

@router.post("/", response_model=VisitResponse)
async def create_visit(
    visit_data: VisitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new visit."""
    # Check if patient exists
    from app.models import Patient
    result = await db.execute(select(Patient).where(Patient.ssn == visit_data.patient_ssn))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Create visit
    visit = PatientVisit(
        patient_ssn=visit_data.patient_ssn,
        notes=visit_data.notes,
        created_by=current_user.user_id
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
    return visit

@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get visit by ID."""
    result = await db.execute(select(PatientVisit).where(PatientVisit.visit_id == visit_id))
    visit = result.scalar_one_or_none()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.put("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: str,
    visit_data: VisitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update visit."""
    result = await db.execute(select(PatientVisit).where(PatientVisit.visit_id == visit_id))
    visit = result.scalar_one_or_none()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    # Update fields
    for field, value in visit_data.dict(exclude_unset=True).items():
        setattr(visit, field, value)
    
    await db.commit()
    await db.refresh(visit)
    return visit