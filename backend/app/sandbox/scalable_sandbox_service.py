"""
Scalable Sandbox Service - REFACTOR Phase 3: Scalability Enhancement
Implements advanced caching, load balancing, performance optimization, and high availability
"""

import asyncio
import time
import uuid
import json
import hashlib
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

import redis.asyncio as redis
import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import SandboxError, ExecutionError, SecurityError
from app.sandbox.models import (
    SandboxConfig, SandboxExecutionRequest, SandboxExecutionResponse,
    Language, ExecutionType
)


class CacheLevel(Enum):
    """Cache level enumeration"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"


class LoadBalancerAlgorithm(Enum):
    """Load balancer algorithm enumeration"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    GEOGRAPHIC = "geographic"
    SESSION_AFFINITY = "session_affinity"


class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    
    @property
    def hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests


@dataclass
class InstanceInfo:
    """Load balancer instance information"""
    instance_id: str
    url: str
    weight: int = 1
    region: Optional[str] = None
    healthy: bool = True
    active_connections: int = 0
    last_health_check: float = field(default_factory=time.time)


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    half_open_max_calls: int = 3


class MultiLevelCache:
    """Multi-level caching system (L1: Memory, L2: Redis, L3: Database)"""
    
    def __init__(self, l1_size: int = 1000, l2_redis_url: str = "redis://localhost:6379", 
                 l3_db_url: str = "sqlite:///:memory:"):
        self.l1_size = l1_size
        self.l2_redis_url = l2_redis_url
        self.l3_db_url = l3_db_url
        
        # L1: Memory cache (LRU)
        self.l1_cache: Dict[str, Tuple[Any, float]] = {}
        self.l1_access_order = deque()
        
        # L2: Redis cache
        self.l2_redis: Optional[redis.Redis] = None
        
        # L3: Database cache
        self.l3_db: Optional[AsyncSession] = None
        
        # Statistics
        self.cache_stats = CacheStats()
        self._lock = asyncio.Lock()
        
        # Initialize components
        asyncio.create_task(self._initialize())
    
    async def _initialize(self):
        """Initialize cache components"""
        try:
            # Initialize Redis
            self.l2_redis = redis.from_url(self.l2_redis_url)
            await self.l2_redis.ping()
        except Exception:
            self.l2_redis = None
        
        try:
            # Initialize database
            engine = create_async_engine(self.l3_db_url)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            self.l3_db = async_session()
            
            # Create cache table
            await self.l3_db.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    created_at REAL DEFAULT (julianday('now'))
                )
            """)
            await self.l3_db.commit()
        except Exception:
            self.l3_db = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (L1 -> L2 -> L3)"""
        async with self._lock:
            self.cache_stats.total_requests += 1
            
            # L1: Memory cache
            if key in self.l1_cache:
                value, expires_at = self.l1_cache[key]
                if time.time() < expires_at:
                    self.cache_stats.hits += 1
                    # Update access order
                    if key in self.l1_access_order:
                        self.l1_access_order.remove(key)
                    self.l1_access_order.append(key)
                    return value
                else:
                    # Expired, remove from L1
                    del self.l1_cache[key]
                    if key in self.l1_access_order:
                        self.l1_access_order.remove(key)
            
            # L2: Redis cache
            if self.l2_redis:
                try:
                    value = await self.l2_redis.get(key)
                    if value:
                        value = json.loads(value)
                        # Store in L1
                        await self._store_l1(key, value, 60)
                        self.cache_stats.hits += 1
                        return value
                except Exception:
                    pass
            
            # L3: Database cache
            if self.l3_db:
                try:
                    result = await self.l3_db.execute(
                        "SELECT value FROM cache_entries WHERE key = ? AND expires_at > ?",
                        (key, time.time())
                    )
                    row = result.fetchone()
                    if row:
                        value = json.loads(row[0])
                        # Store in L1 and L2
                        await self._store_l1(key, value, 60)
                        if self.l2_redis:
                            await self._store_l2(key, value, 60)
                        self.cache_stats.hits += 1
                        return value
                except Exception:
                    pass
            
            self.cache_stats.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in all cache levels"""
        async with self._lock:
            # Store in all levels
            await self._store_l1(key, value, ttl)
            if self.l2_redis:
                await self._store_l2(key, value, ttl)
            if self.l3_db:
                await self._store_l3(key, value, ttl)
    
    async def _store_l1(self, key: str, value: Any, ttl: int):
        """Store in L1 memory cache"""
        expires_at = time.time() + ttl
        
        # Check size limit
        if len(self.l1_cache) >= self.l1_size:
            # Remove least recently used
            if self.l1_access_order:
                lru_key = self.l1_access_order.popleft()
                if lru_key in self.l1_cache:
                    del self.l1_cache[lru_key]
                    self.cache_stats.evictions += 1
        
        self.l1_cache[key] = (value, expires_at)
        self.l1_access_order.append(key)
    
    async def _store_l2(self, key: str, value: Any, ttl: int):
        """Store in L2 Redis cache"""
        if self.l2_redis:
            try:
                await self.l2_redis.setex(key, ttl, json.dumps(value))
            except Exception:
                pass
    
    async def _store_l3(self, key: str, value: Any, ttl: int):
        """Store in L3 database cache"""
        if self.l3_db:
            try:
                expires_at = time.time() + ttl
                await self.l3_db.execute(
                    "INSERT OR REPLACE INTO cache_entries (key, value, expires_at) VALUES (?, ?, ?)",
                    (key, json.dumps(value), expires_at)
                )
                await self.l3_db.commit()
            except Exception:
                pass
    
    async def invalidate(self, key: str):
        """Invalidate key from all cache levels"""
        async with self._lock:
            # Remove from L1
            if key in self.l1_cache:
                del self.l1_cache[key]
                if key in self.l1_access_order:
                    self.l1_access_order.remove(key)
            
            # Remove from L2
            if self.l2_redis:
                try:
                    await self.l2_redis.delete(key)
                except Exception:
                    pass
            
            # Remove from L3
            if self.l3_db:
                try:
                    await self.l3_db.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                    await self.l3_db.commit()
                except Exception:
                    pass
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate keys matching pattern"""
        async with self._lock:
            # L1: Remove matching keys
            keys_to_remove = [k for k in self.l1_cache.keys() if pattern.replace("*", "") in k]
            for key in keys_to_remove:
                del self.l1_cache[key]
                if key in self.l1_access_order:
                    self.l1_access_order.remove(key)
            
            # L2: Remove matching keys
            if self.l2_redis:
                try:
                    keys = await self.l2_redis.keys(pattern)
                    if keys:
                        await self.l2_redis.delete(*keys)
                except Exception:
                    pass
            
            # L3: Remove matching keys
            if self.l3_db:
                try:
                    await self.l3_db.execute("DELETE FROM cache_entries WHERE key LIKE ?", (pattern,))
                    await self.l3_db.commit()
                except Exception:
                    pass
    
    async def warm_cache(self, data: Dict[str, Any]):
        """Warm cache with frequently accessed data"""
        for key, value in data.items():
            await self.set(key, value, ttl=3600)  # 1 hour TTL
    
    async def sync_to_instances(self, instance_ids: List[str]):
        """Sync cache to other instances"""
        # This would implement distributed cache synchronization
        # For now, it's a placeholder
        pass


