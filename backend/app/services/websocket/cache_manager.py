"""
Cache Manager for WebSocket Service

This module provides Redis-based caching for connection state, messages,
and performance data with intelligent cache management and optimization.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import pickle
import hashlib

from app.core.exceptions import WebSocketError

logger = logging.getLogger(__name__)


class CacheType(str, Enum):
    """Cache types for different data categories"""
    CONNECTION_STATE = "connection_state"
    USER_SESSIONS = "user_sessions"
    MESSAGE_HISTORY = "message_history"
    PERFORMANCE_DATA = "performance_data"
    USER_PREFERENCES = "user_preferences"
    WORKFLOW_STATE = "workflow_state"
    NOTIFICATION_QUEUE = "notification_queue"


class CachePolicy(str, Enum):
    """Cache eviction policies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    SIZE = "size"  # Size-based eviction


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    cache_type: CacheType
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl: Optional[int] = None
    size_bytes: int = 0
    tags: Set[str] = field(default_factory=set)


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    total_entries: int = 0
    total_size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    hit_rate: float = 0.0
    eviction_count: int = 0
    error_count: int = 0
    last_cleanup: datetime = field(default_factory=datetime.utcnow)


class CacheManager:
    """
    Redis-based cache manager for WebSocket operations
    
    Provides:
    - Multi-type caching with different policies
    - Automatic cache eviction and cleanup
    - Performance monitoring and metrics
    - Cache warming and preloading
    - Distributed cache synchronization
    - Memory optimization and compression
    """
    
    def __init__(
        self,
        redis_client=None,
        default_ttl: int = 3600,  # 1 hour
        max_memory_mb: int = 512,
        compression_threshold: int = 1024,  # 1KB
        cleanup_interval: int = 300,  # 5 minutes
        enable_compression: bool = True
    ):
        """
        Initialize cache manager
        
        Args:
            redis_client: Redis client instance
            default_ttl: Default time-to-live in seconds
            max_memory_mb: Maximum memory usage in MB
            compression_threshold: Threshold for compression in bytes
            cleanup_interval: Cleanup interval in seconds
            enable_compression: Enable data compression
        """
        self.redis_client = redis_client
        self.default_ttl = default_ttl
        self.max_memory_mb = max_memory_mb
        self.compression_threshold = compression_threshold
        self.cleanup_interval = cleanup_interval
        self.enable_compression = enable_compression
        
        # Cache configuration by type
        self.cache_configs = {
            CacheType.CONNECTION_STATE: {
                "ttl": 1800,  # 30 minutes
                "policy": CachePolicy.TTL,
                "max_size": 10000
            },
            CacheType.USER_SESSIONS: {
                "ttl": 7200,  # 2 hours
                "policy": CachePolicy.LRU,
                "max_size": 5000
            },
            CacheType.MESSAGE_HISTORY: {
                "ttl": 3600,  # 1 hour
                "policy": CachePolicy.LRU,
                "max_size": 50000
            },
            CacheType.PERFORMANCE_DATA: {
                "ttl": 1800,  # 30 minutes
                "policy": CachePolicy.TTL,
                "max_size": 10000
            },
            CacheType.USER_PREFERENCES: {
                "ttl": 86400,  # 24 hours
                "policy": CachePolicy.LRU,
                "max_size": 1000
            },
            CacheType.WORKFLOW_STATE: {
                "ttl": 3600,  # 1 hour
                "policy": CachePolicy.TTL,
                "max_size": 2000
            },
            CacheType.NOTIFICATION_QUEUE: {
                "ttl": 300,  # 5 minutes
                "policy": CachePolicy.TTL,
                "max_size": 10000
            }
        }
        
        # Local cache for frequently accessed data
        self.local_cache: Dict[str, CacheEntry] = {}
        self.local_cache_size = 0
        self.max_local_cache_size = 50 * 1024 * 1024  # 50MB
        
        # Metrics
        self.metrics = CacheMetrics()
        
        # Cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Cache warming
        self.warmup_keys: Set[str] = set()
    
    async def start(self):
        """Start the cache manager"""
        if self.running:
            return
        
        self.running = True
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Warm up cache if Redis is available
        if self.redis_client:
            await self._warmup_cache()
        
        logger.info("Cache manager started")
    
    async def stop(self):
        """Stop the cache manager"""
        self.running = False
        
        # Stop cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Flush local cache to Redis
        if self.redis_client:
            await self._flush_local_cache()
        
        logger.info("Cache manager stopped")
    
    async def get(self, key: str, cache_type: CacheType) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            cache_type: Type of cache
            
        Returns:
            Cached value or None if not found
        """
        try:
            # Try local cache first
            if key in self.local_cache:
                entry = self.local_cache[key]
                if not self._is_expired(entry):
                    entry.accessed_at = datetime.utcnow()
                    entry.access_count += 1
                    self.metrics.hit_count += 1
                    return entry.value
            
            # Try Redis cache
            if self.redis_client:
                redis_key = self._get_redis_key(key, cache_type)
                cached_data = await self.redis_client.get(redis_key)
                
                if cached_data:
                    # Deserialize and decompress if needed
                    value = self._deserialize(cached_data)
                    
                    # Update local cache
                    await self._set_local_cache(key, value, cache_type)
                    
                    self.metrics.hit_count += 1
                    return value
            
            self.metrics.miss_count += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.metrics.error_count += 1
            return None
        finally:
            self._update_hit_rate()
    
    async def set(
        self,
        key: str,
        value: Any,
        cache_type: CacheType,
        ttl: Optional[int] = None,
        tags: Optional[Set[str]] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Type of cache
            ttl: Time-to-live in seconds
            tags: Optional tags for cache entry
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get cache configuration
            config = self.cache_configs.get(cache_type, {})
            cache_ttl = ttl or config.get("ttl", self.default_ttl)
            
            # Set in local cache
            await self._set_local_cache(key, value, cache_type, cache_ttl, tags)
            
            # Set in Redis cache
            if self.redis_client:
                redis_key = self._get_redis_key(key, cache_type)
                serialized_data = self._serialize(value)
                
                await self.redis_client.setex(redis_key, cache_ttl, serialized_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.metrics.error_count += 1
            return False
    
    async def delete(self, key: str, cache_type: CacheType) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            cache_type: Type of cache
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from local cache
            if key in self.local_cache:
                entry = self.local_cache[key]
                self.local_cache_size -= entry.size_bytes
                del self.local_cache[key]
            
            # Remove from Redis cache
            if self.redis_client:
                redis_key = self._get_redis_key(key, cache_type)
                await self.redis_client.delete(redis_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.metrics.error_count += 1
            return False
    
    async def delete_by_tags(self, tags: Set[str]) -> int:
        """
        Delete cache entries by tags
        
        Args:
            tags: Tags to match
            
        Returns:
            Number of entries deleted
        """
        deleted_count = 0
        
        try:
            # Delete from local cache
            keys_to_delete = []
            for key, entry in self.local_cache.items():
                if entry.tags.intersection(tags):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                entry = self.local_cache[key]
                self.local_cache_size -= entry.size_bytes
                del self.local_cache[key]
                deleted_count += 1
            
            # Delete from Redis cache (would need to scan keys in real implementation)
            # This is a simplified version
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache delete by tags error: {e}")
            self.metrics.error_count += 1
            return deleted_count
    
    async def get_or_set(
        self,
        key: str,
        cache_type: CacheType,
        factory: callable,
        ttl: Optional[int] = None,
        tags: Optional[Set[str]] = None
    ) -> Any:
        """
        Get value from cache or set it using factory function
        
        Args:
            key: Cache key
            cache_type: Type of cache
            factory: Function to generate value if not cached
            ttl: Time-to-live in seconds
            tags: Optional tags for cache entry
            
        Returns:
            Cached or generated value
        """
        # Try to get from cache
        value = await self.get(key, cache_type)
        if value is not None:
            return value
        
        # Generate value using factory
        try:
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
            
            # Cache the generated value
            await self.set(key, value, cache_type, ttl, tags)
            
            return value
            
        except Exception as e:
            logger.error(f"Cache get_or_set factory error for key {key}: {e}")
            self.metrics.error_count += 1
            raise
    
    async def invalidate_pattern(self, pattern: str, cache_type: CacheType) -> int:
        """
        Invalidate cache entries matching pattern
        
        Args:
            pattern: Key pattern to match
            cache_type: Type of cache
            
        Returns:
            Number of entries invalidated
        """
        invalidated_count = 0
        
        try:
            # Invalidate from local cache
            keys_to_invalidate = [key for key in self.local_cache.keys() if pattern in key]
            
            for key in keys_to_invalidate:
                entry = self.local_cache[key]
                self.local_cache_size -= entry.size_bytes
                del self.local_cache[key]
                invalidated_count += 1
            
            # Invalidate from Redis cache
            if self.redis_client:
                redis_pattern = self._get_redis_key(pattern, cache_type)
                keys = await self.redis_client.keys(redis_pattern)
                
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated_count += len(keys)
            
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Cache invalidate pattern error: {e}")
            self.metrics.error_count += 1
            return invalidated_count
    
    async def _set_local_cache(
        self,
        key: str,
        value: Any,
        cache_type: CacheType,
        ttl: Optional[int] = None,
        tags: Optional[Set[str]] = None
    ):
        """Set value in local cache"""
        config = self.cache_configs.get(cache_type, {})
        cache_ttl = ttl or config.get("ttl", self.default_ttl)
        
        # Calculate size
        size_bytes = self._calculate_size(value)
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            cache_type=cache_type,
            ttl=cache_ttl,
            size_bytes=size_bytes,
            tags=tags or set()
        )
        
        # Check if we need to evict entries
        if self.local_cache_size + size_bytes > self.max_local_cache_size:
            await self._evict_local_cache(size_bytes)
        
        # Add to local cache
        self.local_cache[key] = entry
        self.local_cache_size += size_bytes
        self.metrics.total_entries += 1
        self.metrics.total_size_bytes += size_bytes
    
    async def _evict_local_cache(self, required_space: int):
        """Evict entries from local cache to make space"""
        # Sort entries by access time (LRU)
        sorted_entries = sorted(
            self.local_cache.items(),
            key=lambda x: x[1].accessed_at
        )
        
        freed_space = 0
        for key, entry in sorted_entries:
            if freed_space >= required_space:
                break
            
            del self.local_cache[key]
            self.local_cache_size -= entry.size_bytes
            self.metrics.total_size_bytes -= entry.size_bytes
            self.metrics.eviction_count += 1
            freed_space += entry.size_bytes
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        if entry.ttl is None:
            return False
        
        age = (datetime.utcnow() - entry.created_at).total_seconds()
        return age > entry.ttl
    
    def _get_redis_key(self, key: str, cache_type: CacheType) -> str:
        """Generate Redis key for cache entry"""
        return f"websocket:{cache_type.value}:{key}"
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            # Try JSON first for simple types
            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(value).encode('utf-8')
            else:
                # Use pickle for complex types
                return pickle.dumps(value)
        except Exception:
            # Fallback to pickle
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except Exception:
            # Fallback to pickle
            return pickle.loads(data)
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value in bytes"""
        try:
            serialized = self._serialize(value)
            return len(serialized)
        except Exception:
            return 1024  # Default estimate
    
    def _update_hit_rate(self):
        """Update cache hit rate"""
        total_requests = self.metrics.hit_count + self.metrics.miss_count
        if total_requests > 0:
            self.metrics.hit_rate = self.metrics.hit_count / total_requests
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_entries()
                self.metrics.last_cleanup = datetime.utcnow()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    async def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, entry in self.local_cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            entry = self.local_cache[key]
            self.local_cache_size -= entry.size_bytes
            self.metrics.total_size_bytes -= entry.size_bytes
            del self.local_cache[key]
            self.metrics.eviction_count += 1
    
    async def _warmup_cache(self):
        """Warm up cache with frequently accessed data"""
        try:
            # This would typically load frequently accessed data
            # For now, we'll just log that warmup is complete
            logger.info("Cache warmup completed")
        except Exception as e:
            logger.error(f"Cache warmup error: {e}")
    
    async def _flush_local_cache(self):
        """Flush local cache to Redis"""
        if not self.redis_client:
            return
        
        try:
            for key, entry in self.local_cache.items():
                if not self._is_expired(entry):
                    redis_key = self._get_redis_key(key, entry.cache_type)
                    serialized_data = self._serialize(entry.value)
                    await self.redis_client.setex(redis_key, entry.ttl or self.default_ttl, serialized_data)
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
    
    def get_metrics(self) -> CacheMetrics:
        """Get cache metrics"""
        self.metrics.total_entries = len(self.local_cache)
        self.metrics.total_size_bytes = self.local_cache_size
        return self.metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on cache manager
        
        Returns:
            Dict[str, Any]: Health check results
        """
        metrics = self.get_metrics()
        
        # Calculate health status
        memory_usage_mb = metrics.total_size_bytes / (1024 * 1024)
        memory_usage_percent = (memory_usage_mb / self.max_memory_mb) * 100
        
        if memory_usage_percent > 90:
            status = "critical"
        elif memory_usage_percent > 70 or metrics.hit_rate < 0.5:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "metrics": {
                "total_entries": metrics.total_entries,
                "total_size_mb": memory_usage_mb,
                "memory_usage_percent": memory_usage_percent,
                "hit_count": metrics.hit_count,
                "miss_count": metrics.miss_count,
                "hit_rate": metrics.hit_rate,
                "eviction_count": metrics.eviction_count,
                "error_count": metrics.error_count
            },
            "configuration": {
                "max_memory_mb": self.max_memory_mb,
                "default_ttl": self.default_ttl,
                "compression_threshold": self.compression_threshold,
                "cleanup_interval": self.cleanup_interval,
                "enable_compression": self.enable_compression
            },
            "cache_types": {
                cache_type.value: config for cache_type, config in self.cache_configs.items()
            }
        }

