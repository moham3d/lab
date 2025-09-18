import React, { useState, useRef, useEffect } from 'react';
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
  Alert,
  Card,
  CardContent,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormGroup,
  Switch,
  LinearProgress,
  Badge
} from '@mui/material';
import {
  Save as SaveIcon,
  Send as SendIcon,
  Print as PrintIcon,
  Person as PersonIcon,
  Favorite as HeartIcon,
  Psychology as PsychIcon,
  Restaurant as NutritionIcon,
  DirectionsWalk as MobilityIcon,
  School as EducationIcon,
  Healing as PainIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckIcon,
  LocalHospital as HospitalIcon,
  Assessment as AssessmentIcon,
  Security as SafetyIcon,
  Elderly as ElderlyIcon,
  Accessible as AccessibleIcon
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import SignatureCanvas from 'react-signature-canvas';

// Import API service
import { nursingService } from '../services/api';

// Validation Schema
const validationSchema = Yup.object({
  patientName: Yup.string().required('Patient name is required'),
  age: Yup.number().min(0).max(150).required('Age is required'),
  chiefComplaint: Yup.string().required('Chief complaint is required'),
  temperature: Yup.number().min(30).max(45),
  pulse: Yup.number().min(40).max(200),
  bloodPressureSystolic: Yup.number().min(60).max(250),
  bloodPressureDiastolic: Yup.number().min(40).max(150),
  respiratoryRate: Yup.number().min(8).max(60),
  oxygenSaturation: Yup.number().min(70).max(100),
  weight: Yup.number().min(0.5).max(500),
  height: Yup.number().min(30).max(250)
});

const NursingForm = () => {
  const [saveStatus, setSaveStatus] = useState(null);
  const [expandedSection, setExpandedSection] = useState('arrival');
  const [fallRiskScore, setFallRiskScore] = useState(0);
  const [fallRiskLevel, setFallRiskLevel] = useState('low');
  const [humptyDumptyScore, setHumptyDumptyScore] = useState(0);
  const [humptyDumptyRisk, setHumptyDumptyRisk] = useState('low');
  const nurseSignRef = useRef(null);

  const formik = useFormik({
    initialValues: {
      // Arrival Information
      arrivalMode: '',
      chiefComplaint: '',
      age: '',
      accompaniedBy: '',
      languageSpoken: 'arabic',
      
      // Vital Signs
      temperature: '',
      pulse: '',
      bloodPressureSystolic: '',
      bloodPressureDiastolic: '',
      respiratoryRate: '',
      oxygenSaturation: '',
      bloodSugar: '',
      weight: '',
      height: '',
      
      // Psychosocial History
      psychologicalProblems: [],
      smoking: false,
      
      // Allergies
      hasAllergies: false,
      medicationAllergies: '',
      foodAllergies: '',
      otherAllergies: '',
      
      // Nutritional Assessment
      dietType: 'regular',
      appetite: 'good',
      hasGitProblems: false,
      gitProblemsDetails: '',
      weightLoss: false,
      weightGain: false,
      referToNutritionist: false,
      
      // Functional Assessment
      selfCareFeeding: 'independent',
      selfCareHygiene: 'independent',
      selfCareToileting: 'independent',
      selfCareAmbulation: 'independent',
      
      // Musculoskeletal Status
      musculoskeletalProblems: [],
      assistingEquipment: [],
      
      // Educational Needs
      educationalNeeds: [],
      
      // Pain Assessment
      hasPain: false,
      painIntensity: 0,
      painLocation: '',
      painFrequency: '',
      painDuration: '',
      painCharacter: '',
      painActionTaken: '',
      
      // Fall Risk Assessment (Morse Scale)
      previousFall: false,
      secondaryDiagnosis: false,
      ambulatoryAid: 'none',
      ivTherapy: false,
      gaitStatus: 'normal',
      mentalStatus: 'oriented',
      
      // Pediatric Fall Assessment (Humpty Dumpty Scale)
      patientAge: '',
      gender: '',
      diagnosis: '',
      cognitiveImpairment: 'aware',
      environmentalFactors: 'outpatient',
      surgerySedation: 'more_than_48h',
      medicationUse: 'none',
      
      // Elderly Assessment
      elderlyDailyActivities: 'independent',
      cognitiveAssessment: 'normal',
      moodAssessment: 'not_depressed',
      speechDisorder: false,
      hearingDisorder: false,
      visionDisorder: false,
      sleepDisorder: false,
      
      // Disabled Patients Assessment
      disabilityType: '',
      hasAssistiveDevices: false,
      
      // Abuse/Neglect
      abuseNeglectConcern: '',
      
      // Nurse Signature
      nurseSignature: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setSaveStatus('saving');
        
        // Capture signature
        if (nurseSignRef.current) {
          values.nurseSignature = nurseSignRef.current.toDataURL();
        }
        
        // Calculate final scores
        values.fallRiskScore = fallRiskScore;
        values.fallRiskLevel = fallRiskLevel;
        values.humptyDumptyScore = humptyDumptyScore;
        values.humptyDumptyRisk = humptyDumptyRisk;
        
        // Submit to API
        const response = await nursingService.createAssessment(values);
        
        console.log('Nursing Assessment submitted:', response);
        setSaveStatus('success');
        
        // Reset form after successful submission
        setTimeout(() => {
          formik.resetForm();
          setExpandedSection('arrival');
          setSaveStatus(null);
          if (nurseSignRef.current) nurseSignRef.current.clear();
        }, 3000);
        
      } catch (error) {
        console.error('Submission error:', error);
        setSaveStatus('error');
      }
    }
  });

  // Handle save draft functionality
  const handleSaveDraft = async () => {
    try {
      setSaveStatus('saving');
      
      const values = formik.values;
      
      // Capture signature if available
      if (nurseSignRef.current) {
        values.nurseSignature = nurseSignRef.current.toDataURL();
      }
      
      // Calculate scores
      values.fallRiskScore = fallRiskScore;
      values.fallRiskLevel = fallRiskLevel;
      values.humptyDumptyScore = humptyDumptyScore;
      values.humptyDumptyRisk = humptyDumptyRisk;
      
      // Save draft to API
      const response = await nursingService.saveDraft(values);
      
      console.log('Nursing Assessment draft saved:', response);
      setSaveStatus('success');
      
      // Reset status after showing success
      setTimeout(() => {
        setSaveStatus(null);
      }, 3000);
      
    } catch (error) {
      console.error('Draft save error:', error);
      setSaveStatus('error');
    }
  };

  // Calculate Morse Fall Risk Score
  const calculateMorseFallRisk = () => {
    let score = 0;
    
    if (formik.values.previousFall) score += 25;
    if (formik.values.secondaryDiagnosis) score += 15;
    
    switch (formik.values.ambulatoryAid) {
      case 'furniture': score += 30; break;
      case 'crutches_walker': score += 15; break;
      default: score += 0;
    }
    
    if (formik.values.ivTherapy) score += 20;
    
    switch (formik.values.gaitStatus) {
      case 'impaired': score += 20; break;
      case 'weak': score += 10; break;
      default: score += 0;
    }
    
    if (formik.values.mentalStatus === 'forgets_limitations') score += 15;
    
    let riskLevel = 'low';
    if (score >= 25 && score <= 49) riskLevel = 'moderate';
    else if (score >= 50) riskLevel = 'high';
    
    setFallRiskScore(score);
    setFallRiskLevel(riskLevel);
  };

  // Calculate Humpty Dumpty Score
  const calculateHumptyDumptyScore = () => {
    let score = 0;
    const age = parseInt(formik.values.age) || 0;
    
    // Age scoring
    if (age >= 6 && age < 7) score += 3;
    else if (age >= 7 && age < 13) score += 2;
    else if (age >= 13) score += 1;
    
    // Gender scoring
    if (formik.values.gender === 'male') score += 2;
    else score += 1;
    
    // Diagnosis scoring
    switch (formik.values.diagnosis) {
      case 'neurological': score += 4; break;
      case 'oxygenation': score += 3; break;
      case 'behavioral': score += 2; break;
      default: score += 1;
    }
    
    // Cognitive impairment
    switch (formik.values.cognitiveImpairment) {
      case 'unaware': score += 3; break;
      case 'forgets': score += 2; break;
      default: score += 1;
    }
    
    // Environmental factors
    switch (formik.values.environmentalFactors) {
      case 'history_fall': score += 4; break;
      case 'assistive_devices': score += 3; break;
      case 'infant_bed': score += 2; break;
      default: score += 1;
    }
    
    // Surgery/sedation
    switch (formik.values.surgerySedation) {
      case 'within_24h': score += 3; break;
      case 'within_48h': score += 2; break;
      default: score += 1;
    }
    
    // Medication use
    switch (formik.values.medicationUse) {
      case 'multiple': score += 3; break;
      case 'one': score += 2; break;
      default: score += 1;
    }
    
    let riskLevel = 'low';
    if (score >= 7 && score <= 11) riskLevel = 'moderate';
    else if (score >= 12) riskLevel = 'high';
    
    setHumptyDumptyScore(score);
    setHumptyDumptyRisk(riskLevel);
  };

  // Recalculate scores when relevant values change
  useEffect(() => {
    calculateMorseFallRisk();
  }, [
    formik.values.previousFall,
    formik.values.secondaryDiagnosis,
    formik.values.ambulatoryAid,
    formik.values.ivTherapy,
    formik.values.gaitStatus,
    formik.values.mentalStatus
  ]);

  useEffect(() => {
    if (parseInt(formik.values.age) < 18) {
      calculateHumptyDumptyScore();
    }
  }, [
    formik.values.age,
    formik.values.gender,
    formik.values.diagnosis,
    formik.values.cognitiveImpairment,
    formik.values.environmentalFactors,
    formik.values.surgerySedation,
    formik.values.medicationUse
  ]);

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedSection(isExpanded ? panel : false);
  };

  const clearSignature = () => {
    if (nurseSignRef.current) {
      nurseSignRef.current.clear();
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'high': return 'error';
      case 'moderate': return 'warning';
      default: return 'success';
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 1400, margin: '0 auto', p: 3 }}>
      {/* Header */}
  <Paper sx={{ p: 3, mb: 3, background: '#35507b', color: '#fff', border: '1px solid #e0e4ea', boxShadow: 'none' }}>
        <Typography variant="h4" gutterBottom align="center">
          Nursing Assessment & Screening Form
        </Typography>
        <Typography variant="h6" align="center" sx={{ direction: 'rtl' }}>
          نموذج الفحص والتقييم التمريضي
        </Typography>
      </Paper>

      {/* Status Alerts */}
      {saveStatus === 'saving' && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Saving nursing assessment...
        </Alert>
      )}
      {saveStatus === 'success' && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Nursing assessment submitted successfully!
        </Alert>
      )}
      {saveStatus === 'error' && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error saving assessment. Please try again.
        </Alert>
      )}

      {/* Risk Score Display */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: getRiskColor(fallRiskLevel) + '.light' }}>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                <WarningIcon sx={{ mr: 1 }} />
                Morse Fall Risk Score
              </Typography>
              <Typography variant="h4">{fallRiskScore}</Typography>
              <Chip 
                label={`${fallRiskLevel.toUpperCase()} RISK`} 
                color={getRiskColor(fallRiskLevel)}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        
        {parseInt(formik.values.age) < 18 && (
          <Grid item xs={12} md={6}>
            <Card sx={{ bgcolor: getRiskColor(humptyDumptyRisk) + '.light' }}>
              <CardContent>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                  <WarningIcon sx={{ mr: 1 }} />
                  Humpty Dumpty Score (Pediatric)
                </Typography>
                <Typography variant="h4">{humptyDumptyScore}</Typography>
                <Chip 
                  label={`${humptyDumptyRisk.toUpperCase()} RISK`} 
                  color={getRiskColor(humptyDumptyRisk)}
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      <form onSubmit={formik.handleSubmit}>
        {/* Arrival Information */}
        <Accordion 
          expanded={expandedSection === 'arrival'} 
          onChange={handleAccordionChange('arrival')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Arrival Information (معلومات الوصول)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Mode of Arrival</InputLabel>
                  <Select
                    name="arrivalMode"
                    value={formik.values.arrivalMode}
                    onChange={formik.handleChange}
                    label="Mode of Arrival"
                  >
                    <MenuItem value="walk">Walking (يمشي على قدمه)</MenuItem>
                    <MenuItem value="wheelchair">Wheelchair (كرسي متحرك)</MenuItem>
                    <MenuItem value="stretcher">Stretcher (نقالة)</MenuItem>
                    <MenuItem value="ambulatory">Ambulatory (إسعاف)</MenuItem>
                    <MenuItem value="other">Other (أخرى)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  name="age"
                  label="Age (العمر) *"
                  type="number"
                  value={formik.values.age}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.age && Boolean(formik.errors.age)}
                  helperText={formik.touched.age && formik.errors.age}
                />
              </Grid>

              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Accompanied By</InputLabel>
                  <Select
                    name="accompaniedBy"
                    value={formik.values.accompaniedBy}
                    onChange={formik.handleChange}
                    label="Accompanied By"
                  >
                    <MenuItem value="spouse">Spouse (زوج)</MenuItem>
                    <MenuItem value="relative">Relative (قريب)</MenuItem>
                    <MenuItem value="other">Other (أخرى)</MenuItem>
                    <MenuItem value="alone">Alone</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  name="chiefComplaint"
                  label="Chief Complaints (الشكوى الحالية) *"
                  multiline
                  rows={3}
                  value={formik.values.chiefComplaint}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.chiefComplaint && Boolean(formik.errors.chiefComplaint)}
                  helperText={formik.touched.chiefComplaint && formik.errors.chiefComplaint}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Language Spoken</InputLabel>
                  <Select
                    name="languageSpoken"
                    value={formik.values.languageSpoken}
                    onChange={formik.handleChange}
                    label="Language Spoken"
                  >
                    <MenuItem value="arabic">Arabic (عربي)</MenuItem>
                    <MenuItem value="english">English (إنجليزي)</MenuItem>
                    <MenuItem value="other">Other (أخرى)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Vital Signs */}
        <Accordion 
          expanded={expandedSection === 'vitals'} 
          onChange={handleAccordionChange('vitals')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <HeartIcon sx={{ mr: 1, color: 'error.main' }} />
              <Typography variant="h6">Vital Signs & Measurements (العلامات الحيوية)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="temperature"
                  label="Temperature (°C) (درجة الحرارة)"
                  type="number"
                  value={formik.values.temperature}
                  onChange={formik.handleChange}
                  inputProps={{ step: 0.1, min: 30, max: 45 }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="pulse"
                  label="Pulse (b/min) (النبض)"
                  type="number"
                  value={formik.values.pulse}
                  onChange={formik.handleChange}
                  inputProps={{ min: 40, max: 200 }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="bloodPressureSystolic"
                  label="BP Systolic (mmHg)"
                  type="number"
                  value={formik.values.bloodPressureSystolic}
                  onChange={formik.handleChange}
                  inputProps={{ min: 60, max: 250 }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="bloodPressureDiastolic"
                  label="BP Diastolic (mmHg)"
                  type="number"
                  value={formik.values.bloodPressureDiastolic}
                  onChange={formik.handleChange}
                  inputProps={{ min: 40, max: 150 }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="respiratoryRate"
                  label="Respiratory Rate (/min) (التنفس)"
                  type="number"
                  value={formik.values.respiratoryRate}
                  onChange={formik.handleChange}
                  inputProps={{ min: 8, max: 60 }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="oxygenSaturation"
                  label="O₂ Saturation (%) (تشبع الأكسجين)"
                  type="number"
                  value={formik.values.oxygenSaturation}
                  onChange={formik.handleChange}
                  inputProps={{ min: 70, max: 100 }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="bloodSugar"
                  label="Blood Sugar (mg/dl) (سكر الدم)"
                  type="number"
                  value={formik.values.bloodSugar}
                  onChange={formik.handleChange}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="weight"
                  label="Weight (kg) (الوزن)"
                  type="number"
                  value={formik.values.weight}
                  onChange={formik.handleChange}
                  inputProps={{ step: 0.1, min: 0.5, max: 500 }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  name="height"
                  label="Height (cm) (الطول)"
                  type="number"
                  value={formik.values.height}
                  onChange={formik.handleChange}
                  inputProps={{ min: 30, max: 250 }}
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Psychosocial History */}
        <Accordion 
          expanded={expandedSection === 'psychosocial'} 
          onChange={handleAccordionChange('psychosocial')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PsychIcon sx={{ mr: 1, color: 'info.main' }} />
              <Typography variant="h6">Psychosocial History (التاريخ النفسي)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Psychological Problems (المشاكل النفسية)
                </Typography>
                <FormGroup row>
                  <FormControlLabel
                    control={<Checkbox />}
                    label="None identified (لا توجد مشكلة محددة)"
                  />
                  <FormControlLabel
                    control={<Checkbox />}
                    label="Anxious (قلق)"
                  />
                  <FormControlLabel
                    control={<Checkbox />}
                    label="Agitated (مضطرب)"
                  />
                  <FormControlLabel
                    control={<Checkbox />}
                    label="Depressed (مكتئب)"
                  />
                  <FormControlLabel
                    control={<Checkbox />}
                    label="Isolated (يميل إلى العزلة)"
                  />
                </FormGroup>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Special Habits
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.smoking}
                      onChange={formik.handleChange}
                      name="smoking"
                    />
                  }
                  label="Smoking (التدخين)"
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Allergies (الحساسية)
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.hasAllergies}
                      onChange={formik.handleChange}
                      name="hasAllergies"
                    />
                  }
                  label="Has Allergies"
                />
                
                {formik.values.hasAllergies && (
                  <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        name="medicationAllergies"
                        label="Medication Allergies"
                        value={formik.values.medicationAllergies}
                        onChange={formik.handleChange}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        name="foodAllergies"
                        label="Food Allergies"
                        value={formik.values.foodAllergies}
                        onChange={formik.handleChange}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        name="otherAllergies"
                        label="Other Allergies"
                        value={formik.values.otherAllergies}
                        onChange={formik.handleChange}
                      />
                    </Grid>
                  </Grid>
                )}
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Nutritional Assessment */}
        <Accordion 
          expanded={expandedSection === 'nutrition'} 
          onChange={handleAccordionChange('nutrition')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <NutritionIcon sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6">Nutritional Assessment (التقييم التغذوي)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Diet Type</InputLabel>
                  <Select
                    name="dietType"
                    value={formik.values.dietType}
                    onChange={formik.handleChange}
                    label="Diet Type"
                  >
                    <MenuItem value="regular">Regular (عادي)</MenuItem>
                    <MenuItem value="special">Special Diet (أطعمة خاصة)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl component="fieldset">
                  <FormLabel component="legend">Appetite (الشهية)</FormLabel>
                  <RadioGroup
                    name="appetite"
                    value={formik.values.appetite}
                    onChange={formik.handleChange}
                    row
                  >
                    <FormControlLabel value="good" control={<Radio />} label="Good" />
                    <FormControlLabel value="poor" control={<Radio />} label="Poor" />
                  </RadioGroup>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <FormGroup row>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.hasGitProblems}
                        onChange={formik.handleChange}
                        name="hasGitProblems"
                      />
                    }
                    label="GIT Problems"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.weightLoss}
                        onChange={formik.handleChange}
                        name="weightLoss"
                      />
                    }
                    label="Weight Loss"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.weightGain}
                        onChange={formik.handleChange}
                        name="weightGain"
                      />
                    }
                    label="Weight Gain"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.referToNutritionist}
                        onChange={formik.handleChange}
                        name="referToNutritionist"
                      />
                    }
                    label="Refer to Nutritionist"
                  />
                </FormGroup>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Pain Assessment */}
        <Accordion 
          expanded={expandedSection === 'pain'} 
          onChange={handleAccordionChange('pain')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PainIcon sx={{ mr: 1, color: 'error.main' }} />
              <Typography variant="h6">Pain Assessment (تقييم الألم)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.hasPain}
                      onChange={formik.handleChange}
                      name="hasPain"
                    />
                  }
                  label="Patient has pain"
                />
              </Grid>

              {formik.values.hasPain && (
                <>
                  <Grid item xs={12}>
                    <Typography gutterBottom>
                      Pain Intensity (0-10): {formik.values.painIntensity}
                    </Typography>
                    <Slider
                      name="painIntensity"
                      value={formik.values.painIntensity}
                      onChange={(e, value) => formik.setFieldValue('painIntensity', value)}
                      min={0}
                      max={10}
                      step={1}
                      marks
                      valueLabelDisplay="auto"
                      sx={{ width: '100%' }}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      name="painLocation"
                      label="Pain Location (المكان)"
                      value={formik.values.painLocation}
                      onChange={formik.handleChange}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      name="painFrequency"
                      label="Pain Frequency (التكرار)"
                      value={formik.values.painFrequency}
                      onChange={formik.handleChange}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      name="painDuration"
                      label="Pain Duration (المدة)"
                      value={formik.values.painDuration}
                      onChange={formik.handleChange}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      name="painCharacter"
                      label="Pain Character (طبيعة الألم)"
                      value={formik.values.painCharacter}
                      onChange={formik.handleChange}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      name="painActionTaken"
                      label="Action Taken (الإجراء المتبع)"
                      value={formik.values.painActionTaken}
                      onChange={formik.handleChange}
                      multiline
                      rows={2}
                    />
                  </Grid>
                </>
              )}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Fall Risk Assessment */}
        <Accordion 
          expanded={expandedSection === 'fallrisk'} 
          onChange={handleAccordionChange('fallrisk')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <SafetyIcon sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6">Fall Risk Assessment (تقييم خطر السقوط)</Typography>
              <Chip 
                label={`Score: ${fallRiskScore}`} 
                color={getRiskColor(fallRiskLevel)}
                sx={{ ml: 2 }}
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Alert severity="info" sx={{ mb: 3 }}>
              Modified Morse Fall Scale Assessment
            </Alert>
            
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Risk Factor</TableCell>
                    <TableCell>Assessment</TableCell>
                    <TableCell align="center">Points</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Previous fall in last 3 months</TableCell>
                    <TableCell>
                      <FormControl fullWidth>
                        <RadioGroup
                          name="previousFall"
                          value={formik.values.previousFall}
                          onChange={(e) => formik.setFieldValue('previousFall', e.target.value === 'true')}
                          row
                        >
                          <FormControlLabel value={false} control={<Radio />} label="No (0)" />
                          <FormControlLabel value={true} control={<Radio />} label="Yes (25)" />
                        </RadioGroup>
                      </FormControl>
                    </TableCell>
                    <TableCell align="center">
                      {formik.values.previousFall ? 25 : 0}
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell>Secondary diagnosis (2 or more)</TableCell>
                    <TableCell>
                      <FormControl fullWidth>
                        <RadioGroup
                          name="secondaryDiagnosis"
                          value={formik.values.secondaryDiagnosis}
                          onChange={(e) => formik.setFieldValue('secondaryDiagnosis', e.target.value === 'true')}
                          row
                        >
                          <FormControlLabel value={false} control={<Radio />} label="No (0)" />
                          <FormControlLabel value={true} control={<Radio />} label="Yes (15)" />
                        </RadioGroup>
                      </FormControl>
                    </TableCell>
                    <TableCell align="center">
                      {formik.values.secondaryDiagnosis ? 15 : 0}
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell>Ambulatory aid</TableCell>
                    <TableCell>
                      <FormControl fullWidth>
                        <RadioGroup
                          name="ambulatoryAid"
                          value={formik.values.ambulatoryAid}
                          onChange={formik.handleChange}
                        >
                          <FormControlLabel value="none" control={<Radio />} label="None/bedrest/nurse assist (0)" />
                          <FormControlLabel value="crutches_walker" control={<Radio />} label="Crutches/walker (15)" />
                          <FormControlLabel value="furniture" control={<Radio />} label="Furniture (30)" />
                        </RadioGroup>
                      </FormControl>
                    </TableCell>
                    <TableCell align="center">
                      {formik.values.ambulatoryAid === 'furniture' ? 30 : 
                       formik.values.ambulatoryAid === 'crutches_walker' ? 15 : 0}
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell>IV therapy</TableCell>
                    <TableCell>
                      <FormControl fullWidth>
                        <RadioGroup
                          name="ivTherapy"
                          value={formik.values.ivTherapy}
                          onChange={(e) => formik.setFieldValue('ivTherapy', e.target.value === 'true')}
                          row
                        >
                          <FormControlLabel value={false} control={<Radio />} label="No (0)" />
                          <FormControlLabel value={true} control={<Radio />} label="Yes (20)" />
                        </RadioGroup>
                      </FormControl>
                    </TableCell>
                    <TableCell align="center">
                      {formik.values.ivTherapy ? 20 : 0}
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell>Gait/transferring</TableCell>
                    <TableCell>
                      <FormControl fullWidth>
                        <RadioGroup
                          name="gaitStatus"
                          value={formik.values.gaitStatus}
                          onChange={formik.handleChange}
                        >
                          <FormControlLabel value="normal" control={<Radio />} label="Normal/bedfast (0)" />
                          <FormControlLabel value="weak" control={<Radio />} label="Weak (10)" />
                          <FormControlLabel value="impaired" control={<Radio />} label="Impaired (20)" />
                        </RadioGroup>
                      </FormControl>
                    </TableCell>
                    <TableCell align="center">
                      {formik.values.gaitStatus === 'impaired' ? 20 : 
                       formik.values.gaitStatus === 'weak' ? 10 : 0}
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell>Mental status</TableCell>
                    <TableCell>
                      <FormControl fullWidth>
                        <RadioGroup
                          name="mentalStatus"
                          value={formik.values.mentalStatus}
                          onChange={formik.handleChange}
                          row
                        >
                          <FormControlLabel value="oriented" control={<Radio />} label="Oriented (0)" />
                          <FormControlLabel value="forgets_limitations" control={<Radio />} label="Forgets limitations (15)" />
                        </RadioGroup>
                      </FormControl>
                    </TableCell>
                    <TableCell align="center">
                      {formik.values.mentalStatus === 'forgets_limitations' ? 15 : 0}
                    </TableCell>
                  </TableRow>

                  <TableRow sx={{ bgcolor: 'grey.100' }}>
                    <TableCell><strong>Total Score</strong></TableCell>
                    <TableCell><strong>Risk Level: {fallRiskLevel.toUpperCase()}</strong></TableCell>
                    <TableCell align="center"><strong>{fallRiskScore}</strong></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>

            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Risk Level Guidelines:</Typography>
              <Typography variant="body2">• Low Risk (0-24): Standard fall prevention</Typography>
              <Typography variant="body2">• Moderate Risk (25-49): Implement fall prevention measures</Typography>
              <Typography variant="body2">• High Risk (≥50): High-intensity fall prevention protocol</Typography>
            </Box>
          </AccordionDetails>
        </Accordion>

        {/* Pediatric Fall Assessment (Humpty Dumpty) */}
        {parseInt(formik.values.age) < 18 && (
          <Accordion 
            expanded={expandedSection === 'pediatric'} 
            onChange={handleAccordionChange('pediatric')}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SafetyIcon sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Pediatric Fall Assessment (Humpty Dumpty Scale)</Typography>
                <Chip 
                  label={`Score: ${humptyDumptyScore}`} 
                  color={getRiskColor(humptyDumptyRisk)}
                  sx={{ ml: 2 }}
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Alert severity="info" sx={{ mb: 3 }}>
                Humpty Dumpty Fall Assessment Scale (for patients under 18 years)
              </Alert>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Gender</InputLabel>
                    <Select
                      name="gender"
                      value={formik.values.gender}
                      onChange={formik.handleChange}
                      label="Gender"
                    >
                      <MenuItem value="female">Female (1 point)</MenuItem>
                      <MenuItem value="male">Male (2 points)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Diagnosis</InputLabel>
                    <Select
                      name="diagnosis"
                      value={formik.values.diagnosis}
                      onChange={formik.handleChange}
                      label="Diagnosis"
                    >
                      <MenuItem value="other">Other diagnoses (1 point)</MenuItem>
                      <MenuItem value="behavioral">Behavioral/Psychiatric (2 points)</MenuItem>
                      <MenuItem value="oxygenation">Changes in oxygenation (3 points)</MenuItem>
                      <MenuItem value="neurological">Neurological disorders (4 points)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Cognitive Impairment</InputLabel>
                    <Select
                      name="cognitiveImpairment"
                      value={formik.values.cognitiveImpairment}
                      onChange={formik.handleChange}
                      label="Cognitive Impairment"
                    >
                      <MenuItem value="aware">Aware of ability (1 point)</MenuItem>
                      <MenuItem value="forgets">Forgets limitations (2 points)</MenuItem>
                      <MenuItem value="unaware">Not aware of limitations (3 points)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Environmental Factors</InputLabel>
                    <Select
                      name="environmentalFactors"
                      value={formik.values.environmentalFactors}
                      onChange={formik.handleChange}
                      label="Environmental Factors"
                    >
                      <MenuItem value="outpatient">Outpatient area (1 point)</MenuItem>
                      <MenuItem value="infant_bed">Infant placed in bed (2 points)</MenuItem>
                      <MenuItem value="assistive_devices">Uses assistive devices (3 points)</MenuItem>
                      <MenuItem value="history_fall">History of falls/infant in bed/wheelchair (4 points)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Surgery/Sedation</InputLabel>
                    <Select
                      name="surgerySedation"
                      value={formik.values.surgerySedation}
                      onChange={formik.handleChange}
                      label="Surgery/Sedation"
                    >
                      <MenuItem value="more_than_48h">More than 48 hours (1 point)</MenuItem>
                      <MenuItem value="within_48h">Within 48 hours (2 points)</MenuItem>
                      <MenuItem value="within_24h">Within 24 hours (3 points)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Medication Use</InputLabel>
                    <Select
                      name="medicationUse"
                      value={formik.values.medicationUse}
                      onChange={formik.handleChange}
                      label="Medication Use"
                    >
                      <MenuItem value="none">None (1 point)</MenuItem>
                      <MenuItem value="one">One of the medications (2 points)</MenuItem>
                      <MenuItem value="multiple">Multiple medications (3 points)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <Card sx={{ bgcolor: getRiskColor(humptyDumptyRisk) + '.light', p: 2 }}>
                    <Typography variant="h6">
                      Total Score: {humptyDumptyScore} - Risk Level: {humptyDumptyRisk.toUpperCase()}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      • Low Risk (0-6): Standard fall prevention measures
                    </Typography>
                    <Typography variant="body2">
                      • Moderate Risk (7-11): Enhanced fall prevention protocol
                    </Typography>
                    <Typography variant="body2">
                      • High Risk (≥12): Intensive fall prevention measures
                    </Typography>
                  </Card>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {/* Elderly Assessment */}
        <Accordion 
          expanded={expandedSection === 'elderly'} 
          onChange={handleAccordionChange('elderly')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <ElderlyIcon sx={{ mr: 1, color: 'secondary.main' }} />
              <Typography variant="h6">Elderly Assessment (تقييم كبار السن)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Daily Activities</InputLabel>
                  <Select
                    name="elderlyDailyActivities"
                    value={formik.values.elderlyDailyActivities}
                    onChange={formik.handleChange}
                    label="Daily Activities"
                  >
                    <MenuItem value="independent">Independent (معتمد على نفسه)</MenuItem>
                    <MenuItem value="needs_help">Needs help (يحتاج إلى مساعدة)</MenuItem>
                    <MenuItem value="dependent">Dependent on others (يعتمد على الآخرين)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Cognitive Assessment</InputLabel>
                  <Select
                    name="cognitiveAssessment"
                    value={formik.values.cognitiveAssessment}
                    onChange={formik.handleChange}
                    label="Cognitive Assessment"
                  >
                    <MenuItem value="normal">Normal</MenuItem>
                    <MenuItem value="mild_impairment">Mild cognitive impairment</MenuItem>
                    <MenuItem value="moderate_delirium">Moderate delirium</MenuItem>
                    <MenuItem value="severe_delirium">Severe delirium</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Mood Assessment</InputLabel>
                  <Select
                    name="moodAssessment"
                    value={formik.values.moodAssessment}
                    onChange={formik.handleChange}
                    label="Mood Assessment"
                  >
                    <MenuItem value="not_depressed">Not depressed (غير مكتئب)</MenuItem>
                    <MenuItem value="depressed">Depressed (مكتئب)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Additional Assessments
                </Typography>
                <FormGroup row>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.speechDisorder}
                        onChange={formik.handleChange}
                        name="speechDisorder"
                      />
                    }
                    label="Speech Disorder (اضطراب النطق)"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.hearingDisorder}
                        onChange={formik.handleChange}
                        name="hearingDisorder"
                      />
                    }
                    label="Hearing Disorder (اضطراب السمع)"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.visionDisorder}
                        onChange={formik.handleChange}
                        name="visionDisorder"
                      />
                    }
                    label="Vision Disorder (اضطراب الرؤية)"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formik.values.sleepDisorder}
                        onChange={formik.handleChange}
                        name="sleepDisorder"
                      />
                    }
                    label="Sleep Disorder (اضطراب النوم)"
                  />
                </FormGroup>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Disabled Patients Assessment */}
        <Accordion 
          expanded={expandedSection === 'disabled'} 
          onChange={handleAccordionChange('disabled')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AccessibleIcon sx={{ mr: 1, color: 'info.main' }} />
              <Typography variant="h6">Special Needs Assessment (تقييم ذوي الاحتياجات الخاصة)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Disability Type</InputLabel>
                  <Select
                    name="disabilityType"
                    value={formik.values.disabilityType}
                    onChange={formik.handleChange}
                    label="Disability Type"
                  >
                    <MenuItem value="">None</MenuItem>
                    <MenuItem value="hearing">Hearing (سمعية)</MenuItem>
                    <MenuItem value="visual">Visual (بصرية)</MenuItem>
                    <MenuItem value="mobility">Mobility (حركية)</MenuItem>
                    <MenuItem value="other">Other (أخرى)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formik.values.hasAssistiveDevices}
                      onChange={formik.handleChange}
                      name="hasAssistiveDevices"
                    />
                  }
                  label="Has assistive devices available with patient"
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Abuse/Neglect Screening */}
        <Accordion 
          expanded={expandedSection === 'abuse'} 
          onChange={handleAccordionChange('abuse')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <WarningIcon sx={{ mr: 1, color: 'error.main' }} />
              <Typography variant="h6">Abuse & Neglect Screening</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Alert severity="warning" sx={{ mb: 2 }}>
                  This section is confidential. Report any concerns immediately to appropriate authorities.
                </Alert>
                <TextField
                  fullWidth
                  name="abuseNeglectConcern"
                  label="Abuse/Neglect Concerns (if any)"
                  multiline
                  rows={3}
                  value={formik.values.abuseNeglectConcern}
                  onChange={formik.handleChange}
                  placeholder="Document any signs, symptoms, or concerns regarding potential abuse or neglect..."
                />
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Digital Signature */}
        <Accordion 
          expanded={expandedSection === 'signature'} 
          onChange={handleAccordionChange('signature')}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CheckIcon sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="h6">Nurse Signature (توقيع الممرض)</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 2, background: '#fff', border: '1px solid #e0e4ea', boxShadow: 'none' }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Nurse Signature (توقيع الممرض القائم بالتقييم)
                  </Typography>
                  <Box sx={{ border: '1px solid #ccc', borderRadius: 1, mb: 2 }}>
                    <SignatureCanvas
                      ref={nurseSignRef}
                      penColor="black"
                      canvasProps={{
                        width: 500,
                        height: 200,
                        className: 'signature-canvas',
                        style: { border: 'none' }
                      }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={clearSignature}
                      size="small"
                    >
                      Clear Signature
                    </Button>
                    <Typography variant="body2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                      Date: {new Date().toLocaleDateString()} | Time: {new Date().toLocaleTimeString()}
                    </Typography>
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Form Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 4 }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={handleSaveDraft}
              disabled={saveStatus === 'saving'}
            >
              Save Draft
            </Button>

            <Button
              variant="outlined"
              startIcon={<PrintIcon />}
              onClick={() => window.print()}
            >
              Print Assessment
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
            Submit Assessment
          </Button>
        </Box>
      </form>
    </Box>
  );
};

export default NursingForm;