"""
REFACTOR Phase 1: Optimized Context Aggregator

Advanced caching, parallel processing, and smart filtering capabilities
for the Context Aggregator component.
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, Any, List, Optional, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from app.vibe_coding.context_aggregator import ContextAggregator, ContextAggregatorConfig
from app.vibe_coding.models import (
    ContextSource, ContextAggregationRequest, ContextAggregationResponse,
    UnifiedContext, ContextQualityMetrics
)
from app.core.exceptions import ContextGatherError


class CacheLevel(Enum):
    """Cache level enumeration"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"


@dataclass
class CacheConfig:
    """Cache configuration"""
    l1_cache_size: int = 100
    l1_ttl: int = 300  # 5 minutes
    l2_redis_enabled: bool = True
    l2_redis_ttl: int = 1800  # 30 minutes
    l3_db_enabled: bool = True
    l3_db_ttl: int = 3600  # 1 hour
    cache_warming_enabled: bool = True
    cache_analytics_enabled: bool = True


@dataclass
class ParallelConfig:
    """Parallel processing configuration"""
    max_workers: int = 4
    batch_size: int = 10
    streaming_enabled: bool = True
    progress_tracking_enabled: bool = True
    cancellation_enabled: bool = True


@dataclass
class SmartFilterConfig:
    """Smart filtering configuration"""
    relevance_scoring_enabled: bool = True
    context_compression_enabled: bool = True
    context_versioning_enabled: bool = True
    quality_metrics_enabled: bool = True
    max_context_items: int = 100


@dataclass
class CacheStats:
    """Cache statistics"""
    l1_hits: int = 0
    l1_misses: int = 0
    l2_hits: int = 0
    l2_misses: int = 0
    l3_hits: int = 0
    l3_misses: int = 0
    
    @property
    def hit_ratio(self) -> float:
        """Calculate overall hit ratio"""
        total_requests = self.l1_hits + self.l1_misses + self.l2_hits + self.l2_misses + self.l3_hits + self.l3_misses
        total_hits = self.l1_hits + self.l2_hits + self.l3_hits
        return total_hits / total_requests if total_requests > 0 else 0.0


