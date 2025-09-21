"""
Assessment service for nursing and radiology form management
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import NursingAssessment, RadiologyAssessment
from app.models.visit import PatientVisit, VisitStatus
from app.schemas.assessment import (
    NursingAssessmentCreate,
    NursingAssessmentResponse,
    NursingAssessmentUpdate,
    RadiologyAssessmentCreate,
    RadiologyAssessmentResponse,
    RadiologyAssessmentUpdate,
)


class AssessmentService:
    """Service class for assessment operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Nursing Assessment Methods
    async def get_nursing_assessment(self, assessment_id: UUID) -> Optional[NursingAssessment]:
        """Get nursing assessment by ID"""
        query = select(NursingAssessment).where(NursingAssessment.assessment_id == assessment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_nursing_assessment_by_visit(self, visit_id: UUID) -> Optional[NursingAssessment]:
        """Get nursing assessment by visit ID"""
        query = select(NursingAssessment).where(NursingAssessment.visit_id == visit_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_nursing_assessment(
        self,
        assessment_data: NursingAssessmentCreate,
        assessed_by: UUID
    ) -> NursingAssessment:
        """Create a new nursing assessment"""
        # Verify visit exists and is open
        query = select(PatientVisit).where(
            PatientVisit.id == assessment_data.visit_id,
            PatientVisit.status == VisitStatus.OPEN
        )
        result = await self.db.execute(query)
        visit = result.scalar_one_or_none()
        if not visit:
            raise ValueError("Visit not found or not open for assessment")

        # Check if assessment already exists for this visit
        existing = await self.get_nursing_assessment_by_visit(assessment_data.visit_id)
        if existing:
            raise ValueError("Nursing assessment already exists for this visit")

        # Calculate BMI if weight and height provided
        bmi = None
        if assessment_data.weight_kg and assessment_data.height_cm:
            height_m = assessment_data.height_cm / 100
            bmi = round(assessment_data.weight_kg / (height_m ** 2), 1)

        assessment = NursingAssessment(
            **assessment_data.dict(),
            bmi=bmi,
            assessed_by=assessed_by
        )
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def update_nursing_assessment(
        self,
        assessment_id: UUID,
        assessment_data: NursingAssessmentUpdate,
        updated_by: UUID
    ) -> Optional[NursingAssessment]:
        """Update nursing assessment"""
        assessment = await self.get_nursing_assessment(assessment_id)
        if not assessment:
            return None

        # Verify visit is still open
        query = select(PatientVisit).where(
            PatientVisit.id == assessment.visit_id,
            PatientVisit.status == VisitStatus.OPEN
        )
        result = await self.db.execute(query)
        visit = result.scalar_one_or_none()
        if not visit:
            raise ValueError("Cannot update assessment for completed or cancelled visit")

        update_data = assessment_data.dict(exclude_unset=True)
        if not update_data:
            return assessment

        # Recalculate BMI if weight or height changed
        if 'weight_kg' in update_data or 'height_cm' in update_data:
            weight = update_data.get('weight_kg', assessment.weight_kg)
            height = update_data.get('height_cm', assessment.height_cm)
            if weight and height:
                height_m = height / 100
                update_data['bmi'] = round(weight / (height_m ** 2), 1)

        # Update assessment
        for field, value in update_data.items():
            setattr(assessment, field, value)

        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    # Radiology Assessment Methods
    async def get_radiology_assessment(self, assessment_id: UUID) -> Optional[RadiologyAssessment]:
        """Get radiology assessment by ID"""
        query = select(RadiologyAssessment).where(RadiologyAssessment.radiology_id == assessment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_radiology_assessment_by_visit(self, visit_id: UUID) -> Optional[RadiologyAssessment]:
        """Get radiology assessment by visit ID"""
        query = select(RadiologyAssessment).where(RadiologyAssessment.visit_id == visit_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_radiology_assessment(
        self,
        assessment_data: RadiologyAssessmentCreate,
        assessed_by: UUID
    ) -> RadiologyAssessment:
        """Create a new radiology assessment"""
        # Verify visit exists and is open
        query = select(PatientVisit).where(
            PatientVisit.id == assessment_data.visit_id,
            PatientVisit.status == VisitStatus.OPEN
        )
        result = await self.db.execute(query)
        visit = result.scalar_one_or_none()
        if not visit:
            raise ValueError("Visit not found or not open for assessment")

        # Check if assessment already exists for this visit
        existing = await self.get_radiology_assessment_by_visit(assessment_data.visit_id)
        if existing:
            raise ValueError("Radiology assessment already exists for this visit")

        assessment = RadiologyAssessment(
            **assessment_data.dict(),
            assessed_by=assessed_by
        )
        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    async def update_radiology_assessment(
        self,
        assessment_id: UUID,
        assessment_data: RadiologyAssessmentUpdate,
        updated_by: UUID
    ) -> Optional[RadiologyAssessment]:
        """Update radiology assessment"""
        assessment = await self.get_radiology_assessment(assessment_id)
        if not assessment:
            return None

        # Verify visit is still open
        query = select(PatientVisit).where(
            PatientVisit.id == assessment.visit_id,
            PatientVisit.status == VisitStatus.OPEN
        )
        result = await self.db.execute(query)
        visit = result.scalar_one_or_none()
        if not visit:
            raise ValueError("Cannot update assessment for completed or cancelled visit")

        update_data = assessment_data.dict(exclude_unset=True)
        if not update_data:
            return assessment

        # Update assessment
        for field, value in update_data.items():
            setattr(assessment, field, value)

        await self.db.commit()
        await self.db.refresh(assessment)
        return assessment

    # Utility Methods
    async def get_visit_assessments(self, visit_id: UUID) -> dict:
        """Get both nursing and radiology assessments for a visit"""
        nursing = await self.get_nursing_assessment_by_visit(visit_id)
        radiology = await self.get_radiology_assessment_by_visit(visit_id)

        return {
            "nursing_assessment": nursing,
            "radiology_assessment": radiology,
            "has_nursing": nursing is not None,
            "has_radiology": radiology is not None,
            "assessments_complete": nursing is not None and radiology is not None
        }

    async def can_complete_visit(self, visit_id: UUID) -> bool:
        """Check if visit can be completed (both assessments done)"""
        assessments = await self.get_visit_assessments(visit_id)
        return assessments["assessments_complete"]