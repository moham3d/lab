"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('nurse', 'physician', 'admin', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create patients table
    op.create_table('patients',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('ssn', sa.String(length=14), nullable=False),
        sa.Column('mobile_number', sa.String(length=11), nullable=False),
        sa.Column('phone_number', sa.String(length=11), nullable=True),
        sa.Column('medical_number', sa.String(length=20), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.Enum('male', 'female', 'other', name='gender'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for patients
    op.create_index(op.f('ix_patients_ssn'), 'patients', ['ssn'], unique=True)
    op.create_index(op.f('ix_patients_mobile_number'), 'patients', ['mobile_number'], unique=False)
    op.create_index(op.f('ix_patients_medical_number'), 'patients', ['medical_number'], unique=True)
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)

    # Create patient_visits table
    op.create_table('patient_visits',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('patient_id', sa.UUID(), nullable=False),
        sa.Column('visit_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Enum('open', 'completed', 'cancelled', name='visitstatus'), nullable=False),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for patient_visits
    op.create_index(op.f('ix_patient_visits_patient_id'), 'patient_visits', ['patient_id'], unique=False)
    op.create_index(op.f('ix_patient_visits_visit_date'), 'patient_visits', ['visit_date'], unique=False)
    op.create_index(op.f('ix_patient_visits_status'), 'patient_visits', ['status'], unique=False)
    op.create_index(op.f('ix_patient_visits_id'), 'patient_visits', ['id'], unique=False)

    # Create nursing_assessments table
    op.create_table('nursing_assessments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('visit_id', sa.UUID(), nullable=False),
        sa.Column('temperature_celsius', sa.Float(), nullable=True),
        sa.Column('pulse_bpm', sa.Integer(), nullable=True),
        sa.Column('blood_pressure_systolic', sa.Integer(), nullable=True),
        sa.Column('blood_pressure_diastolic', sa.Integer(), nullable=True),
        sa.Column('respiratory_rate_per_min', sa.Integer(), nullable=True),
        sa.Column('oxygen_saturation_percent', sa.Float(), nullable=True),
        sa.Column('pain_assessment', sa.String(), nullable=True),
        sa.Column('fall_risk_assessment', sa.String(), nullable=True),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('height_cm', sa.Float(), nullable=True),
        sa.Column('bmi', sa.Float(), nullable=True),
        sa.Column('general_condition', sa.String(length=100), nullable=True),
        sa.Column('consciousness_level', sa.String(length=50), nullable=True),
        sa.Column('skin_condition', sa.Text(), nullable=True),
        sa.Column('mobility_status', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('assessed_by', sa.UUID(), nullable=False),
        sa.Column('assessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['visit_id'], ['patient_visits.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('visit_id')
    )

    # Create radiology_assessments table
    op.create_table('radiology_assessments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('visit_id', sa.UUID(), nullable=False),
        sa.Column('findings', sa.Text(), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('modality', sa.String(length=50), nullable=True),
        sa.Column('body_region', sa.String(length=100), nullable=True),
        sa.Column('contrast_used', sa.String(length=100), nullable=True),
        sa.Column('image_urls', sa.String(), nullable=True),
        sa.Column('assessed_by', sa.UUID(), nullable=False),
        sa.Column('assessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['visit_id'], ['patient_visits.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('visit_id')
    )


def downgrade() -> None:
    # Drop radiology_assessments table
    op.drop_table('radiology_assessments')
    
    # Drop nursing_assessments table
    op.drop_table('nursing_assessments')
    
    # Drop indexes for patient_visits
    op.drop_index(op.f('ix_patient_visits_id'), table_name='patient_visits')
    op.drop_index(op.f('ix_patient_visits_status'), table_name='patient_visits')
    op.drop_index(op.f('ix_patient_visits_visit_date'), table_name='patient_visits')
    op.drop_index(op.f('ix_patient_visits_patient_id'), table_name='patient_visits')
    
    # Drop patient_visits table
    op.drop_table('patient_visits')
    
    # Drop indexes for patients
    op.drop_index(op.f('ix_patients_id'), table_name='patients')
    op.drop_index(op.f('ix_patients_medical_number'), table_name='patients')
    op.drop_index(op.f('ix_patients_mobile_number'), table_name='patients')
    op.drop_index(op.f('ix_patients_ssn'), table_name='patients')
    
    # Drop patients table
    op.drop_table('patients')
    
    # Drop indexes
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
    # Drop users table
    op.drop_table('users')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS visitstatus")
    op.execute("DROP TYPE IF EXISTS gender")
    op.execute("DROP TYPE IF EXISTS userrole")