"""
User model for authentication and authorization
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models import Base


class UserRole(str, Enum):
    """User role enumeration"""
    NURSE = "nurse"
    PHYSICIAN = "physician"
    ADMIN = "admin"


class User(Base):
    """User database model"""
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.NURSE)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, role={self.role})>"