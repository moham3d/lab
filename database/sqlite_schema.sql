-- SQLite Schema for Medical Forms System
-- Adapted from PostgreSQL schema for SQLite compatibility

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK (role IN ('admin', 'doctor', 'nurse', 'technician')) NOT NULL,
    full_name TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    medical_id TEXT UNIQUE NOT NULL,
    id_number TEXT UNIQUE NOT NULL,
    name_arabic TEXT NOT NULL,
    name_english TEXT,
    phone TEXT,
    email TEXT,
    birth_date DATE,
    age INTEGER,
    gender TEXT CHECK (gender IN ('male', 'female')),
    address TEXT,
    emergency_contact TEXT,
    emergency_phone TEXT,
    created_by TEXT REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PET CT Forms
CREATE TABLE IF NOT EXISTS pet_ct_forms (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    patient_id TEXT REFERENCES patients(id) ON DELETE CASCADE,
    created_by TEXT REFERENCES users(id),

    -- Basic Info
    attending_physician TEXT,
    weight DECIMAL(5,2),
    height DECIMAL(5,2),

    -- Medical Info
    fasting_hours INTEGER,
    is_diabetic INTEGER DEFAULT 0,
    blood_sugar DECIMAL(5,2),

    -- Injection Details
    dose TEXT,
    injection_site TEXT,
    injection_time TIME,
    preparation_time TIME,

    -- Technical Parameters
    ctd1vol TEXT,
    dlp TEXT,
    with_contrast INTEGER DEFAULT 0,
    kidney_function TEXT,

    -- Study Info
    is_first_exam INTEGER DEFAULT 1,
    comparison_study_code TEXT,
    report_disc TEXT,

    -- Clinical Info
    diagnosis TEXT NOT NULL,
    study_reason TEXT,

    -- Treatment History
    chemotherapy INTEGER DEFAULT 0,
    chemotherapy_details TEXT,
    chemotherapy_sessions INTEGER,

    radiotherapy INTEGER DEFAULT 0,
    radiotherapy_site TEXT,
    radiotherapy_sessions INTEGER,
    radiotherapy_last_date DATE,

    hormonal_treatment INTEGER DEFAULT 0,
    hormonal_last_dose DATE,

    -- Previous Studies
    previous_studies TEXT, -- JSON string for array of previous study types

    -- Signatures
    patient_signature TEXT, -- Base64 encoded signature
    doctor_signature TEXT,

    -- Metadata
    form_status TEXT DEFAULT 'draft' CHECK (form_status IN ('draft', 'completed', 'reviewed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- General Forms (X-Ray, CT, MRI)
CREATE TABLE IF NOT EXISTS general_forms (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    patient_id TEXT REFERENCES patients(id) ON DELETE CASCADE,
    created_by TEXT REFERENCES users(id),

    -- Form Type
    form_type TEXT CHECK (form_type IN ('xray', 'ct', 'mri')) NOT NULL,

    -- Technical Parameters
    ctd1vol TEXT,
    dlp TEXT,
    kv TEXT,
    mas TEXT,

    -- Study Info
    study_reason TEXT NOT NULL,
    diagnosis TEXT,

    -- Medical History Questions
    has_gypsum_splint INTEGER DEFAULT 0,
    chronic_diseases TEXT,
    has_pacemaker INTEGER DEFAULT 0,
    has_implants INTEGER DEFAULT 0,
    implant_details TEXT,

    -- For Women
    is_pregnant INTEGER DEFAULT 0,

    -- Symptoms
    has_pain INTEGER DEFAULT 0,
    pain_location TEXT,
    pain_duration TEXT,

    has_spinal_deformity INTEGER DEFAULT 0,
    has_swelling INTEGER DEFAULT 0,
    swelling_location TEXT,

    -- Brain Study Specific
    has_headache INTEGER DEFAULT 0,
    has_visual_problems INTEGER DEFAULT 0,
    has_hearing_problems INTEGER DEFAULT 0,
    has_balance_issues INTEGER DEFAULT 0,

    -- General
    has_fever INTEGER DEFAULT 0,

    -- Medical History
    previous_operations TEXT, -- JSON string for array of operations with dates
    tumor_history TEXT,
    previous_investigations TEXT, -- JSON string for array of previous studies
    has_disc_problems INTEGER DEFAULT 0,

    -- Medications
    fall_risk_medications TEXT,
    current_medications TEXT,

    -- Signatures
    patient_signature TEXT,
    doctor_signature TEXT,

    -- Metadata
    form_status TEXT DEFAULT 'draft' CHECK (form_status IN ('draft', 'completed', 'reviewed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Nursing Assessment Forms
CREATE TABLE IF NOT EXISTS nursing_assessments (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    patient_id TEXT REFERENCES patients(id) ON DELETE CASCADE,
    created_by TEXT REFERENCES users(id),

    -- Arrival Info
    arrival_mode TEXT CHECK (arrival_mode IN ('walk', 'wheelchair', 'stretcher', 'ambulatory', 'other')),
    chief_complaint TEXT,
    accompanied_by TEXT,
    language_spoken TEXT DEFAULT 'arabic',

    -- Vital Signs
    temperature DECIMAL(4,1),
    pulse INTEGER,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    respiratory_rate INTEGER,
    oxygen_saturation DECIMAL(4,1),
    blood_sugar DECIMAL(5,2),
    weight DECIMAL(5,2),
    height DECIMAL(5,2),

    -- Psychosocial History
    psychological_problems TEXT, -- JSON string for array of issues
    smoking INTEGER DEFAULT 0,

    -- Allergies
    has_allergies INTEGER DEFAULT 0,
    medication_allergies TEXT,
    food_allergies TEXT,
    other_allergies TEXT,

    -- Nutritional Assessment
    diet_type TEXT DEFAULT 'regular',
    appetite TEXT CHECK (appetite IN ('good', 'poor')),
    has_git_problems INTEGER DEFAULT 0,
    git_problems_details TEXT,
    weight_loss INTEGER DEFAULT 0,
    weight_gain INTEGER DEFAULT 0,
    refer_to_nutritionist INTEGER DEFAULT 0,

    -- Functional Assessment
    self_care_status TEXT, -- JSON string for object with feeding, hygiene, toileting, ambulation statuses
    musculoskeletal_status TEXT, -- JSON string for object with various conditions
    assisting_equipment TEXT, -- JSON string for array of equipment used

    -- Educational Needs
    educational_needs TEXT, -- JSON string for array of educational requirements

    -- Pain Assessment
    has_pain INTEGER DEFAULT 0,
    pain_intensity INTEGER CHECK (pain_intensity BETWEEN 0 AND 10),
    pain_location TEXT,
    pain_frequency TEXT,
    pain_duration TEXT,
    pain_character TEXT,
    pain_action_taken TEXT,

    -- Fall Risk Assessment (Morse Scale)
    fall_risk_score INTEGER DEFAULT 0,
    fall_risk_level TEXT CHECK (fall_risk_level IN ('low', 'moderate', 'high')),
    previous_fall INTEGER DEFAULT 0,
    secondary_diagnosis INTEGER DEFAULT 0,
    ambulatory_aid TEXT,
    iv_therapy INTEGER DEFAULT 0,
    gait_status TEXT,
    mental_status TEXT,

    -- Pediatric Fall Assessment (Humpty Dumpty Scale)
    humpty_dumpty_score INTEGER,
    humpty_dumpty_risk TEXT CHECK (humpty_dumpty_risk IN ('low', 'moderate', 'high')),

    -- Elderly Assessment
    elderly_daily_activities TEXT,
    cognitive_assessment TEXT,
    mood_assessment TEXT,
    speech_disorder INTEGER DEFAULT 0,
    hearing_disorder INTEGER DEFAULT 0,
    vision_disorder INTEGER DEFAULT 0,
    sleep_disorder INTEGER DEFAULT 0,

    -- Disabled Patients Assessment
    disability_type TEXT,
    has_assistive_devices INTEGER DEFAULT 0,

    -- Abuse/Neglect
    abuse_neglect_concern TEXT,

    -- Nurse Info
    nurse_signature TEXT,
    assessment_date DATE DEFAULT CURRENT_DATE,
    assessment_time TIME DEFAULT CURRENT_TIME,

    -- Metadata
    form_status TEXT DEFAULT 'draft' CHECK (form_status IN ('draft', 'completed', 'reviewed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_patients_medical_id ON patients(medical_id);
CREATE INDEX IF NOT EXISTS idx_patients_name_arabic ON patients(name_arabic);
CREATE INDEX IF NOT EXISTS idx_patients_id_number ON patients(id_number);
CREATE INDEX IF NOT EXISTS idx_pet_ct_forms_patient_id ON pet_ct_forms(patient_id);
CREATE INDEX IF NOT EXISTS idx_pet_ct_forms_created_at ON pet_ct_forms(created_at);
CREATE INDEX IF NOT EXISTS idx_general_forms_patient_id ON general_forms(patient_id);
CREATE INDEX IF NOT EXISTS idx_general_forms_form_type ON general_forms(form_type);
CREATE INDEX IF NOT EXISTS idx_nursing_assessments_patient_id ON nursing_assessments(patient_id);
CREATE INDEX IF NOT EXISTS idx_nursing_assessments_assessment_date ON nursing_assessments(assessment_date);

-- Insert sample users
INSERT OR IGNORE INTO users (username, email, password_hash, role, full_name) VALUES
('admin', 'admin@hospital.com', '$2b$10$dummy_hash_here', 'admin', 'System Administrator'),
('dr.ahmed', 'ahmed@hospital.com', '$2b$10$dummy_hash_here', 'doctor', 'Dr. Ahmed Mohamed'),
('nurse.sara', 'sara@hospital.com', '$2b$10$dummy_hash_here', 'nurse', 'Sara Ali');

-- Insert sample patient
INSERT OR IGNORE INTO patients (medical_id, id_number, name_arabic, name_english, phone, birth_date, age, gender) VALUES
('MED-2024-001', '12345678901234', 'أحمد محمد علي حسن', 'Ahmed Mohamed Ali Hassan', '+201234567890', '1985-05-15', 39, 'male'),
('MED-2024-002', '98765432109876', 'فاطمة أحمد سالم', 'Fatima Ahmed Salem', '+201234567891', '1979-03-20', 45, 'female');