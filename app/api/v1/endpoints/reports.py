"""
Reports API routes for dashboard and analytics
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.report import (
    DashboardReportResponse,
    PatientStatisticsResponse,
    VisitVolumeResponse,
    ClinicalAssessmentsResponse,
    DashboardRequest,
    PatientStatsRequest,
    VisitVolumeRequest,
    AssessmentReportRequest
)
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardReportResponse)
async def get_dashboard_report(
    request: DashboardRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics and recent activity
    """
    try:
        # Check if user has admin access (for now, allow all authenticated users)
        # TODO: Add role-based access control for admin-only reports

        report = await ReportService.generate_dashboard_report(
            db=db,
            start_date=request.start_date,
            end_date=request.end_date
        )

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard report: {str(e)}")


@router.get("/patients/statistics", response_model=PatientStatisticsResponse)
async def get_patient_statistics(
    request: PatientStatsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get patient demographics and statistics
    """
    try:
        # Check admin access
        if current_user.role not in ["admin", "physician"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        report = await ReportService.generate_patient_statistics(
            db=db,
            start_date=request.start_date,
            end_date=request.end_date
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate patient statistics: {str(e)}")


@router.get("/visits/volume", response_model=VisitVolumeResponse)
async def get_visit_volume_report(
    group_by: str = Query("day", description="Group by: day, week, month"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get visit volume statistics and trends
    """
    try:
        # Check admin access
        if current_user.role not in ["admin", "physician"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # Validate group_by parameter
        if group_by not in ["day", "week", "month"]:
            raise HTTPException(status_code=400, detail="Invalid group_by parameter")

        report = await ReportService.generate_visit_volume_report(
            db=db,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate visit volume report: {str(e)}")


@router.get("/clinical/assessments", response_model=ClinicalAssessmentsResponse)
async def get_clinical_assessments_report(
    request: AssessmentReportRequest = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get clinical assessments statistics and quality metrics
    """
    try:
        # Check admin access
        if current_user.role not in ["admin", "physician"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        report = await ReportService.generate_clinical_assessments_report(
            db=db,
            start_date=request.start_date,
            end_date=request.end_date
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate clinical assessments report: {str(e)}")


# Additional utility endpoints for report generation

@router.post("/generate/{report_type}")
async def generate_custom_report(
    report_type: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("json", description="Output format: json, csv, pdf"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a custom report (placeholder for future implementation)
    """
    try:
        # Check admin access
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Validate report type
        valid_types = ["dashboard", "patients", "visits", "assessments"]
        if report_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid report type. Valid types: {', '.join(valid_types)}")

        # Validate format
        valid_formats = ["json", "csv", "pdf"]
        if format not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Invalid format. Valid formats: {', '.join(valid_formats)}")

        # For now, return a placeholder response
        # In a real implementation, this would queue a background task
        return {
            "message": f"Report generation started for type: {report_type}",
            "format": format,
            "status": "queued",
            "estimated_completion": "2025-09-21T15:30:00Z"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/list")
async def list_available_reports(
    current_user: User = Depends(get_current_user)
):
    """
    List all available report types and their descriptions
    """
    try:
        # Check admin access
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        reports = [
            {
                "type": "dashboard",
                "name": "Dashboard Report",
                "description": "Comprehensive overview of system statistics and recent activity",
                "access_level": "user"
            },
            {
                "type": "patients",
                "name": "Patient Statistics",
                "description": "Patient demographics, visit patterns, and statistics",
                "access_level": "admin"
            },
            {
                "type": "visits",
                "name": "Visit Volume Report",
                "description": "Visit volume statistics, trends, and patterns over time",
                "access_level": "admin"
            },
            {
                "type": "assessments",
                "name": "Clinical Assessments Report",
                "description": "Assessment completion rates, quality metrics, and findings",
                "access_level": "admin"
            }
        ]

        return {
            "reports": reports,
            "total_count": len(reports)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")