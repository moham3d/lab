from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.db.init_db import get_db
from app.models import Report, User, PatientVisit
from app.schemas.report_schemas import ReportCreate, ReportUpdate, ReportResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve a list of reports with pagination."""
    result = await db.execute(select(Report).offset(skip).limit(limit))
    reports = result.scalars().all()
    return reports

@router.post("/", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new report for a patient visit."""
    # Check if visit exists
    result = await db.execute(select(PatientVisit).where(PatientVisit.visit_id == report_data.visit_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Visit not found")
    
    # Create report
    report = Report(
        visit_id=report_data.visit_id,
        summary=report_data.summary,
        doctor_notes=report_data.doctor_notes,
        created_by=current_user.user_id
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve a specific report by ID."""
    result = await db.execute(select(Report).where(Report.report_id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: str,
    report_data: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update report information. Requires ownership or admin role."""
    result = await db.execute(select(Report).where(Report.report_id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user can update (owner or admin)
    if current_user.role != "admin" and report.created_by != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update fields
    for field, value in report_data.dict(exclude_unset=True).items():
        setattr(report, field, value)
    
    await db.commit()
    await db.refresh(report)
    return report