from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta
from app.db.init_db import get_db
from app.models import PatientVisit, Patient, User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics for the current user."""
    try:
        # Get total patients count
        total_patients_result = await db.execute(select(func.count(Patient.patient_id)))
        total_patients = total_patients_result.scalar()

        # Get today's visits count
        today = datetime.utcnow().date()
        today_visits_result = await db.execute(
            select(func.count(PatientVisit.visit_id)).where(
                func.date(PatientVisit.created_at) == today
            )
        )
        today_visits = today_visits_result.scalar()

        # Get pending assessments (visits that are in progress)
        pending_assessments_result = await db.execute(
            select(func.count(PatientVisit.visit_id)).where(
                PatientVisit.visit_status == 'in_progress'
            )
        )
        pending_assessments = pending_assessments_result.scalar()

        # Get this week's visits count
        week_start = datetime.utcnow() - timedelta(days=7)
        week_visits_result = await db.execute(
            select(func.count(PatientVisit.visit_id)).where(
                PatientVisit.created_at >= week_start
            )
        )
        week_visits = week_visits_result.scalar()

        return {
            "totalPatients": total_patients or 0,
            "todayVisits": today_visits or 0,
            "pendingAssessments": pending_assessments or 0,
            "weekVisits": week_visits or 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/activity", response_model=list)
async def get_recent_activity(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent activity for the dashboard."""
    try:
        # Get recent visits with patient info
        result = await db.execute(
            select(
                PatientVisit.visit_id,
                PatientVisit.status,
                PatientVisit.created_at,
                Patient.full_name,
                Patient.ssn
            ).join(
                Patient, PatientVisit.patient_ssn == Patient.ssn
            ).order_by(
                PatientVisit.created_at.desc()
            ).limit(limit)
        )

        activities = []
        for row in result:
            activities.append({
                "id": str(row.visit_id),
                "type": "visit",
                "description": f"Visit for patient {row.full_name}",
                "status": row.visit_status,
                "timestamp": row.created_at.isoformat(),
                "patient_ssn": row.ssn
            })

        return activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent activity: {str(e)}")