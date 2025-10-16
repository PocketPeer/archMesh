"""
Redis client configuration and connection management.

This module provides Redis connection with connection pooling and
async support for caching and session management.
"""

import json
from typing import Any, Optional, Union

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from app.config import settings

# Create Redis connection pool
redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """
    Initialize Redis connection pool and client.
    
    Should be called during application startup.
    """
    global redis_pool, redis_client
    
    redis_pool = ConnectionPool.from_url(
        settings.redis_url,
        max_connections=settings.redis_max_connections,
        retry_on_timeout=True,
        health_check_interval=30,
    )
    
    redis_client = redis.Redis(connection_pool=redis_pool)


async def get_redis() -> redis.Redis:
    """
    Get Redis client instance.
    
    Returns:
        redis.Redis: Redis client instance
        
    Raises:
        RuntimeError: If Redis client is not initialized
        
    Example:
        ```python
        redis_client = await get_redis()
        await redis_client.set("key", "value")
        ```
    """
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client


async def close_redis() -> None:
    """
    Close Redis connections.
    
    Should be called during application shutdown.
    """
    global redis_pool, redis_client
    
    if redis_client:
        await redis_client.close()
        redis_client = None
    
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None


class RedisCache:
    """
    Redis cache utility class with JSON serialization.
    
    Provides convenient methods for caching data with automatic
    JSON serialization/deserialization.
    """
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize Redis cache.
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Deserialized value or None if not found
        """
        value = await self.redis.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Return raw value if not JSON
            return value.decode() if isinstance(value, bytes) else value
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
            
        Returns:
            True if successful
        """
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value)
        elif not isinstance(value, (str, bytes)):
            value = str(value)
        
        return await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted
        """
        return bool(await self.redis.delete(key))
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        return bool(await self.redis.exists(key))
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            
        Returns:
            True if successful
        """
        return await self.redis.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        """
        Get time to live for key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        return await self.redis.ttl(key)


async def get_cache() -> RedisCache:
    """
    Get Redis cache instance.
    
    Returns:
        RedisCache: Cache instance
        
    Example:
        ```python
        cache = await get_cache()
        await cache.set("user:123", {"name": "John"})
        user = await cache.get("user:123")
        ```
    """
    redis_client = await get_redis()
    return RedisCache(redis_client)
