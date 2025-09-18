import React, { useState, useEffect, createContext, useContext } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CssBaseline,
  ThemeProvider,
  createTheme,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Card,
  CardContent,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  Assignment as AssignmentIcon,
  LocalHospital as HospitalIcon,
  AssignmentTurnedIn as NursingIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  Menu as MenuIcon,
  Language as LanguageIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';

// Import form components
import PETCTForm from './components/PETCTForm';
import NursingForm from './components/NursingForm';
import GeneralForm from './components/GeneralForm';

// Import API services
import {
  patientService,
  petCtService,
  generalFormService,
  nursingService
} from './services/api';

// Monochrome blue/white professional theme
const theme = createTheme({
  direction: 'rtl',
  palette: {
    primary: {
      main: '#183153', // professional blue
      light: '#35507b',
      dark: '#0d1a2b',
      contrastText: '#fff',
    },
    secondary: {
      main: '#35507b', // lighter blue for accents
      contrastText: '#fff',
    },
    background: {
      default: '#f7f9fc', // very light blue/white
      paper: '#fff',
    },
    text: {
      primary: '#183153',
      secondary: '#35507b',
    },
    divider: '#e0e4ea',
  },
  typography: {
    fontFamily: 'Cairo, Tahoma, Arial, sans-serif',
    h4: {
      fontWeight: 700,
      fontSize: '2.2rem',
      lineHeight: 1.2,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.3,
    },
    body1: {
      fontSize: '1.05rem',
      lineHeight: 1.7,
    },
    body2: {
      fontSize: '0.95rem',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 700,
      fontSize: '1rem',
    },
  },
  shape: {
    borderRadius: 4,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          boxShadow: 'none',
          border: '1px solid #e0e4ea',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          textTransform: 'none',
          fontWeight: 700,
          padding: '10px 28px',
          boxShadow: 'none',
          backgroundImage: 'none',
        },
        contained: {
          boxShadow: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          boxShadow: 'none',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 4,
            background: '#f7f9fc',
            border: '1px solid #e0e4ea',
            transition: 'border-color 0.2s',
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#183153',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderWidth: 2,
              borderColor: '#183153',
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          fontWeight: 600,
          background: '#f7f9fc',
          color: '#183153',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          boxShadow: 'none',
          background: '#183153',
          color: '#fff',
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          minHeight: 48,
        },
        indicator: {
          backgroundColor: '#35507b',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          minHeight: 48,
          fontWeight: 700,
        },
      },
    },
  },
});

// Context for app state
const AppContext = createContext();

const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

