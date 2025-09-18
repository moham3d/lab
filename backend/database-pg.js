const { Pool } = require('pg');
const path = require('path');

class PostgreSQLDatabaseManager {
  constructor() {
    this.pool = null;
    this.initialized = false;
  }

  async initialize() {
    try {
      // Create connection pool
      this.pool = new Pool({
        connectionString: process.env.DATABASE_URL || 'postgresql://localhost:5432/medical_forms',
        max: 20,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000,
      });

      // Test connection
      await this.pool.query('SELECT NOW()');
      this.initialized = true;
      console.log('✅ PostgreSQL Database initialized successfully');

    } catch (error) {
      console.error('❌ PostgreSQL Database initialization failed:', error);
      throw error;
    }
  }

  // Patient operations
  async getAllPatients({ page = 1, limit = 50, search } = {}) {
    const offset = (page - 1) * limit;
    let query = `
      SELECT * FROM patients 
      WHERE deleted_at IS NULL
    `;
    let countQuery = `SELECT COUNT(*) FROM patients WHERE deleted_at IS NULL`;
    const params = [];

    if (search) {
      query += ` AND (
        name_english ILIKE $${params.length + 1} OR
        name_arabic ILIKE $${params.length + 1} OR
        medical_id ILIKE $${params.length + 1} OR
        id_number ILIKE $${params.length + 1}
      )`;
      countQuery += ` AND (
        name_english ILIKE $1 OR
        name_arabic ILIKE $1 OR
        medical_id ILIKE $1 OR
        id_number ILIKE $1
      )`;
      params.push(`%${search}%`);
    }

    query += ` ORDER BY created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(limit, offset);

    const [patientsResult, countResult] = await Promise.all([
      this.pool.query(query, params),
      this.pool.query(countQuery, search ? [params[0]] : [])
    ]);

    return {
      patients: patientsResult.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: parseInt(countResult.rows[0].count),
        pages: Math.ceil(countResult.rows[0].count / limit)
      }
    };
  }

  async getPatientById(id) {
    const result = await this.pool.query(
      'SELECT * FROM patients WHERE id = $1 AND deleted_at IS NULL',
      [id]
    );
    return result.rows[0];
  }

  async createPatient(patientData) {
    const query = `
      INSERT INTO patients (
        medical_id, id_number, name_arabic, name_english, 
        phone, email, birth_date, age, gender, address,
        emergency_contact, emergency_phone
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
      RETURNING *
    `;

    const result = await this.pool.query(query, [
      patientData.medicalId,
      patientData.idNumber,
      patientData.nameArabic,
      patientData.nameEnglish,
      patientData.phone,
      patientData.email,
      patientData.birthDate,
      patientData.age,
      patientData.gender,
      patientData.address,
      patientData.emergencyContact,
      patientData.emergencyPhone
    ]);

    return result.rows[0];
  }

  async updatePatient(id, patientData) {
    const fields = [];
    const values = [];
    let paramCount = 1;

    Object.entries(patientData).forEach(([key, value]) => {
      if (value !== undefined) {
        fields.push(`${key} = $${paramCount}`);
        values.push(value);
        paramCount++;
      }
    });

    if (fields.length === 0) {
      throw new Error('No fields to update');
    }

    values.push(id);
    const query = `
      UPDATE patients 
      SET ${fields.join(', ')}, updated_at = NOW()
      WHERE id = $${paramCount} AND deleted_at IS NULL
      RETURNING *
    `;

    const result = await this.pool.query(query, values);
    if (result.rows.length === 0) {
      throw new Error('Patient not found');
    }

    return result.rows[0];
  }

  async deletePatient(id) {
    const result = await this.pool.query(
      'UPDATE patients SET deleted_at = NOW() WHERE id = $1 RETURNING id',
      [id]
    );
    return result.rows.length > 0;
  }

  // Form operations
  async getAllForms(formType, { page = 1, limit = 50, status, patientId } = {}) {
    const tableName = this.getTableName(formType);
    const offset = (page - 1) * limit;
    
    let query = `SELECT * FROM ${tableName} WHERE deleted_at IS NULL`;
    let countQuery = `SELECT COUNT(*) FROM ${tableName} WHERE deleted_at IS NULL`;
    const params = [];

    if (status) {
      query += ` AND form_status = $${params.length + 1}`;
      countQuery += ` AND form_status = $1`;
      params.push(status);
    }

    if (patientId) {
      query += ` AND patient_id = $${params.length + 1}`;
      countQuery += params.length > 0 ? ` AND patient_id = $2` : ` AND patient_id = $1`;
      params.push(patientId);
    }

    query += ` ORDER BY created_at DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(limit, offset);

    const [formsResult, countResult] = await Promise.all([
      this.pool.query(query, params),
      this.pool.query(countQuery, params.slice(0, params.length - 2))
    ]);

    return {
      forms: formsResult.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: parseInt(countResult.rows[0].count),
        pages: Math.ceil(countResult.rows[0].count / limit)
      }
    };
  }

  async createForm(formType, formData) {
    const tableName = this.getTableName(formType);
    const columns = Object.keys(formData);
    const values = Object.values(formData);
    const placeholders = columns.map((_, i) => `$${i + 1}`);

    const query = `
      INSERT INTO ${tableName} (${columns.join(', ')})
      VALUES (${placeholders.join(', ')})
      RETURNING *
    `;

    const result = await this.pool.query(query, values);
    return result.rows[0];
  }

  // Utility methods
  getTableName(formType) {
    const tableMap = {
      'pet-ct': 'pet_ct_forms',
      'general': 'general_forms',
      'nursing': 'nursing_assessments'
    };
    return tableMap[formType] || formType;
  }

  // Close database connection
  async close() {
    if (this.pool) {
      await this.pool.end();
      this.initialized = false;
    }
  }

  // Get database stats
  async getStats() {
    if (!this.initialized) return null;

    const queries = [
      this.pool.query('SELECT COUNT(*) FROM patients WHERE deleted_at IS NULL'),
      this.pool.query('SELECT COUNT(*) FROM pet_ct_forms WHERE deleted_at IS NULL'),
      this.pool.query('SELECT COUNT(*) FROM general_forms WHERE deleted_at IS NULL'),
      this.pool.query('SELECT COUNT(*) FROM nursing_assessments WHERE deleted_at IS NULL')
    ];

    const results = await Promise.all(queries);

    return {
      patients: parseInt(results[0].rows[0].count),
      pet_ct_forms: parseInt(results[1].rows[0].count),
      general_forms: parseInt(results[2].rows[0].count),
      nursing_assessments: parseInt(results[3].rows[0].count)
    };
  }
}

// Export singleton instance
const dbManager = new PostgreSQLDatabaseManager();

module.exports = dbManager;