from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Text, DECIMAL, ForeignKey, UUID, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # nurse, physician, admin
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))

class Patient(Base):
    __tablename__ = "patients"
    
    ssn = Column(String(20), primary_key=True)
    mobile_number = Column(String(20), nullable=False)
    phone_number = Column(String(20))
    medical_number = Column(String(50), unique=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(10))  # male, female, other
    address = Column(Text)
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    is_active = Column(Boolean, default=True)

class PatientVisit(Base):
    __tablename__ = "patient_visits"
    
    visit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_ssn = Column(String(20), ForeignKey("patients.ssn"), nullable=False)
    visit_date = Column(DateTime(timezone=True), server_default=func.now())
    visit_status = Column(String(20), default='open')
    primary_diagnosis = Column(Text)
    secondary_diagnosis = Column(Text)
    diagnosis_code = Column(String(20))
    visit_type = Column(String(30), default='outpatient')
    department = Column(String(100))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assigned_physician = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    completed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FormDefinition(Base):
    __tablename__ = "form_definitions"
    
    form_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_code = Column(String(20), unique=True, nullable=False)
    form_name = Column(String(255), nullable=False)
    form_version = Column(String(10), nullable=False)
    form_description = Column(Text)
    form_role = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.visit_id"), nullable=False)
    form_id = Column(UUID(as_uuid=True), ForeignKey("form_definitions.form_id"), nullable=False)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    submission_status = Column(String(20), default='draft')
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    approved_at = Column(DateTime(timezone=True))

class NursingAssessment(Base):
    __tablename__ = "nursing_assessments"
    
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.submission_id"), nullable=False)
    
    # Basic assessment info
    mode_of_arrival = Column(String(20))
    arrival_other_desc = Column(Text)
    age = Column(Integer)
    chief_complaint = Column(Text)
    accompanied_by = Column(String(20))
    language_spoken = Column(String(20), default='arabic')
    language_other_desc = Column(Text)
    
    # Vital signs
    temperature_celsius = Column(DECIMAL(4,2))
    pulse_bpm = Column(Integer)
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    respiratory_rate_per_min = Column(Integer)
    oxygen_saturation_percent = Column(DECIMAL(5,2))
    blood_sugar_mg_dl = Column(Integer)
    weight_kg = Column(DECIMAL(5,2))
    height_cm = Column(DECIMAL(5,2))
    
    # General assessment
    general_condition = Column(String(100))
    consciousness_level = Column(String(50))
    skin_condition = Column(Text)
    mobility_status = Column(String(100))
    
    # Psychosocial history
    psychological_problem = Column(String(50))
    psychological_other_desc = Column(Text)
    is_smoker = Column(Boolean, default=False)
    has_allergies = Column(Boolean, default=False)
    medication_allergies = Column(Text)
    food_allergies = Column(Text)
    other_allergies = Column(Text)
    
    # Nutritional screening
    diet_type = Column(String(20), default='regular')
    special_diet_desc = Column(Text)
    appetite = Column(String(20))
    has_git_problems = Column(Boolean, default=False)
    git_problems_desc = Column(Text)
    has_weight_loss = Column(Boolean, default=False)
    has_weight_gain = Column(Boolean, default=False)
    refer_to_nutritionist = Column(Boolean, default=False)
    
    # Functional assessment
    feeding_status = Column(String(20))
    hygiene_status = Column(String(20))
    toileting_status = Column(String(20))
    ambulation_status = Column(String(20))
    has_musculoskeletal_problems = Column(Boolean, default=False)
    has_deformities = Column(Boolean, default=False)
    has_contractures = Column(Boolean, default=False)
    is_amputee = Column(Boolean, default=False)
    is_bedridden = Column(Boolean, default=False)
    has_musculoskeletal_pain = Column(Boolean, default=False)
    uses_walker = Column(Boolean, default=False)
    uses_wheelchair = Column(Boolean, default=False)
    uses_transfer_device = Column(Boolean, default=False)
    uses_raised_toilet_seat = Column(Boolean, default=False)
    uses_other_equipment = Column(Boolean, default=False)
    other_equipment_desc = Column(Text)
    
    # Pain assessment
    pain_intensity = Column(Integer)
    pain_location = Column(Text)
    pain_frequency = Column(Text)
    pain_duration = Column(Text)
    pain_character = Column(Text)
    action_taken = Column(Text)
    
    # Fall risk assessment
    fall_history_3months = Column(Boolean, default=False)
    secondary_diagnosis = Column(Boolean, default=False)
    ambulatory_aid = Column(String(30))
    iv_therapy = Column(Boolean, default=False)
    gait_status = Column(String(20))
    mental_status = Column(String(20))
    morse_total_score = Column(Integer)
    
    # Pediatric fall risk
    age_score = Column(Integer)
    gender_score = Column(Integer)
    diagnosis_score = Column(Integer)
    cognitive_score = Column(Integer)
    environmental_score = Column(Integer)
    surgery_anesthesia_score = Column(Integer)
    medication_score = Column(Integer)
    humpty_total_score = Column(Integer)
    
    # Educational needs
    needs_medication_education = Column(Boolean, default=False)
    needs_diet_nutrition_education = Column(Boolean, default=False)
    needs_medical_equipment_education = Column(Boolean, default=False)
    needs_rehabilitation_education = Column(Boolean, default=False)
    needs_drug_interaction_education = Column(Boolean, default=False)
    needs_pain_symptom_education = Column(Boolean, default=False)
    needs_fall_prevention_education = Column(Boolean, default=False)
    other_needs = Column(Boolean, default=False)
    other_needs_desc = Column(Text)
    
    # Elderly assessment
    daily_activities = Column(String(30))
    cognitive_assessment = Column(String(30))
    mood_assessment = Column(String(20))
    speech_disorder = Column(Boolean, default=False)
    hearing_disorder = Column(Boolean, default=False)
    vision_disorder = Column(Boolean, default=False)
    sleep_disorder = Column(Boolean, default=False)
    
    # Disabled patients assessment
    disability_type = Column(String(20))
    disability_other_desc = Column(Text)
    has_assistive_devices = Column(Boolean, default=False)
    assistive_devices_desc = Column(Text)
    
    # Abuse and neglect screening
    has_signs_of_abuse = Column(Boolean, default=False)
    abuse_description = Column(Text)
    reported_to_authorities = Column(Boolean, default=False)
    reporting_date = Column(DateTime(timezone=True))
    
    # Audit fields
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())