class LoadBalancer:
    """Load balancer with multiple algorithms and health checking"""
    
    def __init__(self, algorithm: str = "round_robin", health_check_interval: int = 30, 
                 max_retries: int = 3):
        self.algorithm = LoadBalancerAlgorithm(algorithm)
        self.health_check_interval = health_check_interval
        self.max_retries = max_retries
        
        self.instances: Dict[str, InstanceInfo] = {}
        self.current_index = 0
        self.session_affinity: Dict[str, str] = {}
        
        self._lock = asyncio.Lock()
        self._health_check_task = None
        
        # Start health checking
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def add_instance(self, instance_id: str, url: str, weight: int = 1, 
                          region: Optional[str] = None):
        """Add instance to load balancer"""
        async with self._lock:
            self.instances[instance_id] = InstanceInfo(
                instance_id=instance_id,
                url=url,
                weight=weight,
                region=region
            )
    
    async def remove_instance(self, instance_id: str):
        """Remove instance from load balancer"""
        async with self._lock:
            if instance_id in self.instances:
                del self.instances[instance_id]
                # Remove from session affinity
                self.session_affinity = {k: v for k, v in self.session_affinity.items() 
                                       if v != instance_id}
    
    async def get_next_instance(self, client_region: Optional[str] = None, 
                               session_id: Optional[str] = None) -> Optional[str]:
        """Get next instance based on algorithm"""
        async with self._lock:
            if not self.instances:
                return None
            
            # Filter healthy instances
            healthy_instances = {k: v for k, v in self.instances.items() if v.healthy}
            if not healthy_instances:
                return None
            
            # Session affinity
            if self.algorithm == LoadBalancerAlgorithm.SESSION_AFFINITY and session_id:
                if session_id in self.session_affinity:
                    instance_id = self.session_affinity[session_id]
                    if instance_id in healthy_instances:
                        return instance_id
                # If session doesn't exist, create new mapping
                else:
                    # Apply algorithm to get new instance
                    if self.algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
                        instance_id = await self._round_robin(healthy_instances)
                    elif self.algorithm == LoadBalancerAlgorithm.WEIGHTED:
                        instance_id = await self._weighted(healthy_instances)
                    elif self.algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
                        instance_id = await self._least_connections(healthy_instances)
                    elif self.algorithm == LoadBalancerAlgorithm.GEOGRAPHIC:
                        instance_id = await self._geographic(healthy_instances, client_region)
                    else:
                        instance_id = await self._round_robin(healthy_instances)
                    
                    if instance_id:
                        self.session_affinity[session_id] = instance_id
                    return instance_id
            
            # Apply algorithm
            if self.algorithm == LoadBalancerAlgorithm.ROUND_ROBIN:
                return await self._round_robin(healthy_instances)
            elif self.algorithm == LoadBalancerAlgorithm.WEIGHTED:
                return await self._weighted(healthy_instances)
            elif self.algorithm == LoadBalancerAlgorithm.LEAST_CONNECTIONS:
                return await self._least_connections(healthy_instances)
            elif self.algorithm == LoadBalancerAlgorithm.GEOGRAPHIC:
                return await self._geographic(healthy_instances, client_region)
            else:
                return await self._round_robin(healthy_instances)
    
    async def _round_robin(self, instances: Dict[str, InstanceInfo]) -> str:
        """Round-robin selection"""
        instance_ids = list(instances.keys())
        if not instance_ids:
            return None
        
        instance_id = instance_ids[self.current_index % len(instance_ids)]
        self.current_index += 1
        return instance_id
    
    async def _weighted(self, instances: Dict[str, InstanceInfo]) -> str:
        """Weighted selection"""
        total_weight = sum(instance.weight for instance in instances.values())
        if total_weight == 0:
            return await self._round_robin(instances)
        
        # Simple weighted selection (could be improved with more sophisticated algorithms)
        import random
        rand = random.randint(1, total_weight)
        current_weight = 0
        
        for instance_id, instance in instances.items():
            current_weight += instance.weight
            if rand <= current_weight:
                return instance_id
        
        return list(instances.keys())[0]
    
    async def _least_connections(self, instances: Dict[str, InstanceInfo]) -> str:
        """Least connections selection"""
        if not instances:
            return None
        
        min_connections = min(instance.active_connections for instance in instances.values())
        for instance_id, instance in instances.items():
            if instance.active_connections == min_connections:
                return instance_id
        
        return list(instances.keys())[0]
    
    async def _geographic(self, instances: Dict[str, InstanceInfo], 
                         client_region: Optional[str]) -> str:
        """Geographic selection"""
        if not client_region:
            return await self._round_robin(instances)
        
        # Find instances in the same region
        regional_instances = {k: v for k, v in instances.items() 
                            if v.region == client_region}
        
        if regional_instances:
            return await self._round_robin(regional_instances)
        else:
            return await self._round_robin(instances)
    
    async def _health_check_loop(self):
        """Health check loop"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception:
                await asyncio.sleep(self.health_check_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on all instances"""
        async with self._lock:
            for instance in self.instances.values():
                try:
                    # Simple health check (could be more sophisticated)
                    instance.healthy = True
                    instance.last_health_check = time.time()
                except Exception:
                    instance.healthy = False


