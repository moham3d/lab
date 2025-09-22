from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Text, DECIMAL, ForeignKey, UUID, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    # Unique identifier for the user
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Username for login, must be unique
    username = Column(String(50), unique=True, nullable=False)
    # Email address, must be unique
    email = Column(String(255), unique=True, nullable=False)
    # Full name of the user
    full_name = Column(String(255), nullable=False)
    # Role of the user: nurse, physician, admin
    role = Column(String(20), nullable=False)  # nurse, physician, admin
    # Hashed password for authentication
    password_hash = Column(String(255), nullable=False)
    # Whether the user account is active
    is_active = Column(Boolean, default=True)
    # Account creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Last login timestamp
    last_login = Column(DateTime(timezone=True))

class Patient(Base):
    __tablename__ = "patients"
    
    # Social Security Number (Egyptian format, 14 digits), primary key
    ssn = Column(String(20), primary_key=True)
    # Mobile phone number
    mobile_number = Column(String(20), nullable=False)
    # Additional phone number
    phone_number = Column(String(20))
    # Medical record number, unique
    medical_number = Column(String(50), unique=True)
    # Full name of the patient
    full_name = Column(String(255), nullable=False)
    # Date of birth
    date_of_birth = Column(Date)
    # Gender: male, female, other
    gender = Column(String(10))  # male, female, other
    # Residential address
    address = Column(Text)
    # Emergency contact name
    emergency_contact_name = Column(String(255))
    # Emergency contact phone number
    emergency_contact_phone = Column(String(20))
    # Emergency contact relation
    emergency_contact_relation = Column(String(50))
    # Record creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Last update timestamp
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # User who created the record
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    # Whether the patient record is active
    is_active = Column(Boolean, default=True)

class PatientVisit(Base):
    __tablename__ = "patient_visits"
    
    # Unique identifier for the visit
    visit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Patient's SSN (foreign key)
    patient_ssn = Column(String(20), ForeignKey("patients.ssn"), nullable=False)
    # Date and time of the visit
    visit_date = Column(DateTime(timezone=True), server_default=func.now())
    # Status of the visit: initiated, nursing_completed, physician_completed, closed
    visit_status = Column(String(20), default='initiated')
    # Primary diagnosis
    primary_diagnosis = Column(Text)
    # Secondary diagnosis
    secondary_diagnosis = Column(Text)
    # Diagnosis code (ICD or similar)
    diagnosis_code = Column(String(20))
    # Type of visit: outpatient, inpatient, etc.
    visit_type = Column(String(30), default='outpatient')
    # Department handling the visit
    department = Column(String(100))
    # User who created the visit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    # Assigned physician
    assigned_physician = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    # Timestamp when visit was completed
    completed_at = Column(DateTime(timezone=True))
    # Additional notes
    notes = Column(Text)
    # Record creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Last update timestamp
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FormDefinition(Base):
    __tablename__ = "form_definitions"
    
    # Unique identifier for the form
    form_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Code for the form, unique
    form_code = Column(String(20), unique=True, nullable=False)
    # Name of the form
    form_name = Column(String(255), nullable=False)
    # Version of the form
    form_version = Column(String(10), nullable=False)
    # Description of the form
    form_description = Column(Text)
    # Role required to fill the form: nurse, physician
    form_role = Column(String(20), nullable=False)
    # Whether the form is active
    is_active = Column(Boolean, default=True)
    # Creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    # Unique identifier for the submission
    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Associated visit ID
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.visit_id"), nullable=False)
    # Form definition ID
    form_id = Column(UUID(as_uuid=True), ForeignKey("form_definitions.form_id"), nullable=False)
    # User who submitted the form
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    # Status of the submission: draft, submitted, approved
    submission_status = Column(String(20), default='draft')
    # Submission timestamp
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    # User who approved the submission
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    # Approval timestamp
    approved_at = Column(DateTime(timezone=True))

