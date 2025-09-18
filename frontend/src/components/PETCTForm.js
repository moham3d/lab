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
  Stepper,
  Step,
  StepLabel,
  Paper,
  Checkbox,
  Autocomplete,
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
  MenuItem
} from '@mui/material';
import {
  Save as SaveIcon,
  Send as SendIcon,
  Print as PrintIcon,
  Person as PersonIcon,
  LocalHospital as HospitalIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import SignatureCanvas from 'react-signature-canvas';

// Import API service
import { petCtService } from '../services/api';

// Validation Schema
const validationSchema = Yup.object({
  patientName: Yup.string().required('Patient name is required'),
  age: Yup.number().min(0).max(150).required('Age is required'),
  weight: Yup.number().min(0).max(500).required('Weight is required'),
  height: Yup.number().min(0).max(300).required('Height is required'),
  diagnosis: Yup.string().required('Diagnosis is required'),
  studyReason: Yup.string().required('Study reason is required'),
  attendingPhysician: Yup.string().required('Attending physician is required')
});

const PETCTForm = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [showPreview, setShowPreview] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const patientSignRef = useRef(null);
  const doctorSignRef = useRef(null);

  const steps = [
    'Patient Information',
    'Medical History', 
    'Study Details',
    'Treatment History',
    'Review & Submit'
  ];

  const formik = useFormik({
    initialValues: {
      // Patient Info
      patientName: '',
      medicalId: '',
      age: '',
      gender: '',
      birthDate: '',
      weight: '',
      height: '',
      phone: '',
      attendingPhysician: '',
      
      // Medical Details
      fastingHours: '',
      isDiabetic: false,
      bloodSugar: '',
      
      // Injection Details
      dose: '',
      injectionSite: '',
      injectionTime: '',
      preparationTime: '',
      
      // Technical Parameters
      ctd1vol: '',
      dlp: '',
      withContrast: false,
      kidneyFunction: '',
      
      // Study Info
      isFirstExam: true,
      comparisonStudyCode: '',
      reportDisc: '',
      diagnosis: '',
      studyReason: '',
      
      // Treatment History
      chemotherapy: false,
      chemotherapyType: '',
      chemotherapyDetails: '',
      chemotherapySessions: '',
      
      radiotherapy: false,
      radiotherapySite: '',
      radiotherapySessions: '',
      radiotherapyLastDate: '',
      
      hormonalTreatment: false,
      hormonalLastDose: '',
      
      // Previous Studies
      previousStudies: [],
      
      // Additional Notes
      additionalNotes: '',
      
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
        const result = await petCtService.submitForm(values);
        
        console.log('Form submitted successfully:', result);
        setSaveStatus('success');
        
        // Reset form after successful submission
        setTimeout(() => {
          formik.resetForm();
          setActiveStep(0);
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

  const handleNext = () => {
    // Validate current step before proceeding
    const stepValidation = {
      0: ['patientName', 'age', 'weight', 'height', 'attendingPhysician'],
      1: ['fastingHours'],
      2: ['diagnosis', 'studyReason'],
      3: [],
      4: []
    };
    
    const fieldsToValidate = stepValidation[activeStep] || [];
    const hasErrors = fieldsToValidate.some(field => 
      formik.errors[field] && formik.touched[field]
    );
    
    if (!hasErrors) {
      setActiveStep((prevStep) => prevStep + 1);
    } else {
      // Touch all fields in current step to show validation errors
      fieldsToValidate.forEach(field => formik.setFieldTouched(field, true));
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

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
      
      // Save draft to API
      const result = await petCtService.saveDraft(draftData);
      
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

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom color="primary" sx={{ display: 'flex', alignItems: 'center' }}>
                <PersonIcon sx={{ mr: 1 }} />
                Patient Information (معلومات المريض)
              </Typography>
            </Grid>
            
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
                label="Medical ID (الرقم الطبي)"
                value={formik.values.medicalId}
                onChange={formik.handleChange}
                placeholder="MED-2024-001"
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
                inputProps={{ min: 0, max: 150 }}
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
                name="weight"
                label="Weight (kg) (الوزن) *"
                type="number"
                value={formik.values.weight}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.weight && Boolean(formik.errors.weight)}
                helperText={formik.touched.weight && formik.errors.weight}
                inputProps={{ min: 0, max: 500, step: 0.1 }}
              />
            </Grid>

            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                name="height"
                label="Height (cm) (الطول) *"
                type="number"
                value={formik.values.height}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.height && Boolean(formik.errors.height)}
                helperText={formik.touched.height && formik.errors.height}
                inputProps={{ min: 0, max: 300 }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="phone"
                label="Phone Number (رقم التليفون)"
                value={formik.values.phone}
                onChange={formik.handleChange}
                placeholder="+20 123 456 7890"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="attendingPhysician"
                label="Attending Physician (الطبيب المعالج) *"
                value={formik.values.attendingPhysician}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.attendingPhysician && Boolean(formik.errors.attendingPhysician)}
                helperText={formik.touched.attendingPhysician && formik.errors.attendingPhysician}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom color="primary" sx={{ display: 'flex', alignItems: 'center' }}>
                <HospitalIcon sx={{ mr: 1 }} />
                Medical History & Preparation (التاريخ الطبي والتحضير)
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="fastingHours"
                label="Fasting Hours (عدد ساعات الصيام) *"
                type="number"
                value={formik.values.fastingHours}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.fastingHours && Boolean(formik.errors.fastingHours)}
                helperText={formik.touched.fastingHours && formik.errors.fastingHours}
                inputProps={{ min: 0, max: 24 }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl component="fieldset">
                <FormLabel component="legend">Diabetic Patient (مريض سكر)</FormLabel>
                <RadioGroup
                  name="isDiabetic"
                  value={formik.values.isDiabetic}
                  onChange={(e) => formik.setFieldValue('isDiabetic', e.target.value === 'true')}
                  row
                >
                  <FormControlLabel value={true} control={<Radio />} label="Yes (نعم)" />
                  <FormControlLabel value={false} control={<Radio />} label="No (لا)" />
                </RadioGroup>
              </FormControl>
            </Grid>

            {formik.values.isDiabetic && (
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  name="bloodSugar"
                  label="Blood Sugar Level (mg/dl) (نسبة السكر بالدم)"
                  type="number"
                  value={formik.values.bloodSugar}
                  onChange={formik.handleChange}
                  inputProps={{ min: 0 }}
                />
              </Grid>
            )}

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" gutterBottom>
                Injection Details (تفاصيل الحقن)
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="dose"
                label="Dose (الجرعة)"
                value={formik.values.dose}
                onChange={formik.handleChange}
                placeholder="e.g., 10 mCi"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="injectionSite"
                label="Injection Site (مكان الحقن)"
                value={formik.values.injectionSite}
                onChange={formik.handleChange}
                placeholder="e.g., Right arm"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="injectionTime"
                label="Injection Time (وقت الحقن)"
                type="time"
                value={formik.values.injectionTime}
                onChange={formik.handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="preparationTime"
                label="Preparation Time (وقت التحضير)"
                type="time"
                value={formik.values.preparationTime}
                onChange={formik.handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" gutterBottom>
                Technical Parameters (المعايير التقنية)
              </Typography>
            </Grid>

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
              <FormControlLabel
                control={
                  <Checkbox
                    name="withContrast"
                    checked={formik.values.withContrast}
                    onChange={formik.handleChange}
                  />
                }
                label="With Contrast (بالصبغة)"
              />
            </Grid>

            {formik.values.withContrast && (
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="kidneyFunction"
                  label="Kidney Function (وظائف الكلى)"
                  value={formik.values.kidneyFunction}
                  onChange={formik.handleChange}
                />
              </Grid>
            )}
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom color="primary" sx={{ display: 'flex', alignItems: 'center' }}>
                <AssignmentIcon sx={{ mr: 1 }} />
                Study Details (تفاصيل الفحص)
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl component="fieldset">
                <FormLabel component="legend">First Examination (فحص أول مرة)</FormLabel>
                <RadioGroup
                  name="isFirstExam"
                  value={formik.values.isFirstExam}
                  onChange={(e) => formik.setFieldValue('isFirstExam', e.target.value === 'true')}
                  row
                >
                  <FormControlLabel value={true} control={<Radio />} label="Yes (نعم)" />
                  <FormControlLabel value={false} control={<Radio />} label="No (لا)" />
                </RadioGroup>
              </FormControl>
            </Grid>

            {!formik.values.isFirstExam && (
              <>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    name="comparisonStudyCode"
                    label="Previous Study Code (كود الفحص السابق)"
                    value={formik.values.comparisonStudyCode}
                    onChange={formik.handleChange}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    name="reportDisc"
                    label="Report Disc (اسطوانة التقرير)"
                    value={formik.values.reportDisc}
                    onChange={formik.handleChange}
                  />
                </Grid>
              </>
            )}

            <Grid item xs={12}>
              <Autocomplete
                options={[]} // Will be populated from API in future
                freeSolo
                value={formik.values.diagnosis}
                onChange={(event, newValue) => {
                  formik.setFieldValue('diagnosis', newValue || '');
                }}
                onInputChange={(event, newInputValue) => {
                  formik.setFieldValue('diagnosis', newInputValue);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    name="diagnosis"
                    label="Diagnosis (التشخيص) *"
                    error={formik.touched.diagnosis && Boolean(formik.errors.diagnosis)}
                    helperText={formik.touched.diagnosis && formik.errors.diagnosis}
                    onBlur={formik.handleBlur}
                    multiline
                    rows={2}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Autocomplete
                options={[]} // Will be populated from API in future
                freeSolo
                value={formik.values.studyReason}
                onChange={(event, newValue) => {
                  formik.setFieldValue('studyReason', newValue || '');
                }}
                onInputChange={(event, newInputValue) => {
                  formik.setFieldValue('studyReason', newInputValue);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    name="studyReason"
                    label="Reason of Study (سبب الفحص) *"
                    error={formik.touched.studyReason && Boolean(formik.errors.studyReason)}
                    helperText={formik.touched.studyReason && formik.errors.studyReason}
                    onBlur={formik.handleBlur}
                    multiline
                    rows={2}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Previous Studies (الفحوصات السابقة)
              </Typography>
              <Autocomplete
                multiple
                options={[]} // Will be populated from API in future
                value={formik.values.previousStudies}
                onChange={(event, newValue) => {
                  formik.setFieldValue('previousStudies', newValue);
                }}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip variant="outlined" label={option} {...getTagProps({ index })} />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    placeholder="Select previous studies"
                    helperText="Select all applicable previous studies"
                  />
                )}
              />
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom color="primary">
                Treatment History (تاريخ العلاج)
              </Typography>
            </Grid>

            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Chemotherapy (العلاج الكيميائي)
                  </Typography>
                  
                  <FormControl component="fieldset" sx={{ mb: 2 }}>
                    <RadioGroup
                      name="chemotherapy"
                      value={formik.values.chemotherapy}
                      onChange={(e) => formik.setFieldValue('chemotherapy', e.target.value === 'true')}
                      row
                    >
                      <FormControlLabel value={true} control={<Radio />} label="Yes (نعم)" />
                      <FormControlLabel value={false} control={<Radio />} label="No (لا)" />
                    </RadioGroup>
                  </FormControl>

                  {formik.values.chemotherapy && (
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth>
                          <InputLabel>Type</InputLabel>
                          <Select
                            name="chemotherapyType"
                            value={formik.values.chemotherapyType}
                            onChange={formik.handleChange}
                            label="Type"
                          >
                            <MenuItem value="tablets">Tablets (أقراص)</MenuItem>
                            <MenuItem value="infusion">Infusion (حقن وريدي)</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          name="chemotherapySessions"
                          label="Number of Sessions"
                          type="number"
                          value={formik.values.chemotherapySessions}
                          onChange={formik.handleChange}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          name="chemotherapyDetails"
                          label="Details"
                          multiline
                          rows={2}
                          value={formik.values.chemotherapyDetails}
                          onChange={formik.handleChange}
                        />
                      </Grid>
                    </Grid>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Radiotherapy (العلاج الإشعاعي)
                  </Typography>
                  
                  <FormControl component="fieldset" sx={{ mb: 2 }}>
                    <RadioGroup
                      name="radiotherapy"
                      value={formik.values.radiotherapy}
                      onChange={(e) => formik.setFieldValue('radiotherapy', e.target.value === 'true')}
                      row
                    >
                      <FormControlLabel value={true} control={<Radio />} label="Yes (نعم)" />
                      <FormControlLabel value={false} control={<Radio />} label="No (لا)" />
                    </RadioGroup>
                  </FormControl>

                  {formik.values.radiotherapy && (
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          name="radiotherapySite"
                          label="Anatomical Site"
                          value={formik.values.radiotherapySite}
                          onChange={formik.handleChange}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          name="radiotherapySessions"
                          label="Number of Sessions"
                          type="number"
                          value={formik.values.radiotherapySessions}
                          onChange={formik.handleChange}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          name="radiotherapyLastDate"
                          label="Date of Last Session"
                          type="date"
                          value={formik.values.radiotherapyLastDate}
                          onChange={formik.handleChange}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                    </Grid>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Hormonal Treatment (العلاج الهرموني)
                  </Typography>
                  
                  <FormControl component="fieldset" sx={{ mb: 2 }}>
                    <RadioGroup
                      name="hormonalTreatment"
                      value={formik.values.hormonalTreatment}
                      onChange={(e) => formik.setFieldValue('hormonalTreatment', e.target.value === 'true')}
                      row
                    >
                      <FormControlLabel value={true} control={<Radio />} label="Yes (نعم)" />
                      <FormControlLabel value={false} control={<Radio />} label="No (لا)" />
                    </RadioGroup>
                  </FormControl>

                  {formik.values.hormonalTreatment && (
                    <TextField
                      fullWidth
                      name="hormonalLastDose"
                      label="Date of Last Dose"
                      type="date"
                      value={formik.values.hormonalLastDose}
                      onChange={formik.handleChange}
                      InputLabelProps={{ shrink: true }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                name="additionalNotes"
                label="Additional Notes (ملاحظات إضافية)"
                multiline
                rows={3}
                value={formik.values.additionalNotes}
                onChange={formik.handleChange}
              />
            </Grid>
          </Grid>
        );

      case 4:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom color="primary" sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckIcon sx={{ mr: 1 }} />
                Review & Submit (مراجعة وإرسال)
              </Typography>
            </Grid>

            {/* Patient Summary Card */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    Patient Information
                  </Typography>
                  <Typography><strong>Name:</strong> {formik.values.patientName}</Typography>
                  <Typography><strong>Medical ID:</strong> {formik.values.medicalId}</Typography>
                  <Typography><strong>Age:</strong> {formik.values.age} years</Typography>
                  <Typography><strong>Gender:</strong> {formik.values.gender}</Typography>
                  <Typography><strong>Weight:</strong> {formik.values.weight} kg</Typography>
                  <Typography><strong>Height:</strong> {formik.values.height} cm</Typography>
                  <Typography><strong>Physician:</strong> {formik.values.attendingPhysician}</Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Study Summary Card */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    Study Information
                  </Typography>
                  <Typography><strong>Diagnosis:</strong> {formik.values.diagnosis}</Typography>
                  <Typography><strong>Study Reason:</strong> {formik.values.studyReason}</Typography>
                  <Typography><strong>First Exam:</strong> {formik.values.isFirstExam ? 'Yes' : 'No'}</Typography>
                  <Typography><strong>Fasting Hours:</strong> {formik.values.fastingHours}</Typography>
                  <Typography><strong>Diabetic:</strong> {formik.values.isDiabetic ? 'Yes' : 'No'}</Typography>
                  {formik.values.isDiabetic && (
                    <Typography><strong>Blood Sugar:</strong> {formik.values.bloodSugar} mg/dl</Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Treatment History Summary */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    Treatment History
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Typography><strong>Chemotherapy:</strong> {formik.values.chemotherapy ? 'Yes' : 'No'}</Typography>
                      {formik.values.chemotherapy && (
                        <>
                          <Typography variant="body2">Type: {formik.values.chemotherapyType}</Typography>
                          <Typography variant="body2">Sessions: {formik.values.chemotherapySessions}</Typography>
                        </>
                      )}
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography><strong>Radiotherapy:</strong> {formik.values.radiotherapy ? 'Yes' : 'No'}</Typography>
                      {formik.values.radiotherapy && (
                        <>
                          <Typography variant="body2">Site: {formik.values.radiotherapySite}</Typography>
                          <Typography variant="body2">Sessions: {formik.values.radiotherapySessions}</Typography>
                        </>
                      )}
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography><strong>Hormonal Treatment:</strong> {formik.values.hormonalTreatment ? 'Yes' : 'No'}</Typography>
                      {formik.values.hormonalTreatment && (
                        <Typography variant="body2">Last Dose: {formik.values.hormonalLastDose}</Typography>
                      )}
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Previous Studies */}
            {formik.values.previousStudies.length > 0 && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Previous Studies
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {formik.values.previousStudies.map((study, index) => (
                        <Chip key={index} label={study} variant="outlined" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Digital Signatures */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Digital Signatures (التوقيعات الرقمية)
              </Typography>
            </Grid>

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

            {/* Additional Notes */}
            {formik.values.additionalNotes && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Additional Notes
                    </Typography>
                    <Typography>{formik.values.additionalNotes}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        );

      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 1200, margin: '0 auto', p: 3 }}>
      {/* Header */}
  <Paper sx={{ p: 3, mb: 3, background: '#183153', color: '#fff', border: '1px solid #e0e4ea', boxShadow: 'none' }}>
        <Typography variant="h4" gutterBottom align="center">
          PET CT Form
        </Typography>
        <Typography variant="h6" align="center" sx={{ direction: 'rtl' }}>
          استمارة فحص البوزيترون المقطعي
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
          Form submitted successfully! Redirecting...
        </Alert>
      )}
      {saveStatus === 'error' && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error saving form. Please try again.
        </Alert>
      )}

      {/* Stepper */}
      <Stepper activeStep={activeStep} sx={{ mb: 4 }} alternativeLabel>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Form Content */}
  <Paper sx={{ p: 3, mb: 3, background: '#fff', border: '1px solid #e0e4ea', boxShadow: 'none' }}>
        <form onSubmit={formik.handleSubmit}>
          {renderStepContent(activeStep)}
        </form>
      </Paper>

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button
          disabled={activeStep === 0}
          onClick={handleBack}
          variant="outlined"
          size="large"
        >
          Back
        </Button>

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

        {activeStep === steps.length - 1 ? (
          <Button
            type="submit"
            onClick={formik.handleSubmit}
            variant="contained"
            color="primary"
            size="large"
            startIcon={<SendIcon />}
            disabled={saveStatus === 'saving' || !formik.isValid}
          >
            Submit Form
          </Button>
        ) : (
          <Button
            onClick={handleNext}
            variant="contained"
            color="primary"
            size="large"
          >
            Next
          </Button>
        )}
      </Box>

      {/* Preview Dialog */}
      <Dialog
        open={showPreview}
        onClose={() => setShowPreview(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Form Preview
        </DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>
            PET CT Examination Form
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
              <Typography><strong>Diagnosis:</strong> {formik.values.diagnosis}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography><strong>Study Reason:</strong> {formik.values.studyReason}</Typography>
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

export default PETCTForm;