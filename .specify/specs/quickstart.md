# Healthcare Frontend Quick Start Guide

## Prerequisites

Before starting development, ensure you have:

- **Backend API**: FastAPI application running on `http://localhost:8000`
- **Node.js**: Version 16+ for build tools
- **Git**: For version control
- **Modern Browser**: Chrome, Firefox, or Safari
- **Code Editor**: VS Code recommended

## Project Setup

### 1. Clone and Initialize
```bash
git clone <repository-url>
cd healthcare-frontend
npm install
```

### 2. Environment Configuration
Create `.env` file:
```env
API_BASE_URL=http://localhost:8000/api/v1
NODE_ENV=development
```

### 3. Start Development Server
```bash
npm run dev
```
Access at `http://localhost:3000`

## Project Structure

```
healthcare-frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable HTMX components
│   │   ├── auth/          # Authentication components
│   │   ├── patients/      # Patient management
│   │   ├── forms/         # Medical forms
│   │   └── ui/            # Base UI components
│   ├── layouts/           # Page layouts
│   ├── pages/             # Main pages
│   ├── stores/            # Alpine.js stores
│   ├── utils/             # Helper functions
│   └── styles/            # Tailwind CSS
├── tests/                 # Test files
└── docs/                  # Documentation
```

## Core Concepts

### HTMX Integration
HTMX enables dynamic content loading without complex JavaScript:

```html
<!-- Load patient list -->
<div hx-get="/api/v1/patients" hx-trigger="load">
  Loading patients...
</div>

<!-- Auto-save form -->
<form hx-post="/api/v1/forms/check-eval" hx-trigger="input delay:2s">
  <input name="temperature" type="number">
</form>
```

### Alpine.js State Management
Use Alpine stores for reactive state:

```javascript
// stores/auth.js
export default () => ({
  user: null,
  token: localStorage.getItem('token'),

  async login(credentials) {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      localStorage.setItem('token', this.token);
      // Load user data...
    }
  }
});
```

### Authentication Flow
1. **Login**: POST credentials to `/api/v1/auth/login`
2. **Store Token**: Save JWT in localStorage
3. **Include Token**: Add to all API requests
4. **Handle Expiry**: Redirect to login on 401

```javascript
// utils/api.js
export function apiRequest(url, options = {}) {
  const token = localStorage.getItem('token');
  return fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
}
```

## Development Workflow

### 1. Component Development
Create reusable HTMX components:

```html
<!-- components/PatientCard.html -->
<div class="patient-card" x-data="patientCard()">
  <h3 x-text="patient.full_name"></h3>
  <p x-text="patient.ssn"></p>
  <button @click="editPatient">Edit</button>
</div>

<script>
function patientCard() {
  return {
    patient: null,
    async loadPatient(ssn) {
      const response = await apiRequest(`/api/v1/patients/${ssn}`);
      this.patient = await response.json();
    }
  }
}
</script>
```

### 2. Form Handling
Implement auto-save forms with validation:

```html
<!-- forms/CheckEvalForm.html -->
<form hx-post="/api/v1/forms/check-eval"
      hx-trigger="input delay:2s"
      hx-target="#save-status">

  <div class="form-section">
    <label>Temperature (°C):</label>
    <input name="temperature_celsius"
           type="number"
           step="0.1"
           min="30"
           max="45"
           required>
  </div>

  <div id="save-status">Ready</div>
</form>
```

### 3. Error Handling
Implement comprehensive error handling:

```html
<!-- components/ErrorHandler.html -->
<div x-data="errorHandler()" x-show="hasErrors">
  <div class="error-message" x-text="errorMessage"></div>
  <button @click="clearErrors">Dismiss</button>
</div>

<script>
function errorHandler() {
  return {
    hasErrors: false,
    errorMessage: '',

    showError(message) {
      this.errorMessage = message;
      this.hasErrors = true;
      setTimeout(() => this.clearErrors(), 5000);
    },

    clearErrors() {
      this.hasErrors = false;
      this.errorMessage = '';
    }
  }
}
</script>
```

## Testing

### Unit Tests
```bash
npm run test:unit
```

### Integration Tests
```bash
npm run test:integration
```

### E2E Tests
```bash
npm run test:e2e
```

## Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Static Hosting
```bash
# Netlify
npm run deploy:netlify

# Vercel
npm run deploy:vercel
```

### Environment Variables
Set production environment variables:
```env
API_BASE_URL=https://api.healthcare-system.com/api/v1
NODE_ENV=production
```

## Common Patterns

### Loading States
```html
<button hx-post="/api/save" hx-indicator="#loading">
  <span id="loading" class="htmx-indicator">Saving...</span>
  <span>Save</span>
</button>
```

### Pagination
```html
<div hx-get="/api/patients?page=1" hx-target="#results">
  <div id="results"><!-- Patient list --></div>
  <button hx-get="/api/patients?page=2" hx-target="#results">Next</button>
</div>
```

### Real-time Search
```html
<input type="search"
       hx-get="/api/patients/search"
       hx-trigger="input delay:300ms"
       hx-target="#search-results"
       name="q"
       placeholder="Search patients...">

<div id="search-results"></div>
```

## Troubleshooting

### Common Issues

**HTMX requests failing:**
- Check API_BASE_URL configuration
- Verify JWT token is included
- Check CORS settings on backend

**Alpine.js reactivity not working:**
- Ensure x-data is properly initialized
- Check for JavaScript errors in console
- Verify Alpine.js is loaded before components

**Styling issues:**
- Clear Tailwind cache: `npm run build:css`
- Check for CSS conflicts
- Verify responsive breakpoints

### Debug Mode
Enable debug logging:
```javascript
window.htmx.logAll();
```

## Next Steps

1. **Complete Authentication**: Implement login/logout flow
2. **Build Patient Management**: Search, create, update patients
3. **Develop Forms**: Start with Check-Eval form
4. **Add Navigation**: Role-based menu system
5. **Implement Reports**: Basic reporting functionality

## Resources

- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Guide](https://alpinejs.dev/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [API Documentation](/docs/api.md)

---

**Last Updated:** September 21, 2025
**Version:** 1.0.0</content>
<parameter name="filePath">/home/mohamed/lab/.specify/specs/quickstart.md