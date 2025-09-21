# GitHub Copilot Instructions for Patient Visit Management System

## Project Overview
This is a FastAPI-based healthcare backend API for managing patient visits, assessments, and documents with HIPAA compliance.

## Technology Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy 2.0 and asyncpg
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic models
- **Migrations**: SQL schema files (schema.sql) for database initialization
- **Testing**: pytest with asyncio
- **Documentation**: Automatic OpenAPI/Swagger
- **File Handling**: aiofiles with validation
- **Background Tasks**: Celery with Redis
- **Environment**: python-dotenv

## Architecture Patterns
- **Dependency Injection**: Use FastAPI's dependency system for database sessions and authentication
- **Repository Pattern**: Separate data access logic from business logic
- **Service Layer**: Business logic in service classes
- **Pydantic Models**: Request/response validation and serialization
- **Async Operations**: All database operations use async/await
- **Error Handling**: Custom exceptions with meaningful messages
- **Logging**: Structured logging with context

## Security Requirements
- **HIPAA Compliance**: All patient data (PHI) must be encrypted
- **Role-Based Access**: nurse, physician, admin roles with specific permissions
- **Audit Logging**: All actions logged with user, timestamp, IP
- **Input Validation**: Strict validation of medical data formats
- **Secure File Storage**: Unique naming, size limits, type validation

## Code Style
- **Type Hints**: Use typing for all function parameters and return values
- **Docstrings**: Google-style docstrings for all public functions
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Imports**: Standard library first, then third-party, then local
- **Error Handling**: Use specific exceptions, avoid bare except
- **Async**: Use async/await consistently, avoid blocking operations

## Database Patterns
- **Models**: SQLAlchemy declarative models with relationships
- **Sessions**: Async session management with dependency injection
- **Migrations**: SQL schema files for database initialization
- **Constraints**: Database-level constraints for data integrity
- **Indexes**: Appropriate indexes for query performance

## API Design
- **RESTful**: Standard HTTP methods and status codes
- **Versioning**: /api/v1/ prefix for all endpoints
- **Pagination**: For list endpoints with large datasets
- **Filtering**: Query parameters for search and filter
- **Validation**: Pydantic models for all request/response data
- **Documentation**: Automatic API docs with examples

## Testing Strategy
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints with database
- **Fixtures**: Use pytest fixtures for test data
- **Async Tests**: Use pytest-asyncio for async test functions
- **Coverage**: Aim for >80% test coverage
- **Mocking**: Mock external dependencies

## File Structure
```
app/
├── main.py              # FastAPI app initialization
├── config.py            # Settings with Pydantic
├── database.py          # Database connection and session
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── api/                 # API route handlers
├── core/                # Core functionality (auth, security)
├── services/            # Business logic services
├── utils/               # Utility functions
└── tests/               # Test files
```

## Common Patterns
- **CRUD Operations**: Standard create, read, update, delete with validation
- **Search**: Flexible search with multiple fields
- **Relationships**: Proper handling of foreign keys and relationships
- **Transactions**: Use database transactions for data consistency
- **Caching**: Redis for frequently accessed data
- **Background Jobs**: Celery for long-running tasks

## Medical Data Validation
- **SSN**: 14-digit Egyptian format
- **Mobile**: 01[0-2] followed by 8 digits
- **Vital Signs**: Medical ranges (temperature 30-45°C, pulse 30-200 bpm, etc.)
- **Dates**: Proper date validation and formatting
- **Enums**: Use enums for categorical data (gender, status, roles)

## Error Responses
- **400 Bad Request**: Validation errors with field details
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflicts (duplicate data)
- **422 Unprocessable Entity**: Business logic validation failures
- **500 Internal Server Error**: Unexpected errors (logged)

## Performance Considerations
- **Async Database**: Use asyncpg for connection pooling
- **Indexes**: Database indexes on frequently queried fields
- **Pagination**: Limit and offset for large result sets
- **Caching**: Redis for session and data caching
- **Background Tasks**: Offload heavy operations to Celery
- **File Storage**: Secure file storage with metadata

## Compliance Requirements
- **Audit Trail**: Log all user actions with context
- **Data Retention**: Configurable retention policies
- **Encryption**: Encrypt sensitive data at rest
- **Access Control**: Granular permissions based on roles
- **Data Export**: Secure data export for compliance
- **Monitoring**: Health checks and error monitoring

## Development Workflow
1. **Planning**: Use spec and plan documents for requirements
2. **Implementation**: Follow TDD with contract tests
3. **Testing**: Comprehensive test coverage
4. **Review**: Code review with security checklist
5. **Deployment**: Docker containerization with health checks
6. **Monitoring**: Logging and error tracking

## Recent Changes
- Initial project setup with FastAPI and PostgreSQL
- Authentication system with JWT and role-based access
- Patient and visit management with validation
- Assessment forms for nursing and radiology
- Document upload and storage
- Admin reporting system
- Audit logging for compliance
- Docker deployment configuration