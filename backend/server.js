// Backend Express Server for Medical Forms System
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
require('dotenv').config();

// Import database manager
const dbManager = require('./database-json');

const app = express();
const PORT = process.env.PORT || 8004;

// Middleware
app.use(helmet({
  crossOriginEmbedderPolicy: false,
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

app.use(cors({
  origin: process.env.FRONTEND_URL || 'https://millio.space:8005',
  credentials: true,
}));

app.use(compression());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// File upload configuration
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadPath = path.join(__dirname, 'uploads');
    try {
      await fs.mkdir(uploadPath, { recursive: true });
      cb(null, uploadPath);
    } catch (error) {
      cb(error);
    }
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|pdf|doc|docx/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  }
});

// Utility functions
const generateMedicalId = async () => {
  const year = new Date().getFullYear();
  const timestamp = Date.now().toString().slice(-6);
  return `MED-${year}-${timestamp}`;
};

const calculateFallRisk = (assessmentData) => {
  let score = 0;

  // Previous fall in last 3 months
  if (assessmentData.previousFall) score += 25;

  // Secondary diagnosis (2 or more medical diagnoses)
  if (assessmentData.secondaryDiagnosis) score += 15;

  // Ambulatory aid
  if (assessmentData.ambulatoryAid === 'furniture') score += 30;
  else if (assessmentData.ambulatoryAid === 'crutches_walker') score += 15;

  // IV therapy
  if (assessmentData.ivTherapy) score += 20;

  // Gait
  if (assessmentData.gaitStatus === 'impaired') score += 20;
  else if (assessmentData.gaitStatus === 'weak') score += 10;

  // Mental status
  if (assessmentData.mentalStatus === 'forgets_limitations') score += 15;

  let riskLevel;
  if (score <= 24) riskLevel = 'low';
  else if (score <= 49) riskLevel = 'moderate';
  else riskLevel = 'high';

  return { score, riskLevel };
};

const calculateHumptyDumptyScore = (assessmentData) => {
  let score = 0;

  // Age
  if (assessmentData.age >= 6 && assessmentData.age < 7) score += 3;
  else if (assessmentData.age >= 7 && assessmentData.age < 13) score += 2;
  else if (assessmentData.age >= 13) score += 1;

  // Gender
  if (assessmentData.gender === 'male') score += 2;
  else score += 1;

  // Diagnosis
  if (assessmentData.diagnosis === 'neurological') score += 4;
  else if (assessmentData.diagnosis === 'oxygenation') score += 3;
  else if (assessmentData.diagnosis === 'behavioral') score += 2;
  else score += 1;

  // Cognitive impairment
  if (assessmentData.cognitiveImpairment === 'unaware') score += 3;
  else if (assessmentData.cognitiveImpairment === 'forgets') score += 2;
  else score += 1;

  // Environmental factors
  if (assessmentData.environmentalFactors === 'history_fall') score += 4;
  else if (assessmentData.environmentalFactors === 'assistive_devices') score += 3;
  else if (assessmentData.environmentalFactors === 'infant_bed') score += 2;
  else score += 1;

  // Surgery/sedation
  if (assessmentData.surgerySedation === 'within_24h') score += 3;
  else if (assessmentData.surgerySedation === 'within_48h') score += 2;
  else score += 1;

  // Medication use
  if (assessmentData.medicationUse === 'multiple') score += 3;
  else if (assessmentData.medicationUse === 'one') score += 2;
  else score += 1;

  let riskLevel;
  if (score <= 6) riskLevel = 'low';
  else if (score <= 11) riskLevel = 'moderate';
  else riskLevel = 'high';

  return { score, riskLevel };
};

// Routes

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Initialize database
async function startServer() {
  try {
    await dbManager.initialize();
    console.log('✅ Database initialized successfully');
    
    app.listen(PORT, () => {
      console.log(`Medical Forms Server running on port ${PORT}`);
      console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
      console.log(`Frontend URL: ${process.env.FRONTEND_URL || 'http://p.millio.space:8005'}`);
    });
  } catch (error) {
    console.error('❌ Failed to initialize database:', error);
    process.exit(1);
  }
}

startServer();

