"""
Assessment API routes for nursing and radiology forms
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.assessment import (
    NursingAssessmentCreate,
    NursingAssessmentResponse,
    NursingAssessmentUpdate,
    RadiologyAssessmentCreate,
    RadiologyAssessmentResponse,
    RadiologyAssessmentUpdate,
)
from app.services.assessment_service import AssessmentService

router = APIRouter()


# Nursing Assessment Routes
@router.post("/nursing/", response_model=NursingAssessmentResponse)
async def create_nursing_assessment(
    assessment: NursingAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new nursing assessment"""
    service = AssessmentService(db)
    try:
        db_assessment = await service.create_nursing_assessment(assessment, current_user.id)
        return NursingAssessmentResponse.from_orm(db_assessment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nursing/{assessment_id}", response_model=NursingAssessmentResponse)
async def get_nursing_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get nursing assessment by ID"""
    service = AssessmentService(db)
    db_assessment = await service.get_nursing_assessment(assessment_id)
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Nursing assessment not found")
    return NursingAssessmentResponse.from_orm(db_assessment)


@router.get("/visit/{visit_id}/nursing", response_model=NursingAssessmentResponse)
async def get_nursing_assessment_by_visit(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get nursing assessment by visit ID"""
    service = AssessmentService(db)
    db_assessment = await service.get_nursing_assessment_by_visit(visit_id)
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Nursing assessment not found for this visit")
    return NursingAssessmentResponse.from_orm(db_assessment)


@router.put("/nursing/{assessment_id}", response_model=NursingAssessmentResponse)
async def update_nursing_assessment(
    assessment_id: UUID,
    assessment_update: NursingAssessmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update nursing assessment"""
    service = AssessmentService(db)
    try:
        db_assessment = await service.update_nursing_assessment(assessment_id, assessment_update, current_user.id)
        if not db_assessment:
            raise HTTPException(status_code=404, detail="Nursing assessment not found")
        return NursingAssessmentResponse.from_orm(db_assessment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Radiology Assessment Routes
@router.post("/radiology/", response_model=RadiologyAssessmentResponse)
async def create_radiology_assessment(
    assessment: RadiologyAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new radiology assessment"""
    service = AssessmentService(db)
    try:
        db_assessment = await service.create_radiology_assessment(assessment, current_user.id)
        return RadiologyAssessmentResponse.from_orm(db_assessment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/radiology/{assessment_id}", response_model=RadiologyAssessmentResponse)
async def get_radiology_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get radiology assessment by ID"""
    service = AssessmentService(db)
    db_assessment = await service.get_radiology_assessment(assessment_id)
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Radiology assessment not found")
    return RadiologyAssessmentResponse.from_orm(db_assessment)


@router.get("/visit/{visit_id}/radiology", response_model=RadiologyAssessmentResponse)
async def get_radiology_assessment_by_visit(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get radiology assessment by visit ID"""
    service = AssessmentService(db)
    db_assessment = await service.get_radiology_assessment_by_visit(visit_id)
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Radiology assessment not found for this visit")
    return RadiologyAssessmentResponse.from_orm(db_assessment)


@router.put("/radiology/{assessment_id}", response_model=RadiologyAssessmentResponse)
async def update_radiology_assessment(
    assessment_id: UUID,
    assessment_update: RadiologyAssessmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update radiology assessment"""
    service = AssessmentService(db)
    try:
        db_assessment = await service.update_radiology_assessment(assessment_id, assessment_update, current_user.id)
        if not db_assessment:
            raise HTTPException(status_code=404, detail="Radiology assessment not found")
        return RadiologyAssessmentResponse.from_orm(db_assessment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Visit Assessment Status Routes
@router.get("/visit/{visit_id}/status")
async def get_visit_assessment_status(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get assessment status for a visit"""
    service = AssessmentService(db)
    status_info = await service.get_visit_assessments(visit_id)
    return {
        "visit_id": visit_id,
        "has_nursing_assessment": status_info["has_nursing"],
        "has_radiology_assessment": status_info["has_radiology"],
        "assessments_complete": status_info["assessments_complete"],
        "can_complete_visit": status_info["assessments_complete"]
    }


@router.get("/visit/{visit_id}/summary")
async def get_visit_assessment_summary(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get assessment summary for a visit"""
    service = AssessmentService(db)
    status_info = await service.get_visit_assessments(visit_id)

    summary = {
        "visit_id": visit_id,
        "assessments_complete": status_info["assessments_complete"],
        "nursing_assessment": None,
        "radiology_assessment": None
    }

    if status_info["nursing_assessment"]:
        nursing = status_info["nursing_assessment"]
        summary["nursing_assessment"] = {
            "id": nursing.id,
            "assessed_at": nursing.assessed_at,
            "has_critical_vitals": nursing.is_critical_vitals,
            "blood_pressure": nursing.blood_pressure_string,
            "temperature": nursing.temperature_celsius,
            "pulse": nursing.pulse_bpm,
            "oxygen_saturation": nursing.oxygen_saturation_percent
        }

    if status_info["radiology_assessment"]:
        radiology = status_info["radiology_assessment"]
        summary["radiology_assessment"] = {
            "id": radiology.id,
            "assessed_at": radiology.assessed_at,
            "modality": radiology.modality,
            "has_diagnosis": radiology.has_diagnosis,
            "findings_summary": radiology.findings_summary
        }

    return summary