class NursingAssessment(Base):
    __tablename__ = "nursing_assessments"
    
    # Unique identifier for the assessment
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Associated form submission
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.submission_id"), nullable=False)
    
    # Basic assessment info
    # Mode of arrival: walk, ambulatory, wheelchair, stretcher, other
    mode_of_arrival = Column(String(20))
    # Description if mode is other
    arrival_other_desc = Column(Text)
    # Patient's age
    age = Column(Integer)
    # Chief complaint described by patient
    chief_complaint = Column(Text)
    # Who accompanied the patient: spouse, relative, other
    accompanied_by = Column(String(20))
    # Language spoken: arabic, english, other
    language_spoken = Column(String(20), default='arabic')
    # Description if language is other
    language_other_desc = Column(Text)
    
    # Vital signs
    # Body temperature in Celsius
    temperature_celsius = Column(DECIMAL(4,2))
    # Pulse rate in beats per minute
    pulse_bpm = Column(Integer)
    # Systolic blood pressure
    blood_pressure_systolic = Column(Integer)
    # Diastolic blood pressure
    blood_pressure_diastolic = Column(Integer)
    # Respiratory rate per minute
    respiratory_rate_per_min = Column(Integer)
    # Oxygen saturation percentage
    oxygen_saturation_percent = Column(DECIMAL(5,2))
    # Blood sugar level in mg/dl
    blood_sugar_mg_dl = Column(Integer)
    # Weight in kilograms
    weight_kg = Column(DECIMAL(5,2))
    # Height in centimeters
    height_cm = Column(DECIMAL(5,2))
    
    # General assessment
    # Overall general condition
    general_condition = Column(String(100))
    # Level of consciousness
    consciousness_level = Column(String(50))
    # Condition of the skin
    skin_condition = Column(Text)
    # Mobility status
    mobility_status = Column(String(100))
    
    # Psychosocial history
    # Psychological problem: none, anxious, agitated, depressed, etc.
    psychological_problem = Column(String(50))
    # Description if psychological problem is other
    psychological_other_desc = Column(Text)
    # Whether the patient is a smoker
    is_smoker = Column(Boolean, default=False)
    # Whether the patient has allergies
    has_allergies = Column(Boolean, default=False)
    # Medication allergies
    medication_allergies = Column(Text)
    # Food allergies
    food_allergies = Column(Text)
    # Other allergies
    other_allergies = Column(Text)
    
    # Nutritional screening
    # Diet type: regular, special
    diet_type = Column(String(20), default='regular')
    # Description of special diet
    special_diet_desc = Column(Text)
    # Appetite: good, poor
    appetite = Column(String(20))
    # Whether the patient has GIT problems
    has_git_problems = Column(Boolean, default=False)
    # Description of GIT problems
    git_problems_desc = Column(Text)
    # Whether the patient has weight loss
    has_weight_loss = Column(Boolean, default=False)
    # Whether the patient has weight gain
    has_weight_gain = Column(Boolean, default=False)
    # Whether to refer to nutritionist
    refer_to_nutritionist = Column(Boolean, default=False)
    
    # Functional assessment
    # Self-caring status for feeding
    feeding_status = Column(String(20))
    # Self-caring status for hygiene
    hygiene_status = Column(String(20))
    # Self-caring status for toileting
    toileting_status = Column(String(20))
    # Self-caring status for ambulation
    ambulation_status = Column(String(20))
    # Whether the patient has musculoskeletal problems
    has_musculoskeletal_problems = Column(Boolean, default=False)
    # Whether the patient has deformities
    has_deformities = Column(Boolean, default=False)
    # Whether the patient has contractures
    has_contractures = Column(Boolean, default=False)
    # Whether the patient is amputee
    is_amputee = Column(Boolean, default=False)
    # Whether the patient is bedridden
    is_bedridden = Column(Boolean, default=False)
    # Whether the patient has musculoskeletal pain
    has_musculoskeletal_pain = Column(Boolean, default=False)
    # Whether the patient uses walker
    uses_walker = Column(Boolean, default=False)
    # Whether the patient uses wheelchair
    uses_wheelchair = Column(Boolean, default=False)
    # Whether the patient uses transfer device
    uses_transfer_device = Column(Boolean, default=False)
    # Whether the patient uses raised toilet seat
    uses_raised_toilet_seat = Column(Boolean, default=False)
    # Whether the patient uses other equipment
    uses_other_equipment = Column(Boolean, default=False)
    # Description of other equipment
    other_equipment_desc = Column(Text)
    
    # Pain assessment
    # Intensity of pain (scale)
    pain_intensity = Column(Integer)
    # Location of pain
    pain_location = Column(Text)
    # Frequency of pain
    pain_frequency = Column(Text)
    # Duration of pain
    pain_duration = Column(Text)
    # Character/nature of pain
    pain_character = Column(Text)
    # Action taken for pain
    action_taken = Column(Text)
    
    # Fall risk assessment
    # History of fall in last 3 months
    fall_history_3months = Column(Boolean, default=False)
    # Secondary diagnosis
    secondary_diagnosis = Column(Boolean, default=False)
    # Ambulatory aid used
    ambulatory_aid = Column(String(30))
    # Whether on IV therapy
    iv_therapy = Column(Boolean, default=False)
    # Gait status
    gait_status = Column(String(20))
    # Mental status
    mental_status = Column(String(20))
    # Total Morse fall scale score
    morse_total_score = Column(Integer)
    
    # Pediatric fall risk
    # Age score for Humpty Dumpty scale
    age_score = Column(Integer)
    # Gender score
    gender_score = Column(Integer)
    # Diagnosis score
    diagnosis_score = Column(Integer)
    # Cognitive score
    cognitive_score = Column(Integer)
    # Environmental score
    environmental_score = Column(Integer)
    # Surgery/anesthesia score
    surgery_anesthesia_score = Column(Integer)
    # Medication score
    medication_score = Column(Integer)
    # Total Humpty Dumpty score
    humpty_total_score = Column(Integer)
    
    # Educational needs
    # Needs education on medication use
    needs_medication_education = Column(Boolean, default=False)
    # Needs education on diet and nutrition
    needs_diet_nutrition_education = Column(Boolean, default=False)
    # Needs education on medical equipment use
    needs_medical_equipment_education = Column(Boolean, default=False)
    # Needs education on rehabilitation techniques
    needs_rehabilitation_education = Column(Boolean, default=False)
    # Needs education on drug interactions
    needs_drug_interaction_education = Column(Boolean, default=False)
    # Needs education on pain and symptoms
    needs_pain_symptom_education = Column(Boolean, default=False)
    # Needs education on fall prevention
    needs_fall_prevention_education = Column(Boolean, default=False)
    # Other educational needs
    other_needs = Column(Boolean, default=False)
    # Description of other needs
    other_needs_desc = Column(Text)
    
    # Elderly assessment
    # Daily activities status: independent, needs assistance, dependent
    daily_activities = Column(String(30))
    # Cognitive assessment
    cognitive_assessment = Column(String(30))
    # Mood assessment
    mood_assessment = Column(String(20))
    # Speech disorder
    speech_disorder = Column(Boolean, default=False)
    # Hearing disorder
    hearing_disorder = Column(Boolean, default=False)
    # Vision disorder
    vision_disorder = Column(Boolean, default=False)
    # Sleep disorder
    sleep_disorder = Column(Boolean, default=False)
    
    # Disabled patients assessment
    # Type of disability: hearing, visual, motor, other
    disability_type = Column(String(20))
    # Description if disability is other
    disability_other_desc = Column(Text)
    # Whether the patient has assistive devices
    has_assistive_devices = Column(Boolean, default=False)
    # Description of assistive devices
    assistive_devices_desc = Column(Text)
    
    # Abuse and neglect screening
    # Signs of abuse
    has_signs_of_abuse = Column(Boolean, default=False)
    # Description of abuse
    abuse_description = Column(Text)
    # Whether reported to authorities
    reported_to_authorities = Column(Boolean, default=False)
    # Date of reporting
    reporting_date = Column(DateTime(timezone=True))
    
    # Nurse signature
    nurse_signature = Column(Text)
    
    # Audit fields
    # User who performed the assessment
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    # Timestamp of assessment
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())