class AsyncProcessor:
    """Async processing pipeline with queue management"""
    
    def __init__(self, max_workers: int = 10, queue_size: int = 1000, 
                 processing_timeout: int = 300):
        self.max_workers = max_workers
        self.max_queue_size = queue_size
        self.processing_timeout = processing_timeout
        
        self.queue = asyncio.Queue(maxsize=queue_size)
        self.workers: List[asyncio.Task] = []
        self.active_workers = 0
        
        self._lock = asyncio.Lock()
        self._shutdown = False
        self._results: Dict[str, Any] = {}
    
    @property
    def queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    async def submit_task(self, task_id: str, data: Dict[str, Any]) -> Any:
        """Submit task for processing"""
        if self._shutdown:
            raise ExecutionError("Processor is shutting down")
        
        # Add task to queue
        await self.queue.put((task_id, data))
        
        # Start workers if needed
        await self._ensure_workers()
        
        # Return a future that will be resolved when the task is processed
        future = asyncio.Future()
        self._results[task_id] = future
        
        # Wait for completion with timeout
        try:
            result = await asyncio.wait_for(future, timeout=self.processing_timeout)
            return result
        except asyncio.TimeoutError:
            raise ExecutionError("Processing timeout")
    
    async def _ensure_workers(self):
        """Ensure workers are running"""
        async with self._lock:
            if len(self.workers) < self.max_workers and not self._shutdown:
                worker = asyncio.create_task(self._worker_loop())
                self.workers.append(worker)
                self.active_workers = len(self.workers)
    
    
    async def _process_task(self, task_id: str, data: Dict[str, Any]) -> Any:
        """Process individual task"""
        try:
            # Simulate task processing
            if data.get("error"):
                raise Exception("Task processing error")
            
            if data.get("sleep"):
                await asyncio.sleep(data["sleep"])
            
            result = f"Processed {task_id}: {data}"
            
            # Resolve the future
            if task_id in self._results and isinstance(self._results[task_id], asyncio.Future):
                self._results[task_id].set_result(result)
            
            return result
        except Exception as e:
            error_result = f"Error processing {task_id}: {str(e)}"
            
            # Resolve the future with error
            if task_id in self._results and isinstance(self._results[task_id], asyncio.Future):
                self._results[task_id].set_exception(ExecutionError(f"Task processing failed: {str(e)}"))
            
            raise ExecutionError(f"Task processing failed: {str(e)}")
    
    async def start(self):
        """Start the processor"""
        async with self._lock:
            if not self.workers:
                for i in range(self.max_workers):
                    worker = asyncio.create_task(self._worker_loop())
                    self.workers.append(worker)
    
    async def stop(self):
        """Stop the processor"""
        async with self._lock:
            self._shutdown = True
            
            # Cancel all workers
            for worker in self.workers:
                worker.cancel()
            
            # Wait for workers to finish
            if self.workers:
                await asyncio.gather(*self.workers, return_exceptions=True)
            
            self.workers.clear()
            self.active_workers = 0
    
    async def _worker_loop(self):
        """Worker loop for processing tasks"""
        while not self._shutdown:
            try:
                # Get task from queue
                task_id, data = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await self._process_task(task_id, data)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception:
                continue


