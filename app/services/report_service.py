""""""

Report service for dashboard and analytics data generationReport service for dashboard and analytics data generation

""""""



from datetime import datetime, date, timedeltafrom datetime import datetime, date, timedelta

from typing import Dict, Any, List, Optionalfrom typing import Dict, Any, Lis        # Pending assessments (visits with nursing but no radiology assessment)

from uuid import UUID        pending_query = select(func.count(PatientVisit.id)).where(

            and_(

from sqlalchemy.ext.asyncio import AsyncSession                PatientVisit.status == "open",

from sqlalchemy import select, func, and_, or_, desc, extract                PatientVisit.id.in_(

                    select(NursingAssessment.visit_id).where(

from app.models.patient import Patient                        NursingAssessment.visit_id.not_in(

from app.models.visit import PatientVisit                            select(RadiologyAssessment.visit_id)

from app.models.assessment import NursingAssessment, RadiologyAssessment                        )

# from app.models.document import Document  # Temporarily disabled                    )

from app.models.user import User                )

from app.models.audit import AuditLog            )

from app.schemas.report import (        )rom uuid import UUID

    DashboardStats,

    PatientDemographics,from sqlalchemy.ext.asyncio import AsyncSession

    VisitVolumeStats,from sqlalchemy import select, func, and_, or_, desc, extract

    AssessmentStats,

    DashboardReportResponse,from app.models.patient import Patient

    PatientStatisticsResponse,from app.models.visit import PatientVisit

    VisitVolumeResponse,from app.models.assessment import NursingAssessment, RadiologyAssessment

    ClinicalAssessmentsResponse# from app.models.document import Document  # Temporarily disabled

)from app.models.user import User

from app.models.audit import AuditLog

from app.schemas.report import (

class ReportService:    DashboardStats,

    """Service for generating reports and analytics"""    PatientDemographics,

    VisitVolumeStats,

    @staticmethod    AssessmentStats,

    async def generate_dashboard_report(    DashboardReportResponse,

        db: AsyncSession,    PatientStatisticsResponse,

        start_date: Optional[date] = None,    VisitVolumeResponse,

        end_date: Optional[date] = None    ClinicalAssessmentsResponse

    ) -> DashboardReportResponse:)

        """

        Generate comprehensive dashboard statistics

        """class ReportService:

        # Set default date range (last 30 days)    """Service for generating reports and analytics"""

        if not end_date:

            end_date = date.today()    @staticmethod

        if not start_date:    async def generate_dashboard_report(

            start_date = end_date - timedelta(days=30)        db: AsyncSession,

        start_date: Optional[date] = None,

        # Get basic stats        end_date: Optional[date] = None

        stats = await ReportService._get_dashboard_stats(db, start_date, end_date)    ) -> DashboardReportResponse:

        """

        # Get recent activity        Generate comprehensive dashboard statistics

        recent_activity = await ReportService._get_recent_activity(db, limit=10)        """

        # Set default date range (last 30 days)

        # Get system alerts (placeholder for now)        if not end_date:

        alerts = await ReportService._get_system_alerts(db)            end_date = date.today()

        if not start_date:

        return DashboardReportResponse(            start_date = end_date - timedelta(days=30)

            stats=stats,

            recent_activity=recent_activity,        # Get basic stats

            alerts=alerts,        stats = await ReportService._get_dashboard_stats(db, start_date, end_date)

            generated_at=datetime.utcnow()

        )        # Get recent activity

        recent_activity = await ReportService._get_recent_activity(db, limit=10)

    @staticmethod

    async def generate_patient_statistics(        # Get system alerts (placeholder for now)

        db: AsyncSession,        alerts = await ReportService._get_system_alerts(db)

        start_date: Optional[date] = None,

        end_date: Optional[date] = None        return DashboardReportResponse(

    ) -> PatientStatisticsResponse:            stats=stats,

        """            recent_activity=recent_activity,

        Generate patient demographics and statistics            alerts=alerts,

        """            generated_at=datetime.utcnow()

        demographics = await ReportService._get_patient_demographics(db)        )

        visit_patterns = await ReportService._get_patient_visit_patterns(db, start_date, end_date)

    @staticmethod

        return PatientStatisticsResponse(    async def generate_patient_statistics(

            demographics=demographics,        db: AsyncSession,

            visit_patterns=visit_patterns,        start_date: Optional[date] = None,

            generated_at=datetime.utcnow()        end_date: Optional[date] = None

        )    ) -> PatientStatisticsResponse:

        """

    @staticmethod        Generate patient demographics and statistics

    async def generate_visit_volume_report(        """

        db: AsyncSession,        demographics = await ReportService._get_patient_demographics(db)

        start_date: Optional[date] = None,        visit_patterns = await ReportService._get_patient_visit_patterns(db, start_date, end_date)

        end_date: Optional[date] = None,

        group_by: str = "day"        return PatientStatisticsResponse(

    ) -> VisitVolumeResponse:            demographics=demographics,

        """            visit_patterns=visit_patterns,

        Generate visit volume statistics and trends            generated_at=datetime.utcnow()

        """        )

        volume_stats = await ReportService._get_visit_volume_stats(db, start_date, end_date)

        trends = await ReportService._get_visit_trends(db, start_date, end_date, group_by)    @staticmethod

    async def generate_visit_volume_report(

        return VisitVolumeResponse(        db: AsyncSession,

            volume_stats=volume_stats,        start_date: Optional[date] = None,

            trends=trends,        end_date: Optional[date] = None,

            generated_at=datetime.utcnow()        group_by: str = "day"

        )    ) -> VisitVolumeResponse:

        """

    @staticmethod        Generate visit volume statistics and trends

    async def generate_clinical_assessments_report(        """

        db: AsyncSession,        volume_stats = await ReportService._get_visit_volume_stats(db, start_date, end_date)

        start_date: Optional[date] = None,        trends = await ReportService._get_visit_trends(db, start_date, end_date, group_by)

        end_date: Optional[date] = None

    ) -> ClinicalAssessmentsResponse:        return VisitVolumeResponse(

        """            volume_stats=volume_stats,

        Generate clinical assessments statistics and quality metrics            trends=trends,

        """            generated_at=datetime.utcnow()

        assessment_stats = await ReportService._get_assessment_stats(db, start_date, end_date)        )

        quality_metrics = await ReportService._get_assessment_quality_metrics(db, start_date, end_date)

    @staticmethod

        return ClinicalAssessmentsResponse(    async def generate_clinical_assessments_report(

            assessment_stats=assessment_stats,        db: AsyncSession,

            quality_metrics=quality_metrics,        start_date: Optional[date] = None,

            generated_at=datetime.utcnow()        end_date: Optional[date] = None

        )    ) -> ClinicalAssessmentsResponse:

        """

    @staticmethod        Generate clinical assessments statistics and quality metrics

    async def _get_dashboard_stats(        """

        db: AsyncSession,        assessment_stats = await ReportService._get_assessment_stats(db, start_date, end_date)

        start_date: date,        quality_metrics = await ReportService._get_assessment_quality_metrics(db, start_date, end_date)

        end_date: date

    ) -> DashboardStats:        return ClinicalAssessmentsResponse(

        """Get dashboard statistics"""            assessment_stats=assessment_stats,

        # Total patients            quality_metrics=quality_metrics,

        patients_query = select(func.count(Patient.id))            generated_at=datetime.utcnow()

        patients_result = await db.execute(patients_query)        )

        total_patients = patients_result.scalar() or 0

    @staticmethod

        # Active visits (status = 'open')    async def _get_dashboard_stats(

        active_visits_query = select(func.count(PatientVisit.id)).where(        db: AsyncSession,

            PatientVisit.status == "open"        start_date: date,

        )        end_date: date

        active_result = await db.execute(active_visits_query)    ) -> DashboardStats:

        active_visits = active_result.scalar() or 0        """Get dashboard statistics"""

        # Total patients

        # Completed visits today        patients_query = select(func.count(Patient.ssn))

        today = date.today()        patients_result = await db.execute(patients_query)

        completed_today_query = select(func.count(PatientVisit.id)).where(        total_patients = patients_result.scalar() or 0

            and_(

                PatientVisit.status == "completed",        # Active visits (status = 'open')

                func.date(PatientVisit.updated_at) == today        active_visits_query = select(func.count(PatientVisit.id)).where(

            )            PatientVisit.status == "open"

        )        )

        completed_result = await db.execute(completed_today_query)        active_result = await db.execute(active_visits_query)

        completed_visits_today = completed_result.scalar() or 0        active_visits = active_result.scalar() or 0



        # Pending assessments (visits with nursing but no radiology assessment)        # Completed visits today

        pending_query = select(func.count(PatientVisit.id)).where(        today = date.today()

            and_(        completed_today_query = select(func.count(PatientVisit.id)).where(

                PatientVisit.status == "open",            and_(

                PatientVisit.id.in_(                PatientVisit.status == "completed",

                    select(NursingAssessment.visit_id).where(                func.date(PatientVisit.updated_at) == today

                        NursingAssessment.visit_id.not_in(            )

                            select(RadiologyAssessment.visit_id)        )

                        )        completed_result = await db.execute(completed_today_query)

                    )        completed_visits_today = completed_result.scalar() or 0

                )

            )        # Pending assessments (visits with nursing but no radiology assessment)

        )        pending_query = select(func.count(PatientVisit.id)).where(

        pending_result = await db.execute(pending_query)            and_(

        pending_assessments = pending_result.scalar() or 0                PatientVisit.status == "open",

                PatientVisit.id.in_(

        # Documents uploaded today                    select(NursingAssessment.visit_id).where(

        # docs_today_query = select(func.count(Document.id)).where(                        NursingAssessment.visit_id.not_in(

        #     func.date(Document.uploaded_at) == today                            select(RadiologyAssessment.visit_id)

        # )                        )

        # docs_result = await db.execute(docs_today_query)                    )

        # uploaded_documents_today = docs_result.scalar() or 0                )

        uploaded_documents_today = 0  # Temporarily disabled            )

        )

        # System users        pending_result = await db.execute(pending_query)

        users_query = select(func.count(User.user_id))        pending_assessments = pending_result.scalar() or 0

        users_result = await db.execute(users_query)

        system_users = users_result.scalar() or 0        # Documents uploaded today

        # docs_today_query = select(func.count(Document.id)).where(

        return DashboardStats(        #     func.date(Document.uploaded_at) == today

            total_patients=total_patients,        # )

            active_visits=active_visits,        # docs_result = await db.execute(docs_today_query)

            completed_visits_today=completed_visits_today,        # uploaded_documents_today = docs_result.scalar() or 0

            pending_assessments=pending_assessments,        uploaded_documents_today = 0  # Temporarily disabled

            uploaded_documents_today=uploaded_documents_today,

            system_users=system_users        # System users

        )        users_query = select(func.count(User.user_id))

        users_result = await db.execute(users_query)

    @staticmethod        system_users = users_result.scalar() or 0

    async def _get_patient_demographics(db: AsyncSession) -> PatientDemographics:

        """Get patient demographic statistics"""        return DashboardStats(

        # Total patients            total_patients=total_patients,

        total_query = select(func.count(Patient.id))            active_visits=active_visits,

        total_result = await db.execute(total_query)            completed_visits_today=completed_visits_today,

        total_patients = total_result.scalar() or 0            pending_assessments=pending_assessments,

            uploaded_documents_today=uploaded_documents_today,

        # Age distribution            system_users=system_users

        age_distribution = {}        )

        current_year = date.today().year

    @staticmethod

        # Calculate age from date_of_birth    async def _get_patient_demographics(db: AsyncSession) -> PatientDemographics:

        age_cases = [        """Get patient demographic statistics"""

            (func.extract('year', func.age(Patient.date_of_birth)) < 18, "0-17"),        # Total patients

            (func.extract('year', func.age(Patient.date_of_birth)) < 35, "18-34"),        total_query = select(func.count(Patient.ssn))

            (func.extract('year', func.age(Patient.date_of_birth)) < 55, "35-54"),        total_result = await db.execute(total_query)

            (func.extract('year', func.age(Patient.date_of_birth)) >= 55, "55+")        total_patients = total_result.scalar() or 0

        ]

        # Age distribution

        for condition, label in age_cases:        age_distribution = {}

            age_query = select(func.count(Patient.id)).where(        current_year = date.today().year

                and_(Patient.date_of_birth.is_not(None), condition)

            )        # Calculate age from date_of_birth

            age_result = await db.execute(age_query)        age_cases = [

            age_distribution[label] = age_result.scalar() or 0            (func.extract('year', func.age(Patient.date_of_birth)) < 18, "0-17"),

            (func.extract('year', func.age(Patient.date_of_birth)) < 35, "18-34"),

        # Gender distribution            (func.extract('year', func.age(Patient.date_of_birth)) < 55, "35-54"),

        gender_query = select(Patient.gender, func.count(Patient.id)).group_by(Patient.gender)            (func.extract('year', func.age(Patient.date_of_birth)) >= 55, "55+")

        gender_result = await db.execute(gender_query)        ]

        gender_distribution = {row[0] or "unknown": row[1] for row in gender_result.all()}

        for condition, label in age_cases:

        # Visit frequency (visits per patient)            age_query = select(func.count(Patient.ssn)).where(

        visit_freq_query = select(                and_(Patient.date_of_birth.is_not(None), condition)

            func.count(PatientVisit.id).label('visit_count'),            )

            func.count().label('patient_count')            age_result = await db.execute(age_query)

        ).select_from(PatientVisit).group_by(PatientVisit.patient_id)            age_distribution[label] = age_result.scalar() or 0



        # This is a simplified version - in practice you'd want more sophisticated analysis        # Gender distribution

        visit_frequency = {"0-1": 0, "2-5": 0, "6+": 0}        gender_query = select(Patient.gender, func.count(Patient.ssn)).group_by(Patient.gender)

        gender_result = await db.execute(gender_query)

        return PatientDemographics(        gender_distribution = {row[0] or "unknown": row[1] for row in gender_result.all()}

            total_patients=total_patients,

            age_distribution=age_distribution,        # Visit frequency (visits per patient)

            gender_distribution=gender_distribution,        visit_freq_query = select(

            visit_frequency=visit_frequency            func.count(PatientVisit.id).label('visit_count'),

        )            func.count().label('patient_count')

        ).select_from(PatientVisit).group_by(PatientVisit.patient_id)

    @staticmethod

    async def _get_visit_volume_stats(        # This is a simplified version - in practice you'd want more sophisticated analysis

        db: AsyncSession,        visit_frequency = {"0-1": 0, "2-5": 0, "6+": 0}

        start_date: Optional[date],

        end_date: Optional[date]        return PatientDemographics(

    ) -> VisitVolumeStats:            total_patients=total_patients,

        """Get visit volume statistics"""            age_distribution=age_distribution,

        # Base query with date filter            gender_distribution=gender_distribution,

        base_query = select(PatientVisit)            visit_frequency=visit_frequency

        if start_date:        )

            base_query = base_query.where(func.date(PatientVisit.created_at) >= start_date)

        if end_date:    @staticmethod

            base_query = base_query.where(func.date(PatientVisit.created_at) <= end_date)    async def _get_visit_volume_stats(

        db: AsyncSession,

        # Total visits        start_date: Optional[date],

        total_query = select(func.count()).select_from(base_query.subquery())        end_date: Optional[date]

        total_result = await db.execute(total_query)    ) -> VisitVolumeStats:

        total_visits = total_result.scalar() or 0        """Get visit volume statistics"""

        # Base query with date filter

        # Visits by date (last 30 days)        base_query = select(PatientVisit)

        date_range = end_date or date.today()        if start_date:

        start_range = start_date or (date_range - timedelta(days=30))            base_query = base_query.where(func.date(PatientVisit.created_at) >= start_date)

        if end_date:

        visits_by_date_query = select(            base_query = base_query.where(func.date(PatientVisit.created_at) <= end_date)

            func.date(PatientVisit.created_at).label('date'),

            func.count(PatientVisit.id).label('count')        # Total visits

        ).where(        total_query = select(func.count()).select_from(base_query.subquery())

            and_(        total_result = await db.execute(total_query)

                func.date(PatientVisit.created_at) >= start_range,        total_visits = total_result.scalar() or 0

                func.date(PatientVisit.created_at) <= date_range

            )        # Visits by date (last 30 days)

        ).group_by(func.date(PatientVisit.created_at)).order_by(func.date(PatientVisit.created_at))        date_range = end_date or date.today()

        start_range = start_date or (date_range - timedelta(days=30))

        date_result = await db.execute(visits_by_date_query)

        visits_by_date = [        visits_by_date_query = select(

            {"date": str(row[0]), "count": row[1]}            func.date(PatientVisit.created_at).label('date'),

            for row in date_result.all()            func.count(PatientVisit.id).label('count')

        ]        ).where(

            and_(

        # Visits by status                func.date(PatientVisit.created_at) >= start_range,

        status_query = select(                func.date(PatientVisit.created_at) <= date_range

            PatientVisit.status,            )

            func.count(PatientVisit.id)        ).group_by(func.date(PatientVisit.created_at)).order_by(func.date(PatientVisit.created_at))

        ).select_from(base_query.subquery()).group_by(PatientVisit.status)

        date_result = await db.execute(visits_by_date_query)

        status_result = await db.execute(status_query)        visits_by_date = [

        visits_by_status = {row[0]: row[1] for row in status_result.all()}            {"date": str(row[0]), "count": row[1]}

            for row in date_result.all()

        # Visits by type (placeholder - would need a visit_type field)        ]

        visits_by_type = {"routine": total_visits // 2, "emergency": total_visits // 4, "followup": total_visits // 4}

        # Visits by status

        # Average visits per day        status_query = select(

        days_diff = (date_range - start_range).days or 1            PatientVisit.status,

        average_visits_per_day = total_visits / days_diff            func.count(PatientVisit.id)

        ).select_from(base_query.subquery()).group_by(PatientVisit.status)

        return VisitVolumeStats(

            total_visits=total_visits,        status_result = await db.execute(status_query)

            visits_by_date=visits_by_date,        visits_by_status = {row[0]: row[1] for row in status_result.all()}

            visits_by_status=visits_by_status,

            visits_by_type=visits_by_type,        # Visits by type (placeholder - would need a visit_type field)

            average_visits_per_day=round(average_visits_per_day, 2)        visits_by_type = {"routine": total_visits // 2, "emergency": total_visits // 4, "followup": total_visits // 4}

        )

        # Average visits per day

    @staticmethod        days_diff = (date_range - start_range).days or 1

    async def _get_assessment_stats(        average_visits_per_day = total_visits / days_diff

        db: AsyncSession,

        start_date: Optional[date],        return VisitVolumeStats(

        end_date: Optional[date]            total_visits=total_visits,

    ) -> AssessmentStats:            visits_by_date=visits_by_date,

        """Get assessment statistics"""            visits_by_status=visits_by_status,

        # Nursing assessments            visits_by_type=visits_by_type,

        nursing_query = select(NursingAssessment)            average_visits_per_day=round(average_visits_per_day, 2)

        if start_date:        )

            nursing_query = nursing_query.where(func.date(NursingAssessment.assessed_at) >= start_date)

        if end_date:    @staticmethod

            nursing_query = nursing_query.where(func.date(NursingAssessment.assessed_at) <= end_date)    async def _get_assessment_stats(

        db: AsyncSession,

        nursing_count_query = select(func.count()).select_from(nursing_query.subquery())        start_date: Optional[date],

        nursing_result = await db.execute(nursing_count_query)        end_date: Optional[date]

        nursing_count = nursing_result.scalar() or 0    ) -> AssessmentStats:

        """Get assessment statistics"""

        # Radiology assessments        # Nursing assessments

        radiology_query = select(RadiologyAssessment)        nursing_query = select(NursingAssessment)

        if start_date:        if start_date:

            radiology_query = radiology_query.where(func.date(RadiologyAssessment.assessed_at) >= start_date)            nursing_query = nursing_query.where(func.date(NursingAssessment.assessed_at) >= start_date)

        if end_date:        if end_date:

            radiology_query = radiology_query.where(func.date(RadiologyAssessment.assessed_at) <= end_date)            nursing_query = nursing_query.where(func.date(NursingAssessment.assessed_at) <= end_date)



        radiology_count_query = select(func.count()).select_from(radiology_query.subquery())        nursing_count_query = select(func.count()).select_from(nursing_query.subquery())

        radiology_result = await db.execute(radiology_count_query)        nursing_result = await db.execute(nursing_count_query)

        radiology_count = radiology_result.scalar() or 0        nursing_count = nursing_result.scalar() or 0



        total_assessments = nursing_count + radiology_count        # Radiology assessments

        completed_assessments = total_assessments  # Assuming all have required fields        radiology_query = select(RadiologyAssessment)

        pending_assessments = 0  # Would need more complex logic        if start_date:

            radiology_query = radiology_query.where(func.date(RadiologyAssessment.assessed_at) >= start_date)

        completion_rate = (completed_assessments / total_assessments * 100) if total_assessments > 0 else 0        if end_date:

            radiology_query = radiology_query.where(func.date(RadiologyAssessment.assessed_at) <= end_date)

        assessments_by_type = {

            "nursing": nursing_count,        radiology_count_query = select(func.count()).select_from(radiology_query.subquery())

            "radiology": radiology_count        radiology_result = await db.execute(radiology_count_query)

        }        radiology_count = radiology_result.scalar() or 0



        # Common findings (simplified)        total_assessments = nursing_count + radiology_count

        common_findings = [        completed_assessments = total_assessments  # Assuming all have required fields

            {"finding": "Normal", "count": max(1, total_assessments // 3)},        pending_assessments = 0  # Would need more complex logic

            {"finding": "Abnormal", "count": max(1, total_assessments // 4)},

            {"finding": "Requires follow-up", "count": max(1, total_assessments // 6)}        completion_rate = (completed_assessments / total_assessments * 100) if total_assessments > 0 else 0

        ]

        assessments_by_type = {

        return AssessmentStats(            "nursing": nursing_count,

            total_assessments=total_assessments,            "radiology": radiology_count

            completed_assessments=completed_assessments,        }

            pending_assessments=pending_assessments,

            completion_rate=round(completion_rate, 2),        # Common findings (simplified)

            average_completion_time_hours=None,  # Would need timestamp tracking        common_findings = [

            assessments_by_type=assessments_by_type,            {"finding": "Normal", "count": max(1, total_assessments // 3)},

            common_findings=common_findings            {"finding": "Abnormal", "count": max(1, total_assessments // 4)},

        )            {"finding": "Requires follow-up", "count": max(1, total_assessments // 6)}

        ]

    @staticmethod

    async def _get_recent_activity(db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:        return AssessmentStats(

        """Get recent system activity"""            total_assessments=total_assessments,

        # Recent visits            completed_assessments=completed_assessments,

        visits_query = select(PatientVisit, Patient.full_name).join(            pending_assessments=pending_assessments,

            Patient, PatientVisit.patient_id == Patient.id            completion_rate=round(completion_rate, 2),

        ).order_by(desc(PatientVisit.created_at)).limit(limit)            average_completion_time_hours=None,  # Would need timestamp tracking

            assessments_by_type=assessments_by_type,

        visits_result = await db.execute(visits_query)            common_findings=common_findings

        recent_visits = [        )

            {

                "type": "visit",    @staticmethod

                "description": f"Visit created for {row[1]}",    async def _get_recent_activity(db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:

                "timestamp": row[0].created_at.isoformat(),        """Get recent system activity"""

                "status": row[0].status        # Recent visits

            }        visits_query = select(PatientVisit, Patient.full_name).join(

            for row in visits_result.all()            Patient, PatientVisit.patient_id == Patient.id

        ]        ).order_by(desc(PatientVisit.created_at)).limit(limit)



        # Recent documents        visits_result = await db.execute(visits_query)

        # docs_query = select(Document, Patient.full_name).join(        recent_visits = [

        #     PatientVisit, Document.visit_id == PatientVisit.id            {

        # ).join(                "type": "visit",

        #     Patient, PatientVisit.patient_id == Patient.id                "description": f"Visit created for {row[1]}",

        # ).order_by(desc(Document.uploaded_at)).limit(limit)                "timestamp": row[0].created_at.isoformat(),

        # docs_result = await db.execute(docs_query)                "status": row[0].status

        # recent_docs = [            }

        #     {            for row in visits_result.all()

        #         "type": "document",        ]

        #         "description": f"Document uploaded for {row[1]}",

        #         "timestamp": row[0].uploaded_at.isoformat(),        # Recent documents

        #         "filename": row[0].original_filename        # docs_query = select(Document, Patient.full_name).join(

        #     }        #     PatientVisit, Document.visit_id == PatientVisit.id

        #     for row in docs_result.all()        # ).join(

        # ]        #     Patient, PatientVisit.patient_id == Patient.id

        recent_docs = []  # Temporarily disabled        # ).order_by(desc(Document.uploaded_at)).limit(limit)

        # docs_result = await db.execute(docs_query)

        # Combine and sort by timestamp        # recent_docs = [

        all_activity = recent_visits + recent_docs        #     {

        all_activity.sort(key=lambda x: x["timestamp"], reverse=True)        #         "type": "document",

        #         "description": f"Document uploaded for {row[1]}",

        return all_activity[:limit]        #         "timestamp": row[0].uploaded_at.isoformat(),

        #         "filename": row[0].original_filename

    @staticmethod        #     }

    async def _get_system_alerts(db: AsyncSession) -> List[str]:        #     for row in docs_result.all()

        """Get system alerts and notifications"""        # ]

        alerts = []        recent_docs = []  # Temporarily disabled



        # Check for pending assessments        # Combine and sort by timestamp

        pending_query = select(func.count(PatientVisit.id)).where(        all_activity = recent_visits + recent_docs

            and_(        all_activity.sort(key=lambda x: x["timestamp"], reverse=True)

                PatientVisit.status == "open",

                PatientVisit.created_at < datetime.utcnow() - timedelta(days=1)        return all_activity[:limit]

            )

        )    @staticmethod

        pending_result = await db.execute(pending_query)    async def _get_system_alerts(db: AsyncSession) -> List[str]:

        pending_count = pending_result.scalar() or 0        """Get system alerts and notifications"""

        alerts = []

        if pending_count > 0:

            alerts.append(f"{pending_count} visits have been open for more than 24 hours")        # Check for pending assessments

        pending_query = select(func.count(PatientVisit.id)).where(

        # Check for old documents without assessments            and_(

        # old_docs_query = select(func.count(Document.id)).where(                PatientVisit.status == "open",

        #     Document.uploaded_at < datetime.utcnow() - timedelta(days=7)                PatientVisit.created_at < datetime.utcnow() - timedelta(days=1)

        # ).where(            )

        #     Document.visit_id.in_(        )

        #         select(PatientVisit.id).where(PatientVisit.status == "open")        pending_result = await db.execute(pending_query)

        #     )        pending_count = pending_result.scalar() or 0

        # )

        # old_docs_result = await db.execute(old_docs_query)        if pending_count > 0:

        # old_docs_count = old_docs_result.scalar() or 0            alerts.append(f"{pending_count} visits have been open for more than 24 hours")

        # if old_docs_count > 0:

        #     alerts.append(f"{old_docs_count} documents uploaded over a week ago are still unassessed")        # Check for old documents without assessments

        pass  # Temporarily disabled        # old_docs_query = select(func.count(Document.id)).where(

        #     Document.uploaded_at < datetime.utcnow() - timedelta(days=7)

        return alerts        # ).where(

        #     Document.visit_id.in_(

    @staticmethod        #         select(PatientVisit.id).where(PatientVisit.status == "open")

    async def _get_patient_visit_patterns(        #     )

        db: AsyncSession,        # )

        start_date: Optional[date],        # old_docs_result = await db.execute(old_docs_query)

        end_date: Optional[date]        # old_docs_count = old_docs_result.scalar() or 0

    ) -> Dict[str, Any]:        # if old_docs_count > 0:

        """Get patient visit patterns"""        #     alerts.append(f"{old_docs_count} documents uploaded over a week ago are still unassessed")

        # This would contain more sophisticated analysis        pass  # Temporarily disabled

        return {

            "frequent_visitors": 0,        return alerts

            "return_visit_rate": 0.0,

            "average_days_between_visits": 0,    @staticmethod

            "peak_visit_days": [],    async def _get_patient_visit_patterns(

            "seasonal_patterns": {}        db: AsyncSession,

        }        start_date: Optional[date],

        end_date: Optional[date]

    @staticmethod    ) -> Dict[str, Any]:

    async def _get_visit_trends(        """Get patient visit patterns"""

        db: AsyncSession,        # This would contain more sophisticated analysis

        start_date: Optional[date],        return {

        end_date: Optional[date],            "frequent_visitors": 0,

        group_by: str            "return_visit_rate": 0.0,

    ) -> Dict[str, Any]:            "average_days_between_visits": 0,

        """Get visit trends over time"""            "peak_visit_days": [],

        return {            "seasonal_patterns": {}

            "trend_direction": "stable",        }

            "percentage_change": 0.0,

            "peak_periods": [],    @staticmethod

            "forecast_next_month": 0    async def _get_visit_trends(

        }        db: AsyncSession,

        start_date: Optional[date],

    @staticmethod        end_date: Optional[date],

    async def _get_assessment_quality_metrics(        group_by: str

        db: AsyncSession,    ) -> Dict[str, Any]:

        start_date: Optional[date],        """Get visit trends over time"""

        end_date: Optional[date]        return {

    ) -> Dict[str, Any]:            "trend_direction": "stable",

        """Get assessment quality metrics"""            "percentage_change": 0.0,

        return {            "peak_periods": [],

            "average_assessment_time": 0,            "forecast_next_month": 0

            "completion_rate_trend": "stable",        }

            "error_rate": 0.0,

            "quality_score": 85.0,    @staticmethod

            "improvement_areas": []    async def _get_assessment_quality_metrics(

        }        db: AsyncSession,
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