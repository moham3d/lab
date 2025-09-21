"""
Database connection and session management
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    future=True,
    poolclass=NullPool,  # Disable connection pooling for async
    # Don't check for table existence on startup
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    # Database tables already exist, skip creation to avoid conflicts
    # Since we have existing database schema, we don't want to recreate tables
    # that might have different column names or foreign key references
    print("Skipping table creation - using existing database schema")

    # Explicitly clear metadata to prevent any table creation attempts
    from app.models import Base
    Base.metadata.clear()

    # Don't create any tables
    pass


async def drop_tables():
    """Drop all database tables (for testing/cleanup)"""
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)