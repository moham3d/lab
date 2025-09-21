from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import create_tables
from app.api.routes import auth, users, patients, visits, forms, reports

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Healthcare backend API for managing patient visits, assessments, and documents with HIPAA compliance."
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(visits.router, prefix="/api/v1/visits", tags=["Visits"])
app.include_router(forms.router, prefix="/api/v1/forms", tags=["Forms"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    await create_tables()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Patient Visit Management System API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}