class MultiLevelCache:
    """Multi-level cache implementation"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.l1_cache: Dict[str, Tuple[Any, float]] = {}
        self.l2_redis = None  # Would be Redis client in production
        self.l3_db = None  # Would be database connection in production
        self.stats = CacheStats()
        self.logger = logging.getLogger(__name__)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with fallback through levels"""
        # L1 Cache (Memory)
        if key in self.l1_cache:
            value, timestamp = self.l1_cache[key]
            if time.time() - timestamp < self.config.l1_ttl:
                self.stats.l1_hits += 1
                return value
            else:
                del self.l1_cache[key]
        
        self.stats.l1_misses += 1
        
        # L2 Cache (Redis)
        if self.config.l2_redis_enabled and self.l2_redis:
            try:
                value = await self._get_from_l2_cache(key)
                if value is not None:
                    self.stats.l2_hits += 1
                    # Promote to L1
                    await self._set_to_l1_cache(key, value)
                    return value
            except Exception as e:
                self.logger.warning(f"L2 cache error: {e}")
        
        self.stats.l2_misses += 1
        
        # L3 Cache (Database)
        if self.config.l3_db_enabled and self.l3_db:
            try:
                value = await self._get_from_l3_cache(key)
                if value is not None:
                    self.stats.l3_hits += 1
                    # Promote to L2 and L1
                    await self._set_to_l2_cache(key, value)
                    await self._set_to_l1_cache(key, value)
                    return value
            except Exception as e:
                self.logger.warning(f"L3 cache error: {e}")
        
        self.stats.l3_misses += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in all cache levels"""
        # Set in L1
        await self._set_to_l1_cache(key, value)
        
        # Set in L2 if enabled
        if self.config.l2_redis_enabled and self.l2_redis:
            try:
                await self._set_to_l2_cache(key, value, ttl or self.config.l2_redis_ttl)
            except Exception as e:
                self.logger.warning(f"L2 cache set error: {e}")
        
        # Set in L3 if enabled
        if self.config.l3_db_enabled and self.l3_db:
            try:
                await self._set_to_l3_cache(key, value, ttl or self.config.l3_db_ttl)
            except Exception as e:
                self.logger.warning(f"L3 cache set error: {e}")
    
    async def invalidate(self, key: str) -> None:
        """Invalidate key from all cache levels"""
        # Remove from L1
        self.l1_cache.pop(key, None)
        
        # Remove from L2
        if self.config.l2_redis_enabled and self.l2_redis:
            try:
                await self._invalidate_l2_cache(key)
            except Exception as e:
                self.logger.warning(f"L2 cache invalidation error: {e}")
        
        # Remove from L3
        if self.config.l3_db_enabled and self.l3_db:
            try:
                await self._invalidate_l3_cache(key)
            except Exception as e:
                self.logger.warning(f"L3 cache invalidation error: {e}")
    
    async def _get_from_l1_cache(self, key: str) -> Optional[Any]:
        """Get from L1 cache"""
        if key in self.l1_cache:
            value, timestamp = self.l1_cache[key]
            if time.time() - timestamp < self.config.l1_ttl:
                return value
            else:
                del self.l1_cache[key]
        return None
    
    async def _set_to_l1_cache(self, key: str, value: Any) -> None:
        """Set in L1 cache with size management"""
        # Manage cache size
        if len(self.l1_cache) >= self.config.l1_cache_size:
            # Remove oldest entry
            oldest_key = min(self.l1_cache.keys(), key=lambda k: self.l1_cache[k][1])
            del self.l1_cache[oldest_key]
        
        self.l1_cache[key] = (value, time.time())
    
    async def _get_from_l2_cache(self, key: str) -> Optional[Any]:
        """Get from L2 cache (Redis)"""
        # Mock implementation - would use Redis in production
        return None
    
    async def _set_to_l2_cache(self, key: str, value: Any, ttl: int) -> None:
        """Set in L2 cache (Redis)"""
        # Mock implementation - would use Redis in production
        pass
    
    async def _invalidate_l2_cache(self, key: str) -> None:
        """Invalidate L2 cache (Redis)"""
        # Mock implementation - would use Redis in production
        pass
    
    async def _get_from_l3_cache(self, key: str) -> Optional[Any]:
        """Get from L3 cache (Database)"""
        # Mock implementation - would use database in production
        return None
    
    async def _set_to_l3_cache(self, key: str, value: Any, ttl: int) -> None:
        """Set in L3 cache (Database)"""
        # Mock implementation - would use database in production
        pass
    
    async def _invalidate_l3_cache(self, key: str) -> None:
        """Invalidate L3 cache (Database)"""
        # Mock implementation - would use database in production
        pass
    
    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics"""
        return self.stats