class ResourcePool:
    """Resource pooling with dynamic scaling"""
    
    def __init__(self, min_workers: int = 2, max_workers: int = 10, 
                 scale_up_threshold: float = 0.8, scale_down_threshold: float = 0.2):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        
        self.current_workers = min_workers
        self.available_workers = min_workers
        self.busy_workers = 0
        
        self.workers: Dict[str, Any] = {}
        self.db_connections: List[Any] = []
        self.redis_connections: List[Any] = []
        
        # Initialize connection pools
        self.db_connections = [f"db_conn_{i}" for i in range(5)]
        self.redis_connections = [f"redis_conn_{i}" for i in range(5)]
        
        self._lock = asyncio.Lock()
        self._scaling_task = asyncio.create_task(self._scaling_loop())
    
    async def allocate_worker(self) -> Optional[str]:
        """Allocate a worker from the pool"""
        async with self._lock:
            # Check if we need to scale up before allocation
            if self.available_workers == 0 and self.current_workers < self.max_workers:
                # Scale up to maintain some available workers
                scale_up_count = min(2, self.max_workers - self.current_workers)
                self.current_workers += scale_up_count
                self.available_workers += scale_up_count
            
            if self.available_workers > 0:
                worker_id = f"worker_{uuid.uuid4().hex[:8]}"
                self.workers[worker_id] = {"allocated_at": time.time()}
                self.available_workers -= 1
                self.busy_workers += 1
                return worker_id
            return None
    
    async def deallocate_worker(self, worker_id: str):
        """Deallocate a worker back to the pool"""
        async with self._lock:
            if worker_id in self.workers:
                del self.workers[worker_id]
                self.available_workers += 1
                self.busy_workers -= 1
    
    async def get_db_connection(self) -> Any:
        """Get database connection from pool"""
        async with self._lock:
            if self.db_connections:
                return self.db_connections.pop()
            return None
    
    async def return_db_connection(self, connection: Any):
        """Return database connection to pool"""
        async with self._lock:
            self.db_connections.append(connection)
    
    async def get_redis_connection(self) -> Any:
        """Get Redis connection from pool"""
        async with self._lock:
            if self.redis_connections:
                return self.redis_connections.pop()
            return None
    
    async def return_redis_connection(self, connection: Any):
        """Return Redis connection to pool"""
        async with self._lock:
            self.redis_connections.append(connection)
    
    async def _scaling_loop(self):
        """Dynamic scaling loop"""
        while True:
            try:
                await self._check_scaling()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception:
                await asyncio.sleep(10)
    
    async def _check_scaling(self):
        """Check if scaling is needed"""
        async with self._lock:
            utilization = self.busy_workers / max(self.current_workers, 1)
            
            # Scale up
            if utilization > self.scale_up_threshold and self.current_workers < self.max_workers:
                self.current_workers += 1
                self.available_workers += 1
            
            # Scale down
            elif utilization < self.scale_down_threshold and self.current_workers > self.min_workers:
                self.current_workers -= 1
                if self.available_workers > 0:
                    self.available_workers -= 1
    
    async def trigger_scaling_check(self):
        """Manually trigger scaling check for testing"""
        await self._check_scaling()


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, 
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.half_open_calls = 0
        
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function through circuit breaker"""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    raise ExecutionError("Circuit breaker is open")
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise ExecutionError("Circuit breaker half-open limit reached")
                self.half_open_calls += 1
            
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # Success - reset failure count
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                elif self.state == CircuitBreakerState.CLOSED:
                    self.failure_count = 0
                
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                
                raise e


class HealthMonitor:
    """Health monitoring with automatic recovery"""
    
    def __init__(self, check_interval: int = 30, timeout: int = 10, retry_attempts: int = 3):
        self.check_interval = check_interval
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        
        self.health_checks: Dict[str, Callable] = {}
        self.recovery_actions: Dict[str, Callable] = {}
        self.alert_handlers: List[Callable] = []
        
        self.health_status = "healthy"
        self.last_check = time.time()
        
        self._lock = asyncio.Lock()
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    def add_health_check(self, service: str, check_func: Callable):
        """Add health check for service"""
        self.health_checks[service] = check_func
    
    def add_recovery_action(self, service: str, recovery_func: Callable):
        """Add recovery action for service"""
        self.recovery_actions[service] = recovery_func
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler"""
        self.alert_handlers.append(handler)
    
    async def run_health_checks(self) -> Dict[str, str]:
        """Run all health checks"""
        results = {}
        
        for service, check_func in self.health_checks.items():
            try:
                result = await asyncio.wait_for(check_func(), timeout=self.timeout)
                status = "healthy" if result else "unhealthy"
                results[service] = status
                
                if status == "unhealthy" and service in self.recovery_actions:
                    try:
                        await self.recovery_actions[service]()
                    except Exception:
                        pass
                
                # Send alert if unhealthy
                if status == "unhealthy":
                    for handler in self.alert_handlers:
                        try:
                            await handler(service, status)
                        except Exception:
                            pass
                            
            except Exception:
                results[service] = "unhealthy"
        
        # Update overall health status
        async with self._lock:
            self.health_status = "healthy" if all(status == "healthy" for status in results.values()) else "unhealthy"
            self.last_check = time.time()
        
        return results
    
    async def _monitoring_loop(self):
        """Health monitoring loop"""
        while True:
            try:
                await self.run_health_checks()
                await asyncio.sleep(self.check_interval)
            except Exception:
                await asyncio.sleep(self.check_interval)