// Dashboard Component
const Dashboard = () => {
  const { patients, forms, loading, error } = useAppContext();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
        <CircularProgress size={32} thickness={4} />
        <Typography sx={{ ml: 2, color: 'text.secondary' }}>Loading dashboard data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2, borderRadius: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          Unable to Load Dashboard
        </Typography>
        {error}
      </Alert>
    );
  }

  const stats = {
    totalPatients: patients.length,
    totalForms: forms.length,
    completedForms: forms.filter(f => f.status === 'completed').length,
    draftForms: forms.filter(f => f.status === 'draft').length
  };

  // Flat, clean stat card
  const StatCard = ({ title, value, subtitle, icon }) => (
    <Card sx={{
      height: '100%',
      background: '#183153',
      color: '#fff',
      border: '1.5px solid #e0e4ea',
      boxShadow: 'none',
      p: 0,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
    }}>
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box>
            <Typography variant="h3" sx={{ fontWeight: 700, mb: 0.5 }}>
              {value}
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" sx={{ mt: 0.5, color: '#fff' }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{
            backgroundColor: '#fff',
            borderRadius: '50%',
            p: 1.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#183153',
            border: '1.5px solid #e0e4ea',
          }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: 'text.primary' }}>
          🏥 Medical Forms Dashboard
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary', mb: 3 }}>
          Welcome to your medical forms management system. Here's an overview of your current data.
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Patients"
            value={stats.totalPatients}
            subtitle="Active patients in system"
            icon={<PersonIcon sx={{ fontSize: 32 }} />}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Forms"
            value={stats.totalForms}
            subtitle="All medical forms created"
            icon={<AssignmentIcon sx={{ fontSize: 32 }} />}
            color="secondary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed Forms"
            value={stats.completedForms}
            subtitle="Successfully submitted forms"
            icon={<CheckIcon sx={{ fontSize: 32 }} />}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Draft Forms"
            value={stats.draftForms}
            subtitle="Forms in progress"
            icon={<AssignmentIcon sx={{ fontSize: 32 }} />}
            color="warning"
          />
        </Grid>
      </Grid>

      <Card sx={{ p: 2, background: '#fff', border: '1.5px solid #e0e0e0', boxShadow: 'none' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#1a237e' }}>
            📋 أحدث الأنشطة
          </Typography>
          <Typography variant="body2" sx={{ color: '#888', ml: 2 }}>
            آخر نماذج وبيانات المرضى
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {forms.slice(0, 5).map((form) => {
            if (!form || typeof form !== 'object') return null;
            const patient = patients.find(p => p.id === form.patientId);
            return (
              <Box key={form.id || Math.random()} sx={{
                p: 2,
                bgcolor: '#f5f6fa',
                borderRadius: 2,
                border: '1px solid #e0e0e0',
                transition: 'background 0.2s',
                '&:hover': {
                  bgcolor: '#e8eaf6',
                  borderColor: '#fbc02d',
                }
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1a237e' }}>
                    {typeof form.type === 'string' ? form.type.toUpperCase() : 'UNKNOWN'}
                  </Typography>
                  <Chip
                    label={typeof form.status === 'string' ? form.status : 'Unknown'}
                    color={form.status === 'completed' ? 'success' : 'warning'}
                    size="small"
                    sx={{ borderRadius: 2, fontWeight: 700 }}
                  />
                </Box>
                <Typography variant="body2" sx={{ mb: 0.5, color: '#1a237e' }}>
                  👤 {patient?.nameEnglish && typeof patient.nameEnglish === 'string' ? patient.nameEnglish : 'Unknown Patient'}
                </Typography>
                <Typography variant="body2" sx={{ color: '#888', direction: 'rtl', mb: 0.5 }}>
                  {patient?.nameArabic && typeof patient.nameArabic === 'string' ? patient.nameArabic : ''}
                </Typography>
                <Typography variant="body2" sx={{ color: '#888' }}>
                  📅 {form.createdAt ? new Date(form.createdAt).toLocaleDateString() : 'Unknown'}
                  {form.createdBy && ` • 👨‍⚕️ ${form.createdBy}`}
                </Typography>
              </Box>
            );
          })}
          {forms.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1" sx={{ color: '#888' }}>
                لا يوجد نماذج بعد.
              </Typography>
              <Typography variant="body2" sx={{ color: '#888', mt: 1 }}>
                أضف مريضًا وابدأ بإنشاء أول نموذج طبي.
              </Typography>
            </Box>
          )}
        </Box>
      </Card>
    </Box>
  );
};

// Patients Management Component
const PatientsManagement = () => {
  const { patients, setPatients, loading, error } = useAppContext();
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
        <CircularProgress size={32} thickness={4} />
        <Typography sx={{ ml: 2, color: 'text.secondary' }}>Loading patients...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2, borderRadius: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          Unable to Load Patients
        </Typography>
        {error}
      </Alert>
    );
  }

  const filteredPatients = patients.filter(patient => {
    if (!patient || typeof patient !== 'object') return false;
    const nameEnglish = patient.nameEnglish?.toLowerCase() || '';
    const nameArabic = (typeof patient.nameArabic === 'string' ? patient.nameArabic : '').toLowerCase();
    const medicalId = (typeof patient.medicalId === 'string' ? patient.medicalId.toLowerCase() : '');
    const idNumber = (typeof patient.idNumber === 'string' ? patient.idNumber.toLowerCase() : '');
    const search = searchTerm.toLowerCase();
    return nameEnglish.includes(search) || nameArabic.includes(search) || medicalId.includes(search) || idNumber.includes(search);
  });

  const handleAddPatient = () => {
    setSelectedPatient(null);
    setOpenDialog(true);
  };

  const handleEditPatient = (patient) => {
    setSelectedPatient(patient);
    setOpenDialog(true);
  };

  const handleSavePatient = async () => {
    try {
      // Check for duplicate ID number (only for new patients or when ID number changed)
      if (selectedPatient?.idNumber) {
        const existingPatient = patients.find(p =>
          p.idNumber === selectedPatient.idNumber &&
          p.id !== selectedPatient.id // Exclude current patient when editing
        );

        if (existingPatient) {
          alert(`ID Number "${selectedPatient.idNumber}" already exists for patient: ${existingPatient.nameEnglish}`);
          return;
        }
      }

      if (selectedPatient.id) {
        // Update existing patient
        const updatedPatient = await patientService.updatePatient(selectedPatient.id, selectedPatient);
        setPatients(prev => prev.map(p => p.id === selectedPatient.id ? updatedPatient : p));
      } else {
        // Create new patient
        const newPatient = await patientService.createPatient(selectedPatient);
        // Add lastVisit field for display purposes
        const patientWithLastVisit = { ...newPatient, lastVisit: 'Never' };
        setPatients(prev => [...prev, patientWithLastVisit]);
      }
      setOpenDialog(false);
      setSelectedPatient(null);
    } catch (error) {
      console.error('Error saving patient:', error);
      alert('Error saving patient: ' + (error?.response?.data?.message || error.message));
    }
  };

  const PatientCard = ({ patient }) => (
    <Card sx={{
      height: '100%',
      cursor: 'pointer',
      transition: 'all 0.3s ease-in-out',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)'
      }
    }} onClick={() => handleEditPatient(patient)}>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{
            backgroundColor: 'primary.main',
            borderRadius: '50%',
            width: 48,
            height: 48,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mr: 2
          }}>
            <PersonIcon sx={{ color: 'white', fontSize: 24 }} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
              {typeof patient.nameEnglish === 'string' ? patient.nameEnglish : 'Unknown Patient'}
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', direction: 'rtl' }}>
              {typeof patient.nameArabic === 'string' ? patient.nameArabic : ''}
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 500, minWidth: 80 }}>
              🆔 Medical ID:
            </Typography>
            <Typography variant="body2" sx={{ ml: 1 }}>
              {typeof patient.medicalId === 'string' ? patient.medicalId : 'N/A'}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 500, minWidth: 80 }}>
              🆔 ID Number:
            </Typography>
            <Typography variant="body2" sx={{ ml: 1 }}>
              {typeof patient.idNumber === 'string' ? patient.idNumber : 'N/A'}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 500, minWidth: 80 }}>
              🎂 Age:
            </Typography>
            <Typography variant="body2" sx={{ ml: 1 }}>
              {typeof patient.age === 'number' || typeof patient.age === 'string' ? patient.age : 'N/A'} years
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 500, minWidth: 80 }}>
              ⚧ Gender:
            </Typography>
            <Typography variant="body2" sx={{ ml: 1 }}>
              {typeof patient.gender === 'string' ? patient.gender : 'N/A'}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 500, minWidth: 80 }}>
              📅 Last Visit:
            </Typography>
            <Typography variant="body2" sx={{ ml: 1 }}>
              {typeof patient.lastVisit === 'string' ? patient.lastVisit : 'Never'}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary', mb: 1 }}>
            👥 Patients Management
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>
            Manage patient records and information
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddPatient}
          sx={{
            px: 3,
            py: 1.5,
            fontSize: '1rem',
            fontWeight: 600
          }}
        >
          Add New Patient
        </Button>
      </Box>

      <Card sx={{ p: 2, background: '#fff', border: '1.5px solid #e0e0e0', boxShadow: 'none', mb: 3 }}>
        <TextField
          fullWidth
          placeholder="🔍 ابحث باسم المريض أو الرقم القومي..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: '#1a237e' }} />
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              backgroundColor: '#f5f6fa',
              border: '1px solid #e0e0e0',
            }
          }}
        />
        <Typography variant="body2" sx={{ color: '#888', mt: 1 }}>
          عرض {filteredPatients.length} من {patients.length} مريض
        </Typography>
      </Card>

      <Grid container spacing={3}>
        {filteredPatients.map((patient) => {
          if (!patient || typeof patient !== 'object') return null;
          return (
            <Grid item xs={12} md={6} lg={4} key={patient.id || Math.random()}>
              <PatientCard patient={patient} />
            </Grid>
          );
        })}
      </Grid>

      {filteredPatients.length === 0 && searchTerm && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 2 }}>
            No patients found
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>
            Try adjusting your search terms or add a new patient.
          </Typography>
        </Box>
      )}

      {patients.length === 0 && !searchTerm && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 2 }}>
            No patients yet
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', mb: 3 }}>
            Start by adding your first patient to the system.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddPatient}
            size="large"
          >
            Add First Patient
          </Button>
        </Box>
      )}

      {/* Patient Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}>
        <DialogTitle sx={{
          pb: 1,
          borderBottom: '1px solid',
          borderColor: 'grey.200'
        }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            {selectedPatient && selectedPatient.id ? '✏️ Edit Patient' : '➕ Add New Patient'}
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary', mt: 1 }}>
            {selectedPatient && selectedPatient.id ? 'Update patient information' : 'Enter patient details to create a new record'}
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="nameEnglish"
                label="👤 Patient Name (English)"
                value={selectedPatient?.nameEnglish || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, nameEnglish: e.target.value }))}
                required
                helperText="Enter the patient's full name in English"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="nameArabic"
                label="👤 Patient Name (Arabic)"
                value={selectedPatient?.nameArabic || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, nameArabic: e.target.value }))}
                required
                helperText="Enter the patient's full name in Arabic"
                sx={{ direction: 'rtl' }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="phone"
                label="📞 Phone Number"
                value={selectedPatient?.phone || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, phone: e.target.value }))}
                required
                helperText="Enter a valid phone number"
                placeholder="+20 123 456 7890"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="idNumber"
                label="🆔 National ID / Passport Number"
                value={selectedPatient?.idNumber || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, idNumber: e.target.value }))}
                required
                helperText="Must be unique across all patients"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="age"
                label="🎂 Age"
                type="number"
                value={selectedPatient?.age || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, age: parseInt(e.target.value) || '' }))}
                required
                helperText="Patient's current age in years"
                inputProps={{ min: 0, max: 150 }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth required>
                <InputLabel>⚧ Gender</InputLabel>
                <Select
                  name="gender"
                  value={selectedPatient?.gender || ''}
                  onChange={(e) => setSelectedPatient(prev => ({ ...prev, gender: e.target.value }))}
                  label="⚧ Gender"
                >
                  <MenuItem value="male">👨 Male</MenuItem>
                  <MenuItem value="female">👩 Female</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="birthDate"
                label="📅 Birth Date"
                type="date"
                value={selectedPatient?.birthDate || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, birthDate: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                helperText="Patient's date of birth"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="address"
                label="🏠 Address"
                multiline
                rows={2}
                value={selectedPatient?.address || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, address: e.target.value }))}
                helperText="Patient's residential address"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="emergencyContact"
                label="🚨 Emergency Contact"
                value={selectedPatient?.emergencyContact || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, emergencyContact: e.target.value }))}
                helperText="Name of emergency contact person"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="emergencyPhone"
                label="📞 Emergency Phone"
                value={selectedPatient?.emergencyPhone || ''}
                onChange={(e) => setSelectedPatient(prev => ({ ...prev, emergencyPhone: e.target.value }))}
                helperText="Emergency contact phone number"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{
          p: 3,
          borderTop: '1px solid',
          borderColor: 'grey.200'
        }}>
          <Button onClick={() => setOpenDialog(false)} sx={{ mr: 1 }}>
            Cancel
          </Button>
          <Button
            onClick={handleSavePatient}
            variant="contained"
            disabled={!selectedPatient?.nameEnglish || !selectedPatient?.nameArabic || !selectedPatient?.phone || !selectedPatient?.idNumber || !selectedPatient?.age || !selectedPatient?.gender}
            sx={{ px: 4 }}
          >
            {selectedPatient?.id ? '💾 Update Patient' : '➕ Save Patient'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Forms Management Component
const FormsManagement = () => {
  const { forms, patients, loading, error } = useAppContext();
  const [activeTab, setActiveTab] = useState(0);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
        <CircularProgress size={32} thickness={4} />
        <Typography sx={{ ml: 2, color: 'text.secondary' }}>Loading forms...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2, borderRadius: 3 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          Unable to Load Forms
        </Typography>
        {error}
      </Alert>
    );
  }

  const formTypes = ['All Forms', 'PET CT Forms', 'General Forms', 'Nursing Assessments'];

  const filteredForms = activeTab === 0 ? forms : 
    forms.filter(form => {
      if (!form || typeof form !== 'object') return false;
      const typeMap = { 1: 'pet_ct', 2: 'general', 3: 'nursing' };
      return form.type === typeMap[activeTab];
    });

  const FormCard = ({ form }) => {
    const patient = patients.find(p => p.id === form.patientId);
    const getFormIcon = (type) => {
      switch (type) {
        case 'pet_ct': return <HospitalIcon sx={{ fontSize: 24 }} />;
        case 'general': return <AssignmentIcon sx={{ fontSize: 24 }} />;
        case 'nursing': return <NursingIcon sx={{ fontSize: 24 }} />;
        default: return <AssignmentIcon sx={{ fontSize: 24 }} />;
      }
    };

    const getStatusColor = (status) => {
      switch (status) {
        case 'completed': return 'success';
        case 'draft': return 'warning';
        case 'submitted': return 'info';
        default: return 'default';
      }
    };

    return (
      <Card sx={{
        height: '100%',
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)'
        }
      }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{
              backgroundColor: 'primary.main',
              borderRadius: '50%',
              width: 48,
              height: 48,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mr: 2
            }}>
              {getFormIcon(form.type)}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                {typeof form.type === 'string' ? form.type.toUpperCase().replace('_', ' ') : 'UNKNOWN'} Form
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                📋 Form ID: {form.id || 'N/A'}
              </Typography>
            </Box>
            <Chip
              label={typeof form.status === 'string' ? form.status : 'Unknown'}
              color={getStatusColor(form.status)}
              size="small"
              sx={{ borderRadius: 2 }}
            />
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
              👤 Patient Information
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.primary', mb: 0.5 }}>
              {patient?.nameEnglish && typeof patient.nameEnglish === 'string' ? patient.nameEnglish : 'Unknown Patient'}
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', direction: 'rtl', mb: 1 }}>
              {patient?.nameArabic && typeof patient.nameArabic === 'string' ? patient.nameArabic : ''}
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              🆔 Medical ID: {patient?.medicalId || 'N/A'}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ fontWeight: 500, minWidth: 70 }}>
                📅 Created:
              </Typography>
              <Typography variant="body2" sx={{ ml: 1 }}>
                {form.createdAt ? new Date(form.createdAt).toLocaleDateString() : 'Unknown'}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ fontWeight: 500, minWidth: 70 }}>
                👨‍⚕️ By:
              </Typography>
              <Typography variant="body2" sx={{ ml: 1 }}>
                {typeof form.createdBy === 'string' ? form.createdBy : 'Unknown'}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
            <Button size="small" variant="outlined" sx={{ flex: 1, borderRadius: 2 }}>
              👁️ View
            </Button>
            <Button size="small" variant="contained" sx={{ flex: 1, borderRadius: 2 }}>
              ✏️ Edit
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary', mb: 1 }}>
          📋 Forms Management
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          View and manage all medical forms in the system
        </Typography>
      </Box>

      <Card sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{
            px: 3,
            pt: 2,
            '& .MuiTab-root': {
              borderRadius: 2,
              mr: 1,
              minHeight: 48,
              textTransform: 'none',
              fontWeight: 600
            }
          }}
        >
          {formTypes.map((type, index) => (
            <Tab
              key={index}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {index === 0 && '📋'}
                  {index === 1 && '🏥'}
                  {index === 2 && '📄'}
                  {index === 3 && '👩‍⚕️'}
                  <Typography sx={{ ml: 1 }}>{type}</Typography>
                </Box>
              }
            />
          ))}
        </Tabs>
      </Card>

      <Box sx={{ mb: 3 }}>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          Showing {filteredForms.length} of {forms.length} forms
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {filteredForms.map((form) => {
          if (!form || typeof form !== 'object') return null;
          return (
            <Grid item xs={12} md={6} lg={4} key={form.id || Math.random()}>
              <FormCard form={form} />
            </Grid>
          );
        })}
      </Grid>

      {filteredForms.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 6 }}>
          <Typography variant="h6" sx={{ color: 'text.secondary', mb: 2 }}>
            No forms found
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', mb: 3 }}>
            {activeTab === 0
              ? 'No forms have been created yet. Start by adding patients and creating medical forms.'
              : `No ${formTypes[activeTab].toLowerCase()} found. Try switching to a different category or create a new form.`
            }
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            size="large"
          >
            Create New Form
          </Button>
        </Box>
      )}
    </Box>
  );
};

// Main App Component
const MedicalFormsApp = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [patients, setPatients] = useState([]);
  const [forms, setForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const drawerWidth = 240;

  // Fetch data from API on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch patients
        const patientsResponse = await patientService.getAllPatients();
        const patientsData = (patientsResponse.patients || []).map(patient => ({
          ...patient,
          lastVisit: patient.lastVisit || 'Never'
        }));

        // Fetch forms from different services
        const [petCtResponse, generalResponse, nursingResponse] = await Promise.all([
          petCtService.getAllForms(),
          generalFormService.getAllForms(),
          nursingService.getAllAssessments()
        ]);

        // Extract arrays from response objects
        const petCtForms = petCtResponse.forms || [];
        const generalForms = generalResponse.forms || [];
        const nursingForms = nursingResponse.assessments || [];

        // Combine all forms with proper type mapping
        const allForms = [
          ...petCtForms.map(form => ({ ...form, type: 'pet_ct' })),
          ...generalForms.map(form => ({ ...form, type: 'general' })),
          ...nursingForms.map(form => ({ ...form, type: 'nursing' }))
        ];

        setPatients(patientsData);
        setForms(allForms);
      } catch (err) {
        console.error('Error fetching data:', err);
        const errorMessage = err?.message || err?.response?.data?.message || 'Failed to load data from server. Please try again.';
        setError(typeof errorMessage === 'string' ? errorMessage : 'An unexpected error occurred.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const menuItems = [
    { id: 'dashboard', text: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'patients', text: 'Patients', icon: <PersonIcon /> },
    { id: 'forms', text: 'Forms', icon: <AssignmentIcon /> },
    { id: 'pet-ct', text: 'PET CT Forms', icon: <HospitalIcon /> },
    { id: 'general', text: 'General Forms', icon: <AssignmentIcon /> },
    { id: 'nursing', text: 'Nursing Assessment', icon: <NursingIcon /> },
    { id: 'settings', text: 'Settings', icon: <SettingsIcon /> },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const renderCurrentView = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
          <CircularProgress />
          <Typography sx={{ ml: 2 }}>Loading data...</Typography>
        </Box>
      );
    }

    if (error) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      );
    }

    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'patients':
        return <PatientsManagement />;
      case 'forms':
        return <FormsManagement />;
      case 'pet-ct':
        return <PETCTForm />;
      case 'nursing':
        return <NursingForm />;
      case 'general':
        return <GeneralForm />;
      default:
        return <Dashboard />;
    }
  };

  const drawer = (
    <div>
      <Box sx={{
        p: 3,
        background: '#183153',
        color: 'white',
        borderRadius: 0,
        boxShadow: 'none',
        borderBottom: '1.5px solid #e0e4ea',
      }}>
        <Typography variant="h6" sx={{
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          mb: 1
        }}>
          🏥 Medical Forms
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          Digital Healthcare Management
        </Typography>
      </Box>
      <List sx={{ pt: 2 }}>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.id}
            onClick={() => setCurrentView(item.id)}
            selected={currentView === item.id}
            sx={{
              mx: 2,
              mb: 1,
              borderRadius: 2,
              transition: 'all 0.2s ease-in-out',
              '&.Mui-selected': {
                backgroundColor: '#35507b',
                color: '#fff',
                '&:hover': {
                  backgroundColor: '#183153',
                }
              },
              '&:hover': {
                backgroundColor: '#f7f9fc',
                color: '#183153',
                transform: 'none'
              }
            }}
          >
            <ListItemIcon sx={{
              color: currentView === item.id ? 'inherit' : '#35507b',
              minWidth: 40
            }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText
              primary={item.text}
              primaryTypographyProps={{
                fontWeight: currentView === item.id ? 600 : 500,
                fontSize: '0.95rem'
              }}
            />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <AppContext.Provider value={{ patients, setPatients, forms, setForms, loading, error }}>
      <ThemeProvider theme={theme}>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          
          <AppBar
            position="fixed"
            sx={{
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              ml: { sm: `${drawerWidth}px` },
              backgroundColor: 'white',
              color: 'text.primary',
              boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
              borderRadius: 0
            }}
          >
            <Toolbar sx={{ minHeight: 64 }}>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{
                  mr: 2,
                  display: { sm: 'none' },
                  '&:hover': {
                    backgroundColor: 'grey.100'
                  }
                }}
              >
                <MenuIcon />
              </IconButton>

              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h6" sx={{
                  fontWeight: 700,
                  color: 'text.primary',
                  display: 'flex',
                  alignItems: 'center'
                }}>
                  🏥 Digital Medical Forms System
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  Advanced Healthcare Management Platform
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <IconButton
                  sx={{
                    '&:hover': {
                      backgroundColor: 'grey.100'
                    }
                  }}
                >
                  <LanguageIcon />
                </IconButton>

                <IconButton
                  sx={{
                    '&:hover': {
                      backgroundColor: 'grey.100'
                    }
                  }}
                >
                  <Badge badgeContent={4} color="error">
                    <NotificationsIcon />
                  </Badge>
                </IconButton>

                <IconButton
                  size="large"
                  edge="end"
                  aria-label="account of current user"
                  aria-haspopup="true"
                  onClick={handleProfileMenuOpen}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'grey.100'
                    }
                  }}
                >
                  <AccountCircle />
                </IconButton>
              </Box>
            </Toolbar>
          </AppBar>

          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
            <MenuItem onClick={handleMenuClose}>My Account</MenuItem>
            <MenuItem onClick={handleMenuClose}>Logout</MenuItem>
          </Menu>

          <Box
            component="nav"
            sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
          >
            <Drawer
              variant="temporary"
              open={mobileOpen}
              onClose={handleDrawerToggle}
              ModalProps={{
                keepMounted: true,
              }}
              sx={{
                display: { xs: 'block', sm: 'none' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              {drawer}
            </Drawer>
            <Drawer
              variant="permanent"
              sx={{
                display: { xs: 'none', sm: 'block' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box>

          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 4,
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              mt: 10,
              backgroundColor: 'grey.50',
              minHeight: '100vh'
            }}
          >
            <Container maxWidth="xl" sx={{ py: 2 }}>
              {renderCurrentView()}
            </Container>
          </Box>
        </Box>
      </ThemeProvider>
    </AppContext.Provider>
  );
};

export default MedicalFormsApp;