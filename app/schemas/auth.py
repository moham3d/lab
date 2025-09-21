"""
Authentication schemas for request/response validation
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    username: str | None = None


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class RefreshToken(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserCreate(BaseModel):
    """User creation request (admin only)"""
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: str = "nurse"


class UserResponse(BaseModel):
    """User response model"""
    user_id: UUID
    username: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str