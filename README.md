# Patient Visit Management System

A comprehensive FastAPI-based healthcare backend API for managing patient visits, assessments, and documents with HIPAA compliance.

## 🚀 Features

- **Patient Management**: Complete CRUD operations with SSN/mobile search
- **Visit Management**: Lifecycle management with status transitions
- **Clinical Assessments**: Nursing and radiology assessments with vital signs
- **Document Management**: Secure file upload with validation and storage
- **Reporting System**: Dashboard statistics and data export
- **Authentication**: JWT-based authentication with role-based access
- **Audit Logging**: Comprehensive audit trail for compliance
- **Production Ready**: Security headers, rate limiting, health checks

## 🛠️ Technology Stack

- **Backend**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL with asyncpg
- **Authentication**: JWT with python-jose
- **File Storage**: Local filesystem with secure naming
- **Background Tasks**: Celery with Redis
- **Testing**: pytest with comprehensive contract tests
- **Deployment**: Docker with docker-compose

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.13+
- PostgreSQL (for local development)
- Redis (for background tasks)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd patient-visit-management-system

# Copy environment configuration
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 2. Development Setup

```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec app alembic upgrade head

# View logs
docker-compose logs -f app
```

### 3. Production Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

## 📖 API Documentation

Once running, access the API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 Testing

### Run All Tests
```bash
# Contract tests
docker-compose exec app python -m pytest app/tests/contract/ -v

# Unit tests (when implemented)
docker-compose exec app python -m pytest app/tests/unit/ -v

# Integration tests (when implemented)
docker-compose exec app python -m pytest app/tests/integration/ -v
```

### Test Coverage
```bash
docker-compose exec app python -m pytest --cov=app --cov-report=html
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=patient_user
POSTGRES_PASSWORD=your-password
POSTGRES_DB=patient_visits

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 🗄️ Database Management

### Migrations
```bash
# Create new migration
docker-compose exec app alembic revision --autogenerate -m "migration message"

# Apply migrations
docker-compose exec app alembic upgrade head

# Downgrade
docker-compose exec app alembic downgrade -1
```

### Backup & Restore
```bash
# Create backup
./scripts/backup.sh backup

# List backups
./scripts/backup.sh list

# Restore from backup
./scripts/backup.sh restore ./backups/backup_20231201_120000.sql.gz
```

## 🔒 Security Features

- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **Rate Limiting**: 100 requests per minute per IP
- **Input Sanitization**: Protection against injection attacks
- **CORS Configuration**: Properly configured for production
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Admin, Nurse, Physician roles
- **Audit Logging**: Complete audit trail for compliance

## 📊 Monitoring & Health Checks

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Returns comprehensive health status including:
- Database connectivity
- Memory usage
- Disk space
- Upload directory status

### Application Logs
```bash
# View application logs
docker-compose logs -f app

# View all logs
docker-compose logs -f

# Log files location
tail -f logs/app.log
```

## 🏗️ Project Structure

```
patient-visit-management-system/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── core/                 # Core functionality
│   │   ├── config.py        # Settings management
│   │   ├── security.py      # Authentication & security
│   │   └── logging_config.py # Logging configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── tests/               # Test suites
├── scripts/                 # Deployment scripts
├── uploads/                 # File uploads directory
├── logs/                    # Application logs
├── Dockerfile              # Production container
├── docker-compose.yml      # Service orchestration
├── requirements.txt        # Python dependencies
└── .env.example           # Environment template
```

## 🔄 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Patients
- `GET /api/v1/patients/search` - Search patients
- `POST /api/v1/patients/` - Create patient
- `GET /api/v1/patients/{id}` - Get patient details
- `PUT /api/v1/patients/{id}` - Update patient
- `GET /api/v1/patients/{id}/history` - Patient visit history

### Visits
- `GET /api/v1/visits/` - List visits
- `POST /api/v1/visits/` - Create visit
- `GET /api/v1/visits/{id}` - Get visit details
- `PUT /api/v1/visits/{id}` - Update visit

### Assessments
- `POST /api/v1/assessments/nursing/` - Create nursing assessment
- `GET /api/v1/assessments/nursing/{id}` - Get nursing assessment
- `POST /api/v1/assessments/radiology/` - Create radiology assessment
- `GET /api/v1/assessments/radiology/{id}` - Get radiology assessment

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/{id}` - Get document details
- `GET /api/v1/documents/{id}/download` - Download document
- `GET /api/v1/documents/visit/{visit_id}` - List visit documents

### Reports
- `GET /api/v1/reports/dashboard` - Dashboard statistics
- `GET /api/v1/reports/patients` - Patient statistics
- `GET /api/v1/reports/visits/volume` - Visit volume reports
- `GET /api/v1/reports/export/{type}` - Data export

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the logs in the `logs/` directory
- Check the health endpoint at `/health`

## 🔄 Version History

- **v1.0.0**: Initial production release
  - Complete patient, visit, and assessment management
  - Document upload and storage
  - Reporting and analytics
  - Production-ready security and monitoring