const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class SQLite3DatabaseManager {
  constructor() {
    this.dbPath = path.join(__dirname, '..', 'database', 'medical_forms.db');
    this.db = null;
    this.initialized = false;
  }

  initialize() {
    return new Promise((resolve, reject) => {
      try {
        // Ensure database directory exists
        const dbDir = path.dirname(this.dbPath);
        if (!fs.existsSync(dbDir)) {
          fs.mkdirSync(dbDir, { recursive: true });
        }

        // Connect to database
        this.db = new sqlite3.Database(this.dbPath, (err) => {
          if (err) {
            reject(err);
            return;
          }

          // Enable foreign keys
          this.db.run('PRAGMA foreign_keys = ON');

          // Create tables
          this.createTables()
            .then(() => {
              this.initialized = true;
              console.log('✅ SQLite3 Database initialized successfully');
              resolve();
            })
            .catch(reject);
        });

      } catch (error) {
        reject(error);
      }
    });
  }

  createTables() {
    return new Promise((resolve, reject) => {
      const schemaPath = path.join(__dirname, '..', 'database', 'sqlite_schema.sql');
      const schema = fs.readFileSync(schemaPath, 'utf8');

      // Split schema into individual statements
      const statements = schema
        .split(';')
        .map(stmt => stmt.trim())
        .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'));

      let completed = 0;
      const total = statements.length;

      if (total === 0) {
        resolve();
        return;
      }

      statements.forEach((statement) => {
        this.db.run(statement, (err) => {
          if (err && !err.message.includes('already exists')) {
            console.warn('Warning executing statement:', err.message);
          }
          
          completed++;
          if (completed === total) {
            resolve();
          }
        });
      });
    });
  }

  // Patient operations
  getAllPatients({ page = 1, limit = 50, search } = {}) {
    return new Promise((resolve, reject) => {
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

      // Get count first
      this.db.get(countQuery, search ? params.slice(0, 4) : [], (err, countResult) => {
        if (err) {
          reject(err);
          return;
        }

        // Get patients
        this.db.all(query, params, (err, patients) => {
          if (err) {
            reject(err);
            return;
          }

          resolve({
            patients,
            pagination: {
              page: parseInt(page),
              limit: parseInt(limit),
              total: countResult.total,
              pages: Math.ceil(countResult.total / limit)
            }
          });
        });
      });
    });
  }

  getPatientById(id) {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM patients WHERE id = ?', [id], (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  }

  createPatient(patientData) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare(`
        INSERT INTO patients (
          medical_id, id_number, name_arabic, name_english, phone, email,
          birth_date, age, gender, address, emergency_contact, emergency_phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run(
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
        patientData.emergencyPhone,
        function(err) {
          if (err) {
            reject(err);
            return;
          }
          
          // Get the created patient
          this.db.get('SELECT * FROM patients WHERE id = ?', [this.lastID], (err, row) => {
            if (err) reject(err);
            else resolve(row);
          });
        }
      );
    });
  }

  updatePatient(id, patientData) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare(`
        UPDATE patients SET
          id_number = ?, name_arabic = ?, name_english = ?, phone = ?,
          email = ?, birth_date = ?, age = ?, gender = ?, address = ?,
          emergency_contact = ?, emergency_phone = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
      `);

      stmt.run(
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
        id,
        function(err) {
          if (err) {
            reject(err);
            return;
          }

          if (this.changes === 0) {
            reject(new Error('Patient not found'));
            return;
          }

          // Get the updated patient
          this.db.get('SELECT * FROM patients WHERE id = ?', [id], (err, row) => {
            if (err) reject(err);
            else resolve(row);
          });
        }
      );
    });
  }

  // Form operations
  getAllForms(formType, { page = 1, limit = 50, status, patientId } = {}) {
    return new Promise((resolve, reject) => {
      const tableName = this.getTableName(formType);
      const offset = (page - 1) * limit;

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

      // Get count first
      this.db.get(countQuery, params.slice(0, -2), (err, countResult) => {
        if (err) {
          reject(err);
          return;
        }

        // Get forms
        this.db.all(query, params, (err, forms) => {
          if (err) {
            reject(err);
            return;
          }

          resolve({
            forms,
            pagination: {
              page: parseInt(page),
              limit: parseInt(limit),
              total: countResult.total,
              pages: Math.ceil(countResult.total / limit)
            }
          });
        });
      });
    });
  }

  createForm(formType, formData) {
    return new Promise((resolve, reject) => {
      const tableName = this.getTableName(formType);
      const columns = Object.keys(formData);
      const values = Object.values(formData);
      const placeholders = columns.map(() => '?').join(', ');

      const query = `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES (${placeholders})`;
      const stmt = this.db.prepare(query);

      stmt.run(values, function(err) {
        if (err) {
          reject(err);
          return;
        }

        // Get the created form
        this.db.get(`SELECT * FROM ${tableName} WHERE id = ?`, [this.lastID], (err, row) => {
          if (err) reject(err);
          else resolve(row);
        });
      });
    });
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
    return new Promise((resolve, reject) => {
      if (!this.initialized) {
        resolve(null);
        return;
      }

      const stats = {};
      const tables = ['patients', 'pet_ct_forms', 'general_forms', 'nursing_assessments'];
      let completed = 0;

      tables.forEach((table) => {
        this.db.get(`SELECT COUNT(*) as count FROM ${table}`, (err, result) => {
          if (err) {
            console.warn(`Error counting ${table}:`, err.message);
          } else {
            stats[table] = result.count;
          }

          completed++;
          if (completed === tables.length) {
            resolve(stats);
          }
        });
      });
    });
  }
}

// Export singleton instance
const dbManager = new SQLite3DatabaseManager();

module.exports = dbManager;