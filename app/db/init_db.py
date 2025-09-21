import asyncpg
from app.core.config import settings

async def execute_schema():
    """Execute the schema.sql file to create tables."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        with open("app/db/schema.sql", "r") as f:
            schema_sql = f.read()
        await conn.execute(schema_sql)
    finally:
        await conn.close()

# For queries, we can use raw SQL or keep SQLAlchemy for models
# But since schema is executed, models are optional
# Keep SQLAlchemy for session management if needed

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.database_url, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Execute schema.sql to create tables."""
    await execute_schema()