# Healthcare Frontend Data Model

## Overview
This document describes the data structures, API contracts, and integration points for the healthcare patient management frontend. The frontend interacts with the existing FastAPI backend through RESTful APIs using HTMX for dynamic content loading.

## Data Architecture

### Core Entities

#### User
```typescript
interface User {
  user_id: UUID;
  username: string;
  email: string;
  full_name: string;
  role: 'nurse' | 'physician' | 'admin';
  is_active: boolean;
  created_at: Date;
  last_login?: Date;
}
```

**Frontend Usage:**
- Authentication state management
- Role-based UI rendering
- User profile display
- Admin user management

#### Patient
```typescript
interface Patient {
  ssn: string; // 14-digit Egyptian format
  mobile_number: string; // Egyptian format
  full_name: string;
  date_of_birth?: Date;
  gender?: 'male' | 'female' | 'other';
  address?: string;
  phone_number?: string;
  medical_number?: string; // Hospital ID
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  created_at: Date;
  updated_at: Date;
  created_by: UUID;
  is_active: boolean;
}
```

**Frontend Usage:**
- Patient search and registration
- Profile management
- Visit association
- Emergency contact display

#### PatientVisit
```typescript
interface PatientVisit {
  visit_id: UUID;
  patient_ssn: string;
  visit_date: Date;
  visit_status: 'open' | 'in_progress' | 'completed' | 'cancelled';
  visit_type: 'outpatient' | 'inpatient' | 'emergency';
  department?: string;
  primary_diagnosis?: string;
  secondary_diagnosis?: string;
  notes?: string;
  created_by: UUID;
  created_at: Date;
  updated_at: Date;
}
```

**Frontend Usage:**
- Visit creation and tracking
- Form association
- Status management
- Timeline display

#### NursingAssessment (Check-Eval Form)
```typescript
interface NursingAssessment {
  assessment_id: UUID;
  submission_id: UUID;
  assessed_by: UUID;
  assessed_at: Date;

  // Basic Info
  mode_of_arrival?: string;
  age?: number;
  chief_complaint?: string;
  accompanied_by?: string;
  language_spoken?: string;

  // Vital Signs
  temperature_celsius?: number;
  pulse_bpm?: number;
  blood_pressure_systolic?: number;
  blood_pressure_diastolic?: number;
  respiratory_rate_per_min?: number;
  oxygen_saturation_percent?: number;
  blood_sugar_mg_dl?: number;
  weight_kg?: number;
  height_cm?: number;

  // Psychosocial
  psychological_problem?: string;
  is_smoker?: boolean;
  has_allergies?: boolean;
  medication_allergies?: string;
  food_allergies?: string;

  // Nutrition
  diet_type?: string;
  appetite?: string;
  has_git_problems?: boolean;
  has_weight_loss?: boolean;
  refer_to_nutritionist?: boolean;

  // Functional Assessment
  feeding_status?: string;
  hygiene_status?: string;
  toileting_status?: string;
  ambulation_status?: string;

  // Musculoskeletal
  has_deformities?: boolean;
  is_amputee?: boolean;
  is_bedridden?: boolean;
  uses_walker?: boolean;
  uses_wheelchair?: boolean;

  // Pain Assessment
  pain_intensity?: number; // 0-10
  pain_location?: string;
  pain_frequency?: string;
  pain_character?: string;

  // Fall Risk
  fall_history_3months?: boolean;
  ambulatory_aid?: string;
  gait_status?: string;
  mental_status?: string;
  morse_total_score?: number;

  // Educational Needs
  educational_needs?: string[]; // Array of selected needs

  // Elderly/Disabled
  elderly_assessment?: string;
  disability_assessment?: string;
}
```

**Frontend Usage:**
- Multi-section nursing assessment form
- Auto-save functionality
- Progress tracking
- Validation with medical ranges

#### RadiologyAssessment (General Sheet Form)
```typescript
interface RadiologyAssessment {
  radiology_id: UUID;
  submission_id: UUID;
  assessed_by: UUID;
  assessed_at: Date;

  // Preparation & Technical
  preparation_time?: string;
  injection_time?: string;
  injection_site?: string;
  ctd1vol?: number;
  dlp?: number;
  uses_contrast?: boolean;
  kidney_function_value?: number;

  // Study Information
  is_first_time?: boolean;
  is_comparison?: boolean;
  previous_study_code?: string;
  requires_report?: boolean;
  requires_cd?: boolean;

  // Clinical Information
  diagnosis?: string;
  reason_for_study?: string;

  // Assessment Results
  findings: string; // Required
  impression?: string;
  recommendations?: string;

  // Technical Details
  modality?: string; // CT, MRI, X-ray
  body_region?: string;
  contrast_used?: string;

  // Treatment History
  has_chemotherapy?: boolean;
  chemo_type?: string;
  chemo_details?: string;
  chemo_sessions?: number;
  chemo_last_date?: Date;
  has_radiotherapy?: boolean;
  radiotherapy_site?: string;
  radiotherapy_sessions?: number;
  radiotherapy_last_date?: Date;
  has_hormonal_treatment?: boolean;
  hormonal_last_dose_date?: Date;
  other_treatments?: string;

  // Previous Imaging History
  has_operations?: boolean;
  has_endoscopy?: boolean;
  has_biopsies?: boolean;
  has_tc_dtpa_kidney_scan?: boolean;
  has_tc_mdp_bone_scan?: boolean;
  has_mri?: boolean;
  has_mammography?: boolean;
  has_ct?: boolean;
  has_xray?: boolean;
  has_ultrasound?: boolean;
  has_other_imaging?: boolean;
  other_imaging_desc?: string;

  // Additional Fields
  mas?: number; // milliampere-seconds
  kv?: number; // kilovoltage
  has_gypsum_splint?: boolean;
  has_chronic_disease?: boolean;
  chronic_disease_desc?: string;
  has_pacemaker?: boolean;
  has_slats_screws_joints?: boolean;
  is_pregnant?: boolean;
  has_pain_numbness?: boolean;
  pain_numbness_desc?: string;
  has_spinal_deformities?: boolean;
  has_swelling?: boolean;
  swelling_desc?: string;
  has_headache?: boolean;
  has_fever?: boolean;
  has_tumor_history?: boolean;
  tumor_location?: string;
  tumor_type?: string;
  operation_date?: Date;
  operation_reason?: string;
  previous_investigation_type?: string;
  previous_investigation_date?: Date;
  has_disc_slip?: boolean;
  medications_fall_risk?: string;
  current_medications?: string;
  patient_signature?: string;
  physician_signature?: string;
}
```

