"""
Report Pydantic schemas for dashboard and analytics
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DateRangeFilter(BaseModel):
    """Date range filter for reports"""
    start_date: Optional[date] = Field(None, description="Start date for filtering")
    end_date: Optional[date] = Field(None, description="End date for filtering")

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date"""
        if v and values.data.get('start_date') and v < values.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class ReportFilter(DateRangeFilter):
    """Common filters for reports"""
    user_id: Optional[UUID] = Field(None, description="Filter by specific user")
    department: Optional[str] = Field(None, description="Filter by department")
    status: Optional[str] = Field(None, description="Filter by status")


class DashboardStats(BaseModel):
    """Dashboard statistics summary"""
    total_patients: int = Field(..., description="Total number of patients")
    active_visits: int = Field(..., description="Number of active visits")
    completed_visits_today: int = Field(..., description="Visits completed today")
    pending_assessments: int = Field(..., description="Assessments awaiting completion")
    uploaded_documents_today: int = Field(..., description="Documents uploaded today")
    system_users: int = Field(..., description="Total system users")


class PatientDemographics(BaseModel):
    """Patient demographic statistics"""
    total_patients: int
    age_distribution: Dict[str, int]  # e.g., {"0-18": 25, "19-35": 45, ...}
    gender_distribution: Dict[str, int]  # e.g., {"male": 120, "female": 98, "other": 2}
    visit_frequency: Dict[str, int]  # e.g., {"0-1": 50, "2-5": 80, "6+": 30}


class VisitVolumeStats(BaseModel):
    """Visit volume statistics"""
    total_visits: int
    visits_by_date: List[Dict[str, Any]]  # Daily visit counts
    visits_by_status: Dict[str, int]  # e.g., {"open": 15, "completed": 45, "cancelled": 3}
    visits_by_type: Dict[str, int]  # e.g., {"emergency": 10, "routine": 35, "followup": 18}
    average_visits_per_day: float


class AssessmentStats(BaseModel):
    """Clinical assessment statistics"""
    total_assessments: int
    completed_assessments: int
    pending_assessments: int
    completion_rate: float
    average_completion_time_hours: Optional[float]
    assessments_by_type: Dict[str, int]  # e.g., {"nursing": 30, "radiology": 25}
    common_findings: List[Dict[str, Any]]  # Top findings with counts


class DashboardReportResponse(BaseModel):
    """Dashboard report response"""
    stats: DashboardStats
    recent_activity: List[Dict[str, Any]]  # Recent visits, assessments, uploads
    alerts: List[str]  # System alerts or notifications
    generated_at: datetime


class PatientStatisticsResponse(BaseModel):
    """Patient statistics report response"""
    demographics: PatientDemographics
    visit_patterns: Dict[str, Any]  # Patient visit patterns
    generated_at: datetime


class VisitVolumeResponse(BaseModel):
    """Visit volume report response"""
    volume_stats: VisitVolumeStats
    trends: Dict[str, Any]  # Visit trends over time
    generated_at: datetime


class ClinicalAssessmentsResponse(BaseModel):
    """Clinical assessments report response"""
    assessment_stats: AssessmentStats
    quality_metrics: Dict[str, Any]  # Assessment quality metrics
    generated_at: datetime


class AuditLogSummary(BaseModel):
    """Audit log summary for reports"""
    total_actions: int
    actions_by_type: Dict[str, int]  # e.g., {"CREATE": 50, "READ": 200, "UPDATE": 30}
    actions_by_user: Dict[str, int]  # User activity summary
    sensitive_actions: int  # Actions involving PHI
    recent_actions: List[Dict[str, Any]]  # Recent audit entries


class SystemHealthReport(BaseModel):
    """System health and performance report"""
    uptime_percentage: float
    average_response_time_ms: float
    error_rate_percentage: float
    database_connections: int
    active_users: int
    storage_usage_gb: float
    generated_at: datetime


class ReportGenerationRequest(BaseModel):
    """Request to generate a custom report"""
    report_type: str = Field(..., description="Type of report to generate")
    filters: Optional[ReportFilter] = Field(None, description="Report filters")
    include_charts: bool = Field(True, description="Include chart data")
    format: str = Field("json", description="Output format: json, csv, pdf")


class ReportGenerationResponse(BaseModel):
    """Response after generating a report"""
    report_id: UUID
    report_type: str
    status: str  # "pending", "completed", "failed"
    download_url: Optional[str]
    generated_at: datetime
    expires_at: Optional[datetime]


class ReportListResponse(BaseModel):
    """List of available reports"""
    reports: List[Dict[str, Any]]
    total_count: int
    generated_at: datetime


# Request/Response models for specific endpoints
class DashboardRequest(ReportFilter):
    """Request for dashboard data"""
    include_recent_activity: bool = Field(True)
    include_alerts: bool = Field(True)


class PatientStatsRequest(ReportFilter):
    """Request for patient statistics"""
    include_demographics: bool = Field(True)
    include_visit_patterns: bool = Field(True)


class VisitVolumeRequest(ReportFilter):
    """Request for visit volume data"""
    group_by: str = Field("day", description="Group by: day, week, month")
    include_trends: bool = Field(True)


class AssessmentReportRequest(ReportFilter):
    """Request for assessment report"""
    assessment_type: Optional[str] = Field(None, description="Filter by assessment type")
    include_quality_metrics: bool = Field(True)