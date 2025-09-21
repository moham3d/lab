"""
Assessment models for nursing and radiology forms
"""

from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models import Base


class NursingAssessment(Base):
    """
    Nursing assessment with vital signs and patient observations
    """
    __tablename__ = "nursing_assessments"

    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.submission_id"), nullable=False, unique=True)

    # Vital signs
    temperature_celsius = Column(Float, nullable=True)
    pulse_bpm = Column(Integer, nullable=True)
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    respiratory_rate_per_min = Column(Integer, nullable=True)
    oxygen_saturation_percent = Column(Float, nullable=True)

    # Assessment data (stored as JSON)
    pain_assessment = Column(String, nullable=True)  # JSON string
    fall_risk_assessment = Column(String, nullable=True)  # JSON string

    # Additional observations
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)

    # General assessment
    general_condition = Column(String(100), nullable=True)
    consciousness_level = Column(String(50), nullable=True)
    skin_condition = Column(Text, nullable=True)
    mobility_status = Column(String(100), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Audit fields
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    form_submission = relationship("FormSubmission", back_populates="nursing_assessment")

    def __repr__(self):
        return f"<NursingAssessment(assessment_id={self.assessment_id}, submission_id={self.submission_id})>"

    @staticmethod
    def validate_temperature(temp: float) -> bool:
        """Validate temperature range (30.0-45.0°C)"""
        return 30.0 <= temp <= 45.0

    @staticmethod
    def validate_pulse(pulse: int) -> bool:
        """Validate pulse range (30-200 bpm)"""
        return 30 <= pulse <= 200

    @staticmethod
    def validate_blood_pressure(systolic: int, diastolic: int) -> bool:
        """Validate blood pressure ranges"""
        return (70 <= systolic <= 250) and (40 <= diastolic <= 150) and (systolic > diastolic)

    @staticmethod
    def validate_respiratory_rate(rate: int) -> bool:
        """Validate respiratory rate range (8-60/min)"""
        return 8 <= rate <= 60

    @staticmethod
    def validate_oxygen_saturation(sat: float) -> bool:
        """Validate oxygen saturation range (70.0-100.0%)"""
        return 70.0 <= sat <= 100.0

    @property
    def blood_pressure_string(self) -> Optional[str]:
        """Format blood pressure as string"""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None

    @property
    def is_critical_vitals(self) -> bool:
        """Check if any vital signs are in critical range"""
        if self.temperature_celsius and (self.temperature_celsius < 35.0 or self.temperature_celsius > 40.0):
            return True
        if self.pulse_bpm and (self.pulse_bpm < 50 or self.pulse_bpm > 150):
            return True
        if self.oxygen_saturation_percent and self.oxygen_saturation_percent < 90.0:
            return True
        return False


class RadiologyAssessment(Base):
    """
    Radiology assessment with findings and diagnosis
    """
    __tablename__ = "radiology_assessments"

    radiology_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.submission_id"), nullable=False, unique=True)

    # Assessment content
    findings = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)

    # Technical details
    modality = Column(String(50), nullable=True)  # X-ray, CT, MRI, Ultrasound
    body_region = Column(String(100), nullable=True)
    contrast_used = Column(String(100), nullable=True)

    # Image references (for future file attachments)
    image_urls = Column(String, nullable=True)  # JSON array of image URLs

    # Audit fields
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    form_submission = relationship("FormSubmission", back_populates="radiology_assessment")

    def __repr__(self):
        return f"<RadiologyAssessment(radiology_id={self.radiology_id}, submission_id={self.submission_id}, modality={self.modality})>"

    @staticmethod
    def validate_findings(findings: str) -> bool:
        """Validate findings length (10-1000 chars)"""
        return 10 <= len(findings.strip()) <= 1000

    @staticmethod
    def validate_diagnosis(diagnosis: str) -> bool:
        """Validate diagnosis length if provided (10-500 chars)"""
        if not diagnosis:
            return True
        return 10 <= len(diagnosis.strip()) <= 500

    @property
    def has_diagnosis(self) -> bool:
        """Check if diagnosis is provided"""
        return bool(self.diagnosis and self.diagnosis.strip())

    @property
    def findings_summary(self) -> str:
        """Get truncated findings for display"""
        if len(self.findings) <= 100:
            return self.findings
        return self.findings[:97] + "..."