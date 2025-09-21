from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.init_db import get_db
from app.models import NursingAssessment, RadiologyAssessment, User, FormDefinition, FormSubmission, PatientVisit
from app.schemas.form_schemas import (
    CheckEvalCreate, CheckEvalUpdate, CheckEvalResponse,
    GeneralSheetCreate, GeneralSheetUpdate, GeneralSheetResponse
)
from app.api.deps import get_current_user

router = APIRouter()

# Check-Eval endpoints
@router.post("/check-eval", response_model=CheckEvalResponse)
async def create_check_eval(
    form_data: CheckEvalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create Check-Eval form."""
    # Check if visit exists
    result = await db.execute(select(PatientVisit).where(PatientVisit.visit_id == form_data.visit_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Visit not found")
    
    # Get form definition
    result = await db.execute(select(FormDefinition).where(FormDefinition.form_code == 'SH.MR.FRM.05'))
    form_def = result.scalar_one_or_none()
    if not form_def:
        raise HTTPException(status_code=404, detail="Form definition not found")
    
    # Create submission
    submission = FormSubmission(
        visit_id=form_data.visit_id,
        form_id=form_def.form_id,
        submitted_by=current_user.user_id
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    # Create assessment
    form = NursingAssessment(submission_id=submission.submission_id, assessed_by=current_user.user_id)
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form

@router.get("/check-eval/{visit_id}", response_model=CheckEvalResponse)
async def get_check_eval(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Check-Eval form by visit ID."""
    result = await db.execute(
        select(NursingAssessment).join(FormSubmission).where(FormSubmission.visit_id == visit_id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Check-Eval form not found")
    return form

@router.put("/check-eval/{visit_id}", response_model=CheckEvalResponse)
async def update_check_eval(
    visit_id: str,
    form_data: CheckEvalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update Check-Eval form."""
    result = await db.execute(
        select(NursingAssessment).join(FormSubmission).where(FormSubmission.visit_id == visit_id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="Check-Eval form not found")
    
    for field, value in form_data.dict(exclude_unset=True).items():
        setattr(form, field, value)
    
    await db.commit()
    await db.refresh(form)
    return form

# General Sheet endpoints
@router.post("/general-sheet", response_model=GeneralSheetResponse)
async def create_general_sheet(
    form_data: GeneralSheetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create General Sheet form."""
    result = await db.execute(select(PatientVisit).where(PatientVisit.visit_id == form_data.visit_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Visit not found")
    
    result = await db.execute(select(FormDefinition).where(FormDefinition.form_code == 'SH.MR.FRM.04'))
    form_def = result.scalar_one_or_none()
    if not form_def:
        raise HTTPException(status_code=404, detail="Form definition not found")
    
    submission = FormSubmission(
        visit_id=form_data.visit_id,
        form_id=form_def.form_id,
        submitted_by=current_user.user_id
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    form = RadiologyAssessment(submission_id=submission.submission_id, assessed_by=current_user.user_id)
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form

@router.get("/general-sheet/{visit_id}", response_model=GeneralSheetResponse)
async def get_general_sheet(
    visit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get General Sheet form by visit ID."""
    result = await db.execute(
        select(RadiologyAssessment).join(FormSubmission).where(FormSubmission.visit_id == visit_id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="General Sheet form not found")
    return form

@router.put("/general-sheet/{visit_id}", response_model=GeneralSheetResponse)
async def update_general_sheet(
    visit_id: str,
    form_data: GeneralSheetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update General Sheet form."""
    result = await db.execute(
        select(RadiologyAssessment).join(FormSubmission).where(FormSubmission.visit_id == visit_id)
    )
    form = result.scalar_one_or_none()
    if not form:
        raise HTTPException(status_code=404, detail="General Sheet form not found")
    
    for field, value in form_data.dict(exclude_unset=True).items():
        setattr(form, field, value)
    
    await db.commit()
    await db.refresh(form)
    return form