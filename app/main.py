"""
Patient Visit Management System - FastAPI Backend
Healthcare API for managing patient visits, assessments, and documents
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import psutil
import os
from datetime import datetime

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.security import create_initial_admin
from app.core.security_middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    InputSanitizationMiddleware
)
from app.database import create_tables
from app.utils.file_handler import FileHandler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    setup_logging()
    await create_tables()
    await create_initial_admin()
    FileHandler.ensure_upload_directory()

    yield

    # Shutdown
    # Add cleanup logic here if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Production security middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)  # 100 requests per minute
app.add_middleware(InputSanitizationMiddleware)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    from datetime import datetime
    from app.database import get_db
    from sqlalchemy import text

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME,
        "checks": {}
    }

    try:
        # Database health check
        db = await get_db().__anext__()
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {"status": "unhealthy", "message": str(e)}

    # System health checks
    try:
        memory = psutil.virtual_memory()
        health_status["checks"]["memory"] = {
            "status": "healthy" if memory.percent < 90 else "warning",
            "usage_percent": memory.percent,
            "available_mb": memory.available / 1024 / 1024
        }
    except Exception as e:
        health_status["checks"]["memory"] = {"status": "unknown", "message": str(e)}

    # Disk space check
    try:
        disk = psutil.disk_usage('/')
        health_status["checks"]["disk"] = {
            "status": "healthy" if disk.percent < 90 else "warning",
            "usage_percent": disk.percent,
            "free_gb": disk.free / 1024 / 1024 / 1024
        }
    except Exception as e:
        health_status["checks"]["disk"] = {"status": "unknown", "message": str(e)}

    # Upload directory check
    try:
        upload_dir = settings.UPLOAD_DIR
        if os.path.exists(upload_dir):
            health_status["checks"]["uploads"] = {"status": "healthy", "message": "Upload directory exists"}
        else:
            health_status["checks"]["uploads"] = {"status": "unhealthy", "message": "Upload directory missing"}
    except Exception as e:
        health_status["checks"]["uploads"] = {"status": "unknown", "message": str(e)}

    # Overall status
    if any(check.get("status") == "unhealthy" for check in health_status["checks"].values()):
        health_status["status"] = "unhealthy"

    return health_status


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )