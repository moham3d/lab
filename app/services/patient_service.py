"""
Patient service for CRUD operations and business logic
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate


class PatientService:
    """Service class for patient operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_patient(self, patient_id: UUID) -> Optional[Patient]:
        """Get patient by ID"""
        query = select(Patient).where(Patient.id == patient_id, Patient.is_active == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_patient_by_ssn(self, ssn: str) -> Optional[Patient]:
        """Get patient by SSN"""
        query = select(Patient).where(Patient.ssn == ssn, Patient.is_active == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_patient_by_mobile(self, mobile: str) -> Optional[Patient]:
        """Get patient by mobile number"""
        query = select(Patient).where(Patient.mobile_number == mobile, Patient.is_active == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_patient_by_medical_number(self, medical_number: str) -> Optional[Patient]:
        """Get patient by medical number"""
        query = select(Patient).where(Patient.medical_number == medical_number, Patient.is_active == True)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def search_patients(
        self,
        query: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Patient]:
        """Search patients by name, SSN, mobile, or medical number"""
        search_pattern = f"%{query}%"
        stmt = select(Patient).where(
            Patient.is_active == True,
            or_(
                Patient.full_name.ilike(search_pattern),
                Patient.ssn.ilike(search_pattern),
                Patient.mobile_number.ilike(search_pattern),
                Patient.medical_number.ilike(search_pattern) if query else False
            )
        ).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_patient(self, patient_data: PatientCreate, created_by: UUID) -> Patient:
        """Create a new patient"""
        # Check for existing patient with same SSN
        existing = await self.get_patient_by_ssn(patient_data.ssn)
        if existing:
            raise ValueError(f"Patient with SSN {patient_data.ssn} already exists")

        # Check for existing patient with same mobile
        existing = await self.get_patient_by_mobile(patient_data.mobile_number)
        if existing:
            raise ValueError(f"Patient with mobile {patient_data.mobile_number} already exists")

        # Check medical number if provided
        if patient_data.medical_number:
            existing = await self.get_patient_by_medical_number(patient_data.medical_number)
            if existing:
                raise ValueError(f"Patient with medical number {patient_data.medical_number} already exists")

        patient = Patient(
            **patient_data.dict(),
            created_by=created_by,
            updated_by=created_by
        )
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def update_patient(
        self,
        patient_id: UUID,
        patient_data: PatientUpdate,
        updated_by: UUID
    ) -> Optional[Patient]:
        """Update patient information"""
        patient = await self.get_patient(patient_id)
        if not patient:
            return None

        update_data = patient_data.dict(exclude_unset=True)
        if not update_data:
            return patient

        # Check for conflicts if SSN is being updated
        if 'ssn' in update_data and update_data['ssn'] != patient.ssn:
            existing = await self.get_patient_by_ssn(update_data['ssn'])
            if existing and existing.id != patient_id:
                raise ValueError(f"Patient with SSN {update_data['ssn']} already exists")

        # Check for conflicts if mobile is being updated
        if 'mobile_number' in update_data and update_data['mobile_number'] != patient.mobile_number:
            existing = await self.get_patient_by_mobile(update_data['mobile_number'])
            if existing and existing.id != patient_id:
                raise ValueError(f"Patient with mobile {update_data['mobile_number']} already exists")

        # Check for conflicts if medical number is being updated
        if ('medical_number' in update_data and
            update_data['medical_number'] != patient.medical_number and
            update_data['medical_number'] is not None):
            existing = await self.get_patient_by_medical_number(update_data['medical_number'])
            if existing and existing.id != patient_id:
                raise ValueError(f"Patient with medical number {update_data['medical_number']} already exists")

        # Update patient
        for field, value in update_data.items():
            setattr(patient, field, value)

        patient.updated_by = updated_by
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def deactivate_patient(self, patient_id: UUID, updated_by: UUID) -> bool:
        """Deactivate a patient (soft delete)"""
        patient = await self.get_patient(patient_id)
        if not patient:
            return False

        patient.is_active = False
        patient.updated_by = updated_by
        await self.db.commit()
        return True

    async def get_patients_count(self) -> int:
        """Get total count of active patients"""
        query = select(Patient).where(Patient.is_active == True)
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def get_recent_patients(self, limit: int = 10) -> List[Patient]:
        """Get recently created patients"""
        query = select(Patient).where(
            Patient.is_active == True
        ).order_by(Patient.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()