**Frontend Usage:**
- Comprehensive radiology assessment
- Conditional field display
- Rich text editing
- Digital signatures

#### Report
```typescript
interface Report {
  report_id: UUID;
  visit_id: UUID;
  summary?: string;
  doctor_notes?: string;
  created_by: UUID;
  created_at: Date;
}
```

**Frontend Usage:**
- Report generation and viewing
- Export functionality
- Audit trail

## API Integration Patterns

### HTMX Request/Response Patterns

#### Authentication Flow
```html
<!-- Login Form -->
<form hx-post="/api/v1/auth/login" hx-target="#auth-result">
  <input name="username" type="text">
  <input name="password" type="password">
  <button type="submit">Login</button>
</form>
```

#### Data Loading
```html
<!-- Patient List -->
<div hx-get="/api/v1/patients" hx-trigger="load, search-input delay:500ms">
  <!-- Patient data loaded here -->
</div>
```

#### Form Submission
```html
<!-- Auto-save Form -->
<form hx-post="/api/v1/forms/check-eval" hx-trigger="input delay:2s">
  <!-- Form fields -->
</form>
```

### State Management

#### Client-Side State (Alpine.js)
```javascript
// User authentication state
const user = Alpine.store('user', {
  data: null,
  token: localStorage.getItem('token'),
  role: null,

  login(token, userData) {
    this.token = token;
    this.data = userData;
    this.role = userData.role;
    localStorage.setItem('token', token);
  },

  logout() {
    this.token = null;
    this.data = null;
    this.role = null;
    localStorage.removeItem('token');
  }
});
```

#### Server State Synchronization
- HTMX handles server state updates
- Alpine.js manages local reactivity
- JWT tokens included in all requests
- Error states propagated to UI

## Data Validation Rules

### Patient Data
- SSN: 14 digits, Egyptian format validation
- Mobile: 01[0-2] followed by 8 digits
- Email: Standard email format
- Dates: Valid date ranges, no future dates for birth

### Medical Data
- Temperature: 30.0 - 45.0 °C
- Pulse: 30 - 200 bpm
- Blood Pressure: 70-250 / 40-150 mmHg
- Respiratory Rate: 8 - 60 breaths/min
- Oxygen Saturation: 0.0 - 100.0%
- Pain Scale: 0 - 10

### Form Validation
- Required fields marked and validated
- Real-time validation with visual feedback
- Server-side validation as final check
- Custom validation for medical logic

## Error Handling

### HTTP Error Codes
- 400: Validation errors (field-specific messages)
- 401: Authentication required
- 403: Insufficient permissions
- 404: Resource not found
- 422: Business logic validation
- 500: Server errors

### Frontend Error Handling
```html
<!-- Error Display -->
<div id="errors" class="hidden">
  <div class="error-message"></div>
</div>

<!-- HTMX Error Handling -->
<div hx-target="#errors" hx-swap="innerHTML">
  <!-- Error content loaded here -->
</div>
```

### User Feedback
- Toast notifications for success/error
- Inline validation messages
- Loading indicators for async operations
- Progress bars for multi-step processes

## Performance Optimization

### Loading Strategies
- Lazy loading for large forms
- Pagination for data tables
- Debounced search inputs
- Progressive form loading

### Caching Strategy
- Browser caching for static assets
- API response caching where safe
- Local storage for user preferences
- Service worker for offline capabilities

### Bundle Optimization
- Tree shaking for unused code
- Code splitting by routes
- Minification and compression
- CDN delivery for assets

## Security Considerations

### Data Protection
- HTTPS for all communications
- JWT token security
- Input sanitization
- XSS prevention
- CSRF protection

### Access Control
- Role-based UI rendering
- API permission checks
- Audit logging
- Session management

### Compliance
- HIPAA compliance for PHI
- Data encryption at rest/transit
- Access logging and monitoring
- Regular security audits

## Testing Data Structures

### Mock Data for Development
```javascript
const mockPatient = {
  ssn: "12345678901234",
  mobile_number: "01234567890",
  full_name: "John Doe",
  date_of_birth: "1980-01-01",
  gender: "male",
  address: "123 Main St"
};

const mockVisit = {
  visit_id: "123e4567-e89b-12d3-a456-426614174000",
  patient_ssn: "12345678901234",
  visit_date: "2025-09-21T10:00:00Z",
  visit_status: "open",
  department: "Emergency"
};
```

### Test Scenarios
- Valid data submission
- Invalid data validation
- Network error handling
- Authentication failures
- Permission denied scenarios
- Large dataset performance
- Concurrent user access

This data model provides the foundation for building a robust, scalable healthcare frontend that integrates seamlessly with the existing FastAPI backend while maintaining high standards for security, accessibility, and user experience.</content>
<parameter name="filePath">/home/mohamed/lab/.specify/specs/data-model.md