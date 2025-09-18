// API Services for Medical Forms System
import axios from 'axios';

// Configure axios defaults
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://millio.space:8004/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication Services
export const authService = {
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials);
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  },

  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
  },

  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated() {
    return !!localStorage.getItem('authToken');
  }
};

// Patient Services
export const patientService = {
  async getAllPatients(params = {}) {
    try {
      const response = await api.get('/patients', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch patients');
    }
  },

  async getPatientById(id) {
    try {
      const response = await api.get(`/patients/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch patient');
    }
  },

  async createPatient(patientData) {
    try {
      const response = await api.post('/patients', patientData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create patient');
    }
  },

  async updatePatient(id, patientData) {
    try {
      const response = await api.put(`/patients/${id}`, patientData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update patient');
    }
  },

  async deletePatient(id) {
    try {
      await api.delete(`/patients/${id}`);
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete patient');
    }
  },

  async searchPatients(query) {
    try {
      const response = await api.get('/patients/search', { 
        params: { q: query } 
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to search patients');
    }
  }
};

// PET CT Form Services
export const petCtService = {
  async getAllForms(params = {}) {
    try {
      const response = await api.get('/forms/pet-ct', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch PET CT forms');
    }
  },

  async getFormById(id) {
    try {
      const response = await api.get(`/forms/pet-ct/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch PET CT form');
    }
  },

  async createForm(formData) {
    try {
      const response = await api.post('/forms/pet-ct', formData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create PET CT form');
    }
  },

  async updateForm(id, formData) {
    try {
      const response = await api.put(`/forms/pet-ct/${id}`, formData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update PET CT form');
    }
  },

  async deleteForm(id) {
    try {
      await api.delete(`/forms/pet-ct/${id}`);
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete PET CT form');
    }
  },

  async saveDraft(formData) {
    try {
      const response = await api.post('/forms/pet-ct/draft', formData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to save draft');
    }
  },

  async submitForm(formData) {
    try {
      const response = await api.post('/forms/pet-ct/submit', formData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to submit form');
    }
  }
};

// General Form Services
export const generalFormService = {
  async getAllForms(params = {}) {
    try {
      const response = await api.get('/forms/general', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch general forms');
    }
  },

  async getFormById(id) {
    try {
      const response = await api.get(`/forms/general/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch general form');
    }
  },

  async createForm(formData) {
    try {
      const response = await api.post('/forms/general', formData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create general form');
    }
  },

  async updateForm(id, formData) {
    try {
      const response = await api.put(`/forms/general/${id}`, formData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update general form');
    }
  },

  async deleteForm(id) {
    try {
      await api.delete(`/forms/general/${id}`);
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete general form');
    }
  }
};

// Nursing Assessment Services
export const nursingService = {
  async getAllAssessments(params = {}) {
    try {
      const response = await api.get('/forms/nursing', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch nursing assessments');
    }
  },

  async getAssessmentById(id) {
    try {
      const response = await api.get(`/forms/nursing/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch nursing assessment');
    }
  },

  async createAssessment(assessmentData) {
    try {
      const response = await api.post('/forms/nursing', assessmentData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create nursing assessment');
    }
  },

  async updateAssessment(id, assessmentData) {
    try {
      const response = await api.put(`/forms/nursing/${id}`, assessmentData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update nursing assessment');
    }
  },

  async deleteAssessment(id) {
    try {
      await api.delete(`/forms/nursing/${id}`);
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete nursing assessment');
    }
  },

  // Fall risk calculation
  async calculateFallRisk(assessmentData) {
    try {
      const response = await api.post('/forms/nursing/fall-risk', assessmentData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to calculate fall risk');
    }
  },

  // Humpty Dumpty scale calculation for pediatric patients
  async calculateHumptyDumptyScore(assessmentData) {
    try {
      const response = await api.post('/forms/nursing/humpty-dumpty', assessmentData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to calculate Humpty Dumpty score');
    }
  }
};

// File Upload Services
export const fileService = {
  async uploadFile(file, type = 'general') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to upload file');
    }
  },

  async downloadFile(fileId) {
    try {
      const response = await api.get(`/files/${fileId}`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to download file');
    }
  },

  async deleteFile(fileId) {
    try {
      await api.delete(`/files/${fileId}`);
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete file');
    }
  }
};

// Report Services
export const reportService = {
  async generateFormReport(formType, formId, format = 'pdf') {
    try {
      const response = await api.get(`/reports/${formType}/${formId}`, {
        params: { format },
        responseType: format === 'pdf' ? 'blob' : 'json',
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to generate report');
    }
  },

  async getDashboardStats(dateRange = {}) {
    try {
      const response = await api.get('/reports/dashboard', { 
        params: dateRange 
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch dashboard stats');
    }
  },

  async getFormStatistics(formType, dateRange = {}) {
    try {
      const response = await api.get(`/reports/statistics/${formType}`, {
        params: dateRange
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch form statistics');
    }
  },

  async exportData(formType, filters = {}, format = 'excel') {
    try {
      const response = await api.get(`/reports/export/${formType}`, {
        params: { ...filters, format },
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to export data');
    }
  }
};

// Settings Services
export const settingsService = {
  async getSystemSettings() {
    try {
      const response = await api.get('/settings');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch settings');
    }
  },

  async updateSettings(settings) {
    try {
      const response = await api.put('/settings', settings);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update settings');
    }
  },

  async getFormTemplates() {
    try {
      const response = await api.get('/settings/templates');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch form templates');
    }
  },

  async updateFormTemplate(templateId, templateData) {
    try {
      const response = await api.put(`/settings/templates/${templateId}`, templateData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update form template');
    }
  }
};

// Audit Services
export const auditService = {
  async getAuditLogs(params = {}) {
    try {
      const response = await api.get('/audit/logs', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch audit logs');
    }
  },

  async logAction(action, details) {
    try {
      const response = await api.post('/audit/log', { action, details });
      return response.data;
    } catch (error) {
      console.error('Failed to log action:', error);
    }
  }
};

// User Management Services
export const userService = {
  async getAllUsers(params = {}) {
    try {
      const response = await api.get('/users', { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch users');
    }
  },

  async createUser(userData) {
    try {
      const response = await api.post('/users', userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create user');
    }
  },

  async updateUser(id, userData) {
    try {
      const response = await api.put(`/users/${id}`, userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update user');
    }
  },

  async deleteUser(id) {
    try {
      await api.delete(`/users/${id}`);
      return { success: true };
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete user');
    }
  },

  async updateUserRole(id, role) {
    try {
      const response = await api.patch(`/users/${id}/role`, { role });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update user role');
    }
  }
};

// Utility Functions
export const utilityService = {
  // Generate unique medical ID
  generateMedicalId() {
    const year = new Date().getFullYear();
    const timestamp = Date.now().toString().slice(-6);
    return `MED-${year}-${timestamp}`;
  },

  // Format date for display
  formatDate(date, locale = 'en-US') {
    return new Date(date).toLocaleDateString(locale);
  },

  // Format datetime for display
  formatDateTime(datetime, locale = 'en-US') {
    return new Date(datetime).toLocaleString(locale);
  },

  // Calculate age from birth date
  calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    return age;
  },

  // Validate medical ID format
  validateMedicalId(medicalId) {
    const pattern = /^MED-\d{4}-\d{6}$/;
    return pattern.test(medicalId);
  },

  // Calculate BMI
  calculateBMI(weight, height) {
    if (!weight || !height) return null;
    const heightInMeters = height / 100;
    return (weight / (heightInMeters * heightInMeters)).toFixed(1);
  },

  // Get BMI category
  getBMICategory(bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  },

  // Download blob as file
  downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  // Print form data
  printForm(formData, formType) {
    const printWindow = window.open('', '_blank');
    const printContent = this.generatePrintableHTML(formData, formType);
    
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
    printWindow.close();
  },

  // Generate printable HTML
  generatePrintableHTML(formData, formType) {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${formType.toUpperCase()} Form - ${formData.patientName}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { text-align: center; margin-bottom: 20px; }
          .section { margin-bottom: 15px; }
          .field { margin-bottom: 5px; }
          .signature { border: 1px solid #ccc; height: 80px; margin: 10px 0; }
          @media print { 
            .no-print { display: none; }
            body { margin: 0; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>${formType.toUpperCase()} Examination Form</h1>
          <p>Patient: ${formData.patientName} | Medical ID: ${formData.medicalId}</p>
          <p>Date: ${new Date().toLocaleDateString()}</p>
        </div>
        
        <div class="section">
          <h3>Patient Information</h3>
          <div class="field">Name: ${formData.patientName}</div>
          <div class="field">Age: ${formData.age}</div>
          <div class="field">Gender: ${formData.gender}</div>
          ${formData.weight ? `<div class="field">Weight: ${formData.weight} kg</div>` : ''}
          ${formData.height ? `<div class="field">Height: ${formData.height} cm</div>` : ''}
        </div>
        
        ${formData.diagnosis ? `
        <div class="section">
          <h3>Diagnosis</h3>
          <div class="field">${formData.diagnosis}</div>
        </div>
        ` : ''}
        
        ${formData.studyReason ? `
        <div class="section">
          <h3>Study Reason</h3>
          <div class="field">${formData.studyReason}</div>
        </div>
        ` : ''}
        
        <div class="section">
          <h3>Signatures</h3>
          <div style="display: flex; justify-content: space-between;">
            <div style="width: 45%;">
              <p>Patient Signature:</p>
              <div class="signature"></div>
            </div>
            <div style="width: 45%;">
              <p>Doctor Signature:</p>
              <div class="signature"></div>
            </div>
          </div>
        </div>
        
        <script>
          window.onload = function() {
            setTimeout(function() {
              window.print();
            }, 500);
          }
        </script>
      </body>
      </html>
    `;
  }
};

// Error Handling Utilities
export const errorHandler = {
  handleApiError(error) {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || 'An error occurred';
      const status = error.response.status;
      
      switch (status) {
        case 400:
          return { type: 'validation', message };
        case 401:
          return { type: 'auth', message: 'Authentication required' };
        case 403:
          return { type: 'permission', message: 'Access denied' };
        case 404:
          return { type: 'notFound', message: 'Resource not found' };
        case 500:
          return { type: 'server', message: 'Server error' };
        default:
          return { type: 'unknown', message };
      }
    } else if (error.request) {
      // Network error
      return { type: 'network', message: 'Network connection error' };
    } else {
      // Something else happened
      return { type: 'unknown', message: error.message };
    }
  },

  displayError(error, showNotification) {
    const errorInfo = this.handleApiError(error);
    
    if (showNotification) {
      showNotification(errorInfo.message, 'error');
    }
    
    console.error('API Error:', errorInfo);
    return errorInfo;
  }
};

// Cache Management
export const cacheService = {
  // Simple in-memory cache for frequently accessed data
  cache: new Map(),
  
  set(key, data, ttl = 300000) { // Default 5 minutes TTL
    const expiresAt = Date.now() + ttl;
    this.cache.set(key, { data, expiresAt });
  },
  
  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expiresAt) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  },
  
  clear() {
    this.cache.clear();
  },
  
  // Cached wrapper for API calls
  async cachedCall(key, apiCall, ttl = 300000) {
    const cached = this.get(key);
    if (cached) return cached;
    
    const result = await apiCall();
    this.set(key, result, ttl);
    return result;
  }
};

// Export all services
export {
  api,
  API_BASE_URL,
};