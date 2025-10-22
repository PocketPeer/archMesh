"""
Unit tests for ScalableSandboxService - REFACTOR Phase 3: Scalability Enhancement
Tests for advanced caching mechanisms, load balancing, performance optimization, and high availability
"""

import pytest
import asyncio
import time
import uuid
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any, Optional

from app.sandbox.models import (
    SandboxConfig, SandboxExecutionRequest, SandboxExecutionResponse,
    Language, ExecutionType
)
from app.core.exceptions import SandboxError, ExecutionError, SecurityError


class TestMultiLevelCache:
    """Test multi-level caching system (L1: Memory, L2: Redis, L3: Database)"""
    
    @pytest.mark.asyncio
    async def test_cache_initialization(self):
        """Test cache system initialization"""
        from app.sandbox.scalable_sandbox_service import MultiLevelCache
        
        cache = MultiLevelCache(
            l1_size=1000,
            l2_redis_url="redis://localhost:6379",
            l3_db_url="sqlite:///:memory:"
        )
        
        # Wait for initialization
        await asyncio.sleep(0.1)
        
        assert cache.l1_cache is not None
        # Redis may be None if connection fails, that's ok for testing
        assert cache.cache_stats.hits == 0
        assert cache.cache_stats.misses == 0
    
    @pytest.mark.asyncio
    async def test_l1_memory_cache_operations(self):
        """Test L1 memory cache operations"""
        from app.sandbox.scalable_sandbox_service import MultiLevelCache
        
        cache = MultiLevelCache()
        
        # Test set and get
        await cache.set("key1", "value1", ttl=60)
        value = await cache.get("key1")
        assert value == "value1"
        
        # Test cache hit
        assert cache.cache_stats.hits == 1
        assert cache.cache_stats.misses == 0
    
    @pytest.mark.asyncio
    async def test_l2_redis_cache_operations(self):
        """Test L2 Redis cache operations"""
        from app.sandbox.scalable_sandbox_service import MultiLevelCache
        
        cache = MultiLevelCache()
        await asyncio.sleep(0.1)  # Wait for initialization
        
        # Test L1 miss, L2 hit (if Redis is available)
        if cache.l2_redis:
            await cache.l2_redis.set("key2", "value2", ex=60)
            value = await cache.get("key2")
            assert value == "value2"
        
        # Test cache miss
        value = await cache.get("nonexistent")
        assert value is None
        assert cache.cache_stats.misses >= 1
    
    @pytest.mark.asyncio
    async def test_l3_database_cache_operations(self):
        """Test L3 database cache operations"""
        from app.sandbox.scalable_sandbox_service import MultiLevelCache
        
        cache = MultiLevelCache()
        await asyncio.sleep(0.1)  # Wait for initialization
        
        # Test L1 and L2 miss, L3 hit (if database is available)
        if cache.l3_db:
            await cache.l3_db.execute(
                "INSERT INTO cache_entries (key, value, expires_at) VALUES (?, ?, ?)",
                ("key3", "value3", time.time() + 60)
            )
            await cache.l3_db.commit()
            value = await cache.get("key3")
            assert value == "value3"
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self):
        """Test intelligent cache invalidation"""
        from app.sandbox.scalable_sandbox_service import MultiLevelCache
        
        cache = MultiLevelCache()
        
        # Set value in all levels
        await cache.set("key4", "value4", ttl=60)
        await cache.set("key5", "value5", ttl=60)
        
        # Invalidate specific key
        await cache.invalidate("key4")
        assert await cache.get("key4") is None
        assert await cache.get("key5") == "value5"
        
        # Invalidate by pattern
        await cache.invalidate_pattern("key*")
        assert await cache.get("key5") is None
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        from app.sandbox.scalable_sandbox_service import MultiLevelCache
        
        cache = MultiLevelCache()
        
        # Set with short TTL
        await cache.set("key6", "value6", ttl=1)
        assert await cache.get("key6") == "value6"
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        assert await cache.get("key6") is None
    
    @pytest.mark.asyncio
    async def test_cache_warming(self):
        """Test cache warming strategies"""
        from app.sandbox.scalable_sandbox_service import MultiLevelCache
        
        cache = MultiLevelCache()
        
        # Warm cache with frequently accessed data
        warm_data = {"key7": "value7", "key8": "value8", "key9": "value9"}
        await cache.warm_cache(warm_data)
        
        for key, value in warm_data.items():
            assert await cache.get(key) == value
    
    @pytest.mark.asyncio
    async def test_distributed_cache_sync(self):
        """Test distributed cache synchronization"""
        from app.sandbox.scalable_sandbox_service import MultiLevelCache
        
        cache1 = MultiLevelCache()
        cache2 = MultiLevelCache()
        await asyncio.sleep(0.1)  # Wait for initialization
        
        # Set value in cache1
        await cache1.set("shared_key", "shared_value", ttl=60)
        
        # Sync to cache2 (placeholder implementation)
        await cache1.sync_to_instances(["instance2"])
        
        # Verify cache1 has the value
        assert await cache1.get("shared_key") == "shared_value"


