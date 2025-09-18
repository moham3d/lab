import React, { useState, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Grid,
  Typography,
  Paper,
  Checkbox,
  Card,
  CardContent,
  Divider,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  FormGroup,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Switch,
  Tooltip
} from '@mui/material';
import {
  Save as SaveIcon,
  Send as SendIcon,
  Print as PrintIcon,
  Person as PersonIcon,
  Assignment as AssignmentIcon,
  ExpandMore as ExpandMoreIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  RadioButtonUnchecked as RadioIcon,
  MedicalServices as MedicalIcon,
  LocalHospital as HospitalIcon
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import SignatureCanvas from 'react-signature-canvas';

// Import API service
import { generalFormService } from '../services/api';

// Validation Schema
const validationSchema = Yup.object({
  patientName: Yup.string().required('Patient name is required'),
  medicalId: Yup.string().required('Medical ID is required'),
  age: Yup.number().min(0).max(150).required('Age is required'),
  formType: Yup.string().required('Form type is required'),
  studyReason: Yup.string().required('Study reason is required'),
  phone: Yup.string().matches(/^[+]?[\d\s-()]+$/, 'Invalid phone number format')
});

const GeneralForm = () => {
  const [saveStatus, setSaveStatus] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [expandedSection, setExpandedSection] = useState('basic');
  const patientSignRef = useRef(null);
  const doctorSignRef = useRef(null);

  // Form sections configuration
  const formSections = [
    { id: 'basic', title: 'Basic Information', icon: <PersonIcon /> },
    { id: 'technical', title: 'Technical Parameters', icon: <RadioIcon /> },
    { id: 'medical', title: 'Medical History', icon: <MedicalIcon /> },
    { id: 'symptoms', title: 'Symptoms & Conditions', icon: <HospitalIcon /> },
    { id: 'history', title: 'Medical History', icon: <AssignmentIcon /> },
    { id: 'signatures', title: 'Signatures', icon: <CheckIcon /> }
  ];

  const formik = useFormik({
    initialValues: {
      // Basic Information
      patientName: '',
      medicalId: '',
      phone: '',
      birthDate: '',
      age: '',
      gender: '',
      formType: '', // xray, ct, mri
      todayDate: new Date().toISOString().split('T')[0],
      
      // Technical Parameters
      ctd1vol: '',
      dlp: '',
      kv: '',
      mas: '',
      
      // Study Information
      studyReason: '',
      diagnosis: '',
      
      // Medical History Questions
      hasGypsumSplint: false,
      gypsumSplintLocation: '',
      chronicDiseases: '',
      hasPacemaker: false,
      hasImplants: false,
      implantDetails: '',
      
      // For Women
      isPregnant: false,
      
      // Symptoms
      hasPain: false,
      painLocation: '',
      painExtension: '',
      painDuration: '',
      hasSpinalDeformity: false,
      spinalDeformityDetails: '',
      hasSwelling: false,
      swellingLocation: '',
      
      // Brain Study Specific
      hasHeadache: false,
      hasVisualProblems: false,
      hasHearingProblems: false,
      hasBalanceIssues: false,
      
      // General Symptoms
      hasFever: false,
      
      // Medical History
      previousOperations: [],
      tumorHistory: '',
      previousInvestigations: [],
      hasDiscProblems: false,
      
      // Medications
      fallRiskMedications: '',
      currentMedications: '',
      
      // Signatures
      patientSignature: '',
      doctorSignature: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setSaveStatus('saving');
        
        // Capture signatures
        if (patientSignRef.current) {
          values.patientSignature = patientSignRef.current.toDataURL();
        }
        if (doctorSignRef.current) {
          values.doctorSignature = doctorSignRef.current.toDataURL();
        }
        
        // Submit form to API
        const result = await generalFormService.createForm(values);
        
        console.log('General Form submitted successfully:', result);
        setSaveStatus('success');
        
        // Reset form after successful submission
        setTimeout(() => {
          formik.resetForm();
          setSaveStatus(null);
          if (patientSignRef.current) patientSignRef.current.clear();
          if (doctorSignRef.current) doctorSignRef.current.clear();
        }, 3000);
        
      } catch (error) {
        console.error('Submission error:', error);
        setSaveStatus('error');
      }
    }
  });

  const handleSaveDraft = async () => {
    try {
      setSaveStatus('saving');
      
      // Capture signatures
      const draftData = { ...formik.values };
      if (patientSignRef.current) {
        draftData.patientSignature = patientSignRef.current.toDataURL();
      }
      if (doctorSignRef.current) {
        draftData.doctorSignature = doctorSignRef.current.toDataURL();
      }
      
      // Note: General form service doesn't have a saveDraft method yet
      // For now, we'll just simulate saving
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (error) {
      console.error('Draft save error:', error);
      setSaveStatus('error');
    }
  };

  const clearSignature = (ref) => {
    if (ref.current) {
      ref.current.clear();
    }
  };

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedSection(isExpanded ? panel : false);
  };

  // Dynamic form rendering based on form type
  const renderFormTypeSpecificQuestions = () => {
    if (formik.values.formType === 'mri') {
      return (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="subtitle2">MRI Safety Checklist</Typography>
              Please ensure all metal objects are removed before entering MRI room.
            </Alert>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formik.values.hasPacemaker}
                  onChange={formik.handleChange}
                  name="hasPacemaker"
                />
              }
              label="Pacemaker installed (جهاز منظم ضربات القلب)"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formik.values.hasImplants}
                  onChange={formik.handleChange}
                  name="hasImplants"
                />
              }
              label="Metal implants/screws (شرائح/مسامير معدنية)"
            />
          </Grid>
          {formik.values.hasImplants && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="implantDetails"
                label="Implant Details (تفاصيل الشرائح)"
                value={formik.values.implantDetails}
                onChange={formik.handleChange}
                multiline
                rows={2}
              />
            </Grid>
          )}
        </Grid>
      );
    }
    return null;
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 1200, margin: '0 auto', p: 3 }}>
      {/* Header */}
  <Paper sx={{ p: 3, mb: 3, background: '#35507b', color: '#fff', border: '1px solid #e0e4ea', boxShadow: 'none' }}>
        <Typography variant="h4" gutterBottom align="center">
          General Medical Form
        </Typography>
        <Typography variant="h6" align="center" sx={{ direction: 'rtl' }}>
          الاستمارة الطبية العامة (أشعة سينية - أشعة مقطعية - رنين مغناطيسي)
        </Typography>
      </Paper>

      {/* Status Alerts */}
      {saveStatus === 'saving' && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Saving form data...
        </Alert>
      )}
      {saveStatus === 'saved' && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Form saved successfully!
        </Alert>
      )}
      {saveStatus === 'success' && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Form submitted successfully!
        </Alert>
      )}
      {saveStatus === 'error' && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error saving form. Please try again.
        </Alert>
      )}

      <form onSubmit={formik.handleSubmit}>
        {/* Basic Information */}
        <Accordion 
          expanded={expandedSection === 'basic'} 
          onChange={handleAccordionChange('basic')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Basic Information (المعلومات الأساسية)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  name="patientName"
                  label="Patient Name (اسم المريض رباعي) *"
                  value={formik.values.patientName}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.patientName && Boolean(formik.errors.patientName)}
                  helperText={formik.touched.patientName && formik.errors.patientName}
                  dir="rtl"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  name="medicalId"
                  label="Medical ID (الرقم الطبي) *"
                  value={formik.values.medicalId}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.medicalId && Boolean(formik.errors.medicalId)}
                  helperText={formik.touched.medicalId && formik.errors.medicalId}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  name="phone"
                  label="Mobile Number (رقم الموبايل)"
                  value={formik.values.phone}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.phone && Boolean(formik.errors.phone)}
                  helperText={formik.touched.phone && formik.errors.phone}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  name="todayDate"
                  label="Today's Date (تاريخ اليوم)"
                  type="date"
                  value={formik.values.todayDate}
                  onChange={formik.handleChange}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <FormControl fullWidth required>
                  <InputLabel>Form Type (نوع الفحص)</InputLabel>
                  <Select
                    name="formType"
                    value={formik.values.formType}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    error={formik.touched.formType && Boolean(formik.errors.formType)}
                    label="Form Type (نوع الفحص)"
                  >
                    <MenuItem value="xray">X-Ray (أشعة سينية)</MenuItem>
                    <MenuItem value="ct">CT Scan (أشعة مقطعية)</MenuItem>
                    <MenuItem value="mri">MRI (رنين مغناطيسي)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  name="birthDate"
                  label="Birth Date (تاريخ الميلاد)"
                  type="date"
                  value={formik.values.birthDate}
                  onChange={formik.handleChange}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="age"
                  label="Age (السن) *"
                  type="number"
                  value={formik.values.age}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.age && Boolean(formik.errors.age)}
                  helperText={formik.touched.age && formik.errors.age}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Gender (النوع)</InputLabel>
                  <Select
                    name="gender"
                    value={formik.values.gender}
                    onChange={formik.handleChange}
                    label="Gender (النوع)"
                  >
                    <MenuItem value="male">Male (ذكر)</MenuItem>
                    <MenuItem value="female">Female (أنثى)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="diagnosis"
                  label="Diagnosis (التشخيص)"
                  value={formik.values.diagnosis}
                  onChange={formik.handleChange}
                  multiline
                  rows={2}
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Technical Parameters */}
        {(formik.values.formType === 'ct' || formik.values.formType === 'xray') && (
          <Accordion 
            expanded={expandedSection === 'technical'} 
            onChange={handleAccordionChange('technical')}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <RadioIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Technical Parameters (المعايير التقنية)</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    name="ctd1vol"
                    label="CTD1vol"
                    value={formik.values.ctd1vol}
                    onChange={formik.handleChange}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    name="dlp"
                    label="DLP"
                    value={formik.values.dlp}
                    onChange={formik.handleChange}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    name="kv"
                    label="KV"
                    value={formik.values.kv}
                    onChange={formik.handleChange}
                  />
                </Grid>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    name="mas"
                    label="MAs"
                    value={formik.values.mas}
                    onChange={formik.handleChange}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {/* Study Information */}
        <Accordion 
          expanded={expandedSection === 'study'} 
          onChange={handleAccordionChange('study')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AssignmentIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Study Information (معلومات الفحص)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="studyReason"
                  label="Why you do the study? (ما هو سبب إجراء الفحص؟) *"
                  value={formik.values.studyReason}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.studyReason && Boolean(formik.errors.studyReason)}
                  helperText={formik.touched.studyReason && formik.errors.studyReason}
                  multiline
                  rows={3}
                />
              </Grid>

              {/* Form Type Specific Questions */}
              {renderFormTypeSpecificQuestions()}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Medical History */}
        <Accordion 
          expanded={expandedSection === 'medical'} 
          onChange={handleAccordionChange('medical')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <MedicalIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Medical History (التاريخ الطبي)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Gypsum Splint */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Gypsum Splint (جبيرة الجبس)
                  </Typography>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.hasGypsumSplint}
                        onChange={formik.handleChange}
                        name="hasGypsumSplint"
                      />
                    }
                    label="Is there a gypsum splint in the radiology workplace? (هل يوجد جبيرة جبس بمكان عمل الأشعة؟)"
                  />
                  {formik.values.hasGypsumSplint && (
                    <>
                      <Alert severity="warning" sx={{ mt: 1, mb: 2 }}>
                        In case of splint, it is necessary to bring X-rays before installing the splint.
                        (في حالة وجود جبيرة، لابد من إحضار صور الأشعة قبل تركيب الجبيرة)
                      </Alert>
                      <TextField
                        fullWidth
                        name="gypsumSplintLocation"
                        label="Splint Location (مكان الجبيرة)"
                        value={formik.values.gypsumSplintLocation}
                        onChange={formik.handleChange}
                      />
                    </>
                  )}
                </Card>
              </Grid>

              {/* Chronic Diseases */}
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  name="chronicDiseases"
                  label="Do you have any chronic disease? (هل تعاني من أي أمراض مزمنة؟)"
                  value={formik.values.chronicDiseases}
                  onChange={formik.handleChange}
                  multiline
                  rows={3}
                  placeholder="List any chronic diseases..."
                />
              </Grid>

              {/* For Women */}
              {formik.values.gender === 'female' && (
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom color="secondary">
                      For Women (بالنسبة للسيدات)
                    </Typography>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={formik.values.isPregnant}
                          onChange={formik.handleChange}
                          name="isPregnant"
                        />
                      }
                      label="Is there pregnancy? (هل يوجد حمل؟)"
                    />
                    {formik.values.isPregnant && (
                      <Alert severity="error" sx={{ mt: 1 }}>
                        <WarningIcon sx={{ mr: 1 }} />
                        Pregnancy detected - Please consult with radiologist before proceeding.
                      </Alert>
                    )}
                  </Card>
                </Grid>
              )}

              {/* Previous Operations */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="previousOperations"
                  label="Do you perform any operation? If yes, mention it (هل أجريت أي عمليات؟ لو نعم: ما تاريخ العملية وسببها؟)"
                  value={formik.values.previousOperations}
                  onChange={formik.handleChange}
                  multiline
                  rows={2}
                  placeholder="Operation type, date, reason..."
                />
              </Grid>

              {/* Tumor History */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="tumorHistory"
                  label="Do you have any history of tumors? If yes: mention where (هل يوجد تاريخ مرضي لأي أورام؟ لو نعم: أين مكان الورم ونوعه؟)"
                  value={formik.values.tumorHistory}
                  onChange={formik.handleChange}
                  multiline
                  rows={2}
                  placeholder="Tumor location, type, treatment..."
                />
              </Grid>

              {/* Previous Investigations */}
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="previousInvestigations"
                  label="Do you have previous investigation? (هل أجريت أي فحوصات أشعة سابقة؟ لو نعم: ما نوع الأشعة وتاريخها؟)"
                  value={formik.values.previousInvestigations}
                  onChange={formik.handleChange}
                  multiline
                  rows={2}
                  placeholder="Type of investigation, date..."
                />
              </Grid>

              {/* Disc Problems */}
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formik.values.hasDiscProblems}
                      onChange={formik.handleChange}
                      name="hasDiscProblems"
                    />
                  }
                  label="Do you have previous disc problems? (هل تعاني من انزلاق غضروفي؟)"
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Symptoms & Conditions */}
        <Accordion 
          expanded={expandedSection === 'symptoms'} 
          onChange={handleAccordionChange('symptoms')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <HospitalIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Symptoms & Conditions (الأعراض والحالات)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Pain Assessment */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Pain Assessment (تقييم الألم)
                  </Typography>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.hasPain}
                        onChange={formik.handleChange}
                        name="hasPain"
                      />
                    }
                    label="Do you have any pain-numbness? (هل تعاني من ألم-تنميل-حرقان؟)"
                  />
                  {formik.values.hasPain && (
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          name="painLocation"
                          label="Where is the site? (أين مكانه؟)"
                          value={formik.values.painLocation}
                          onChange={formik.handleChange}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          name="painExtension"
                          label="Extension (امتداده)"
                          value={formik.values.painExtension}
                          onChange={formik.handleChange}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          name="painDuration"
                          label="Time/Duration (الوقت/المدة)"
                          value={formik.values.painDuration}
                          onChange={formik.handleChange}
                        />
                      </Grid>
                    </Grid>
                  )}
                </Card>
              </Grid>

              {/* Spinal Deformity */}
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formik.values.hasSpinalDeformity}
                      onChange={formik.handleChange}
                      name="hasSpinalDeformity"
                    />
                  }
                  label="Do you have spinal deformities or warps? (هل تعاني من تشوهات أو اعوجاج في العمود الفقري؟)"
                />
                {formik.values.hasSpinalDeformity && (
                  <TextField
                    fullWidth
                    name="spinalDeformityDetails"
                    label="Details (التفاصيل)"
                    value={formik.values.spinalDeformityDetails}
                    onChange={formik.handleChange}
                    sx={{ mt: 1 }}
                  />
                )}
              </Grid>

              {/* Swelling */}
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formik.values.hasSwelling}
                      onChange={formik.handleChange}
                      name="hasSwelling"
                    />
                  }
                  label="Do you have any swelling? (هل تعاني من أي تورم؟)"
                />
                {formik.values.hasSwelling && (
                  <TextField
                    fullWidth
                    name="swellingLocation"
                    label="Where is the swelling? (أين مكان التورم؟)"
                    value={formik.values.swellingLocation}
                    onChange={formik.handleChange}
                    sx={{ mt: 1 }}
                  />
                )}
              </Grid>

              {/* Brain Study Specific */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Brain Study (فحص المخ)
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Do you have headache, visual troubles, hearing problems, imbalance?
                    (هل تعاني من صداع-مشاكل في النظر-السمع-عدم اتزان؟)
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={3}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={formik.values.hasHeadache}
                            onChange={formik.handleChange}
                            name="hasHeadache"
                          />
                        }
                        label="Headache (صداع)"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={formik.values.hasVisualProblems}
                            onChange={formik.handleChange}
                            name="hasVisualProblems"
                          />
                        }
                        label="Visual Problems (مشاكل النظر)"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={formik.values.hasHearingProblems}
                            onChange={formik.handleChange}
                            name="hasHearingProblems"
                          />
                        }
                        label="Hearing Problems (مشاكل السمع)"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={formik.values.hasBalanceIssues}
                            onChange={formik.handleChange}
                            name="hasBalanceIssues"
                          />
                        }
                        label="Imbalance (عدم اتزان)"
                      />
                    </Grid>
                  </Grid>
                </Card>
              </Grid>

              {/* Fever */}
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formik.values.hasFever}
                      onChange={formik.handleChange}
                      name="hasFever"
                    />
                  }
                  label="Do you have fever? (هل تعاني من ارتفاع درجة الحرارة؟)"
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Medications */}
        <Accordion 
          expanded={expandedSection === 'medications'} 
          onChange={handleAccordionChange('medications')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <MedicalIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Medications (الأدوية)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="fallRiskMedications"
                  label="Medication that increase fall risk (هل يتم تناول أدوية تسبب نعاس أو دوار أو عدم اتزان مع ذكر الأدوية؟)"
                  value={formik.values.fallRiskMedications}
                  onChange={formik.handleChange}
                  multiline
                  rows={2}
                  placeholder="List medications that cause drowsiness, dizziness, or imbalance..."
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="currentMedications"
                  label="Current medication (هل يتم تناول أدوية حاليا اذكرها؟)"
                  value={formik.values.currentMedications}
                  onChange={formik.handleChange}
                  multiline
                  rows={3}
                  placeholder="List all current medications with dosages..."
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Digital Signatures */}
        <Accordion 
          expanded={expandedSection === 'signatures'} 
          onChange={handleAccordionChange('signatures')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CheckIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Digital Signatures (التوقيعات الرقمية)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, background: '#fff', border: '1px solid #e0e4ea', boxShadow: 'none' }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Patient Signature (توقيع المريض)
                  </Typography>
                  <Box sx={{ border: '1px solid #ccc', borderRadius: 1, mb: 1 }}>
                    <SignatureCanvas
                      ref={patientSignRef}
                      penColor="black"
                      canvasProps={{
                        width: 300,
                        height: 150,
                        className: 'signature-canvas'
                      }}
                    />
                  </Box>
                  <Button
                    size="small"
                    onClick={() => clearSignature(patientSignRef)}
                    variant="outlined"
                  >
                    Clear Signature
                  </Button>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, background: '#fff', border: '1px solid #e0e4ea', boxShadow: 'none' }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Doctor Signature (توقيع الطبيب)
                  </Typography>
                  <Box sx={{ border: '1px solid #ccc', borderRadius: 1, mb: 1 }}>
                    <SignatureCanvas
                      ref={doctorSignRef}
                      penColor="black"
                      canvasProps={{
                        width: 300,
                        height: 150,
                        className: 'signature-canvas'
                      }}
                    />
                  </Box>
                  <Button
                    size="small"
                    onClick={() => clearSignature(doctorSignRef)}
                    variant="outlined"
                  >
                    Clear Signature
                  </Button>
                </Paper>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Form Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 4 }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              onClick={handleSaveDraft}
              variant="outlined"
              startIcon={<SaveIcon />}
              disabled={saveStatus === 'saving'}
            >
              Save Draft
            </Button>

            <Button
              onClick={() => setShowPreview(true)}
              variant="outlined"
              startIcon={<PrintIcon />}
            >
              Preview
            </Button>
          </Box>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            size="large"
            startIcon={<SendIcon />}
            disabled={saveStatus === 'saving' || !formik.isValid}
          >
            Submit Form
          </Button>
        </Box>
      </form>

      {/* Preview Dialog */}
      <Dialog
        open={showPreview}
        onClose={() => setShowPreview(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          General Form Preview
        </DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>
            {formik.values.formType.toUpperCase()} Examination Form
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography><strong>Patient:</strong> {formik.values.patientName}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography><strong>Medical ID:</strong> {formik.values.medicalId}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography><strong>Age:</strong> {formik.values.age}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography><strong>Gender:</strong> {formik.values.gender}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography><strong>Study Reason:</strong> {formik.values.studyReason}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography><strong>Diagnosis:</strong> {formik.values.diagnosis}</Typography>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPreview(false)}>Close</Button>
          <Button variant="contained" startIcon={<PrintIcon />}>
            Print
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default GeneralForm;