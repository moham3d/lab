-- Medical Forms Database Schema
-- Drop existing tables if they exist
DROP TABLE IF EXISTS nursing_assessments CASCADE;
DROP TABLE IF EXISTS general_forms CASCADE;
DROP TABLE IF EXISTS pet_ct_forms CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('admin', 'doctor', 'nurse', 'technician')) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients table
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medical_id VARCHAR(50) UNIQUE NOT NULL,
    name_arabic VARCHAR(255) NOT NULL,
    name_english VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    birth_date DATE,
    age INTEGER,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female')),
    address TEXT,
    emergency_contact VARCHAR(255),
    emergency_phone VARCHAR(20),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PET CT Forms
CREATE TABLE pet_ct_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    
    -- Basic Info
    attending_physician VARCHAR(255),
    weight DECIMAL(5,2),
    height DECIMAL(5,2),
    
    -- Medical Info
    fasting_hours INTEGER,
    is_diabetic BOOLEAN DEFAULT false,
    blood_sugar DECIMAL(5,2),
    
    -- Injection Details
    dose VARCHAR(100),
    injection_site VARCHAR(100),
    injection_time TIME,
    preparation_time TIME,
    
    -- Technical Parameters
    ctd1vol VARCHAR(50),
    dlp VARCHAR(50),
    with_contrast BOOLEAN DEFAULT false,
    kidney_function TEXT,
    
    -- Study Info
    is_first_exam BOOLEAN DEFAULT true,
    comparison_study_code VARCHAR(50),
    report_disc VARCHAR(100),
    
    -- Clinical Info
    diagnosis TEXT NOT NULL,
    study_reason TEXT,
    
    -- Treatment History
    chemotherapy BOOLEAN DEFAULT false,
    chemotherapy_details TEXT,
    chemotherapy_sessions INTEGER,
    
    radiotherapy BOOLEAN DEFAULT false,
    radiotherapy_site VARCHAR(255),
    radiotherapy_sessions INTEGER,
    radiotherapy_last_date DATE,
    
    hormonal_treatment BOOLEAN DEFAULT false,
    hormonal_last_dose DATE,
    
    -- Previous Studies
    previous_studies JSONB, -- Store array of previous study types
    
    -- Signatures
    patient_signature TEXT, -- Base64 encoded signature
    doctor_signature TEXT,
    
    -- Metadata
    form_status VARCHAR(20) DEFAULT 'draft' CHECK (form_status IN ('draft', 'completed', 'reviewed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- General Forms (X-Ray, CT, MRI)
CREATE TABLE general_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    
    -- Form Type
    form_type VARCHAR(20) CHECK (form_type IN ('xray', 'ct', 'mri')) NOT NULL,
    
    -- Technical Parameters
    ctd1vol VARCHAR(50),
    dlp VARCHAR(50),
    kv VARCHAR(50),
    mas VARCHAR(50),
    
    -- Study Info
    study_reason TEXT NOT NULL,
    diagnosis TEXT,
    
    -- Medical History Questions
    has_gypsum_splint BOOLEAN DEFAULT false,
    chronic_diseases TEXT,
    has_pacemaker BOOLEAN DEFAULT false,
    has_implants BOOLEAN DEFAULT false,
    implant_details TEXT,
    
    -- For Women
    is_pregnant BOOLEAN DEFAULT false,
    
    -- Symptoms
    has_pain BOOLEAN DEFAULT false,
    pain_location TEXT,
    pain_duration TEXT,
    
    has_spinal_deformity BOOLEAN DEFAULT false,
    has_swelling BOOLEAN DEFAULT false,
    swelling_location TEXT,
    
    -- Brain Study Specific
    has_headache BOOLEAN DEFAULT false,
    has_visual_problems BOOLEAN DEFAULT false,
    has_hearing_problems BOOLEAN DEFAULT false,
    has_balance_issues BOOLEAN DEFAULT false,
    
    -- General
    has_fever BOOLEAN DEFAULT false,
    
    -- Medical History
    previous_operations JSONB, -- Array of operations with dates
    tumor_history TEXT,
    previous_investigations JSONB, -- Array of previous studies
    has_disc_problems BOOLEAN DEFAULT false,
    
    -- Medications
    fall_risk_medications TEXT,
    current_medications TEXT,
    
    -- Signatures
    patient_signature TEXT,
    doctor_signature TEXT,
    
    -- Metadata
    form_status VARCHAR(20) DEFAULT 'draft' CHECK (form_status IN ('draft', 'completed', 'reviewed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nursing Assessment Forms
CREATE TABLE nursing_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    
    -- Arrival Info
    arrival_mode VARCHAR(20) CHECK (arrival_mode IN ('walk', 'wheelchair', 'stretcher', 'ambulatory', 'other')),
    chief_complaint TEXT,
    accompanied_by VARCHAR(50),
    language_spoken VARCHAR(50) DEFAULT 'arabic',
    
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
    psychological_problems JSONB, -- Array of issues
    smoking BOOLEAN DEFAULT false,
    
    -- Allergies
    has_allergies BOOLEAN DEFAULT false,
    medication_allergies TEXT,
    food_allergies TEXT,
    other_allergies TEXT,
    
    -- Nutritional Assessment
    diet_type VARCHAR(50) DEFAULT 'regular',
    appetite VARCHAR(20) CHECK (appetite IN ('good', 'poor')),
    has_git_problems BOOLEAN DEFAULT false,
    git_problems_details TEXT,
    weight_loss BOOLEAN DEFAULT false,
    weight_gain BOOLEAN DEFAULT false,
    refer_to_nutritionist BOOLEAN DEFAULT false,
    
    -- Functional Assessment
    self_care_status JSONB, -- Object with feeding, hygiene, toileting, ambulation statuses
    musculoskeletal_status JSONB, -- Object with various conditions
    assisting_equipment JSONB, -- Array of equipment used
    
    -- Educational Needs
    educational_needs JSONB, -- Array of educational requirements
    
    -- Pain Assessment
    has_pain BOOLEAN DEFAULT false,
    pain_intensity INTEGER CHECK (pain_intensity BETWEEN 0 AND 10),
    pain_location TEXT,
    pain_frequency TEXT,
    pain_duration TEXT,
    pain_character TEXT,
    pain_action_taken TEXT,
    
    -- Fall Risk Assessment (Morse Scale)
    fall_risk_score INTEGER DEFAULT 0,
    fall_risk_level VARCHAR(20) CHECK (fall_risk_level IN ('low', 'moderate', 'high')),
    previous_fall BOOLEAN DEFAULT false,
    secondary_diagnosis BOOLEAN DEFAULT false,
    ambulatory_aid VARCHAR(50),
    iv_therapy BOOLEAN DEFAULT false,
    gait_status VARCHAR(20),
    mental_status VARCHAR(20),
    
    -- Pediatric Fall Assessment (Humpty Dumpty Scale)
    humpty_dumpty_score INTEGER,
    humpty_dumpty_risk VARCHAR(20) CHECK (humpty_dumpty_risk IN ('low', 'moderate', 'high')),
    
    -- Elderly Assessment
    elderly_daily_activities VARCHAR(20),
    cognitive_assessment VARCHAR(20),
    mood_assessment VARCHAR(20),
    speech_disorder BOOLEAN DEFAULT false,
    hearing_disorder BOOLEAN DEFAULT false,
    vision_disorder BOOLEAN DEFAULT false,
    sleep_disorder BOOLEAN DEFAULT false,
    
    -- Disabled Patients Assessment
    disability_type VARCHAR(50),
    has_assistive_devices BOOLEAN DEFAULT false,
    
    -- Abuse/Neglect
    abuse_neglect_concern TEXT,
    
    -- Nurse Info
    nurse_signature TEXT,
    assessment_date DATE DEFAULT CURRENT_DATE,
    assessment_time TIME DEFAULT CURRENT_TIME,
    
    -- Metadata
    form_status VARCHAR(20) DEFAULT 'draft' CHECK (form_status IN ('draft', 'completed', 'reviewed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_patients_medical_id ON patients(medical_id);
CREATE INDEX idx_patients_name_arabic ON patients(name_arabic);
CREATE INDEX idx_pet_ct_forms_patient_id ON pet_ct_forms(patient_id);
CREATE INDEX idx_pet_ct_forms_created_at ON pet_ct_forms(created_at);
CREATE INDEX idx_general_forms_patient_id ON general_forms(patient_id);
CREATE INDEX idx_general_forms_form_type ON general_forms(form_type);
CREATE INDEX idx_nursing_assessments_patient_id ON nursing_assessments(patient_id);
CREATE INDEX idx_nursing_assessments_assessment_date ON nursing_assessments(assessment_date);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to update updated_at automatically
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pet_ct_forms_updated_at BEFORE UPDATE ON pet_ct_forms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_general_forms_updated_at BEFORE UPDATE ON general_forms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_nursing_assessments_updated_at BEFORE UPDATE ON nursing_assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample users
INSERT INTO users (username, email, password_hash, role, full_name) VALUES
('admin', 'admin@hospital.com', '$2b$10$dummy_hash_here', 'admin', 'System Administrator'),
('dr.ahmed', 'ahmed@hospital.com', '$2b$10$dummy_hash_here', 'doctor', 'Dr. Ahmed Mohamed'),
('nurse.sara', 'sara@hospital.com', '$2b$10$dummy_hash_here', 'nurse', 'Sara Ali');

-- Insert sample patient
INSERT INTO patients (medical_id, name_arabic, name_english, phone, birth_date, age, gender) VALUES
('MED-2024-001', 'أحمد محمد علي حسن', 'Ahmed Mohamed Ali Hassan', '+201234567890', '1985-05-15', 39, 'male');