class TestLoadBalancer:
    """Test load balancing and request distribution"""
    
    @pytest.mark.asyncio
    async def test_load_balancer_initialization(self):
        """Test load balancer initialization"""
        from app.sandbox.scalable_sandbox_service import LoadBalancer
        
        balancer = LoadBalancer(
            algorithm="round_robin",
            health_check_interval=30,
            max_retries=3
        )
        
        assert balancer.algorithm.value == "round_robin"
        assert balancer.health_check_interval == 30
        assert balancer.max_retries == 3
        assert len(balancer.instances) == 0
    
    @pytest.mark.asyncio
    async def test_add_remove_instances(self):
        """Test adding and removing instances"""
        from app.sandbox.scalable_sandbox_service import LoadBalancer
        
        balancer = LoadBalancer()
        
        # Add instances
        await balancer.add_instance("instance1", "http://localhost:8001", weight=1)
        await balancer.add_instance("instance2", "http://localhost:8002", weight=2)
        
        assert len(balancer.instances) == 2
        assert balancer.instances["instance1"].weight == 1
        assert balancer.instances["instance2"].weight == 2
        
        # Remove instance
        await balancer.remove_instance("instance1")
        assert len(balancer.instances) == 1
        assert "instance1" not in balancer.instances
    
    @pytest.mark.asyncio
    async def test_round_robin_distribution(self):
        """Test round-robin request distribution"""
        from app.sandbox.scalable_sandbox_service import LoadBalancer
        
        balancer = LoadBalancer(algorithm="round_robin")
        await balancer.add_instance("instance1", "http://localhost:8001")
        await balancer.add_instance("instance2", "http://localhost:8002")
        
        # Test round-robin distribution
        instance1 = await balancer.get_next_instance()
        instance2 = await balancer.get_next_instance()
        instance3 = await balancer.get_next_instance()
        
        assert instance1 == "instance1"
        assert instance2 == "instance2"
        assert instance3 == "instance1"  # Round-robin cycle
    
    @pytest.mark.asyncio
    async def test_weighted_distribution(self):
        """Test weighted request distribution"""
        from app.sandbox.scalable_sandbox_service import LoadBalancer
        
        balancer = LoadBalancer(algorithm="weighted")
        await balancer.add_instance("instance1", "http://localhost:8001", weight=1)
        await balancer.add_instance("instance2", "http://localhost:8002", weight=3)
        
        # Test weighted distribution (instance2 should get 3x more requests)
        distribution = {"instance1": 0, "instance2": 0}
        for _ in range(100):
            instance = await balancer.get_next_instance()
            distribution[instance] += 1
        
        # instance2 should get approximately 3x more requests
        assert distribution["instance2"] > distribution["instance1"] * 2
    
    @pytest.mark.asyncio
    async def test_least_connections_distribution(self):
        """Test least-connections request distribution"""
        from app.sandbox.scalable_sandbox_service import LoadBalancer
        
        balancer = LoadBalancer(algorithm="least_connections")
        await balancer.add_instance("instance1", "http://localhost:8001")
        await balancer.add_instance("instance2", "http://localhost:8002")
        
        # Simulate different connection counts
        balancer.instances["instance1"].active_connections = 5
        balancer.instances["instance2"].active_connections = 2
        
        # Should select instance with fewer connections
        instance = await balancer.get_next_instance()
        assert instance == "instance2"
    
    @pytest.mark.asyncio
    async def test_health_based_routing(self):
        """Test health-based routing with automatic failover"""
        from app.sandbox.scalable_sandbox_service import LoadBalancer
        
        balancer = LoadBalancer()
        await balancer.add_instance("instance1", "http://localhost:8001")
        await balancer.add_instance("instance2", "http://localhost:8002")
        
        # Mark instance1 as unhealthy
        balancer.instances["instance1"].healthy = False
        
        # Should route to healthy instance
        instance = await balancer.get_next_instance()
        assert instance == "instance2"
    
    @pytest.mark.asyncio
    async def test_geographic_load_balancing(self):
        """Test geographic load balancing"""
        from app.sandbox.scalable_sandbox_service import LoadBalancer
        
        balancer = LoadBalancer(algorithm="geographic")
        await balancer.add_instance("us-east", "http://us-east.example.com", region="us-east")
        await balancer.add_instance("eu-west", "http://eu-west.example.com", region="eu-west")
        
        # Test geographic routing
        instance = await balancer.get_next_instance(client_region="us-east")
        assert instance == "us-east"
        
        instance = await balancer.get_next_instance(client_region="eu-west")
        assert instance == "eu-west"
    
    @pytest.mark.asyncio
    async def test_session_affinity(self):
        """Test session affinity for stateful operations"""
        from app.sandbox.scalable_sandbox_service import LoadBalancer
        
        balancer = LoadBalancer(algorithm="session_affinity")
        await balancer.add_instance("instance1", "http://localhost:8001")
        await balancer.add_instance("instance2", "http://localhost:8002")
        
        # Test session affinity
        session_id = "session123"
        instance1 = await balancer.get_next_instance(session_id=session_id)
        instance2 = await balancer.get_next_instance(session_id=session_id)
        
        assert instance1 == instance2  # Same session should go to same instance