class RadiologyAssessment(Base):
    __tablename__ = "radiology_assessments"
    
    # Unique identifier for the radiology assessment
    radiology_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Associated form submission
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.submission_id"), nullable=False)
    
    # Study information
    study_reason = Column(Text)
    gypsum_splint = Column(String(10))  # yes/no
    
    # Medical history
    chronic_disease = Column(String(10))  # yes/no
    chronic_disease_details = Column(Text)
    pacemaker = Column(String(10))  # yes/no
    implants = Column(String(10))  # yes/no
    implants_details = Column(Text)
    pregnancy = Column(String(10))  # yes/no/not_applicable
    
    # Symptoms
    pain_numbness = Column(String(10))  # yes/no
    pain_location = Column(Text)
    pain_duration = Column(Text)
    spinal_deformities = Column(String(10))  # yes/no
    swelling = Column(String(10))  # yes/no
    swelling_location = Column(Text)
    headache = Column(Boolean, default=False)
    vision_problems = Column(Boolean, default=False)
    hearing_problems = Column(Boolean, default=False)
    imbalance = Column(Boolean, default=False)
    
    # Additional medical info
    fever = Column(String(10))  # yes/no
    previous_operations = Column(String(10))  # yes/no
    operation_date = Column(Date)
    operation_reason = Column(Text)
    tumor_history = Column(String(10))  # yes/no
    tumor_location = Column(Text)
    tumor_type = Column(String(100))
    previous_radiology = Column(String(10))  # yes/no
    previous_radiology_type = Column(String(100))
    previous_radiology_date = Column(Date)
    disc_slip = Column(String(10))  # yes/no
    drowsiness_medication = Column(Text)
    current_medication = Column(Text)
    
    # Technical parameters
    dlp = Column(String(50))
    ctd1vol = Column(String(50))
    mas = Column(String(50))
    kv = Column(String(50))
    
    # Diagnosis
    diagnosis = Column(Text)
    
    # Signatures
    patient_signature = Column(Text)
    physician_signature = Column(Text)
    
    # Audit fields
    # User who performed the assessment
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    # Timestamp of assessment
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())

