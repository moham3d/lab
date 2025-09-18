const fs = require('fs').promises;
const path = require('path');

class JSONDatabaseManager {
  constructor() {
    this.dataPath = path.join(__dirname, '..', 'database', 'data.json');
    this.data = {
      patients: [],
      pet_ct_forms: [],
      general_forms: [],
      nursing_assessments: []
    };
    this.initialized = false;
  }

  async initialize() {
    try {
      // Ensure database directory exists
      const dbDir = path.dirname(this.dataPath);
      await fs.mkdir(dbDir, { recursive: true });

      // Try to load existing data
      try {
        const data = await fs.readFile(this.dataPath, 'utf8');
        this.data = JSON.parse(data);
      } catch (error) {
        // File doesn't exist or is corrupted, use default data
        console.log('Creating new database file');
        await this.saveData();
      }

      this.initialized = true;
      console.log('✅ JSON Database initialized successfully');

    } catch (error) {
      console.error('❌ Database initialization failed:', error);
      throw error;
    }
  }

  async saveData() {
    await fs.writeFile(this.dataPath, JSON.stringify(this.data, null, 2));
  }

  // Patient operations
  getAllPatients({ page = 1, limit = 50, search } = {}) {
    let patients = [...this.data.patients];

    if (search) {
      const searchLower = search.toLowerCase();
      patients = patients.filter(patient =>
        patient.nameEnglish?.toLowerCase().includes(searchLower) ||
        patient.nameArabic?.includes(search) ||
        patient.medicalId?.includes(search) ||
        patient.idNumber?.includes(search)
      );
    }

    const offset = (page - 1) * limit;
    const paginatedPatients = patients.slice(offset, offset + limit);

    return {
      patients: paginatedPatients,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: patients.length,
        pages: Math.ceil(patients.length / limit)
      }
    };
  }

  getPatientById(id) {
    return this.data.patients.find(patient => patient.id === id);
  }

  async createPatient(patientData) {
    const newPatient = {
      id: Date.now().toString(),
      medicalId: patientData.medicalId,
      idNumber: patientData.idNumber,
      nameArabic: patientData.nameArabic,
      nameEnglish: patientData.nameEnglish,
      phone: patientData.phone,
      email: patientData.email,
      birthDate: patientData.birthDate,
      age: patientData.age,
      gender: patientData.gender,
      address: patientData.address,
      emergencyContact: patientData.emergencyContact,
      emergencyPhone: patientData.emergencyPhone,
      createdAt: new Date().toISOString()
    };

    this.data.patients.push(newPatient);
    await this.saveData();
    return newPatient;
  }

  async updatePatient(id, patientData) {
    const index = this.data.patients.findIndex(patient => patient.id === id);
    if (index === -1) {
      throw new Error('Patient not found');
    }

    this.data.patients[index] = {
      ...this.data.patients[index],
      ...patientData,
      updatedAt: new Date().toISOString()
    };

    await this.saveData();
    return this.data.patients[index];
  }

  async deletePatient(id) {
    const index = this.data.patients.findIndex(patient => patient.id === id);
    if (index === -1) {
      return false;
    }

    this.data.patients.splice(index, 1);
    await this.saveData();
    return true;
  }

  // Form operations
  getAllForms(formType, { page = 1, limit = 50, status, patientId } = {}) {
    const tableName = this.getTableName(formType);
    let forms = [...this.data[tableName]];

    if (status) {
      forms = forms.filter(form => form.formStatus === status);
    }

    if (patientId) {
      forms = forms.filter(form => form.patientId === patientId);
    }

    const offset = (page - 1) * limit;
    const paginatedForms = forms.slice(offset, offset + limit);

    return {
      forms: paginatedForms,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: forms.length,
        pages: Math.ceil(forms.length / limit)
      }
    };
  }

  async createForm(formType, formData) {
    const tableName = this.getTableName(formType);
    const newForm = {
      id: Date.now().toString(),
      ...formData,
      createdAt: new Date().toISOString()
    };

    this.data[tableName].push(newForm);
    await this.saveData();
    return newForm;
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

  // Close database connection (no-op for JSON)
  close() {
    this.initialized = false;
  }

  // Get database stats
  getStats() {
    if (!this.initialized) return null;

    return {
      patients: this.data.patients.length,
      pet_ct_forms: this.data.pet_ct_forms.length,
      general_forms: this.data.general_forms.length,
      nursing_assessments: this.data.nursing_assessments.length
    };
  }
}

// Export singleton instance
const dbManager = new JSONDatabaseManager();

module.exports = dbManager;