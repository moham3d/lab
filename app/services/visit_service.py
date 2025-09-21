"""
Visit service for patient visit management
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.visit import PatientVisit, VisitStatus
from app.schemas.visit import VisitCreate, VisitResponse, VisitUpdate


class VisitService:
    """Service class for patient visit operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_visit(self, visit_id: UUID) -> Optional[PatientVisit]:
        """Get visit by ID"""
        query = select(PatientVisit).where(PatientVisit.id == visit_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_patient_visits(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[PatientVisit]:
        """Get all visits for a patient"""
        query = select(PatientVisit).where(
            PatientVisit.patient_id == patient_id
        ).order_by(PatientVisit.visit_date.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_visits_by_status(
        self,
        status: VisitStatus,
        skip: int = 0,
        limit: int = 50
    ) -> List[PatientVisit]:
        """Get visits by status"""
        query = select(PatientVisit).where(
            PatientVisit.status == status
        ).order_by(PatientVisit.visit_date.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_visit(self, visit_data: VisitCreate, created_by: UUID) -> PatientVisit:
        """Create a new patient visit"""
        # Verify patient exists
        query = select(Patient).where(Patient.id == visit_data.patient_id, Patient.is_active == True)
        result = await self.db.execute(query)
        patient = result.scalar_one_or_none()
        if not patient:
            raise ValueError(f"Patient with ID {visit_data.patient_id} not found")

        visit = PatientVisit(
            patient_id=visit_data.patient_id,  # Use UUID for the foreign key
            visit_date=visit_data.visit_date,
            notes=visit_data.notes,
            created_by=created_by,
        )
        self.db.add(visit)
        await self.db.commit()
        await self.db.refresh(visit)
        return visit

    async def update_visit(
        self,
        visit_id: UUID,
        visit_data: VisitUpdate,
        updated_by: UUID
    ) -> Optional[PatientVisit]:
        """Update visit information"""
        visit = await self.get_visit(visit_id)
        if not visit:
            return None

        update_data = visit_data.dict(exclude_unset=True)
        if not update_data:
            return visit

        # Handle status transitions
        if 'status' in update_data:
            new_status = update_data['status']
            if not visit.can_transition_to(new_status):
                raise ValueError(f"Cannot transition from {visit.status} to {new_status}")

        # Update visit
        for field, value in update_data.items():
            setattr(visit, field, value)

        await self.db.commit()
        await self.db.refresh(visit)
        return visit

    async def complete_visit(self, visit_id: UUID, updated_by: UUID) -> Optional[PatientVisit]:
        """Mark visit as completed"""
        return await self.update_visit(
            visit_id,
            VisitUpdate(status=VisitStatus.COMPLETED),
            updated_by
        )

    async def cancel_visit(self, visit_id: UUID, updated_by: UUID) -> Optional[PatientVisit]:
        """Cancel a visit"""
        return await self.update_visit(
            visit_id,
            VisitUpdate(status=VisitStatus.CANCELLED),
            updated_by
        )

    async def reopen_visit(self, visit_id: UUID, updated_by: UUID) -> Optional[PatientVisit]:
        """Reopen a completed visit (admin only)"""
        visit = await self.get_visit(visit_id)
        if not visit:
            return None

        if visit.status != VisitStatus.COMPLETED:
            raise ValueError("Only completed visits can be reopened")

        return await self.update_visit(
            visit_id,
            VisitUpdate(status=VisitStatus.OPEN),
            updated_by
        )

    async def get_open_visits_count(self) -> int:
        """Get count of open visits"""
        query = select(PatientVisit).where(PatientVisit.status == VisitStatus.OPEN)
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def get_today_visits(self) -> List[PatientVisit]:
        """Get visits scheduled for today"""
        from datetime import date, time, datetime

        today = date.today()
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)

        query = select(PatientVisit).where(
            PatientVisit.visit_date >= start_of_day,
            PatientVisit.visit_date <= end_of_day
        ).order_by(PatientVisit.visit_date)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_recent_visits(self, limit: int = 20) -> List[PatientVisit]:
        """Get recently created visits"""
        query = select(PatientVisit).order_by(
            PatientVisit.created_at.desc()
        ).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()