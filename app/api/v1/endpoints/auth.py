"""
Authentication endpoints
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import Token, UserLogin, RefreshToken, UserCreate, UserResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


@router.post("/login", response_model=Token)
async def login(
    username: str = Form(..., description="Username for authentication"),
    password: str = Form(..., description="Password for authentication"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Authenticate user and return tokens"""
    user = await AuthService.authenticate_user(db, username, password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = AuthService.create_tokens(user)

    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshToken,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Refresh access token using refresh token"""
    # TODO: Implement refresh token validation
    # For now, return error
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token functionality not yet implemented",
    )


@router.post("/logout")
async def logout() -> Any:
    """Logout user (invalidate tokens)"""
    # TODO: Implement token blacklisting
    return {"message": "Logged out successfully"}


# Admin endpoints
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    # TODO: Add admin permission check
) -> Any:
    """Create new user (admin only)"""
    try:
        user = await AuthService.create_user(db, user_data)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    # TODO: Add admin permission check
) -> Any:
    """List all users (admin only)"""
    users = await AuthService.list_users(db)
    return [UserResponse.from_orm(user) for user in users]