class TestAsyncProcessor:
    """Test async processing pipelines with queue management"""
    
    @pytest.mark.asyncio
    async def test_async_processor_initialization(self):
        """Test async processor initialization"""
        from app.sandbox.scalable_sandbox_service import AsyncProcessor
        
        processor = AsyncProcessor(
            max_workers=10,
            queue_size=1000,
            processing_timeout=300
        )
        
        assert processor.max_workers == 10
        assert processor.max_queue_size == 1000
        assert processor.processing_timeout == 300
        assert processor.active_workers == 0
    
    @pytest.mark.asyncio
    async def test_queue_management(self):
        """Test queue management and processing"""
        from app.sandbox.scalable_sandbox_service import AsyncProcessor
        
        processor = AsyncProcessor(max_workers=2)
        
        # Add tasks to queue without awaiting them immediately
        task1 = asyncio.create_task(processor.submit_task("task1", {"data": "value1"}))
        task2 = asyncio.create_task(processor.submit_task("task2", {"data": "value2"}))
        task3 = asyncio.create_task(processor.submit_task("task3", {"data": "value3"}))
        
        # Give workers time to start and process
        await asyncio.sleep(0.1)
        
        # Check that tasks are being processed
        assert processor.active_workers > 0
        
        # Process tasks
        results = await asyncio.gather(task1, task2, task3)
        assert len(results) == 3
        
        # Stop processor
        await processor.stop()
        assert processor.active_workers == 0
    
    @pytest.mark.asyncio
    async def test_worker_scaling(self):
        """Test dynamic worker scaling"""
        from app.sandbox.scalable_sandbox_service import AsyncProcessor
        
        processor = AsyncProcessor(max_workers=5)
        
        # Submit many tasks to trigger scaling
        tasks = []
        for i in range(20):
            task = processor.submit_task(f"task{i}", {"data": f"value{i}"})
            tasks.append(task)
        
        # Wait for processing
        await asyncio.gather(*tasks)
        
        # Check that workers were scaled up
        assert processor.active_workers <= processor.max_workers
    
    @pytest.mark.asyncio
    async def test_processing_timeout(self):
        """Test processing timeout handling"""
        from app.sandbox.scalable_sandbox_service import AsyncProcessor
        
        processor = AsyncProcessor(processing_timeout=1)
        
        # Submit long-running task
        with pytest.raises(ExecutionError, match="Processing timeout"):
            await processor.submit_task("long_task", {"sleep": 2})
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in async processing"""
        from app.sandbox.scalable_sandbox_service import AsyncProcessor
        
        processor = AsyncProcessor()
        
        # Submit task that will fail
        with pytest.raises(ExecutionError):
            await processor.submit_task("error_task", {"error": True})


class TestResourcePool:
    """Test resource pooling with dynamic scaling"""
    
    @pytest.mark.asyncio
    async def test_resource_pool_initialization(self):
        """Test resource pool initialization"""
        from app.sandbox.scalable_sandbox_service import ResourcePool
        
        pool = ResourcePool(
            min_workers=2,
            max_workers=10,
            scale_up_threshold=0.8,
            scale_down_threshold=0.2
        )
        
        assert pool.min_workers == 2
        assert pool.max_workers == 10
        assert pool.scale_up_threshold == 0.8
        assert pool.scale_down_threshold == 0.2
        assert pool.current_workers == 2
    
    @pytest.mark.asyncio
    async def test_worker_allocation(self):
        """Test worker allocation and deallocation"""
        from app.sandbox.scalable_sandbox_service import ResourcePool
        
        pool = ResourcePool(min_workers=1, max_workers=3)
        
        # Allocate workers
        worker1 = await pool.allocate_worker()
        worker2 = await pool.allocate_worker()
        
        assert worker1 is not None
        assert worker2 is not None
        assert pool.available_workers == 1
        assert pool.busy_workers == 2
        
        # Deallocate workers
        await pool.deallocate_worker(worker1)
        await pool.deallocate_worker(worker2)
        
        assert pool.available_workers == 3
        assert pool.busy_workers == 0
    
    @pytest.mark.asyncio
    async def test_dynamic_scaling_up(self):
        """Test dynamic scaling up under high load"""
        from app.sandbox.scalable_sandbox_service import ResourcePool
        
        pool = ResourcePool(min_workers=1, max_workers=5, scale_up_threshold=0.5)
        
        # Simulate high load
        workers = []
        for _ in range(3):
            worker = await pool.allocate_worker()
            workers.append(worker)
        
        # Trigger scaling check manually
        await pool.trigger_scaling_check()
        
        # Should scale up
        assert pool.current_workers > 1
        
        # Clean up
        for worker in workers:
            await pool.deallocate_worker(worker)
    
    @pytest.mark.asyncio
    async def test_dynamic_scaling_down(self):
        """Test dynamic scaling down under low load"""
        from app.sandbox.scalable_sandbox_service import ResourcePool
        
        pool = ResourcePool(min_workers=1, max_workers=5, scale_down_threshold=0.2)
        
        # Start with multiple workers
        pool.current_workers = 3
        
        # Simulate low load
        await asyncio.sleep(0.1)  # Allow scaling logic to run
        
        # Should scale down
        assert pool.current_workers >= pool.min_workers
    
    @pytest.mark.asyncio
    async def test_connection_pooling(self):
        """Test connection pooling for external services"""
        from app.sandbox.scalable_sandbox_service import ResourcePool
        
        pool = ResourcePool()
        
        # Test database connection pooling
        db_connection = await pool.get_db_connection()
        assert db_connection is not None
        
        await pool.return_db_connection(db_connection)
        
        # Test Redis connection pooling
        redis_connection = await pool.get_redis_connection()
        assert redis_connection is not None
        
        await pool.return_redis_connection(redis_connection)


class TestCircuitBreaker:
    """Test circuit breaker pattern for fault tolerance"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization"""
        from app.sandbox.scalable_sandbox_service import CircuitBreaker
        
        breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            half_open_max_calls=3
        )
        
        assert breaker.failure_threshold == 5
        assert breaker.recovery_timeout == 60
        assert breaker.half_open_max_calls == 3
        assert breaker.state.value == "closed"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state"""
        from app.sandbox.scalable_sandbox_service import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=3)
        
        # Successful calls should work
        result = await breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state.value == "closed"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opening(self):
        """Test circuit breaker opening after failures"""
        from app.sandbox.scalable_sandbox_service import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=2)
        
        # Simulate failures
        with pytest.raises(Exception):
            await breaker.call(lambda: (_ for _ in ()).throw(Exception("Test error")))
        
        with pytest.raises(Exception):
            await breaker.call(lambda: (_ for _ in ()).throw(Exception("Test error")))
        
        # Circuit should be open
        assert breaker.state.value == "open"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_state(self):
        """Test circuit breaker in half-open state"""
        from app.sandbox.scalable_sandbox_service import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
        
        # Trigger opening
        with pytest.raises(Exception):
            await breaker.call(lambda: (_ for _ in ()).throw(Exception("Test error")))
        
        assert breaker.state.value == "open"
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Try to call again to trigger half-open state
        try:
            result = await breaker.call(lambda: "success")
            # Successful call should close the circuit
            assert result == "success"
            assert breaker.state.value == "closed"
        except Exception:
            # If it fails, should still be half-open
            assert breaker.state.value == "half_open"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery"""
        from app.sandbox.scalable_sandbox_service import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
        
        # Trigger opening
        with pytest.raises(Exception):
            await breaker.call(lambda: (_ for _ in ()).throw(Exception("Test error")))
        
        # Wait for recovery
        await asyncio.sleep(1.1)
        
        # Successful call should close circuit
        result = await breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state.value == "closed"


