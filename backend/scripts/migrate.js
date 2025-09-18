const fs = require('fs').promises;
const path = require('path');
const { Pool } = require('pg');

async function migrateData() {
  console.log('🚀 Starting data migration from JSON to PostgreSQL...');

  // Create PostgreSQL connection
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL || 'postgresql://localhost:5432/medical_forms',
  });

  try {
    // Check if JSON database file exists
    const jsonDbPath = path.join(__dirname, '..', 'database', 'data.json');
    let jsonData = null;

    try {
      const data = await fs.readFile(jsonDbPath, 'utf8');
      jsonData = JSON.parse(data);
      console.log('✅ Found JSON database file with data');
    } catch (error) {
      console.log('ℹ️  No existing JSON database found, starting with empty database');
      jsonData = {
        patients: [],
        pet_ct_forms: [],
        general_forms: [],
        nursing_assessments: []
      };
    }

    // Connect to PostgreSQL
    const client = await pool.connect();
    console.log('✅ Connected to PostgreSQL database');

    // Begin transaction
    await client.query('BEGIN');

    // Migrate patients
    console.log('📋 Migrating patients...');
    for (const patient of jsonData.patients) {
      const query = `
        INSERT INTO patients (
          id, medical_id, id_number, name_arabic, name_english,
          phone, email, birth_date, age, gender, address,
          emergency_contact, emergency_phone, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        ON CONFLICT (id) DO NOTHING
      `;

      await client.query(query, [
        patient.id,
        patient.medicalId,
        patient.idNumber,
        patient.nameArabic,
        patient.nameEnglish,
        patient.phone,
        patient.email,
        patient.birthDate,
        patient.age,
        patient.gender,
        patient.address,
        patient.emergencyContact,
        patient.emergencyPhone,
        patient.createdAt,
        patient.updatedAt
      ]);
    }
    console.log(`✅ Migrated ${jsonData.patients.length} patients`);

    // Migrate PET-CT forms
    console.log('📋 Migrating PET-CT forms...');
    for (const form of jsonData.pet_ct_forms) {
      const query = `
        INSERT INTO pet_ct_forms (
          id, patient_id, form_status, created_by, created_at, updated_at,
          examination_type, radiopharmaceutical, dose, route, injection_time,
          acquisition_parameters, reconstruction_parameters, clinical_history,
          findings, impression, recommendations, radiologist_name,
          radiologist_signature, technician_name, technician_signature
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
        )
        ON CONFLICT (id) DO NOTHING
      `;

      await client.query(query, [
        form.id,
        form.patientId,
        form.formStatus,
        form.createdBy,
        form.createdAt,
        form.updatedAt,
        form.examinationType,
        form.radiopharmaceutical,
        form.dose,
        form.route,
        form.injectionTime,
        form.acquisitionParameters,
        form.reconstructionParameters,
        form.clinicalHistory,
        form.findings,
        form.impression,
        form.recommendations,
        form.radiologistName,
        form.radiologistSignature,
        form.technicianName,
        form.technicianSignature
      ]);
    }
    console.log(`✅ Migrated ${jsonData.pet_ct_forms.length} PET-CT forms`);

    // Migrate General forms
    console.log('📋 Migrating General forms...');
    for (const form of jsonData.general_forms) {
      const query = `
        INSERT INTO general_forms (
          id, patient_id, form_type, form_status, created_by, created_at, updated_at,
          examination_type, technical_parameters, clinical_indication,
          medical_history, symptoms, findings, conclusion, radiologist_name,
          radiologist_signature, technician_name, technician_signature
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
        )
        ON CONFLICT (id) DO NOTHING
      `;

      await client.query(query, [
        form.id,
        form.patientId,
        form.formType,
        form.formStatus,
        form.createdBy,
        form.createdAt,
        form.updatedAt,
        form.examinationType,
        form.technicalParameters,
        form.clinicalIndication,
        form.medicalHistory,
        form.symptoms,
        form.findings,
        form.conclusion,
        form.radiologistName,
        form.radiologistSignature,
        form.technicianName,
        form.technicianSignature
      ]);
    }
    console.log(`✅ Migrated ${jsonData.general_forms.length} General forms`);

    // Migrate Nursing assessments
    console.log('📋 Migrating Nursing assessments...');
    for (const assessment of jsonData.nursing_assessments) {
      const query = `
        INSERT INTO nursing_assessments (
          id, patient_id, form_status, created_by, created_at, updated_at,
          vital_signs, pain_assessment, fall_risk_score, fall_risk_level,
          humpty_dumpty_score, humpty_dumpty_risk, assessment_notes,
          nurse_name, nurse_signature
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
        )
        ON CONFLICT (id) DO NOTHING
      `;

      await client.query(query, [
        assessment.id,
        assessment.patientId,
        assessment.formStatus,
        assessment.createdBy,
        assessment.createdAt,
        assessment.updatedAt,
        assessment.vitalSigns,
        assessment.painAssessment,
        assessment.fallRiskScore,
        assessment.fallRiskLevel,
        assessment.humptyDumptyScore,
        assessment.humptyDumptyRisk,
        assessment.assessmentNotes,
        assessment.nurseName,
        assessment.nurseSignature
      ]);
    }
    console.log(`✅ Migrated ${jsonData.nursing_assessments.length} Nursing assessments`);

    // Commit transaction
    await client.query('COMMIT');
    console.log('🎉 Data migration completed successfully!');

    // Show migration summary
    const totalRecords = 
      jsonData.patients.length +
      jsonData.pet_ct_forms.length +
      jsonData.general_forms.length +
      jsonData.nursing_assessments.length;

    console.log(`\n📊 Migration Summary:`);
    console.log(`   Patients: ${jsonData.patients.length}`);
    console.log(`   PET-CT Forms: ${jsonData.pet_ct_forms.length}`);
    console.log(`   General Forms: ${jsonData.general_forms.length}`);
    console.log(`   Nursing Assessments: ${jsonData.nursing_assessments.length}`);
    console.log(`   Total Records: ${totalRecords}`);

  } catch (error) {
    await client.query('ROLLBACK');
    console.error('❌ Migration failed:', error);
    throw error;
  } finally {
    if (client) {
      client.release();
    }
    await pool.end();
  }
}

// Run migration if called directly
if (require.main === module) {
  migrateData().catch(error => {
    console.error('Migration failed:', error);
    process.exit(1);
  });
}

module.exports = { migrateData };