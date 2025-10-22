"""
Unit tests for the Redis client module.

This module tests the Redis client functionality including:
- Connection initialization and management
- Cache operations (get, set, delete, exists, expire, ttl)
- Error handling
- Connection pooling
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Any, Optional

# Mock redis before importing
with patch.dict('sys.modules', {
    'redis': Mock(),
    'redis.asyncio': Mock(),
}):
    import redis.asyncio as redis
    from redis.asyncio import ConnectionPool
    
    # Mock the redis modules
    redis.Redis = Mock
    ConnectionPool.from_url = Mock
    ConnectionPool = Mock
    
    from app.core.redis_client import (
        init_redis, get_redis, close_redis, RedisCache, get_cache
    )


class TestRedisClient:
    """Test cases for Redis client functionality."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        mock_client.get = AsyncMock()
        mock_client.set = AsyncMock()
        mock_client.delete = AsyncMock()
        mock_client.exists = AsyncMock()
        mock_client.expire = AsyncMock()
        mock_client.ttl = AsyncMock()
        return mock_client

    @pytest.fixture
    def mock_connection_pool(self):
        """Create a mock connection pool."""
        mock_pool = Mock()
        return mock_pool

    @pytest.mark.asyncio
    async def test_init_redis_success(self, mock_connection_pool, mock_redis_client):
        """Test successful Redis initialization."""
        with patch('app.core.redis_client.ConnectionPool.from_url', return_value=mock_connection_pool):
            with patch('app.core.redis_client.redis.Redis', return_value=mock_redis_client):
                with patch('app.core.redis_client.settings') as mock_settings:
                    mock_settings.redis_url = "redis://localhost:6379"
                    mock_settings.redis_max_connections = 10
                    
                    await init_redis()
                    
                    # Verify connection pool was created
                    ConnectionPool.from_url.assert_called_once_with(
                        "redis://localhost:6379",
                        max_connections=10,
                        retry_on_timeout=True,
                        health_check_interval=30,
                    )
                    
                    # Verify Redis client was created
                    redis.Redis.assert_called_once_with(connection_pool=mock_connection_pool)

    @pytest.mark.asyncio
    async def test_init_redis_with_error(self):
        """Test Redis initialization with error."""
        with patch('app.core.redis_client.ConnectionPool.from_url', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception, match="Connection failed"):
                await init_redis()

    @pytest.mark.asyncio
    async def test_get_redis_success(self, mock_redis_client):
        """Test getting Redis client successfully."""
        with patch('app.core.redis_client.redis_client', mock_redis_client):
            client = await get_redis()
            assert client == mock_redis_client

    @pytest.mark.asyncio
    async def test_get_redis_not_initialized(self):
        """Test getting Redis client when not initialized."""
        with patch('app.core.redis_client.redis_client', None):
            with pytest.raises(RuntimeError, match="Redis client not initialized"):
                await get_redis()

    @pytest.mark.asyncio
    async def test_close_redis_success(self, mock_redis_client, mock_connection_pool):
        """Test closing Redis connection successfully."""
        mock_redis_client.close = AsyncMock()
        mock_connection_pool.disconnect = AsyncMock()
        
        with patch('app.core.redis_client.redis_client', mock_redis_client):
            with patch('app.core.redis_client.redis_pool', mock_connection_pool):
                await close_redis()
                
                mock_redis_client.close.assert_called_once()
                mock_connection_pool.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_redis_with_error(self, mock_redis_client):
        """Test closing Redis connection with error."""
        mock_redis_client.close = AsyncMock(side_effect=Exception("Close failed"))
        
        with patch('app.core.redis_client.redis_client', mock_redis_client):
            with patch('app.core.redis_client.redis_pool', None):
                # Should not raise exception
                await close_redis()

    @pytest.mark.asyncio
    async def test_redis_cache_get_success(self, mock_redis_client):
        """Test Redis cache get operation success."""
        mock_redis_client.get = AsyncMock(return_value=b'{"key": "value"}')
        
        cache = RedisCache(mock_redis_client)
        result = await cache.get("test_key")
        
        assert result == {"key": "value"}
        mock_redis_client.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_redis_cache_get_not_found(self, mock_redis_client):
        """Test Redis cache get operation when key not found."""
        mock_redis_client.get = AsyncMock(return_value=None)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.get("nonexistent_key")
        
        assert result is None
        mock_redis_client.get.assert_called_once_with("nonexistent_key")

    @pytest.mark.asyncio
    async def test_redis_cache_get_invalid_json(self, mock_redis_client):
        """Test Redis cache get operation with invalid JSON."""
        mock_redis_client.get = AsyncMock(return_value=b"invalid json")
        
        cache = RedisCache(mock_redis_client)
        result = await cache.get("test_key")
        
        assert result is None
        mock_redis_client.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_redis_cache_set_success(self, mock_redis_client):
        """Test Redis cache set operation success."""
        mock_redis_client.set = AsyncMock(return_value=True)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.set("test_key", {"key": "value"}, expire=3600)
        
        assert result is True
        mock_redis_client.set.assert_called_once_with(
            "test_key", 
            '{"key": "value"}', 
            ex=3600
        )

    @pytest.mark.asyncio
    async def test_redis_cache_set_without_expire(self, mock_redis_client):
        """Test Redis cache set operation without expiration."""
        mock_redis_client.set = AsyncMock(return_value=True)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.set("test_key", {"key": "value"})
        
        assert result is True
        mock_redis_client.set.assert_called_once_with(
            "test_key", 
            '{"key": "value"}'
        )

    @pytest.mark.asyncio
    async def test_redis_cache_set_with_error(self, mock_redis_client):
        """Test Redis cache set operation with error."""
        mock_redis_client.set = AsyncMock(side_effect=Exception("Set failed"))
        
        cache = RedisCache(mock_redis_client)
        result = await cache.set("test_key", {"key": "value"})
        
        assert result is False

    @pytest.mark.asyncio
    async def test_redis_cache_delete_success(self, mock_redis_client):
        """Test Redis cache delete operation success."""
        mock_redis_client.delete = AsyncMock(return_value=1)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.delete("test_key")
        
        assert result is True
        mock_redis_client.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_redis_cache_delete_not_found(self, mock_redis_client):
        """Test Redis cache delete operation when key not found."""
        mock_redis_client.delete = AsyncMock(return_value=0)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.delete("nonexistent_key")
        
        assert result is False
        mock_redis_client.delete.assert_called_once_with("nonexistent_key")

    @pytest.mark.asyncio
    async def test_redis_cache_delete_with_error(self, mock_redis_client):
        """Test Redis cache delete operation with error."""
        mock_redis_client.delete = AsyncMock(side_effect=Exception("Delete failed"))
        
        cache = RedisCache(mock_redis_client)
        result = await cache.delete("test_key")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_redis_cache_exists_success(self, mock_redis_client):
        """Test Redis cache exists operation success."""
        mock_redis_client.exists = AsyncMock(return_value=1)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.exists("test_key")
        
        assert result is True
        mock_redis_client.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_redis_cache_exists_not_found(self, mock_redis_client):
        """Test Redis cache exists operation when key not found."""
        mock_redis_client.exists = AsyncMock(return_value=0)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.exists("nonexistent_key")
        
        assert result is False
        mock_redis_client.exists.assert_called_once_with("nonexistent_key")

    @pytest.mark.asyncio
    async def test_redis_cache_exists_with_error(self, mock_redis_client):
        """Test Redis cache exists operation with error."""
        mock_redis_client.exists = AsyncMock(side_effect=Exception("Exists failed"))
        
        cache = RedisCache(mock_redis_client)
        result = await cache.exists("test_key")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_redis_cache_expire_success(self, mock_redis_client):
        """Test Redis cache expire operation success."""
        mock_redis_client.expire = AsyncMock(return_value=True)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.expire("test_key", 3600)
        
        assert result is True
        mock_redis_client.expire.assert_called_once_with("test_key", 3600)

    @pytest.mark.asyncio
    async def test_redis_cache_expire_with_error(self, mock_redis_client):
        """Test Redis cache expire operation with error."""
        mock_redis_client.expire = AsyncMock(side_effect=Exception("Expire failed"))
        
        cache = RedisCache(mock_redis_client)
        result = await cache.expire("test_key", 3600)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_redis_cache_ttl_success(self, mock_redis_client):
        """Test Redis cache TTL operation success."""
        mock_redis_client.ttl = AsyncMock(return_value=3600)
        
        cache = RedisCache(mock_redis_client)
        result = await cache.ttl("test_key")
        
        assert result == 3600
        mock_redis_client.ttl.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_redis_cache_ttl_with_error(self, mock_redis_client):
        """Test Redis cache TTL operation with error."""
        mock_redis_client.ttl = AsyncMock(side_effect=Exception("TTL failed"))
        
        cache = RedisCache(mock_redis_client)
        result = await cache.ttl("test_key")
        
        assert result == -1

    @pytest.mark.asyncio
    async def test_get_cache_success(self, mock_redis_client):
        """Test getting cache instance successfully."""
        with patch('app.core.redis_client.redis_client', mock_redis_client):
            cache = await get_cache()
            assert isinstance(cache, RedisCache)
            assert cache.redis_client == mock_redis_client

    @pytest.mark.asyncio
    async def test_get_cache_not_initialized(self):
        """Test getting cache instance when Redis not initialized."""
        with patch('app.core.redis_client.redis_client', None):
            with pytest.raises(RuntimeError, match="Redis client not initialized"):
                await get_cache()

    @pytest.mark.asyncio
    async def test_redis_cache_with_different_data_types(self, mock_redis_client):
        """Test Redis cache with different data types."""
        cache = RedisCache(mock_redis_client)
        
        # Test with string
        mock_redis_client.set = AsyncMock(return_value=True)
        await cache.set("string_key", "test_string")
        mock_redis_client.set.assert_called_with("string_key", '"test_string"')
        
        # Test with number
        await cache.set("number_key", 42)
        mock_redis_client.set.assert_called_with("number_key", "42")
        
        # Test with boolean
        await cache.set("bool_key", True)
        mock_redis_client.set.assert_called_with("bool_key", "true")
        
        # Test with list
        await cache.set("list_key", [1, 2, 3])
        mock_redis_client.set.assert_called_with("list_key", "[1, 2, 3]")
        
        # Test with dict
        await cache.set("dict_key", {"a": 1, "b": 2})
        mock_redis_client.set.assert_called_with("dict_key", '{"a": 1, "b": 2}')

    @pytest.mark.asyncio
    async def test_redis_cache_connection_error_handling(self, mock_redis_client):
        """Test Redis cache error handling for connection issues."""
        cache = RedisCache(mock_redis_client)
        
        # Test get with connection error
        mock_redis_client.get = AsyncMock(side_effect=redis.ConnectionError("Connection lost"))
        result = await cache.get("test_key")
        assert result is None
        
        # Test set with connection error
        mock_redis_client.set = AsyncMock(side_effect=redis.ConnectionError("Connection lost"))
        result = await cache.set("test_key", "value")
        assert result is False
        
        # Test delete with connection error
        mock_redis_client.delete = AsyncMock(side_effect=redis.ConnectionError("Connection lost"))
        result = await cache.delete("test_key")
        assert result is False
        
        # Test exists with connection error
        mock_redis_client.exists = AsyncMock(side_effect=redis.ConnectionError("Connection lost"))
        result = await cache.exists("test_key")
        assert result is False
        
        # Test expire with connection error
        mock_redis_client.expire = AsyncMock(side_effect=redis.ConnectionError("Connection lost"))
        result = await cache.expire("test_key", 3600)
        assert result is False
        
        # Test ttl with connection error
        mock_redis_client.ttl = AsyncMock(side_effect=redis.ConnectionError("Connection lost"))
        result = await cache.ttl("test_key")
        assert result == -1