class ParallelProcessor:
    """Parallel processing implementation"""
    
    def __init__(self, config: ParallelConfig):
        self.config = config
        self.workers: List[asyncio.Task] = []
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.progress_callbacks: Dict[str, callable] = {}
        self.cancellation_tokens: Dict[str, bool] = {}
        self.logger = logging.getLogger(__name__)
    
    async def process_parallel(self, tasks: List[Tuple[str, callable, Dict[str, Any]]]) -> Dict[str, Any]:
        """Process multiple tasks in parallel"""
        if not tasks:
            return {}
        
        # Create cancellation token for this batch
        batch_id = f"batch_{int(time.time())}"
        self.cancellation_tokens[batch_id] = False
        
        try:
            # Submit tasks to workers
            futures = []
            for task_id, func, kwargs in tasks:
                if self.cancellation_tokens[batch_id]:
                    break
                
                future = asyncio.create_task(self._execute_task(task_id, func, kwargs, batch_id))
                futures.append((task_id, future))
            
            # Wait for completion
            results = {}
            for task_id, future in futures:
                try:
                    result = await future
                    results[task_id] = result
                except Exception as e:
                    self.logger.error(f"Task {task_id} failed: {e}")
                    results[task_id] = None
            
            return results
        
        finally:
            # Clean up cancellation token
            self.cancellation_tokens.pop(batch_id, None)
    
    async def _execute_task(self, task_id: str, func: callable, kwargs: Dict[str, Any], batch_id: str) -> Any:
        """Execute a single task"""
        try:
            # Check cancellation
            if self.cancellation_tokens.get(batch_id, False):
                raise asyncio.CancelledError("Task cancelled")
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                result = func(**kwargs)
            
            # Update progress
            if self.config.progress_tracking_enabled:
                await self._update_progress(task_id, 1.0, "Completed")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Task {task_id} execution failed: {e}")
            raise
    
    async def _update_progress(self, task_id: str, progress: float, message: str) -> None:
        """Update progress for a task"""
        if task_id in self.progress_callbacks:
            try:
                await self.progress_callbacks[task_id](progress, message)
            except Exception as e:
                self.logger.warning(f"Progress callback failed: {e}")
    
    async def cancel_batch(self, batch_id: str) -> None:
        """Cancel a batch of tasks"""
        self.cancellation_tokens[batch_id] = True
    
    async def stream_processing(self, data_stream: AsyncGenerator[Dict[str, Any], None]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream processing for large datasets"""
        async for chunk in data_stream:
            if self.config.cancellation_enabled and any(self.cancellation_tokens.values()):
                break
            
            # Process chunk
            processed_chunk = await self._process_chunk(chunk)
            yield processed_chunk
    
    async def _process_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single chunk"""
        # Mock processing - would implement actual processing logic
        return {"processed": True, "chunk": chunk}


class SmartFilter:
    """Smart filtering implementation"""
    
    def __init__(self, config: SmartFilterConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def filter_by_relevance(self, items: List[Dict[str, Any]], threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Filter items by relevance score"""
        if not self.config.relevance_scoring_enabled:
            return items
        
        filtered_items = []
        for item in items:
            relevance_score = await self._calculate_relevance_score(item)
            if relevance_score >= threshold:
                filtered_items.append({**item, "relevance_score": relevance_score})
        
        return filtered_items
    
    async def _calculate_relevance_score(self, item: Dict[str, Any]) -> float:
        """Calculate relevance score for an item"""
        # Mock implementation - would use ML models in production
        if "relevance" in item:
            return item["relevance"]
        
        # Simple heuristic based on item type and content
        score = 0.5  # Base score
        
        if item.get("type") == "file":
            if item.get("path", "").endswith((".py", ".js", ".ts")):
                score += 0.3
            elif item.get("path", "").endswith((".md", ".txt")):
                score += 0.1
        
        return min(score, 1.0)
    
    async def compress_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compress large context data"""
        if not self.config.context_compression_enabled:
            return context
        
        compressed = {}
        for key, value in context.items():
            if isinstance(value, list) and len(value) > 10:
                # Compress large lists
                compressed[f"{key}_summary"] = f"{len(value)} items"
                compressed[f"{key}_sample"] = value[:5]  # Keep first 5 items
            elif isinstance(value, dict) and len(str(value)) > 1000:
                # Compress large dictionaries
                compressed[f"{key}_summary"] = f"Large {key} data"
                compressed[f"{key}_keys"] = list(value.keys())[:10]
            else:
                compressed[key] = value
        
        return compressed
    
    async def calculate_context_diff(self, old_context: Dict[str, Any], new_context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Calculate diff between two contexts"""
        if not self.config.context_versioning_enabled:
            return {"added": [], "modified": [], "removed": []}
        
        old_keys = set(old_context.keys())
        new_keys = set(new_context.keys())
        
        added = list(new_keys - old_keys)
        removed = list(old_keys - new_keys)
        modified = []
        
        for key in old_keys & new_keys:
            if old_context[key] != new_context[key]:
                modified.append(key)
        
        return {
            "added": added,
            "modified": modified,
            "removed": removed
        }
    
    async def assess_quality(self, context: Dict[str, Any]) -> ContextQualityMetrics:
        """Assess context quality"""
        if not self.config.quality_metrics_enabled:
            return ContextQualityMetrics(
                completeness=0.8,
                accuracy=0.9,
                relevance=0.7,
                freshness=0.6,
                overall_score=0.75
            )
        
        # Calculate quality metrics
        completeness = await self._calculate_completeness(context)
        accuracy = await self._calculate_accuracy(context)
        relevance = await self._calculate_relevance(context)
        freshness = await self._calculate_freshness(context)
        
        overall_score = (completeness + accuracy + relevance + freshness) / 4
        
        return ContextQualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            relevance=relevance,
            freshness=freshness,
            overall_score=overall_score
        )
    
    async def _calculate_completeness(self, context: Dict[str, Any]) -> float:
        """Calculate completeness score"""
        required_fields = ["project_structure", "dependencies", "architecture"]
        present_fields = sum(1 for field in required_fields if field in context and context[field])
        return present_fields / len(required_fields)
    
    async def _calculate_accuracy(self, context: Dict[str, Any]) -> float:
        """Calculate accuracy score"""
        # Mock implementation - would use validation logic
        return 0.9
    
    async def _calculate_relevance(self, context: Dict[str, Any]) -> float:
        """Calculate relevance score"""
        # Mock implementation - would use relevance scoring
        return 0.7
    
    async def _calculate_freshness(self, context: Dict[str, Any]) -> float:
        """Calculate freshness score"""
        # Mock implementation - would check timestamps
        return 0.6


class OptimizedContextAggregator(ContextAggregator):
    """Optimized Context Aggregator with advanced features"""
    
    def __init__(self, config: ContextAggregatorConfig, 
                 cache_config: CacheConfig,
                 parallel_config: ParallelConfig,
                 smart_filter_config: SmartFilterConfig):
        super().__init__(config)
        
        self.cache_config = cache_config
        self.parallel_config = parallel_config
        self.smart_filter_config = smart_filter_config
        
        # Initialize components
        self.cache = MultiLevelCache(cache_config)
        self.parallel_processor = ParallelProcessor(parallel_config)
        self.smart_filter = SmartFilter(smart_filter_config)
        
        self.logger = logging.getLogger(__name__)
    
    async def aggregate_context(self, request: ContextAggregationRequest) -> ContextAggregationResponse:
        """Aggregate context with optimization features"""
        start_time = time.time()
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(request)
            
            # Check cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                self.logger.info(f"Cache hit for key: {cache_key}")
                return ContextAggregationResponse(**cached_result)
            
            # Gather context in parallel
            context_data = await self._gather_context_parallel({
                "project_id": request.project_id,
                "sources": request.sources,
                "include_dependencies": request.include_dependencies,
                "include_architecture": request.include_architecture
            })
            
            # Apply smart filtering
            if self.smart_filter_config.relevance_scoring_enabled:
                context_data = await self._apply_smart_filtering(context_data)
            
            # Create unified context
            unified_context = UnifiedContext(
                project_id=request.project_id,
                project_structure=context_data.get("project_structure", {}),
                dependencies=context_data.get("dependencies", {}),
                architecture=context_data.get("architecture", {}),
                quality_score=0.8
            )
            
            # Assess quality
            quality_metrics = await self.smart_filter.assess_quality(context_data)
            
            # Create response
            response = ContextAggregationResponse(
                unified_context=unified_context,
                quality_metrics=quality_metrics,
                processing_time=time.time() - start_time,
                success=True
            )
            
            # Cache result
            await self.cache.set(cache_key, response.dict())
            
            return response
        
        except Exception as e:
            self.logger.error(f"Context aggregation failed: {e}")
            return ContextAggregationResponse(
                unified_context=None,
                quality_metrics=None,
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def _gather_context_parallel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Gather context from multiple sources in parallel"""
        tasks = []
        
        # Add tasks based on sources
        if ContextSource.PROJECT_STRUCTURE in params.get("sources", []):
            tasks.append(("project_structure", self._gather_project_context, {"project_id": params["project_id"]}))
        
        if params.get("include_dependencies", False):
            tasks.append(("dependencies", self._gather_dependencies_context, {"project_id": params["project_id"]}))
        
        if params.get("include_architecture", False):
            tasks.append(("architecture", self._gather_architecture_context, {"project_id": params["project_id"]}))
        
        # Process in parallel
        results = await self.parallel_processor.process_parallel(tasks)
        
        return results
    
    async def _apply_smart_filtering(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply smart filtering to context data"""
        filtered_data = {}
        
        for key, value in context_data.items():
            if isinstance(value, list):
                # Filter list items by relevance
                filtered_items = await self.smart_filter.filter_by_relevance(value)
                filtered_data[key] = filtered_items
            else:
                filtered_data[key] = value
        
        # Compress if needed
        if self.smart_filter_config.context_compression_enabled:
            filtered_data = await self.smart_filter.compress_context(filtered_data)
        
        return filtered_data
    
    def _generate_cache_key(self, request: ContextAggregationRequest) -> str:
        """Generate cache key for request"""
        key_data = {
            "project_id": request.project_id,
            "sources": [s.value for s in request.sources],
            "include_dependencies": request.include_dependencies,
            "include_architecture": request.include_architecture
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def warm_cache(self, project_id: str) -> None:
        """Warm cache for a project"""
        if not self.cache_config.cache_warming_enabled:
            return
        
        # Create common requests for warming
        common_requests = [
            ContextAggregationRequest(
                project_id=project_id,
                sources=[ContextSource.PROJECT_STRUCTURE],
                include_dependencies=True,
                include_architecture=False
            ),
            ContextAggregationRequest(
                project_id=project_id,
                sources=[ContextSource.PROJECT_STRUCTURE],
                include_dependencies=True,
                include_architecture=True
            )
        ]
        
        # Warm cache
        for request in common_requests:
            try:
                await self.aggregate_context(request)
            except Exception as e:
                self.logger.warning(f"Cache warming failed for {project_id}: {e}")
    
    async def get_cache_analytics(self) -> Dict[str, Any]:
        """Get cache analytics"""
        if not self.cache_config.cache_analytics_enabled:
            return {}
        
        stats = self.cache.get_cache_stats()
        
        return {
            "hit_ratio": stats.hit_ratio,
            "l1_hits": stats.l1_hits,
            "l1_misses": stats.l1_misses,
            "l2_hits": stats.l2_hits,
            "l2_misses": stats.l2_misses,
            "l3_hits": stats.l3_hits,
            "l3_misses": stats.l3_misses,
            "total_requests": stats.l1_hits + stats.l1_misses + stats.l2_hits + stats.l2_misses + stats.l3_hits + stats.l3_misses
        }
    
    async def benchmark_performance(self, operation: str) -> Dict[str, Any]:
        """Benchmark performance of operations"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Execute operation
        if operation == "aggregate_context":
            request = ContextAggregationRequest(
                project_id="benchmark_test",
                sources=[ContextSource.PROJECT_STRUCTURE],
                include_dependencies=True,
                include_architecture=True
            )
            await self.aggregate_context(request)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        return {
            "operation": operation,
            "duration": end_time - start_time,
            "memory_usage": end_memory - start_memory,
            "cpu_usage": 0.3  # Mock value
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the aggregator"""
        return {
            "status": "healthy",
            "cache_status": "operational",
            "processing_status": "operational",
            "memory_usage": self._get_memory_usage(),
            "active_workers": len(self.parallel_processor.workers)
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage (mock implementation)"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
