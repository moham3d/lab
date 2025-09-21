-- ===================================================================
-- Patient Visit Management System - PostgreSQL Database Schema
-- ===================================================================
-- This file is executed during Docker container initialization
-- ===================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===================================================================
-- CORE TABLES
-- ===================================================================

-- User management for nurses and physicians
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('nurse', 'physician', 'admin')),
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Patients table (UUID as primary identifier)
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ssn VARCHAR(20) UNIQUE NOT NULL, -- Social Security Number (unique but not primary)
    mobile_number VARCHAR(20) NOT NULL,
    phone_number VARCHAR(20), -- Additional phone number (landline, work, etc.)
    medical_number VARCHAR(50) UNIQUE, -- Hospital/Medical record number if exists
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    address TEXT, -- Patient address
    emergency_contact_name VARCHAR(255), -- Emergency contact information
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50), -- Relationship to patient
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(user_id), -- Reference to user who created the record
    updated_by UUID REFERENCES users(user_id), -- Reference to user who last updated the record
    is_active BOOLEAN DEFAULT TRUE
);

-- Patient visits
CREATE TABLE patient_visits (
    visit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    visit_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    visit_status VARCHAR(20) DEFAULT 'open' CHECK (visit_status IN ('open', 'in_progress', 'completed', 'cancelled')),
    primary_diagnosis TEXT, -- التشخيص الأساسي
    secondary_diagnosis TEXT, -- التشخيص الثانوي
    diagnosis_code VARCHAR(20), -- ICD-10 or other coding system
    visit_type VARCHAR(30) DEFAULT 'outpatient' CHECK (visit_type IN ('outpatient', 'inpatient', 'emergency', 'consultation')),
    department VARCHAR(100), -- Department/Unit
    created_by UUID NOT NULL REFERENCES users(user_id), -- Nurse who created the visit
    assigned_physician UUID REFERENCES users(user_id), -- Physician assigned to the visit
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- FORM DEFINITIONS AND DATA STORAGE
-- ===================================================================

-- Form definitions (SH.MR.FRM.05, SH.MR.FRM.04, etc.)
CREATE TABLE form_definitions (
    form_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_code VARCHAR(20) UNIQUE NOT NULL, -- e.g., 'SH.MR.FRM.05'
    form_name VARCHAR(255) NOT NULL,
    form_version VARCHAR(10) NOT NULL,
    form_description TEXT,
    form_role VARCHAR(20) NOT NULL CHECK (form_role IN ('nurse', 'physician', 'both')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Form submissions for each visit
CREATE TABLE form_submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    visit_id UUID NOT NULL REFERENCES patient_visits(visit_id) ON DELETE CASCADE,
    form_id UUID NOT NULL REFERENCES form_definitions(form_id),
    submitted_by UUID NOT NULL REFERENCES users(user_id),
    submission_status VARCHAR(20) DEFAULT 'draft' CHECK (submission_status IN ('draft', 'submitted', 'approved', 'rejected')),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_by UUID REFERENCES users(user_id),
    approved_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(visit_id, form_id) -- One submission per form per visit
);

-- ===================================================================
-- NURSING ASSESSMENT FORM (SH.MR.FRM.05) SPECIFIC TABLES
-- ===================================================================

-- Nursing assessment main data
CREATE TABLE nursing_assessments (
    assessment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES form_submissions(submission_id) ON DELETE CASCADE,

    -- Mode of arrival
    mode_of_arrival VARCHAR(20) CHECK (mode_of_arrival IN ('walk', 'ambulatory', 'wheelchair', 'stretcher', 'other')),
    arrival_other_desc TEXT,

    -- Chief complaint and demographics
    age INTEGER,
    chief_complaint TEXT,
    accompanied_by VARCHAR(20) CHECK (accompanied_by IN ('spouse', 'relative', 'other', 'alone')),
    language_spoken VARCHAR(20) DEFAULT 'arabic' CHECK (language_spoken IN ('arabic', 'english', 'other')),
    language_other_desc TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vital signs
CREATE TABLE vital_signs (
    vital_signs_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    temperature_celsius DECIMAL(4,2),
    pulse_bpm INTEGER,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    respiratory_rate_per_min INTEGER,
    oxygen_saturation_percent DECIMAL(5,2),
    blood_sugar_mg_dl INTEGER,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),

    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Psychosocial history
CREATE TABLE psychosocial_history (
    psychosocial_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    psychological_problem VARCHAR(50) CHECK (psychological_problem IN ('none', 'depressed', 'agitated', 'anxious', 'isolated', 'confused', 'other')),
    psychological_other_desc TEXT,
    is_smoker BOOLEAN,

    -- Allergies
    has_allergies BOOLEAN DEFAULT FALSE,
    medication_allergies TEXT,
    food_allergies TEXT,
    other_allergies TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Nutritional screening
CREATE TABLE nutritional_screening (
    nutrition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    diet_type VARCHAR(20) DEFAULT 'regular' CHECK (diet_type IN ('regular', 'special')),
    special_diet_desc TEXT,
    appetite VARCHAR(20) CHECK (appetite IN ('good', 'poor')),
    has_git_problems BOOLEAN DEFAULT FALSE,
    git_problems_desc TEXT,
    has_weight_loss BOOLEAN DEFAULT FALSE,
    has_weight_gain BOOLEAN DEFAULT FALSE,
    refer_to_nutritionist BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Functional assessment
CREATE TABLE functional_assessment (
    functional_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    -- Self-care capabilities
    feeding_status VARCHAR(20) CHECK (feeding_status IN ('independent', 'needs_supervision', 'totally_dependent')),
    hygiene_status VARCHAR(20) CHECK (hygiene_status IN ('independent', 'needs_supervision', 'totally_dependent')),
    toileting_status VARCHAR(20) CHECK (toileting_status IN ('independent', 'needs_supervision', 'totally_dependent')),
    ambulation_status VARCHAR(20) CHECK (ambulation_status IN ('independent', 'needs_supervision', 'totally_dependent')),

    -- Musculoskeletal status
    has_musculoskeletal_problems BOOLEAN DEFAULT FALSE,
    has_deformities BOOLEAN DEFAULT FALSE,
    has_contractures BOOLEAN DEFAULT FALSE,
    is_amputee BOOLEAN DEFAULT FALSE,
    is_bedridden BOOLEAN DEFAULT FALSE,
    has_musculoskeletal_pain BOOLEAN DEFAULT FALSE,

    -- Assisting equipment
    uses_walker BOOLEAN DEFAULT FALSE,
    uses_wheelchair BOOLEAN DEFAULT FALSE,
    uses_transfer_device BOOLEAN DEFAULT FALSE,
    uses_raised_toilet_seat BOOLEAN DEFAULT FALSE,
    uses_other_equipment BOOLEAN DEFAULT FALSE,
    other_equipment_desc TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Pain assessment
CREATE TABLE pain_assessment (
    pain_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    pain_intensity INTEGER CHECK (pain_intensity BETWEEN 0 AND 10),
    pain_location TEXT,
    pain_frequency TEXT,
    pain_duration TEXT,
    pain_character TEXT,
    action_taken TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Fall risk assessment (Modified Morse Scale)
CREATE TABLE fall_risk_assessment (
    fall_risk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    -- Morse scale factors
    fall_history_3months BOOLEAN DEFAULT FALSE, -- 25 points if yes
    secondary_diagnosis BOOLEAN DEFAULT FALSE, -- 15 points if yes
    ambulatory_aid VARCHAR(30) CHECK (ambulatory_aid IN ('none', 'bed_rest_chair', 'crutches_walker', 'furniture')), -- 0, 15, 30 points
    iv_therapy BOOLEAN DEFAULT FALSE, -- 20 points if yes
    gait_status VARCHAR(20) CHECK (gait_status IN ('normal', 'weak', 'impaired')), -- 0, 10, 20 points
    mental_status VARCHAR(20) CHECK (mental_status IN ('oriented', 'forgets_limitations', 'unaware')), -- 0, 15 points

    total_score INTEGER,
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'moderate', 'high')), -- Based on total score

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Humpty Dumpty Scale for pediatric patients
CREATE TABLE pediatric_fall_risk (
    pediatric_fall_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    age_score INTEGER, -- Based on age ranges
    gender_score INTEGER, -- Male: 2, Female: 1
    diagnosis_score INTEGER, -- Based on diagnosis type
    cognitive_score INTEGER, -- Based on cognitive status
    environmental_score INTEGER, -- Based on environmental factors
    surgery_anesthesia_score INTEGER, -- Based on recent surgery/anesthesia
    medication_score INTEGER, -- Based on medications used

    total_score INTEGER,
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'moderate', 'high')),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Educational needs assessment
CREATE TABLE educational_needs (
    education_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    needs_medication_education BOOLEAN DEFAULT FALSE,
    needs_diet_nutrition_education BOOLEAN DEFAULT FALSE,
    needs_medical_equipment_education BOOLEAN DEFAULT FALSE,
    needs_rehabilitation_education BOOLEAN DEFAULT FALSE,
    needs_drug_interaction_education BOOLEAN DEFAULT FALSE,
    needs_pain_symptom_education BOOLEAN DEFAULT FALSE,
    needs_fall_prevention_education BOOLEAN DEFAULT FALSE,
    other_needs BOOLEAN DEFAULT FALSE,
    other_needs_desc TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Elderly assessment
CREATE TABLE elderly_assessment (
    elderly_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    daily_activities VARCHAR(30) CHECK (daily_activities IN ('independent', 'needs_help', 'dependent')),
    cognitive_assessment VARCHAR(30) CHECK (cognitive_assessment IN ('normal', 'mild_delirium', 'moderate_delirium', 'severe_delirium')),
    mood_assessment VARCHAR(20) CHECK (mood_assessment IN ('depressed', 'not_depressed')),
    speech_disorder BOOLEAN DEFAULT FALSE,
    hearing_disorder BOOLEAN DEFAULT FALSE,
    vision_disorder BOOLEAN DEFAULT FALSE,
    sleep_disorder BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Disabled patients assessment
CREATE TABLE disabled_assessment (
    disabled_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    disability_type VARCHAR(20) CHECK (disability_type IN ('hearing', 'visual', 'mobility', 'other')),
    disability_other_desc TEXT,
    has_assistive_devices BOOLEAN DEFAULT FALSE,
    assistive_devices_desc TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Abuse and neglect screening
CREATE TABLE abuse_neglect_screening (
    screening_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES nursing_assessments(assessment_id) ON DELETE CASCADE,

    has_signs_of_abuse BOOLEAN DEFAULT FALSE,
    abuse_description TEXT,
    reported_to_authorities BOOLEAN DEFAULT FALSE,
    reporting_date TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- RADIOLOGY FORM (SH.MR.FRM.04) SPECIFIC TABLES
-- ===================================================================

-- Radiology assessments
CREATE TABLE radiology_assessments (
    radiology_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID NOT NULL REFERENCES form_submissions(submission_id) ON DELETE CASCADE,

    treating_physician VARCHAR(255),
    department VARCHAR(100),
    fasting_hours INTEGER,
    is_diabetic BOOLEAN DEFAULT FALSE,
    blood_sugar_level INTEGER,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),

    -- Injection details
    dose_amount DECIMAL(10,2),
    preparation_time TIME,
    injection_time TIME,
    injection_site VARCHAR(100),

    -- Technical parameters
    ctd1vol DECIMAL(10,2),
    dlp DECIMAL(10,2),

    -- Contrast and kidney function
    uses_contrast BOOLEAN DEFAULT FALSE,
    kidney_function_value DECIMAL(10,2),

    -- Study details
    is_first_time BOOLEAN DEFAULT TRUE,
    is_comparison BOOLEAN DEFAULT FALSE,
    previous_study_code VARCHAR(50),
    requires_report BOOLEAN DEFAULT TRUE,
    requires_cd BOOLEAN DEFAULT FALSE,

    diagnosis TEXT,
    reason_for_study TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Treatment history for radiology patients
CREATE TABLE treatment_history (
    treatment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    radiology_id UUID NOT NULL REFERENCES radiology_assessments(radiology_id) ON DELETE CASCADE,

    -- Chemotherapy
    has_chemotherapy BOOLEAN DEFAULT FALSE,
    chemo_type VARCHAR(20) CHECK (chemo_type IN ('tablets', 'infusion')),
    chemo_details TEXT,
    chemo_sessions INTEGER,
    chemo_last_date DATE,

    -- Radiotherapy
    has_radiotherapy BOOLEAN DEFAULT FALSE,
    radiotherapy_site TEXT,
    radiotherapy_sessions INTEGER,
    radiotherapy_last_date DATE,

    -- Hormonal treatment
    has_hormonal_treatment BOOLEAN DEFAULT FALSE,
    hormonal_last_dose_date DATE,

    -- Other treatments
    other_treatments TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Previous imaging history
CREATE TABLE imaging_history (
    imaging_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    radiology_id UUID NOT NULL REFERENCES radiology_assessments(radiology_id) ON DELETE CASCADE,

    has_operations BOOLEAN DEFAULT FALSE,
    has_endoscopy BOOLEAN DEFAULT FALSE,
    has_biopsies BOOLEAN DEFAULT FALSE,
    has_tc_mdp_bone_scan BOOLEAN DEFAULT FALSE,
    has_tc_dtpa_kidney_scan BOOLEAN DEFAULT FALSE,
    has_mri BOOLEAN DEFAULT FALSE,
    has_mammography BOOLEAN DEFAULT FALSE,
    has_ct BOOLEAN DEFAULT FALSE,
    has_xray BOOLEAN DEFAULT FALSE,
    has_ultrasound BOOLEAN DEFAULT FALSE,
    has_other_imaging BOOLEAN DEFAULT FALSE,
    other_imaging_desc TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- DOCUMENT STORAGE
-- ===================================================================

-- Document storage for scanned papers and attachments
CREATE TABLE visit_documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    visit_id UUID NOT NULL REFERENCES patient_visits(visit_id) ON DELETE CASCADE,
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- 'scanned_form', 'lab_result', 'image', 'report', etc.
    file_path TEXT NOT NULL, -- Path to stored file
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    uploaded_by UUID NOT NULL REFERENCES users(user_id),
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- ===================================================================
-- AUDIT AND LOGGING
-- ===================================================================

-- Audit trail for all changes
CREATE TABLE audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action_type VARCHAR(20) NOT NULL CHECK (action_type IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_by UUID NOT NULL REFERENCES users(user_id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- ===================================================================
-- INDEXES FOR PERFORMANCE
-- ===================================================================

-- Primary lookup indexes
CREATE INDEX idx_patients_mobile ON patients(mobile_number);
CREATE INDEX idx_patients_phone ON patients(phone_number);
CREATE INDEX idx_patients_medical_number ON patients(medical_number);
CREATE INDEX idx_patients_name ON patients USING gin(to_tsvector('english', full_name));
CREATE INDEX idx_visits_patient ON patient_visits(patient_id);
CREATE INDEX idx_visits_date ON patient_visits(visit_date);
CREATE INDEX idx_visits_status ON patient_visits(visit_status);
CREATE INDEX idx_visits_physician ON patient_visits(assigned_physician);
CREATE INDEX idx_visits_diagnosis ON patient_visits USING gin(to_tsvector('english', primary_diagnosis));

-- Form submission indexes
CREATE INDEX idx_submissions_visit ON form_submissions(visit_id);
CREATE INDEX idx_submissions_form ON form_submissions(form_id);
CREATE INDEX idx_submissions_status ON form_submissions(submission_status);

-- Assessment indexes
CREATE INDEX idx_nursing_assessment ON nursing_assessments(submission_id);
CREATE INDEX idx_radiology_assessment ON radiology_assessments(submission_id);

-- Document indexes
CREATE INDEX idx_documents_visit ON visit_documents(visit_id);
CREATE INDEX idx_documents_type ON visit_documents(document_type);

-- Audit indexes
CREATE INDEX idx_audit_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_user_date ON audit_log(changed_by, changed_at);

-- ===================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ===================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS '
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
' LANGUAGE plpgsql;

-- Apply update triggers
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_visits_updated_at BEFORE UPDATE ON patient_visits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- INITIAL DATA SETUP
-- ===================================================================

-- Insert form definitions
INSERT INTO form_definitions (form_code, form_name, form_version, form_description, form_role) VALUES
('SH.MR.FRM.05', 'Nursing Screening & Assessment', '1.0', 'Comprehensive nursing assessment and screening form', 'nurse'),
('SH.MR.FRM.04', 'Radiology Assessment', '1.0', 'Radiology preparation and assessment form', 'physician');

-- ===================================================================
-- VIEWS FOR COMMON QUERIES
-- ===================================================================

-- View for active patient visits with form status
CREATE VIEW v_active_visits AS
SELECT
    pv.visit_id,
    pv.patient_id,
    p.full_name,
    p.mobile_number,
    p.phone_number,
    p.medical_number,
    pv.visit_date,
    pv.visit_status,
    pv.primary_diagnosis,
    pv.secondary_diagnosis,
    pv.visit_type,
    pv.department,
    u_creator.full_name as created_by_nurse,
    u_physician.full_name as assigned_physician,
    COALESCE(nursing_submitted.submission_status, 'not_started') as nursing_form_status,
    COALESCE(radiology_submitted.submission_status, 'not_started') as radiology_form_status
FROM patient_visits pv
JOIN patients p ON pv.patient_id = p.id
JOIN users u_creator ON pv.created_by = u_creator.user_id
LEFT JOIN users u_physician ON pv.assigned_physician = u_physician.user_id
LEFT JOIN (
    SELECT fs.visit_id, fs.submission_status
    FROM form_submissions fs
    JOIN form_definitions fd ON fs.form_id = fd.form_id
    WHERE fd.form_code = 'SH.MR.FRM.05'
) nursing_submitted ON pv.visit_id = nursing_submitted.visit_id
LEFT JOIN (
    SELECT fs.visit_id, fs.submission_status
    FROM form_submissions fs
    JOIN form_definitions fd ON fs.form_id = fd.form_id
    WHERE fd.form_code = 'SH.MR.FRM.04'
) radiology_submitted ON pv.visit_id = radiology_submitted.visit_id
WHERE pv.visit_status IN ('open', 'in_progress');

-- View for patient visit history
CREATE VIEW v_patient_history AS
SELECT
    p.ssn,
    p.full_name,
    p.mobile_number,
    p.phone_number,
    p.medical_number,
    pv.visit_id,
    pv.visit_date,
    pv.visit_status,
    pv.primary_diagnosis,
    pv.secondary_diagnosis,
    pv.visit_type,
    pv.department,
    COUNT(vd.document_id) as document_count,
    COUNT(fs.submission_id) as form_count
FROM patients p
LEFT JOIN patient_visits pv ON p.id = pv.patient_id
LEFT JOIN visit_documents vd ON pv.visit_id = vd.visit_id AND vd.is_active = true
LEFT JOIN form_submissions fs ON pv.visit_id = fs.visit_id
GROUP BY p.ssn, p.full_name, p.mobile_number, p.phone_number, p.medical_number,
         pv.visit_id, pv.visit_date, pv.visit_status, pv.primary_diagnosis,
         pv.secondary_diagnosis, pv.visit_type, pv.department
ORDER BY pv.visit_date DESC;