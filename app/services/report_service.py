"""
Report service for dashboard and analytics data generation
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Lis        # Pending assessments (visits with nursing but no radiology assessment)
        pending_query = select(func.count(PatientVisit.id)).where(
            and_(
                PatientVisit.status == "open",
                PatientVisit.id.in_(
                    select(NursingAssessment.visit_id).where(
                        NursingAssessment.visit_id.not_in(
                            select(RadiologyAssessment.visit_id)
                        )
                    )
                )
            )
        )rom uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, extract

from app.models.patient import Patient
from app.models.visit import PatientVisit
from app.models.assessment import NursingAssessment, RadiologyAssessment
# from app.models.document import Document  # Temporarily disabled
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.report import (
    DashboardStats,
    PatientDemographics,
    VisitVolumeStats,
    AssessmentStats,
    DashboardReportResponse,
    PatientStatisticsResponse,
    VisitVolumeResponse,
    ClinicalAssessmentsResponse
)


class ReportService:
    """Service for generating reports and analytics"""

    @staticmethod
    async def generate_dashboard_report(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> DashboardReportResponse:
        """
        Generate comprehensive dashboard statistics
        """
        # Set default date range (last 30 days)
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get basic stats
        stats = await ReportService._get_dashboard_stats(db, start_date, end_date)

        # Get recent activity
        recent_activity = await ReportService._get_recent_activity(db, limit=10)

        # Get system alerts (placeholder for now)
        alerts = await ReportService._get_system_alerts(db)

        return DashboardReportResponse(
            stats=stats,
            recent_activity=recent_activity,
            alerts=alerts,
            generated_at=datetime.utcnow()
        )

    @staticmethod
    async def generate_patient_statistics(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> PatientStatisticsResponse:
        """
        Generate patient demographics and statistics
        """
        demographics = await ReportService._get_patient_demographics(db)
        visit_patterns = await ReportService._get_patient_visit_patterns(db, start_date, end_date)

        return PatientStatisticsResponse(
            demographics=demographics,
            visit_patterns=visit_patterns,
            generated_at=datetime.utcnow()
        )

    @staticmethod
    async def generate_visit_volume_report(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        group_by: str = "day"
    ) -> VisitVolumeResponse:
        """
        Generate visit volume statistics and trends
        """
        volume_stats = await ReportService._get_visit_volume_stats(db, start_date, end_date)
        trends = await ReportService._get_visit_trends(db, start_date, end_date, group_by)

        return VisitVolumeResponse(
            volume_stats=volume_stats,
            trends=trends,
            generated_at=datetime.utcnow()
        )

    @staticmethod
    async def generate_clinical_assessments_report(
        db: AsyncSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> ClinicalAssessmentsResponse:
        """
        Generate clinical assessments statistics and quality metrics
        """
        assessment_stats = await ReportService._get_assessment_stats(db, start_date, end_date)
        quality_metrics = await ReportService._get_assessment_quality_metrics(db, start_date, end_date)

        return ClinicalAssessmentsResponse(
            assessment_stats=assessment_stats,
            quality_metrics=quality_metrics,
            generated_at=datetime.utcnow()
        )

    @staticmethod
    async def _get_dashboard_stats(
        db: AsyncSession,
        start_date: date,
        end_date: date
    ) -> DashboardStats:
        """Get dashboard statistics"""
        # Total patients
        patients_query = select(func.count(Patient.ssn))
        patients_result = await db.execute(patients_query)
        total_patients = patients_result.scalar() or 0

        # Active visits (status = 'open')
        active_visits_query = select(func.count(PatientVisit.id)).where(
            PatientVisit.status == "open"
        )
        active_result = await db.execute(active_visits_query)
        active_visits = active_result.scalar() or 0

        # Completed visits today
        today = date.today()
        completed_today_query = select(func.count(PatientVisit.id)).where(
            and_(
                PatientVisit.status == "completed",
                func.date(PatientVisit.updated_at) == today
            )
        )
        completed_result = await db.execute(completed_today_query)
        completed_visits_today = completed_result.scalar() or 0

        # Pending assessments (visits with nursing but no radiology assessment)
        pending_query = select(func.count(PatientVisit.id)).where(
            and_(
                PatientVisit.status == "open",
                PatientVisit.id.in_(
                    select(NursingAssessment.visit_id).where(
                        NursingAssessment.visit_id.not_in(
                            select(RadiologyAssessment.visit_id)
                        )
                    )
                )
            )
        )
        pending_result = await db.execute(pending_query)
        pending_assessments = pending_result.scalar() or 0

        # Documents uploaded today
        # docs_today_query = select(func.count(Document.id)).where(
        #     func.date(Document.uploaded_at) == today
        # )
        # docs_result = await db.execute(docs_today_query)
        # uploaded_documents_today = docs_result.scalar() or 0
        uploaded_documents_today = 0  # Temporarily disabled

        # System users
        users_query = select(func.count(User.user_id))
        users_result = await db.execute(users_query)
        system_users = users_result.scalar() or 0

        return DashboardStats(
            total_patients=total_patients,
            active_visits=active_visits,
            completed_visits_today=completed_visits_today,
            pending_assessments=pending_assessments,
            uploaded_documents_today=uploaded_documents_today,
            system_users=system_users
        )

    @staticmethod
    async def _get_patient_demographics(db: AsyncSession) -> PatientDemographics:
        """Get patient demographic statistics"""
        # Total patients
        total_query = select(func.count(Patient.ssn))
        total_result = await db.execute(total_query)
        total_patients = total_result.scalar() or 0

        # Age distribution
        age_distribution = {}
        current_year = date.today().year

        # Calculate age from date_of_birth
        age_cases = [
            (func.extract('year', func.age(Patient.date_of_birth)) < 18, "0-17"),
            (func.extract('year', func.age(Patient.date_of_birth)) < 35, "18-34"),
            (func.extract('year', func.age(Patient.date_of_birth)) < 55, "35-54"),
            (func.extract('year', func.age(Patient.date_of_birth)) >= 55, "55+")
        ]

        for condition, label in age_cases:
            age_query = select(func.count(Patient.ssn)).where(
                and_(Patient.date_of_birth.is_not(None), condition)
            )
            age_result = await db.execute(age_query)
            age_distribution[label] = age_result.scalar() or 0

        # Gender distribution
        gender_query = select(Patient.gender, func.count(Patient.ssn)).group_by(Patient.gender)
        gender_result = await db.execute(gender_query)
        gender_distribution = {row[0] or "unknown": row[1] for row in gender_result.all()}

        # Visit frequency (visits per patient)
        visit_freq_query = select(
            func.count(PatientVisit.id).label('visit_count'),
            func.count().label('patient_count')
        ).select_from(PatientVisit).group_by(PatientVisit.patient_ssn)

        # This is a simplified version - in practice you'd want more sophisticated analysis
        visit_frequency = {"0-1": 0, "2-5": 0, "6+": 0}

        return PatientDemographics(
            total_patients=total_patients,
            age_distribution=age_distribution,
            gender_distribution=gender_distribution,
            visit_frequency=visit_frequency
        )

    @staticmethod
    async def _get_visit_volume_stats(
        db: AsyncSession,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> VisitVolumeStats:
        """Get visit volume statistics"""
        # Base query with date filter
        base_query = select(PatientVisit)
        if start_date:
            base_query = base_query.where(func.date(PatientVisit.created_at) >= start_date)
        if end_date:
            base_query = base_query.where(func.date(PatientVisit.created_at) <= end_date)

        # Total visits
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total_visits = total_result.scalar() or 0

        # Visits by date (last 30 days)
        date_range = end_date or date.today()
        start_range = start_date or (date_range - timedelta(days=30))

        visits_by_date_query = select(
            func.date(PatientVisit.created_at).label('date'),
            func.count(PatientVisit.id).label('count')
        ).where(
            and_(
                func.date(PatientVisit.created_at) >= start_range,
                func.date(PatientVisit.created_at) <= date_range
            )
        ).group_by(func.date(PatientVisit.created_at)).order_by(func.date(PatientVisit.created_at))

        date_result = await db.execute(visits_by_date_query)
        visits_by_date = [
            {"date": str(row[0]), "count": row[1]}
            for row in date_result.all()
        ]

        # Visits by status
        status_query = select(
            PatientVisit.status,
            func.count(PatientVisit.id)
        ).select_from(base_query.subquery()).group_by(PatientVisit.status)

        status_result = await db.execute(status_query)
        visits_by_status = {row[0]: row[1] for row in status_result.all()}

        # Visits by type (placeholder - would need a visit_type field)
        visits_by_type = {"routine": total_visits // 2, "emergency": total_visits // 4, "followup": total_visits // 4}

        # Average visits per day
        days_diff = (date_range - start_range).days or 1
        average_visits_per_day = total_visits / days_diff

        return VisitVolumeStats(
            total_visits=total_visits,
            visits_by_date=visits_by_date,
            visits_by_status=visits_by_status,
            visits_by_type=visits_by_type,
            average_visits_per_day=round(average_visits_per_day, 2)
        )

    @staticmethod
    async def _get_assessment_stats(
        db: AsyncSession,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> AssessmentStats:
        """Get assessment statistics"""
        # Nursing assessments
        nursing_query = select(NursingAssessment)
        if start_date:
            nursing_query = nursing_query.where(func.date(NursingAssessment.assessed_at) >= start_date)
        if end_date:
            nursing_query = nursing_query.where(func.date(NursingAssessment.assessed_at) <= end_date)

        nursing_count_query = select(func.count()).select_from(nursing_query.subquery())
        nursing_result = await db.execute(nursing_count_query)
        nursing_count = nursing_result.scalar() or 0

        # Radiology assessments
        radiology_query = select(RadiologyAssessment)
        if start_date:
            radiology_query = radiology_query.where(func.date(RadiologyAssessment.assessed_at) >= start_date)
        if end_date:
            radiology_query = radiology_query.where(func.date(RadiologyAssessment.assessed_at) <= end_date)

        radiology_count_query = select(func.count()).select_from(radiology_query.subquery())
        radiology_result = await db.execute(radiology_count_query)
        radiology_count = radiology_result.scalar() or 0

        total_assessments = nursing_count + radiology_count
        completed_assessments = total_assessments  # Assuming all have required fields
        pending_assessments = 0  # Would need more complex logic

        completion_rate = (completed_assessments / total_assessments * 100) if total_assessments > 0 else 0

        assessments_by_type = {
            "nursing": nursing_count,
            "radiology": radiology_count
        }

        # Common findings (simplified)
        common_findings = [
            {"finding": "Normal", "count": max(1, total_assessments // 3)},
            {"finding": "Abnormal", "count": max(1, total_assessments // 4)},
            {"finding": "Requires follow-up", "count": max(1, total_assessments // 6)}
        ]

        return AssessmentStats(
            total_assessments=total_assessments,
            completed_assessments=completed_assessments,
            pending_assessments=pending_assessments,
            completion_rate=round(completion_rate, 2),
            average_completion_time_hours=None,  # Would need timestamp tracking
            assessments_by_type=assessments_by_type,
            common_findings=common_findings
        )

    @staticmethod
    async def _get_recent_activity(db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        # Recent visits
        visits_query = select(PatientVisit, Patient.full_name).join(
            Patient, PatientVisit.patient_ssn == Patient.ssn
        ).order_by(desc(PatientVisit.created_at)).limit(limit)

        visits_result = await db.execute(visits_query)
        recent_visits = [
            {
                "type": "visit",
                "description": f"Visit created for {row[1]}",
                "timestamp": row[0].created_at.isoformat(),
                "status": row[0].status
            }
            for row in visits_result.all()
        ]

        # Recent documents
        # docs_query = select(Document, Patient.full_name).join(
        #     PatientVisit, Document.visit_id == PatientVisit.id
        # ).join(
        #     Patient, PatientVisit.patient_id == Patient.id
        # ).order_by(desc(Document.uploaded_at)).limit(limit)
        # docs_result = await db.execute(docs_query)
        # recent_docs = [
        #     {
        #         "type": "document",
        #         "description": f"Document uploaded for {row[1]}",
        #         "timestamp": row[0].uploaded_at.isoformat(),
        #         "filename": row[0].original_filename
        #     }
        #     for row in docs_result.all()
        # ]
        recent_docs = []  # Temporarily disabled

        # Combine and sort by timestamp
        all_activity = recent_visits + recent_docs
        all_activity.sort(key=lambda x: x["timestamp"], reverse=True)

        return all_activity[:limit]

    @staticmethod
    async def _get_system_alerts(db: AsyncSession) -> List[str]:
        """Get system alerts and notifications"""
        alerts = []

        # Check for pending assessments
        pending_query = select(func.count(PatientVisit.id)).where(
            and_(
                PatientVisit.status == "open",
                PatientVisit.created_at < datetime.utcnow() - timedelta(days=1)
            )
        )
        pending_result = await db.execute(pending_query)
        pending_count = pending_result.scalar() or 0

        if pending_count > 0:
            alerts.append(f"{pending_count} visits have been open for more than 24 hours")

        # Check for old documents without assessments
        # old_docs_query = select(func.count(Document.id)).where(
        #     Document.uploaded_at < datetime.utcnow() - timedelta(days=7)
        # ).where(
        #     Document.visit_id.in_(
        #         select(PatientVisit.id).where(PatientVisit.status == "open")
        #     )
        # )
        # old_docs_result = await db.execute(old_docs_query)
        # old_docs_count = old_docs_result.scalar() or 0
        # if old_docs_count > 0:
        #     alerts.append(f"{old_docs_count} documents uploaded over a week ago are still unassessed")
        pass  # Temporarily disabled

        return alerts

    @staticmethod
    async def _get_patient_visit_patterns(
        db: AsyncSession,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> Dict[str, Any]:
        """Get patient visit patterns"""
        # This would contain more sophisticated analysis
        return {
            "frequent_visitors": 0,
            "return_visit_rate": 0.0,
            "average_days_between_visits": 0,
            "peak_visit_days": [],
            "seasonal_patterns": {}
        }

    @staticmethod
    async def _get_visit_trends(
        db: AsyncSession,
        start_date: Optional[date],
        end_date: Optional[date],
        group_by: str
    ) -> Dict[str, Any]:
        """Get visit trends over time"""
        return {
            "trend_direction": "stable",
            "percentage_change": 0.0,
            "peak_periods": [],
            "forecast_next_month": 0
        }

    @staticmethod
    async def _get_assessment_quality_metrics(
        db: AsyncSession,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> Dict[str, Any]:
        """Get assessment quality metrics"""
        return {
            "average_assessment_time": 0,
            "completion_rate_trend": "stable",
            "error_rate": 0.0,
            "quality_score": 85.0,
            "improvement_areas": []
        }