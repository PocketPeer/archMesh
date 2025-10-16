"""
Dependency injection for FastAPI endpoints.

This module provides common dependencies that can be used across
different API endpoints for database sessions, Redis cache, etc.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import get_cache, RedisCache
from app.config import settings


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session instance
        
    Example:
        ```python
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_database_session)):
            # Use db session here
            pass
        ```
    """
    async for session in get_db():
        yield session


async def get_redis_cache() -> RedisCache:
    """
    Dependency to get Redis cache instance.
    
    Returns:
        RedisCache: Cache instance
        
    Example:
        ```python
        @app.get("/cached-data")
        async def get_cached_data(cache: RedisCache = Depends(get_redis_cache)):
            # Use cache here
            pass
        ```
    """
    return await get_cache()


def get_settings():
    """
    Dependency to get application settings.
    
    Returns:
        Settings: Application settings instance
        
    Example:
        ```python
        @app.get("/config")
        async def get_config(settings: Settings = Depends(get_settings)):
            return {"debug": settings.debug}
        ```
    """
    return settings


class CommonQueryParams:
    """
    Common query parameters for pagination and filtering.
    
    Attributes:
        skip: Number of items to skip
        limit: Maximum number of items to return
        search: Search term for filtering
    """
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
    ):
        """
        Initialize common query parameters.
        
        Args:
            skip: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 100)
            search: Search term for filtering (default: None)
        """
        self.skip = max(0, skip)
        self.limit = min(100, max(1, limit))  # Limit between 1 and 100
        self.search = search


def get_common_query_params(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
) -> CommonQueryParams:
    """
    Dependency for common query parameters.
    
    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        search: Search term for filtering
        
    Returns:
        CommonQueryParams: Query parameters instance
        
    Example:
        ```python
        @app.get("/items")
        async def get_items(params: CommonQueryParams = Depends(get_common_query_params)):
            # Use params.skip, params.limit, params.search
            pass
        ```
    """
    return CommonQueryParams(skip=skip, limit=limit, search=search)


def require_debug_mode():
    """
    Dependency that requires debug mode to be enabled.
    
    Raises:
        HTTPException: If debug mode is not enabled
        
    Example:
        ```python
        @app.get("/debug/info")
        async def debug_info(_: None = Depends(require_debug_mode)):
            return {"debug": True}
        ```
    """
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug mode is required for this endpoint"
        )
    return None


def require_production_mode():
    """
    Dependency that requires production mode.
    
    Raises:
        HTTPException: If not in production mode
        
    Example:
        ```python
        @app.get("/production/only")
        async def production_only(_: None = Depends(require_production_mode)):
            return {"production": True}
        ```
    """
    if not settings.is_production:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Production mode is required for this endpoint"
        )
    return None