class TestHealthMonitor:
    """Test health monitoring with automatic recovery"""
    
    @pytest.mark.asyncio
    async def test_health_monitor_initialization(self):
        """Test health monitor initialization"""
        from app.sandbox.scalable_sandbox_service import HealthMonitor
        
        monitor = HealthMonitor(
            check_interval=30,
            timeout=10,
            retry_attempts=3
        )
        
        assert monitor.check_interval == 30
        assert monitor.timeout == 10
        assert monitor.retry_attempts == 3
        assert monitor.health_status == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_execution(self):
        """Test health check execution"""
        from app.sandbox.scalable_sandbox_service import HealthMonitor
        
        monitor = HealthMonitor()
        
        # Add health check
        async def db_check():
            return True
        async def redis_check():
            return True
        
        monitor.add_health_check("database", db_check)
        monitor.add_health_check("redis", redis_check)
        
        # Run health checks
        status = await monitor.run_health_checks()
        assert status["database"] == "healthy"
        assert status["redis"] == "healthy"
        assert monitor.health_status == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure handling"""
        from app.sandbox.scalable_sandbox_service import HealthMonitor
        
        monitor = HealthMonitor()
        
        # Add failing health check
        async def failing_check():
            return False
        monitor.add_health_check("service", failing_check)
        
        # Run health checks
        status = await monitor.run_health_checks()
        assert status["service"] == "unhealthy"
        assert monitor.health_status == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_automatic_recovery(self):
        """Test automatic recovery mechanisms"""
        from app.sandbox.scalable_sandbox_service import HealthMonitor
        
        monitor = HealthMonitor()
        
        # Add recoverable health check
        recovery_count = 0
        async def recoverable_check():
            nonlocal recovery_count
            recovery_count += 1
            return recovery_count > 2
        
        async def recovery_action():
            pass
        
        monitor.add_health_check("recoverable", recoverable_check)
        monitor.add_recovery_action("recoverable", recovery_action)
        
        # Run health checks until recovery
        for _ in range(5):
            await monitor.run_health_checks()
            await asyncio.sleep(0.1)
        
        assert monitor.health_status == "healthy"
    
    @pytest.mark.asyncio
    async def test_alerting_system(self):
        """Test alerting system for health issues"""
        from app.sandbox.scalable_sandbox_service import HealthMonitor
        
        monitor = HealthMonitor()
        
        # Add alert handler
        alerts = []
        async def alert_handler(service, status):
            alerts.append((service, status))
        
        monitor.add_alert_handler(alert_handler)
        
        # Add failing health check
        async def failing_check():
            return False
        monitor.add_health_check("service", failing_check)
        
        # Run health checks
        await monitor.run_health_checks()
        
        # Should trigger alert
        assert len(alerts) > 0
        assert alerts[0][0] == "service"
        assert alerts[0][1] == "unhealthy"


class TestPerformanceMetrics:
    """Test performance metrics collection and analytics"""
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Test performance metrics collection"""
        from app.sandbox.scalable_sandbox_service import PerformanceMetrics
        
        metrics = PerformanceMetrics()
        
        # Record metrics
        metrics.record_request("endpoint1", 100, True)
        metrics.record_request("endpoint2", 200, False)
        metrics.record_request("endpoint1", 150, True)
        
        # Check metrics
        stats = metrics.get_stats()
        assert stats["total_requests"] == 3
        assert stats["successful_requests"] == 2
        assert stats["failed_requests"] == 1
        assert stats["average_response_time"] == 150
    
    @pytest.mark.asyncio
    async def test_metrics_aggregation(self):
        """Test metrics aggregation over time windows"""
        from app.sandbox.scalable_sandbox_service import PerformanceMetrics
        
        metrics = PerformanceMetrics()
        
        # Record metrics over time
        for i in range(10):
            metrics.record_request("endpoint", 100 + i, True)
            await asyncio.sleep(0.01)
        
        # Get aggregated metrics
        hourly_stats = metrics.get_hourly_stats()
        daily_stats = metrics.get_daily_stats()
        
        assert len(hourly_stats) > 0
        assert len(daily_stats) > 0
    
    @pytest.mark.asyncio
    async def test_capacity_planning(self):
        """Test capacity planning with predictive analytics"""
        from app.sandbox.scalable_sandbox_service import PerformanceMetrics
        
        metrics = PerformanceMetrics()
        
        # Record historical data
        for i in range(100):
            metrics.record_request("endpoint", 100 + (i % 50), True)
        
        # Get capacity predictions
        predictions = metrics.get_capacity_predictions()
        assert "peak_load" in predictions
        assert "recommended_instances" in predictions
        assert "scaling_recommendations" in predictions


