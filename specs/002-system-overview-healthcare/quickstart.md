# Quickstart Test Scenarios

## Primary User Story Validation
**As a healthcare professional, I want to manage patient visits through a backend API so that I can archive visits, perform nursing and radiology assessments, and store documents securely.**

### Scenario 1: Nurse Creates Patient and Visit
1. **Given** a nurse is authenticated
2. **When** they create a new patient with valid SSN and mobile number
3. **Then** the patient is created successfully
4. **When** they create a new visit for that patient
5. **Then** the visit is created with status 'open'
6. **When** they submit nursing assessment with vital signs
7. **Then** the assessment is saved and linked to the visit

### Scenario 2: Physician Completes Radiology Assessment
1. **Given** a physician is authenticated
2. **When** they view open visits
3. **Then** they see visits with nursing assessments completed
4. **When** they select a visit and submit radiology assessment
5. **Then** the assessment is saved with findings and diagnosis
6. **When** they update the visit status to completed
7. **Then** the visit is marked as completed

### Scenario 3: Document Upload and Management
1. **Given** a nurse is authenticated with an open visit
2. **When** they upload a document (PDF, image)
3. **Then** the document is stored securely with metadata
4. **When** they view documents for the visit
5. **Then** they see the uploaded document in the list
6. **When** authorized users download the document
7. **Then** the file is retrieved successfully

### Scenario 4: Admin Generates Reports
1. **Given** an admin is authenticated
2. **When** they request dashboard report
3. **Then** they receive aggregated statistics
4. **When** they request patient statistics
5. **Then** they get patient count, demographics, visit frequency
6. **When** they request visit volume report
7. **Then** they get visit counts by date, status, type
8. **When** they request clinical assessments report
9. **Then** they get assessment completion rates, findings summary

### Scenario 5: Role-Based Access Control
1. **Given** a nurse is authenticated
2. **When** they attempt to access admin reports
3. **Then** they receive unauthorized error
4. **Given** a physician is authenticated
5. **When** they attempt to create patients
6. **Then** they receive forbidden error
7. **Given** an admin is authenticated
8. **When** they access all system features
9. **Then** they have full access

### Scenario 6: Data Validation and Error Handling
1. **Given** invalid patient data (wrong SSN format)
2. **When** attempting to create patient
3. **Then** receive validation error with specific message
4. **Given** duplicate SSN
5. **When** attempting to create patient
6. **Then** receive conflict error
7. **Given** invalid vital signs (temperature > 45°C)
8. **When** submitting nursing assessment
9. **Then** receive validation error

### Scenario 7: Audit and Compliance
1. **Given** any user action (create, update, delete)
2. **When** the action completes
3. **Then** audit log entry is created with user, action, resource, timestamp
4. **When** accessing PHI data
5. **Then** access is logged with IP and user agent
6. **When** admin reviews audit logs
7. **Then** they see complete action history

## Performance Validation
- **Response Time**: All API calls <500ms p95
- **Concurrent Users**: Support 1000+ simultaneous connections
- **File Upload**: Handle 10MB files within 30 seconds
- **Report Generation**: Complete within 60 seconds for large datasets

## Security Validation
- **Authentication**: JWT tokens expire correctly
- **Authorization**: Role permissions enforced
- **Data Encryption**: PHI encrypted at rest and in transit
- **Input Validation**: All inputs sanitized and validated
- **Audit Trail**: All actions logged without sensitive data leakage