/**
 * Healthcare Frontend - Main JavaScript
 * Alpine.js stores and utilities for patient management system
 */

// Alpine.js stores for global state management
if (typeof Alpine !== 'undefined') {
  // Authentication store
  Alpine.store('auth', {
    user: null,
    token: localStorage.getItem('auth_token'),
    role: null,
    isAuthenticated: false,

    async init() {
      if (this.token) {
        await this.validateToken();
      } else {
        // No token, user is not authenticated
        this.isAuthenticated = false;
      }
    },

    async login(credentials) {
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(credentials),
        });

        if (!response.ok) {
          throw new Error('Login failed');
        }

        const data = await response.json();
        this.setAuth(data, data.access_token);
        return { success: true };
      } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: error.message };
      }
    },

    async logout() {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        });
      } catch (error) {
        console.error('Logout error:', error);
      }

      this.clearAuth();
      window.location.href = '/login';
    },

    setAuth(data, token) {
      this.user = data.user || { username: data.username || 'user', role: 'user' };
      this.token = token;
      this.role = this.user.role;
      this.isAuthenticated = true;
      localStorage.setItem('auth_token', token);

      // Update HTMX headers
      if (typeof htmx !== 'undefined') {
        htmx.ajax = htmx.ajax || {};
        htmx.ajax.headers = {
          Authorization: `Bearer ${token}`,
        };
      }
    },

    clearAuth() {
      this.user = null;
      this.token = null;
      this.role = null;
      this.isAuthenticated = false;
      localStorage.removeItem('auth_token');
    },

    async validateToken() {
      try {
        const response = await fetch('/api/auth/me', {
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        });

        if (response.ok) {
          const user = await response.json();
          this.setAuth(user, this.token);
        } else {
          this.clearAuth();
        }
      } catch (error) {
        console.error('Token validation error:', error);
        this.clearAuth();
      }
    },

    hasRole(role) {
      return this.role === role;
    },

    hasAnyRole(roles) {
      return roles.includes(this.role);
    },
  });

  // UI store for global UI state
  Alpine.store('ui', {
    loading: false,
    notifications: [],

    setLoading(state) {
      this.loading = state;
    },

    showNotification(message, type = 'info', duration = 5000) {
      const id = Date.now();
      this.notifications.push({
        id,
        message,
        type,
        duration,
      });

      if (duration > 0) {
        setTimeout(() => {
          this.removeNotification(id);
        }, duration);
      }
    },

    removeNotification(id) {
      this.notifications = this.notifications.filter(notification => notification.id !== id);
    },

    clearNotifications() {
      this.notifications = [];
    }
  });

  // Patient management store
  Alpine.store('patients', {
    patients: [],
    currentPatient: null,
    loading: false,
    searchResults: [],

    async loadPatients() {
      this.loading = true;
      try {
        const response = await fetch('/api/patients', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (response.ok) {
          this.patients = await response.json();
        } else if (response.status === 401) {
          window.location.href = '/login';
        } else {
          this.patients = [];
        }
      } catch (error) {
        console.error('Failed to load patients:', error);
        this.patients = [];
      } finally {
        this.loading = false;
      }
    },

    async searchPatients(query) {
      if (!query || query.length < 2) {
        this.searchResults = [];
        return;
      }

      try {
        const response = await fetch(`/api/patients/search?q=${encodeURIComponent(query)}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (response.ok) {
          this.searchResults = await response.json();
        } else {
          this.searchResults = [];
        }
      } catch (error) {
        console.error('Failed to search patients:', error);
        this.searchResults = [];
      }
    },

    async getPatient(ssn) {
      try {
        const response = await fetch(`/api/patients/${ssn}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (response.ok) {
          this.currentPatient = await response.json();
          return this.currentPatient;
        } else {
          this.currentPatient = null;
          return null;
        }
      } catch (error) {
        console.error('Failed to get patient:', error);
        this.currentPatient = null;
        return null;
      }
    },

    validateSSN(ssn) {
      // Egyptian SSN validation (14 digits)
      return /^\d{14}$/.test(ssn);
    },

    validateMobile(mobile) {
      // Egyptian mobile number validation (01xxxxxxxxx)
      return /^01[0-2]\d{8}$/.test(mobile);
    }
  });

  // Visit management store
  Alpine.store('visits', {
    visits: [],
    currentVisit: null,
    loading: false,
    stats: {
      today: 0,
      inProgress: 0,
      completed: 0,
      cancelled: 0
    },

    async loadVisits() {
      this.loading = true;
      try {
        const response = await fetch('/api/visits', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (response.ok) {
          this.visits = await response.json();
          this.calculateStats();
        } else if (response.status === 401) {
          window.location.href = '/login';
        } else {
          this.visits = [];
        }
      } catch (error) {
        console.error('Failed to load visits:', error);
        this.visits = [];
      } finally {
        this.loading = false;
      }
    },

    calculateStats() {
      const today = new Date().toISOString().split('T')[0];
      
      this.stats.today = this.visits.filter(v => v.visit_date === today).length;
      this.stats.inProgress = this.visits.filter(v => v.status === 'in_progress').length;
      this.stats.completed = this.visits.filter(v => v.status === 'completed').length;
      this.stats.cancelled = this.visits.filter(v => v.status === 'cancelled').length;
    },

    async updateVisitStatus(visitId, newStatus) {
      try {
        const response = await fetch(`/api/visits/${visitId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
          await this.loadVisits();
          return true;
        } else {
          return false;
        }
      } catch (error) {
        console.error('Failed to update visit status:', error);
        return false;
      }
    }
  });

  // Medical validation utilities
  Alpine.store('medical', {
    // Vital signs validation
    isValidTemperature(temp) {
      return temp >= 30 && temp <= 45;
    },

    isNormalTemperature(temp) {
      return temp >= 36.1 && temp <= 37.2;
    },

    isValidPulse(pulse) {
      return pulse >= 30 && pulse <= 200;
    },

    isNormalPulse(pulse) {
      return pulse >= 60 && pulse <= 100;
    },

    isValidBloodPressureSystolic(systolic) {
      return systolic >= 70 && systolic <= 250;
    },

    isNormalBloodPressureSystolic(systolic) {
      return systolic >= 90 && systolic <= 140;
    },

    isValidBloodPressureDiastolic(diastolic) {
      return diastolic >= 40 && diastolic <= 150;
    },

    isNormalBloodPressureDiastolic(diastolic) {
      return diastolic >= 60 && diastolic <= 90;
    },

    isValidRespiratoryRate(rate) {
      return rate >= 8 && rate <= 40;
    },

    isNormalRespiratoryRate(rate) {
      return rate >= 12 && rate <= 20;
    },

    isValidOxygenSaturation(sat) {
      return sat >= 70 && sat <= 100;
    },

    isNormalOxygenSaturation(sat) {
      return sat >= 95 && sat <= 100;
    },

    // BMI calculation
    calculateBMI(weight, height) {
      if (!weight || !height) return null;
      const heightInMeters = height / 100;
      return (weight / (heightInMeters * heightInMeters)).toFixed(1);
    },

    getBMICategory(bmi) {
      if (bmi < 18.5) return 'Underweight';
      if (bmi < 25) return 'Normal weight';
      if (bmi < 30) return 'Overweight';
      return 'Obese';
    }
  });

  // Form utilities
  Alpine.store('forms', {
    drafts: {},

    saveDraft(formName, data) {
      try {
        this.drafts[formName] = data;
        localStorage.setItem(`draft_${formName}`, JSON.stringify(data));
      } catch (error) {
        console.error('Failed to save draft:', error);
      }
    },

    loadDraft(formName) {
      try {
        const draft = localStorage.getItem(`draft_${formName}`);
        if (draft) {
          this.drafts[formName] = JSON.parse(draft);
          return this.drafts[formName];
        }
        return null;
      } catch (error) {
        console.error('Failed to load draft:', error);
        return null;
      }
    },

    clearDraft(formName) {
      try {
        delete this.drafts[formName];
        localStorage.removeItem(`draft_${formName}`);
      } catch (error) {
        console.error('Failed to clear draft:', error);
      }
    },

    validateRequired(fields, data) {
      const missing = [];
      fields.forEach(field => {
        if (!data[field] || data[field] === '') {
          missing.push(field);
        }
      });
      return missing;
    }
  });
}

// Utility functions
window.utils = {
  formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  },

  formatTime(timeStr) {
    if (!timeStr) return '';
    return timeStr;
  },

  formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  calculateAge(birthDate) {
    if (!birthDate) return null;
    
    const birth = new Date(birthDate);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    return age;
  },

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Egyptian SSN validation
  validateSSN(ssn) {
    return /^\d{14}$/.test(ssn);
  },

  // Egyptian mobile validation
  validateMobile(mobile) {
    return /^01[0-2]\d{8}$/.test(mobile);
  },

  // API request helper
  async apiRequest(url, options = {}) {
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        ...options.headers
      }
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      
      if (response.status === 401) {
        window.location.href = '/login';
        return null;
      }

      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
};

    removeNotification(id) {
      this.notifications = this.notifications.filter((n) => n.id !== id);
    },

    clearNotifications() {
      this.notifications = [];
    },
  });

  // Patient store for current patient context
  Alpine.store('patient', {
    current: null,
    searchResults: [],
    loading: false,

    setCurrent(patient) {
      this.current = patient;
    },

    clearCurrent() {
      this.current = null;
    },

    async search(query) {
      this.loading = true;
      try {
        const response = await fetch(
          `/api/patients/search?q=${encodeURIComponent(query)}`,
          {
            headers: {
              Authorization: `Bearer ${Alpine.store('auth').token}`,
            },
          }
        );

        if (response.ok) {
          this.searchResults = await response.json();
        } else {
          this.searchResults = [];
        }
      } catch (error) {
        console.error('Patient search error:', error);
        this.searchResults = [];
      } finally {
        this.loading = false;
      }
    },
  });

  // Form store for dynamic forms
  Alpine.store('form', {
    data: {},
    errors: {},
    loading: false,

    init(formData = {}) {
      this.data = { ...formData };
      this.errors = {};
      this.loading = false;
    },

    setField(field, value) {
      this.data[field] = value;
      // Clear field error when user starts typing
      if (this.errors[field]) {
        delete this.errors[field];
      }
    },

    setErrors(errors) {
      this.errors = errors;
    },

    validate() {
      // Basic validation - extend as needed
      const errors = {};

      // Add field-specific validation here

      this.errors = errors;
      return Object.keys(errors).length === 0;
    },

    async submit(url, method = 'POST') {
      if (!this.validate()) {
        return { success: false, errors: this.errors };
      }

      this.loading = true;
      try {
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${Alpine.store('auth').token}`,
          },
          body: JSON.stringify(this.data),
        });

        const result = await response.json();

        if (response.ok) {
          return { success: true, data: result };
        } else {
          this.setErrors(result.detail || result);
          return { success: false, errors: this.errors };
        }
      } catch (error) {
        console.error('Form submission error:', error);
        return { success: false, error: error.message };
      } finally {
        this.loading = false;
      }
    },
  });
}