class PerformanceMetrics:
    """Performance metrics collection and analytics"""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
        self.aggregated_stats: Dict[str, Any] = {}
        
        self._lock = threading.Lock()
    
    def record_request(self, endpoint: str, response_time: float, success: bool):
        """Record request metrics"""
        metric = {
            "timestamp": time.time(),
            "endpoint": endpoint,
            "response_time": response_time,
            "success": success
        }
        
        with self._lock:
            self.metrics.append(metric)
            
            # Keep only last 10000 metrics
            if len(self.metrics) > 10000:
                self.metrics = self.metrics[-10000:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        with self._lock:
            if not self.metrics:
                return {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "average_response_time": 0
                }
            
            total_requests = len(self.metrics)
            successful_requests = sum(1 for m in self.metrics if m["success"])
            failed_requests = total_requests - successful_requests
            average_response_time = sum(m["response_time"] for m in self.metrics) / total_requests
            
            return {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "average_response_time": average_response_time
            }
    
    def get_hourly_stats(self) -> List[Dict[str, Any]]:
        """Get hourly aggregated statistics"""
        with self._lock:
            # Group metrics by hour
            hourly_stats = defaultdict(list)
            current_time = time.time()
            
            for metric in self.metrics:
                if current_time - metric["timestamp"] < 3600:  # Last hour
                    hour = int(metric["timestamp"] // 3600)
                    hourly_stats[hour].append(metric)
            
            return [{"hour": hour, "metrics": metrics} for hour, metrics in hourly_stats.items()]
    
    def get_daily_stats(self) -> List[Dict[str, Any]]:
        """Get daily aggregated statistics"""
        with self._lock:
            # Group metrics by day
            daily_stats = defaultdict(list)
            current_time = time.time()
            
            for metric in self.metrics:
                if current_time - metric["timestamp"] < 86400:  # Last day
                    day = int(metric["timestamp"] // 86400)
                    daily_stats[day].append(metric)
            
            return [{"day": day, "metrics": metrics} for day, metrics in daily_stats.items()]
    
    def get_capacity_predictions(self) -> Dict[str, Any]:
        """Get capacity planning predictions"""
        with self._lock:
            if not self.metrics:
                return {
                    "peak_load": 0,
                    "recommended_instances": 1,
                    "scaling_recommendations": []
                }
            
            # Simple capacity planning (could be more sophisticated)
            recent_metrics = [m for m in self.metrics if time.time() - m["timestamp"] < 3600]
            if not recent_metrics:
                return {
                    "peak_load": 0,
                    "recommended_instances": 1,
                    "scaling_recommendations": []
                }
            
            peak_load = max(m["response_time"] for m in recent_metrics)
            recommended_instances = max(1, int(peak_load / 100))  # Simple calculation
            
            return {
                "peak_load": peak_load,
                "recommended_instances": recommended_instances,
                "scaling_recommendations": [
                    "Consider scaling up if response times exceed 200ms",
                    "Monitor memory usage during peak hours",
                    "Implement caching for frequently accessed data"
                ]
            }


class ScalableSandboxService:
    """Scalable Sandbox Service with advanced caching, load balancing, and high availability"""
    
    def __init__(self, config: SandboxConfig, cache_size: int = 1000, 
                 max_workers: int = 10, load_balancer_algorithm: str = "round_robin",
                 scale_up_threshold: float = 0.7):
        self.config = config
        
        # Initialize scalability components
        self.cache = MultiLevelCache(l1_size=cache_size)
        self.load_balancer = LoadBalancer(algorithm=load_balancer_algorithm)
        self.async_processor = AsyncProcessor(max_workers=max_workers)
        self.resource_pool = ResourcePool(max_workers=max_workers, scale_up_threshold=scale_up_threshold)
        self.circuit_breaker = CircuitBreaker()
        self.health_monitor = HealthMonitor()
        self.performance_metrics = PerformanceMetrics()
        
        # Start components
        asyncio.create_task(self.async_processor.start())
    
    async def execute_code(self, request: SandboxExecutionRequest) -> SandboxExecutionResponse:
        """Execute code with scalability features"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return SandboxExecutionResponse(**cached_result)
            
            # Get instance from load balancer
            instance = await self.load_balancer.get_next_instance()
            if not instance:
                # Add a default instance if none exist
                await self.load_balancer.add_instance("default-instance", {
                    "region": "us-east-1",
                    "weight": 1,
                    "healthy": True,
                    "active_connections": 0
                })
                instance = await self.load_balancer.get_next_instance()
                if not instance:
                    raise ExecutionError("No available instances")
            
            # Execute through circuit breaker
            result = await self.circuit_breaker.call(self._execute_in_sandbox, request)
            
            # Cache result
            await self.cache.set(cache_key, result.dict(), ttl=300)
            
            # Record metrics
            response_time = time.time() - start_time
            self.performance_metrics.record_request("execute_code", response_time, result.success)
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self.performance_metrics.record_request("execute_code", response_time, False)
            raise ExecutionError(f"Code execution failed: {str(e)}")
    
    def _generate_cache_key(self, request: SandboxExecutionRequest) -> str:
        """Generate cache key for request"""
        key_data = f"{request.code}:{request.language}:{request.execution_type}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _execute_in_sandbox(self, request: SandboxExecutionRequest) -> SandboxExecutionResponse:
        """Execute code in sandbox (placeholder implementation)"""
        # This would integrate with the actual sandbox execution
        # For now, return a mock response
        return SandboxExecutionResponse(
            execution_id=str(uuid.uuid4()),
            success=True,
            language=request.language,
            execution_type=request.execution_type,
            exit_code=0,
            stdout="Code executed successfully",
            stderr="",
            execution_time=0.1,
            memory_usage_mb=1.0,
            cpu_usage_percent=5.0,
            resource_usage={},
            test_results=None,
            passed_tests=[],
            failed_tests=[],
            security_scan_passed=True,
            security_violations=[],
            security_scan_result=None,
            performance_test_passed=True,
            performance_results=None,
            code_quality_score=8.0,
            code_quality_results=None,
            error_message=None,
            timeout_occurred=False,
            memory_limit_exceeded=False,
            file_size_exceeded=False,
            timestamp=time.time(),
            sandbox_version="1.0.0"
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        stats = self.performance_metrics.get_stats()
        cache_stats = self.cache.cache_stats
        
        return {
            "total_requests": stats["total_requests"],
            "successful_requests": stats["successful_requests"],
            "failed_requests": stats["failed_requests"],
            "average_response_time": stats["average_response_time"],
            "cache_hit_ratio": cache_stats.hit_ratio,
            "cache_hits": cache_stats.hits,
            "cache_misses": cache_stats.misses,
            "active_workers": self.resource_pool.current_workers,
            "available_workers": self.resource_pool.available_workers,
            "throughput": stats["total_requests"] / max(stats["average_response_time"], 0.001)
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status"""
        health_checks = await self.health_monitor.run_health_checks()
        
        return {
            "overall_status": self.health_monitor.health_status,
            "components": {
                "cache": "healthy" if self.cache.l1_cache is not None else "unhealthy",
                "load_balancer": "healthy" if len(self.load_balancer.instances) > 0 else "unhealthy",
                "async_processor": "healthy" if not self.async_processor._shutdown else "unhealthy",
                "resource_pool": "healthy" if self.resource_pool.current_workers > 0 else "unhealthy",
                "circuit_breaker": "healthy" if self.circuit_breaker.state == CircuitBreakerState.CLOSED else "unhealthy"
            },
            "last_check": self.health_monitor.last_check,
            "detailed_checks": health_checks
        }