class RadiologyAssessment(Base):
    __tablename__ = "radiology_assessments"
    
    radiology_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.submission_id"), nullable=False)
    
    # Physician and department info
    treating_physician = Column(String(255))
    department = Column(String(100))
    
    # Patient preparation
    fasting_hours = Column(Integer)
    is_diabetic = Column(String(10), default='false')
    blood_sugar_level = Column(Integer)
    weight_kg = Column(DECIMAL(5,2))
    height_cm = Column(DECIMAL(5,2))
    
    # Imaging procedure details
    dose_amount = Column(DECIMAL(10,2))
    preparation_time = Column(Text)
    injection_time = Column(Text)
    injection_site = Column(String(100))
    ctd1vol = Column(DECIMAL(10,2))
    dlp = Column(DECIMAL(10,2))
    uses_contrast = Column(String(10), default='false')
    kidney_function_value = Column(DECIMAL(10,2))
    
    # Study information
    is_first_time = Column(String(10), default='true')
    is_comparison = Column(String(10), default='false')
    previous_study_code = Column(String(50))
    requires_report = Column(String(10), default='true')
    requires_cd = Column(String(10), default='false')
    
    # Clinical information
    diagnosis = Column(Text)
    reason_for_study = Column(Text)
    
    # Assessment content
    findings = Column(Text, nullable=False)
    impression = Column(Text)
    recommendations = Column(Text)
    
    # Technical details
    modality = Column(String(50))
    body_region = Column(String(100))
    contrast_used = Column(Text)
    
    # Treatment history
    has_chemotherapy = Column(Boolean, default=False)
    chemo_type = Column(String(20))
    chemo_details = Column(Text)
    chemo_sessions = Column(Integer)
    chemo_last_date = Column(Date)
    has_radiotherapy = Column(Boolean, default=False)
    radiotherapy_site = Column(Text)
    radiotherapy_sessions = Column(Integer)
    radiotherapy_last_date = Column(Date)
    has_hormonal_treatment = Column(Boolean, default=False)
    hormonal_last_dose_date = Column(Date)
    other_treatments = Column(Text)
    
    # Previous imaging history
    has_operations = Column(Boolean, default=False)
    has_endoscopy = Column(Boolean, default=False)
    has_biopsies = Column(Boolean, default=False)
    has_tc_mdp_bone_scan = Column(Boolean, default=False)
    has_tc_dtpa_kidney_scan = Column(Boolean, default=False)
    has_mri = Column(Boolean, default=False)
    has_mammography = Column(Boolean, default=False)
    has_ct = Column(Boolean, default=False)
    has_xray = Column(Boolean, default=False)
    has_ultrasound = Column(Boolean, default=False)
    has_other_imaging = Column(Boolean, default=False)
    other_imaging_desc = Column(Text)
    
    # Audit fields
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())

class VisitDocument(Base):
    __tablename__ = "visit_documents"
    
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.visit_id"), nullable=False)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size_bytes = Column(Integer)
    mime_type = Column(String(100))
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text)
    is_active = Column(Boolean, default=True)

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action_type = Column(String(20), nullable=False)
    old_values = Column(JSON)
    new_values = Column(JSON)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))
    user_agent = Column(Text)

class Report(Base):
    __tablename__ = "reports"
    
    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.visit_id"), nullable=False)
    summary = Column(Text)
    doctor_notes = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())