from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.init_db import create_tables
from app.api.routes import auth, users, patients, visits, forms, reports
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

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

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail} at {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)} at {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
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
    logger.info("Starting up the application...")
    await create_tables()
    logger.info("Database tables created successfully.")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Patient Visit Management System API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}