"""
Visit API routes
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.visit import VisitCreate, VisitResponse, VisitSummary, VisitUpdate, VisitStatus
from app.services.visit_service import VisitService

router = APIRouter()


@router.post("/", response_model=VisitResponse)
async def create_visit(
    visit: VisitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new patient visit"""
    service = VisitService(db)
    try:
        db_visit = await service.create_visit(visit, current_user.id)
        return VisitResponse.from_orm(db_visit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get visit by ID"""
    service = VisitService(db)
    db_visit = await service.get_visit(visit_id)
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return VisitResponse.from_orm(db_visit)


@router.get("/", response_model=List[VisitSummary])
async def get_visits(
    patient_id: UUID = Query(None),
    status: VisitStatus = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get visits with optional filters"""
    service = VisitService(db)

    if patient_id:
        visits = await service.get_patient_visits(patient_id, skip, limit)
    elif status:
        visits = await service.get_visits_by_status(status, skip, limit)
    else:
        visits = await service.get_recent_visits(limit)

    # Convert to summary format
    summaries = []
    for visit in visits:
        summary = VisitSummary(
            id=visit.id,
            patient_id=visit.patient_id,
            patient_name=visit.patient.full_name if visit.patient else "Unknown",
            visit_date=visit.visit_date,
            status=visit.status,
            chief_complaint=visit.chief_complaint,
            created_at=visit.created_at
        )
        summaries.append(summary)

    return summaries


@router.put("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: UUID,
    visit_update: VisitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update visit information"""
    service = VisitService(db)
    try:
        db_visit = await service.update_visit(visit_id, visit_update, current_user.id)
        if not db_visit:
            raise HTTPException(status_code=404, detail="Visit not found")
        return VisitResponse.from_orm(db_visit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{visit_id}/complete", response_model=VisitResponse)
async def complete_visit(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark visit as completed"""
    service = VisitService(db)
    db_visit = await service.complete_visit(visit_id, current_user.id)
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return VisitResponse.from_orm(db_visit)


@router.post("/{visit_id}/cancel", response_model=VisitResponse)
async def cancel_visit(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a visit"""
    service = VisitService(db)
    db_visit = await service.cancel_visit(visit_id, current_user.id)
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return VisitResponse.from_orm(db_visit)


@router.post("/{visit_id}/reopen", response_model=VisitResponse)
async def reopen_visit(
    visit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reopen a completed visit (admin only)"""
    # TODO: Add admin role check
    service = VisitService(db)
    try:
        db_visit = await service.reopen_visit(visit_id, current_user.id)
        if not db_visit:
            raise HTTPException(status_code=404, detail="Visit not found")
        return VisitResponse.from_orm(db_visit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/open-count", response_model=dict)
async def get_open_visits_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get count of open visits"""
    service = VisitService(db)
    count = await service.get_open_visits_count()
    return {"open_visits": count}


@router.get("/today/list", response_model=List[VisitSummary])
async def get_today_visits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get visits scheduled for today"""
    service = VisitService(db)
    visits = await service.get_today_visits()

    # Convert to summary format
    summaries = []
    for visit in visits:
        summary = VisitSummary(
            id=visit.id,
            patient_id=visit.patient_id,
            patient_name=visit.patient.full_name if visit.patient else "Unknown",
            visit_date=visit.visit_date,
            status=visit.status,
            chief_complaint=visit.chief_complaint,
            created_at=visit.created_at
        )
        summaries.append(summary)

    return summaries