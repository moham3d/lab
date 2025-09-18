const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

class DatabaseManager {
  constructor() {
    this.dbPath = path.join(__dirname, '..', 'database', 'medical_forms.db');
    this.db = null;
    this.initialized = false;
  }

  initialize() {
    try {
      // Ensure database directory exists
      const dbDir = path.dirname(this.dbPath);
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      // Connect to database
      this.db = new Database(this.dbPath);

      // Enable foreign keys
      this.db.pragma('foreign_keys = ON');

      // Enable WAL mode for better performance
      this.db.pragma('journal_mode = WAL');

      // Create tables
      this.createTables();

      // Insert sample data
      this.seedData();

      this.initialized = true;
      console.log('✅ Database initialized successfully');

    } catch (error) {
      console.error('❌ Database initialization failed:', error);
      throw error;
    }
  }

  createTables() {
    const schemaPath = path.join(__dirname, '..', 'database', 'sqlite_schema.sql');
    const schema = fs.readFileSync(schemaPath, 'utf8');

    // Split schema into individual statements
    const statements = schema
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'));

    // Execute each statement
    for (const statement of statements) {
      try {
        this.db.exec(statement);
      } catch (error) {
        // Ignore errors for statements that create existing tables/indexes
        if (!error.message.includes('already exists')) {
          console.warn('Warning executing statement:', error.message);
        }
      }
    }
  }

  seedData() {
    // Sample data is already included in the schema file
    // This method can be extended for additional seeding if needed
  }

  // Patient operations
  getAllPatients({ page = 1, limit = 50, search } = {}) {
    const offset = (page - 1) * limit;

    let query = `
      SELECT id, medical_id, id_number, name_arabic, name_english,
             phone, email, birth_date, age, gender, address,
             emergency_contact, emergency_phone, created_at
      FROM patients
    `;

    let countQuery = 'SELECT COUNT(*) as total FROM patients';
    const params = [];

    if (search) {
      const searchCondition = `
        WHERE name_english LIKE ? OR name_arabic LIKE ? OR
              medical_id LIKE ? OR id_number LIKE ?
      `;
      query += searchCondition;
      countQuery += searchCondition;

      const searchParam = `%${search}%`;
      params.push(searchParam, searchParam, searchParam, searchParam);
    }

    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);

    const stmt = this.db.prepare(query);
    const countStmt = this.db.prepare(countQuery);

    const patients = stmt.all(...params);
    const totalResult = countStmt.get(...(search ? params.slice(0, 4) : []));

    return {
      patients,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: totalResult.total,
        pages: Math.ceil(totalResult.total / limit)
      }
    };
  }

  getPatientById(id) {
    const stmt = this.db.prepare('SELECT * FROM patients WHERE id = ?');
    return stmt.get(id);
  }

  createPatient(patientData) {
    const stmt = this.db.prepare(`
      INSERT INTO patients (
        medical_id, id_number, name_arabic, name_english, phone, email,
        birth_date, age, gender, address, emergency_contact, emergency_phone
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const result = stmt.run(
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
    );

    // Get the created patient
    const patientStmt = this.db.prepare('SELECT * FROM patients WHERE id = ?');
    return patientStmt.get(result.lastInsertRowid);
  }

  updatePatient(id, patientData) {
    const stmt = this.db.prepare(`
      UPDATE patients SET
        id_number = ?, name_arabic = ?, name_english = ?, phone = ?,
        email = ?, birth_date = ?, age = ?, gender = ?, address = ?,
        emergency_contact = ?, emergency_phone = ?, updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `);

    const result = stmt.run(
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
      patientData.emergencyPhone,
      id
    );

    if (result.changes === 0) {
      throw new Error('Patient not found');
    }

    // Get the updated patient
    const patientStmt = this.db.prepare('SELECT * FROM patients WHERE id = ?');
    return patientStmt.get(id);
  }

  deletePatient(id) {
    const stmt = this.db.prepare('DELETE FROM patients WHERE id = ?');
    const result = stmt.run(id);
    return result.changes > 0;
  }

  // Form operations
  getAllForms(formType, { page = 1, limit = 50, status, patientId } = {}) {
    const offset = (page - 1) * limit;
    const tableName = this.getTableName(formType);

    let query = `SELECT * FROM ${tableName}`;
    let countQuery = `SELECT COUNT(*) as total FROM ${tableName}`;
    const params = [];

    const conditions = [];
    if (status) {
      conditions.push('form_status = ?');
      params.push(status);
    }
    if (patientId) {
      conditions.push('patient_id = ?');
      params.push(patientId);
    }

    if (conditions.length > 0) {
      const whereClause = ' WHERE ' + conditions.join(' AND ');
      query += whereClause;
      countQuery += whereClause;
    }

    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);

    const stmt = this.db.prepare(query);
    const countStmt = this.db.prepare(countQuery);

    const forms = stmt.all(...params);
    const totalResult = countStmt.get(...params.slice(0, -2));

    return {
      forms,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: totalResult.total,
        pages: Math.ceil(totalResult.total / limit)
      }
    };
  }

  createForm(formType, formData) {
    const tableName = this.getTableName(formType);
    const columns = Object.keys(formData).join(', ');
    const placeholders = Object.keys(formData).map(() => '?').join(', ');

    const query = `INSERT INTO ${tableName} (${columns}) VALUES (${placeholders})`;
    const stmt = this.db.prepare(query);

    const result = stmt.run(...Object.values(formData));

    // Get the created form
    const formStmt = this.db.prepare(`SELECT * FROM ${tableName} WHERE id = ?`);
    return formStmt.get(result.lastInsertRowid);
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
  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
      this.initialized = false;
    }
  }

  // Get database stats
  getStats() {
    if (!this.initialized) return null;

    const stats = {};

    // Count records in each table
    const tables = ['patients', 'pet_ct_forms', 'general_forms', 'nursing_assessments'];
    for (const table of tables) {
      const stmt = this.db.prepare(`SELECT COUNT(*) as count FROM ${table}`);
      stats[table] = stmt.get().count;
    }

    return stats;
  }
}

// Export singleton instance
const dbManager = new DatabaseManager();

module.exports = dbManager;