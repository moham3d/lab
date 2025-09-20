"""
Application configuration using Pydantic settings
"""

from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Project
    PROJECT_NAME: str = "Patient Visit Management System"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Healthcare backend API for patient visit management"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "mohamed"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "patient_visits"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v, info):
        if isinstance(v, str):
            return v
        # In Pydantic v2, we need to access the raw field values
        # The values are available in the model_fields
        user = getattr(cls, 'POSTGRES_USER', 'postgres')
        password = getattr(cls, 'POSTGRES_PASSWORD', 'password')
        server = getattr(cls, 'POSTGRES_SERVER', 'localhost')
        port = getattr(cls, 'POSTGRES_PORT', '5432')
        db = getattr(cls, 'POSTGRES_DB', 'patient_visits')
        return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db}"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
        "https://localhost:3000",
        "https://localhost:8080",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Trusted hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp",
        ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv",
        ".zip", ".rar"
    ]
    ALLOWED_MIME_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/tiff", "image/bmp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain", "text/csv",
        "application/zip", "application/x-zip-compressed"
    ]

    # HIPAA Compliance
    ENCRYPTION_KEY: str = secrets.token_hex(32)
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years

    # Email (for notifications)
    SMTP_SERVER: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()