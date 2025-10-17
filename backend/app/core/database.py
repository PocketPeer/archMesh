"""
Database configuration and session management.

This module provides async SQLAlchemy setup with connection pooling,
session management, and base model for all database tables.
"""

from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings

# Create async engine with connection pooling
# Use in-memory SQLite for testing, PostgreSQL for other environments
database_url = (
    "sqlite+aiosqlite:///:memory:" if settings.environment == "test" 
    else settings.database_url
)

# Configure engine parameters based on database type
if settings.environment == "test":
    # SQLite configuration
    engine = create_async_engine(
        database_url,
        echo=settings.debug,
        poolclass=NullPool,
    )
else:
    # PostgreSQL configuration
    engine = create_async_engine(
        database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections every hour
        echo=settings.debug,  # Log SQL queries in debug mode
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

# Create declarative base with metadata
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base = declarative_base(metadata=metadata)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session instance
        
    Example:
        ```python
        async def some_endpoint(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(SomeModel))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    This function creates all tables defined in the models.
    Should be called during application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    
    Should be called during application shutdown.
    """
    await engine.dispose()
