"""
Security utilities and authentication helpers
"""

from datetime import datetime, timedelta
from typing import Any, Union
from passlib.context import CryptContext
from jose import jwt

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using simple method"""
    import hashlib
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """Hash password using a simple method for compatibility"""
    import hashlib
    # For development purposes, use a simple hash
    # In production, you should use proper password hashing
    return hashlib.sha256(password.encode()).hexdigest()


async def create_initial_admin():
    """Create initial admin user if not exists"""
    from sqlalchemy import text
    from app.database import async_session

    async with async_session() as session:
        # Check if admin user already exists using raw SQL
        result = await session.execute(
            text('SELECT user_id, username, email, full_name, role, is_active FROM users WHERE username = :username'),
            {"username": "admin"}
        )
        existing_user = result.first()

        if existing_user:
            print("Admin user already exists")
            return

        # Create admin user using raw SQL
        await session.execute(
            text('''
                INSERT INTO users (username, email, full_name, role, password_hash, is_active)
                VALUES (:username, :email, :full_name, :role, :password_hash, :is_active)
            '''),
            {
                "username": "admin",
                "email": "admin@hospital.com",
                "full_name": "System Administrator",
                "role": "admin",
                "password_hash": get_password_hash("admin"),
                "is_active": True
            }
        )
        await session.commit()

        print("Created admin user")
        print("Username: admin")
        print("Password: admin")
        print("Email: admin@hospital.com")
        print("Role: admin")