class VisitDocument(Base):
    __tablename__ = "visit_documents"
    
    # Unique identifier for the document
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Associated visit ID
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.visit_id"), nullable=False)
    # Name of the document
    document_name = Column(String(255), nullable=False)
    # Type of the document
    document_type = Column(String(50), nullable=False)
    # File path on disk
    file_path = Column(Text, nullable=False)
    # Size of the file in bytes
    file_size_bytes = Column(Integer)
    # MIME type of the file
    mime_type = Column(String(100))
    # User who uploaded the document
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    # Upload timestamp
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    # Description of the document
    description = Column(Text)
    # Whether the document is active
    is_active = Column(Boolean, default=True)

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    # Unique identifier for the audit entry
    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Name of the table affected
    table_name = Column(String(100), nullable=False)
    # ID of the record affected
    record_id = Column(UUID(as_uuid=True), nullable=False)
    # Type of action: insert, update, delete
    action_type = Column(String(20), nullable=False)
    # Old values before change
    old_values = Column(JSON)
    # New values after change
    new_values = Column(JSON)
    # User who made the change
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    # Timestamp of the change
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    # IP address of the user
    ip_address = Column(String(45))
    # User agent string
    user_agent = Column(Text)

class Report(Base):
    __tablename__ = "reports"
    
    # Unique identifier for the report
    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Associated visit ID
    visit_id = Column(UUID(as_uuid=True), ForeignKey("patient_visits.visit_id"), nullable=False)
    # Summary of the report
    summary = Column(Text)
    # Doctor's notes
    doctor_notes = Column(Text)
    # User who created the report
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    # Creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())