// Patient routes
app.get('/api/patients', async (req, res) => {
  try {
    const { page = 1, limit = 50, search } = req.query;
    const result = await dbManager.getAllPatients({ page, limit, search });
    res.json(result);
  } catch (error) {
    console.error('Get patients error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.put('/api/patients/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const patientData = req.body;

    const updatedPatient = await dbManager.updatePatient(id, patientData);
    res.json(updatedPatient);
  } catch (error) {
    console.error('Update patient error:', error);
    if (error.message === 'Patient not found') {
      res.status(404).json({ message: 'Patient not found' });
    } else {
      res.status(500).json({ message: 'Internal server error' });
    }
  }
});

app.post('/api/patients', async (req, res) => {
  try {
    const patientData = req.body;

    // Generate medical ID
    patientData.medicalId = generateMedicalId();

    const newPatient = await dbManager.createPatient(patientData);
    res.status(201).json(newPatient);
  } catch (error) {
    console.error('Create patient error:', error);
    if (error.message && error.message.includes('duplicate key value')) {
      if (error.message.includes('medical_id')) {
        res.status(409).json({ message: 'Medical ID already exists' });
      } else if (error.message.includes('id_number')) {
        res.status(409).json({ message: 'ID Number already exists' });
      } else {
        res.status(409).json({ message: 'Duplicate data detected' });
      }
    } else {
      res.status(500).json({ message: 'Internal server error' });
    }
  }
});

// PET CT Form routes
app.get('/api/forms/pet-ct', async (req, res) => {
  try {
    const { page = 1, limit = 50, status, patientId } = req.query;
    const result = await dbManager.getAllForms('pet-ct', { page, limit, status, patientId });
    res.json(result);
  } catch (error) {
    console.error('Get PET CT forms error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.post('/api/forms/pet-ct', async (req, res) => {
  try {
    const formData = req.body;

    // Add metadata
    formData.createdBy = '1'; // Mock user ID - should come from auth
    formData.formStatus = formData.formStatus || 'draft';

    const newForm = await dbManager.createForm('pet-ct', formData);
    res.status(201).json(newForm);
  } catch (error) {
    console.error('Create PET CT form error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Save PET-CT draft (explicit endpoint used by frontend)
app.post('/api/forms/pet-ct/draft', async (req, res) => {
  try {
    const formData = req.body || {};
    formData.createdBy = '1';
    formData.formStatus = 'draft';

    const newDraft = await dbManager.createForm('pet-ct', formData);
    res.status(201).json(newDraft);
  } catch (error) {
    console.error('Save PET CT draft error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Server-side validation for PET-CT submit
function validatePetCtSubmission(data) {
  const errors = {};

  if (!data.patientName || typeof data.patientName !== 'string' || data.patientName.trim() === '') {
    errors.patientName = 'Patient name is required';
  }

  const age = data.age;
  if (age === undefined || age === null || age === '' || isNaN(Number(age))) {
    errors.age = 'Age is required and must be a number';
  } else if (Number(age) < 0 || Number(age) > 150) {
    errors.age = 'Age must be between 0 and 150';
  }

  if (data.weight === undefined || data.weight === '' || isNaN(Number(data.weight))) {
    errors.weight = 'Weight is required and must be a number';
  }

  if (data.height === undefined || data.height === '' || isNaN(Number(data.height))) {
    errors.height = 'Height is required and must be a number';
  }

  if (!data.diagnosis || typeof data.diagnosis !== 'string' || data.diagnosis.trim() === '') {
    errors.diagnosis = 'Diagnosis is required';
  }

  if (!data.studyReason || typeof data.studyReason !== 'string' || data.studyReason.trim() === '') {
    errors.studyReason = 'Study reason is required';
  }

  if (!data.attendingPhysician || typeof data.attendingPhysician !== 'string' || data.attendingPhysician.trim() === '') {
    errors.attendingPhysician = 'Attending physician is required';
  }

  return Object.keys(errors).length ? errors : null;
}

// Submit PET-CT form: validates required fields then creates with status 'submitted'
app.post('/api/forms/pet-ct/submit', async (req, res) => {
  try {
    const formData = req.body || {};

    const validationErrors = validatePetCtSubmission(formData);
    if (validationErrors) {
      return res.status(400).json({ message: 'Validation failed', errors: validationErrors });
    }

    formData.createdBy = '1'; // in real app, take from auth
    formData.formStatus = 'submitted';

    const created = await dbManager.createForm('pet-ct', formData);
    res.status(201).json(created);
  } catch (error) {
    console.error('Submit PET CT form error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// General Form routes
app.get('/api/forms/general', async (req, res) => {
  try {
    const { page = 1, limit = 50, formType, status } = req.query;
    const result = await dbManager.getAllForms('general', { page, limit, status, formType });
    res.json(result);
  } catch (error) {
    console.error('Get general forms error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.post('/api/forms/general', async (req, res) => {
  try {
    const formData = req.body;

    // Add metadata
    formData.createdBy = '1'; // Mock user ID - should come from auth
    formData.formStatus = formData.formStatus || 'draft';

    const newForm = await dbManager.createForm('general', formData);
    res.status(201).json(newForm);
  } catch (error) {
    console.error('Create general form error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Nursing Assessment routes
app.get('/api/forms/nursing', async (req, res) => {
  try {
    const { page = 1, limit = 50 } = req.query;
    const result = await dbManager.getAllForms('nursing', { page, limit });
    res.json(result);
  } catch (error) {
    console.error('Get nursing assessments error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.post('/api/forms/nursing', async (req, res) => {
  try {
    const assessmentData = req.body;

    // Calculate fall risk scores
    const fallRisk = calculateFallRisk(assessmentData);
    const humptyDumptyScore = assessmentData.age < 18 ?
      calculateHumptyDumptyScore(assessmentData) : null;

    // Prepare form data
    const formData = {
      ...assessmentData,
      fallRiskScore: fallRisk.score,
      fallRiskLevel: fallRisk.riskLevel,
      humptyDumptyScore: humptyDumptyScore?.score,
      humptyDumptyRisk: humptyDumptyScore?.riskLevel,
      createdBy: '1', // Mock user ID - should come from auth
      formStatus: assessmentData.formStatus || 'draft'
    };

    const newAssessment = await dbManager.createForm('nursing', formData);
    res.status(201).json(newAssessment);
  } catch (error) {
    console.error('Create nursing assessment error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Fall risk calculation endpoint
app.post('/api/forms/nursing/fall-risk', (req, res) => {
  try {
    const assessmentData = req.body;
    const fallRisk = calculateFallRisk(assessmentData);
    res.json(fallRisk);
  } catch (error) {
    console.error('Calculate fall risk error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// File upload routes
app.post('/api/files/upload', upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded' });
    }

    res.json({
      fileId: req.file.filename,
      originalName: req.file.originalname,
      size: req.file.size,
      type: req.file.mimetype,
      url: `/api/files/${req.file.filename}`,
    });
  } catch (error) {
    console.error('File upload error:', error);
    res.status(500).json({ message: 'File upload failed' });
  }
});

app.get('/api/files/:fileId', (req, res) => {
  try {
    const { fileId } = req.params;
    const filePath = path.join(__dirname, 'uploads', fileId);

    // Check if file exists
    if (require('fs').existsSync(filePath)) {
      res.sendFile(filePath);
    } else {
      res.status(404).json({ message: 'File not found' });
    }
  } catch (error) {
    console.error('File download error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Dashboard and reports
app.get('/api/reports/dashboard', async (req, res) => {
  try {
    const stats = await dbManager.getStats();

    // Get recent activity (forms created in last 10 days)
    const recentForms = [];
    const tables = ['pet_ct_forms', 'general_forms', 'nursing_assessments'];

    for (const table of tables) {
      // Query for recent forms from each table
      const query = `
        SELECT id, patient_id, created_at, $1 as type
        FROM ${table}
        WHERE created_at >= NOW() - INTERVAL '10 days' AND deleted_at IS NULL
        ORDER BY created_at DESC
        LIMIT 10
      `;
      
      const result = await dbManager.pool.query(query, [table.replace('_forms', '').replace('_assessments', '')]);
      recentForms.push(...result.rows);
    }

    // Sort by creation date
    recentForms.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    const recentActivity = recentForms.slice(0, 10);

    res.json({
      totalPatients: stats.patients || 0,
      totalForms: (stats.pet_ct_forms || 0) + (stats.general_forms || 0) + (stats.nursing_assessments || 0),
      completedForms: 0, // TODO: Calculate from form statuses
      draftForms: 0, // TODO: Calculate from form statuses
      recentActivity,
    });
  } catch (error) {
    console.error('Dashboard stats error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);

  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ message: 'File size too large' });
    }
  }

  res.status(500).json({ message: 'Internal server error' });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ message: 'Route not found' });
});

// Start server

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('Received SIGINT, shutting down gracefully...');
  await dbManager.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('Received SIGTERM, shutting down gracefully...');
  await dbManager.close();
  process.exit(0);
});

module.exports = app;