// Utility functions
window.HealthcareUtils = {
  // Format date for display
  formatDate(dateString, options = {}) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      ...options,
    });
  },

  // Format date and time
  formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  },

  // Format phone number
  formatPhone(phone) {
    if (!phone) return '';
    // Egyptian phone format: +20 XXX XXX XXXX
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11 && cleaned.startsWith('01')) {
      return `+20 ${cleaned.slice(1, 4)} ${cleaned.slice(4, 7)} ${cleaned.slice(7)}`;
    }
    return phone;
  },

  // Format SSN (Egyptian format)
  formatSSN(ssn) {
    if (!ssn) return '';
    // Egyptian SSN format: XXX-XX-XXXX-XXXXXX
    const cleaned = ssn.replace(/\D/g, '');
    if (cleaned.length === 14) {
      return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 5)}-${cleaned.slice(5, 9)}-${cleaned.slice(9)}`;
    }
    return ssn;
  },

  // Calculate age from birth date
  calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();

    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birth.getDate())
    ) {
      age--;
    }

    return age;
  },

  // Validate vital signs ranges
  validateVitalSigns(vitals) {
    const ranges = {
      temperature: { min: 30, max: 45 }, // Celsius
      pulse: { min: 30, max: 200 }, // bpm
      bloodPressureSystolic: { min: 70, max: 250 }, // mmHg
      bloodPressureDiastolic: { min: 40, max: 150 }, // mmHg
      respiration: { min: 8, max: 60 }, // breaths/min
      oxygenSaturation: { min: 70, max: 100 }, // %
      weight: { min: 1, max: 300 }, // kg
      height: { min: 30, max: 250 }, // cm
    };

    const errors = {};

    Object.keys(vitals).forEach((key) => {
      const value = parseFloat(vitals[key]);
      if (ranges[key] && !isNaN(value)) {
        if (value < ranges[key].min || value > ranges[key].max) {
          errors[key] =
            `Value must be between ${ranges[key].min} and ${ranges[key].max}`;
        }
      }
    });

    return errors;
  },

  // Debounce function for search inputs
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Show loading spinner
  showLoading() {
    Alpine.store('ui').setLoading(true);
  },

  // Hide loading spinner
  hideLoading() {
    Alpine.store('ui').setLoading(false);
  },

  // Show success notification
  showSuccess(message) {
    Alpine.store('ui').showNotification(message, 'success');
  },

  // Show error notification
  showError(message) {
    Alpine.store('ui').showNotification(message, 'error');
  },

  // Confirm dialog
  async confirm(message) {
    return window.confirm(message);
  },
};

// HTMX configuration
document.addEventListener('DOMContentLoaded', function () {
  // Configure HTMX
  htmx.config.globalViewTransitions = true;
  htmx.config.useTemplateFragments = true;

  // Add loading indicators
  document.body.addEventListener('htmx:beforeRequest', function (evt) {
    HealthcareUtils.showLoading();
  });

  document.body.addEventListener('htmx:afterRequest', function (evt) {
    HealthcareUtils.hideLoading();
  });

  // Handle HTMX errors
  document.body.addEventListener('htmx:responseError', function (evt) {
    const error = evt.detail.xhr.responseText || 'An error occurred';
    HealthcareUtils.showError(error);
  });

  // Handle authentication errors
  document.body.addEventListener('htmx:responseError', function (evt) {
    if (evt.detail.xhr.status === 401) {
      Alpine.store('auth').clearAuth();
      window.location.href = '/login';
    }
  });
});

// Alpine components registered globally so SPA-injected pages work
document.addEventListener('alpine:init', () => {
  // Dashboard component
  Alpine.data('dashboard', () => ({
    stats: {
      totalPatients: 0,
      todayVisits: 0,
      pendingAssessments: 0,
      weekVisits: 0,
    },
    recentActivity: [],

    async init() {
      await this.loadStats();
      await this.loadRecentActivity();
    },

    async loadStats() {
      try {
        const response = await fetch('/api/dashboard/stats', {
          headers: {
            Authorization: `Bearer ${Alpine.store('auth').token}`,
          },
        });

        if (response.ok) {
          this.stats = await response.json();
        }
      } catch (error) {
        console.error('Failed to load dashboard stats:', error);
      }
    },

    async loadRecentActivity() {
      try {
        const response = await fetch('/api/dashboard/activity', {
          headers: {
            Authorization: `Bearer ${Alpine.store('auth').token}`,
          },
        });

        if (response.ok) {
          this.recentActivity = await response.json();
        }
      } catch (error) {
        console.error('Failed to load recent activity:', error);
      }
    },
  }));

  // Patients page component
  Alpine.data('patientsPage', () => ({
    patients: [],
    loading: true,
    searchQuery: '',

    async init() {
      await this.loadPatients();
    },

    async loadPatients() {
      this.loading = true;
      try {
        const response = await fetch('/api/patients', {
          headers: {
            Authorization: `Bearer ${Alpine.store('auth').token}`,
          },
        });

        if (response.ok) {
          this.patients = await response.json();
        } else if (response.status === 401) {
          Alpine.store('auth').clearAuth();
          window.location.href = '/login';
        } else {
          this.patients = [];
        }
      } catch (error) {
        console.error('Failed to load patients:', error);
        this.patients = [];
      } finally {
        this.loading = false;
      }
    },

    debouncedSearch() {
      // Simple placeholder for search; enhance later
      console.log('Searching for:', this.searchQuery);
    },
  }));
});