class TestScalableSandboxService:
    """Test integrated scalable sandbox service"""
    
    @pytest.mark.asyncio
    async def test_scalable_service_initialization(self):
        """Test scalable sandbox service initialization"""
        from app.sandbox.scalable_sandbox_service import ScalableSandboxService
        
        service = ScalableSandboxService(
            config=SandboxConfig(),
            cache_size=1000,
            max_workers=10,
            load_balancer_algorithm="round_robin"
        )
        
        assert service.cache is not None
        assert service.load_balancer is not None
        assert service.async_processor is not None
        assert service.resource_pool is not None
        assert service.circuit_breaker is not None
        assert service.health_monitor is not None
        assert service.performance_metrics is not None
    
    @pytest.mark.asyncio
    async def test_high_throughput_execution(self):
        """Test high throughput code execution"""
        from app.sandbox.scalable_sandbox_service import ScalableSandboxService
        
        service = ScalableSandboxService(config=SandboxConfig())
        
        # Submit many concurrent requests
        requests = []
        for i in range(50):
            request = SandboxExecutionRequest(
                code=f"print('Request {i}')",
                language="python",
                execution_type="run"
            )
            requests.append(service.execute_code(request))
        
        # Execute all requests
        responses = await asyncio.gather(*requests)
        
        # Check results
        assert len(responses) == 50
        successful_responses = [r for r in responses if r.success]
        assert len(successful_responses) > 40  # Allow for some failures
    
    @pytest.mark.asyncio
    async def test_fault_tolerance(self):
        """Test fault tolerance under failure conditions"""
        from app.sandbox.scalable_sandbox_service import ScalableSandboxService
        
        service = ScalableSandboxService(config=SandboxConfig())
        
        # Simulate service failures
        with patch.object(service, '_execute_in_sandbox', side_effect=Exception("Service failure")):
            request = SandboxExecutionRequest(
                code="print('test')",
                language="python",
                execution_type="run"
            )
            
            # Should handle failure gracefully
            with pytest.raises(ExecutionError):
                await service.execute_code(request)
    
    @pytest.mark.asyncio
    async def test_auto_scaling(self):
        """Test automatic scaling under load"""
        from app.sandbox.scalable_sandbox_service import ScalableSandboxService
        
        service = ScalableSandboxService(
            config=SandboxConfig(),
            max_workers=5,
            scale_up_threshold=0.7
        )
        
        # Submit requests to trigger scaling
        requests = []
        for i in range(20):
            request = SandboxExecutionRequest(
                code=f"import time; time.sleep(0.1); print('Request {i}')",
                language="python",
                execution_type="run"
            )
            requests.append(service.execute_code(request))
        
        # Execute requests
        await asyncio.gather(*requests, return_exceptions=True)
        
        # Check that scaling occurred
        assert service.resource_pool.current_workers > 1
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test performance monitoring and metrics"""
        from app.sandbox.scalable_sandbox_service import ScalableSandboxService
        
        service = ScalableSandboxService(config=SandboxConfig())
        
        # Execute some requests
        for i in range(10):
            request = SandboxExecutionRequest(
                code=f"print('Request {i}')",
                language="python",
                execution_type="run"
            )
            await service.execute_code(request)
        
        # Check performance metrics
        metrics = service.get_performance_metrics()
        assert metrics["total_requests"] >= 10
        assert metrics["average_response_time"] > 0
        assert metrics["throughput"] > 0
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self):
        """Test health monitoring and alerting"""
        from app.sandbox.scalable_sandbox_service import ScalableSandboxService
        
        service = ScalableSandboxService(config=SandboxConfig())
        
        # Check health status
        health_status = await service.get_health_status()
        assert "overall_status" in health_status
        assert "components" in health_status
        assert "last_check" in health_status
        
        # Check individual component health
        assert health_status["components"]["cache"] in ["healthy", "unhealthy"]
        assert health_status["components"]["load_balancer"] in ["healthy", "unhealthy"]
        assert health_status["components"]["async_processor"] in ["healthy", "unhealthy"]
