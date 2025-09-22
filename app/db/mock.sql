-- ===================================================================
-- Mock Data for Healthcare Patient Management System
-- ===================================================================
-- Sample data for testing and development
-- ===================================================================

-- Insert sample patients
INSERT INTO patients (ssn, mobile_number, phone_number, medical_number, full_name, date_of_birth, gender, address, emergency_contact_name, emergency_contact_phone, emergency_contact_relation, created_by) VALUES
('12345678901234', '01234567890', '0223456789', 'MED001', 'Ahmed Mohamed Hassan', '1985-03-15', 'male', '123 Nile Street, Cairo', 'Fatima Hassan', '01234567891', 'wife', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f'),
('23456789012345', '01234567891', '0223456788', 'MED002', 'Sara Ali Mahmoud', '1990-07-22', 'female', '456 Pyramids Road, Giza', 'Omar Mahmoud', '01234567892', 'husband', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f'),
('34567890123456', '01234567892', '0223456787', 'MED003', 'Mohamed Ibrahim Saleh', '1975-11-08', 'male', '789 Alexandria Highway, Alexandria', 'Amina Saleh', '01234567893', 'daughter', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f'),
('45678901234567', '01234567893', '0223456786', 'MED004', 'Layla Hassan Omar', '1982-05-30', 'female', '321 Suez Canal Street, Suez', 'Hassan Omar', '01234567894', 'father', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f'),
('56789012345678', '01234567894', '0223456785', 'MED005', 'Omar Ahmed Khalil', '1995-09-12', 'male', '654 Red Sea Avenue, Hurghada', 'Ahmed Khalil', '01234567895', 'father', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f');

-- Insert sample visits
INSERT INTO patient_visits (patient_ssn, visit_date, visit_status, primary_diagnosis, secondary_diagnosis, diagnosis_code, visit_type, department, created_by, assigned_physician, notes) VALUES
('12345678901234', CURRENT_TIMESTAMP - INTERVAL '2 days', 'completed', 'Hypertension', 'Type 2 Diabetes', 'I10', 'outpatient', 'Cardiology', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'Patient responded well to medication. Follow up in 3 months.'),
('23456789012345', CURRENT_TIMESTAMP - INTERVAL '1 day', 'in_progress', 'Acute Bronchitis', NULL, 'J20.9', 'outpatient', 'Pulmonology', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'Prescribed antibiotics and cough syrup. Monitor symptoms.'),
('34567890123456', CURRENT_TIMESTAMP, 'open', 'Knee Osteoarthritis', NULL, 'M17.9', 'outpatient', 'Orthopedics', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'Recommended physical therapy and pain management.'),
('45678901234567', CURRENT_TIMESTAMP + INTERVAL '1 day', 'open', 'Routine Checkup', NULL, 'Z00.00', 'outpatient', 'General Medicine', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'Annual health checkup appointment.'),
('56789012345678', CURRENT_TIMESTAMP + INTERVAL '2 days', 'open', 'Dental Caries', NULL, 'K02.9', 'outpatient', 'Dentistry', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'Multiple cavities detected. Needs dental work.');

-- Insert form submissions (linking visits to forms)
INSERT INTO form_submissions (visit_id, form_id, submitted_by, submission_status) VALUES
((SELECT visit_id FROM patient_visits WHERE patient_ssn = '12345678901234' LIMIT 1), (SELECT form_id FROM form_definitions WHERE form_code = 'SH.MR.FRM.05' LIMIT 1), 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'submitted'),
((SELECT visit_id FROM patient_visits WHERE patient_ssn = '23456789012345' LIMIT 1), (SELECT form_id FROM form_definitions WHERE form_code = 'SH.MR.FRM.05' LIMIT 1), 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'draft'),
((SELECT visit_id FROM patient_visits WHERE patient_ssn = '34567890123456' LIMIT 1), (SELECT form_id FROM form_definitions WHERE form_code = 'SH.MR.FRM.04' LIMIT 1), 'fa0038a5-85b1-44ef-a18e-98f71835ad2f', 'submitted');

-- Insert sample nursing assessment (partial data for testing)
INSERT INTO nursing_assessments (submission_id, age, chief_complaint, temperature_celsius, pulse_bpm, blood_pressure_systolic, blood_pressure_diastolic, respiratory_rate_per_min, oxygen_saturation_percent, weight_kg, height_cm, general_condition, consciousness_level, skin_condition, mobility_status, assessed_by) VALUES
((SELECT submission_id FROM form_submissions WHERE visit_id = (SELECT visit_id FROM patient_visits WHERE patient_ssn = '12345678901234' LIMIT 1) LIMIT 1), 38, 'High blood pressure and chest pain', 36.8, 78, 145, 92, 16, 98.0, 75.5, 170.0, 'Stable', 'Alert and oriented', 'Normal skin color and turgor', 'Independent', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f'),
((SELECT submission_id FROM form_submissions WHERE visit_id = (SELECT visit_id FROM patient_visits WHERE patient_ssn = '23456789012345' LIMIT 1) LIMIT 1), 33, 'Cough and fever', 38.2, 85, 120, 80, 18, 96.0, 62.0, 165.0, 'Fair', 'Alert', 'Warm and dry', 'Independent with assistance', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f');

-- Insert sample radiology assessment (partial data for testing)
INSERT INTO radiology_assessments (submission_id, treating_physician, department, diagnosis, findings, impression, modality, body_region, assessed_by) VALUES
((SELECT submission_id FROM form_submissions WHERE visit_id = (SELECT visit_id FROM patient_visits WHERE patient_ssn = '34567890123456' LIMIT 1) LIMIT 1), 'Dr. Ahmed Hassan', 'Orthopedics', 'Knee pain', 'Mild osteoarthritis changes in the knee joint', 'Early degenerative changes', 'X-ray', 'Knee', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f');

-- Insert sample audit logs
INSERT INTO audit_log (table_name, record_id, action_type, old_values, new_values, changed_by) VALUES
('patients', '12345678901234', 'INSERT', NULL, '{"ssn": "12345678901234", "full_name": "Ahmed Mohamed Hassan"}', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f'),
('patient_visits', (SELECT visit_id FROM patient_visits WHERE patient_ssn = '12345678901234' LIMIT 1), 'INSERT', NULL, '{"patient_ssn": "12345678901234", "visit_status": "completed"}', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f'),
('nursing_assessments', (SELECT assessment_id FROM nursing_assessments LIMIT 1), 'INSERT', NULL, '{"temperature_celsius": 36.8, "pulse_bpm": 78}', 'fa0038a5-85b1-44ef-a18e-98f71835ad2f');