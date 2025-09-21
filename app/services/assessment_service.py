"""
Assessment service for nursing and radiology form management
"""

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment import NursingAssessment, RadiologyAssessment
from app.models.form import FormDefinition, FormSubmission
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

    async def _get_or_create_form_definition(self, form_type: str) -> FormDefinition:
        """Get or create form definition for assessment type"""
        query = select(FormDefinition).where(
            FormDefinition.form_type == form_type,
            FormDefinition.is_active == "active"
        )
        result = await self.db.execute(query)
        form_def = result.scalar_one_or_none()
        
        if not form_def:
            # Create default form definition
            form_def = FormDefinition(
                form_name=f"{form_type.title()} Assessment",
                form_type=form_type,
                description=f"Default {form_type} assessment form",
                created_by=uuid4()  # System user - in real app would be proper admin
            )
            self.db.add(form_def)
            await self.db.commit()
            await self.db.refresh(form_def)
        
        return form_def

    async def _create_form_submission(self, visit_id: UUID, form_type: str, submitted_by: UUID) -> FormSubmission:
        """Create form submission for assessment"""
        form_def = await self._get_or_create_form_definition(form_type)
        
        # Check if submission already exists
        query = select(FormSubmission).where(
            FormSubmission.visit_id == visit_id,
            FormSubmission.form_id == form_def.form_id
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        submission = FormSubmission(
            visit_id=visit_id,
            form_id=form_def.form_id,
            submitted_by=submitted_by,
            submission_status="submitted"
        )
        self.db.add(submission)
        await self.db.commit()
        await self.db.refresh(submission)
        return submission

    # Nursing Assessment Methods
    async def get_nursing_assessment(self, assessment_id: UUID) -> Optional[NursingAssessment]:
        """Get nursing assessment by ID"""
        query = select(NursingAssessment).where(NursingAssessment.assessment_id == assessment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_nursing_assessment_by_visit(self, visit_id: UUID) -> Optional[NursingAssessment]:
        """Get nursing assessment by visit ID"""
        query = select(NursingAssessment).join(FormSubmission).where(
            FormSubmission.visit_id == visit_id
        )
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

        # Create form submission
        submission = await self._create_form_submission(assessment_data.visit_id, "nursing", assessed_by)

        # Calculate BMI if weight and height provided
        bmi = None
        if assessment_data.weight_kg and assessment_data.height_cm:
            height_m = assessment_data.height_cm / 100
            bmi = round(assessment_data.weight_kg / (height_m ** 2), 1)

        # Create assessment data excluding visit_id
        assessment_dict = assessment_data.dict()
        assessment_dict.pop('visit_id', None)  # Remove visit_id since we use submission_id
        
        assessment = NursingAssessment(
            **assessment_dict,
            submission_id=submission.submission_id,
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

        # Get visit through form submission
        query = select(PatientVisit).join(FormSubmission).where(
            FormSubmission.submission_id == assessment.submission_id,
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
        query = select(RadiologyAssessment).join(FormSubmission).where(
            FormSubmission.visit_id == visit_id
        )
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

        # Create form submission
        submission = await self._create_form_submission(assessment_data.visit_id, "radiology", assessed_by)

        # Create assessment data excluding visit_id
        assessment_dict = assessment_data.dict()
        assessment_dict.pop('visit_id', None)  # Remove visit_id since we use submission_id

        assessment = RadiologyAssessment(
            **assessment_dict,
            submission_id=submission.submission_id,
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

        # Get visit through form submission
        query = select(PatientVisit).join(FormSubmission).where(
            FormSubmission.submission_id == assessment.submission_id,
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