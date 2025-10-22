"""
Unit Tests for Optimized Sandbox Code Testing Service

This module tests the optimized sandbox service with enhanced performance,
resource management, and scalability features.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from app.sandbox.models import (
    SandboxExecutionRequest,
    SandboxExecutionResponse,
    SandboxConfig,
    ExecutionType
)
from app.sandbox.optimized_sandbox_service import (
    OptimizedSandboxService,
    ResourcePool,
    ExecutionCache,
    ExecutionMetrics
)
from app.core.exceptions import SandboxError, SecurityError, ExecutionError, TimeoutError


@pytest.fixture
def sandbox_config():
    """Sandbox configuration for testing"""
    return SandboxConfig(
        max_execution_time=30,
        max_memory_mb=512,
        max_cpu_percent=80,
        enable_network_access=False,
        enable_file_system_access=True,
        allowed_file_extensions=[".py", ".js", ".ts", ".java", ".cpp"],
        max_file_size_mb=10,
        security_scan_enabled=True,
        performance_testing_enabled=True,
        code_quality_analysis_enabled=True,
        isolation_level="container",
        cleanup_after_execution=True
    )


@pytest.fixture
def sample_code():
    """Sample code for testing"""
    return {
        "python": """
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

if __name__ == "__main__":
    test_add()
    print("All tests passed!")
""",
        "javascript": """
function add(a, b) {
    return a + b;
}

function testAdd() {
    console.assert(add(2, 3) === 5);
    console.assert(add(-1, 1) === 0);
    console.assert(add(0, 0) === 0);
    console.log("All tests passed!");
}

testAdd();
"""
    }


class TestResourcePool:
    """Test cases for Resource Pool"""
    
    def test_resource_pool_initialization(self):
        """Test resource pool initialization"""
        pool = ResourcePool(max_workers=5)
        
        assert pool.max_workers == 5
        assert len(pool.available_workers) == 5
        assert len(pool.busy_workers) == 0
        assert len(pool.worker_metrics) == 5
        
        # Check worker IDs
        for i in range(5):
            worker_id = f"worker-{i}"
            assert worker_id in pool.available_workers
            assert worker_id in pool.worker_metrics
    
    def test_acquire_worker(self):
        """Test worker acquisition"""
        pool = ResourcePool(max_workers=3)
        
        # Acquire all workers
        workers = []
        for _ in range(3):
            worker = pool.acquire_worker()
            assert worker is not None
            workers.append(worker)
        
        # All workers should be busy
        assert len(pool.available_workers) == 0
        assert len(pool.busy_workers) == 3
        
        # Try to acquire another worker (should fail)
        worker = pool.acquire_worker()
        assert worker is None
    
    def test_release_worker(self):
        """Test worker release"""
        pool = ResourcePool(max_workers=2)
        
        # Acquire worker
        worker_id = pool.acquire_worker()
        assert worker_id is not None
        assert len(pool.busy_workers) == 1
        assert len(pool.available_workers) == 1
        
        # Release worker
        pool.release_worker(worker_id, 1.5, True)
        assert len(pool.busy_workers) == 0
        assert len(pool.available_workers) == 2
        assert worker_id in pool.available_workers
        
        # Check metrics update
        metrics = pool.worker_metrics[worker_id]
        assert metrics["total_executions"] == 1
        assert metrics["successful_executions"] == 1
        assert metrics["failed_executions"] == 0
        assert metrics["average_execution_time"] == 1.5
    
    def test_release_worker_failure(self):
        """Test worker release with failure"""
        pool = ResourcePool(max_workers=2)
        
        worker_id = pool.acquire_worker()
        pool.release_worker(worker_id, 2.0, False)
        
        metrics = pool.worker_metrics[worker_id]
        assert metrics["total_executions"] == 1
        assert metrics["successful_executions"] == 0
        assert metrics["failed_executions"] == 1
        assert metrics["average_execution_time"] == 2.0
    
    def test_get_pool_status(self):
        """Test pool status retrieval"""
        pool = ResourcePool(max_workers=3)
        
        # Acquire one worker
        worker_id = pool.acquire_worker()
        
        status = pool.get_pool_status()
        
        assert status["available_workers"] == 2
        assert status["busy_workers"] == 1
        assert status["total_workers"] == 3
        assert status["utilization_rate"] == 1/3
        assert len(status["worker_metrics"]) == 3


class TestExecutionCache:
    """Test cases for Execution Cache"""
    
    def test_cache_initialization(self):
        """Test cache initialization"""
        cache = ExecutionCache(max_size=100, ttl_seconds=3600)
        
        assert cache.max_size == 100
        assert cache.ttl_seconds == 3600
        assert len(cache.cache) == 0
        assert len(cache.access_times) == 0
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        cache = ExecutionCache()
        
        request1 = SandboxExecutionRequest(
            code="print('hello')",
            language="python",
            execution_type="run"
        )
        
        request2 = SandboxExecutionRequest(
            code="print('hello')",
            language="python",
            execution_type="run"
        )
        
        request3 = SandboxExecutionRequest(
            code="print('world')",
            language="python",
            execution_type="run"
        )
        
        key1 = cache._generate_cache_key(request1)
        key2 = cache._generate_cache_key(request2)
        key3 = cache._generate_cache_key(request3)
        
        assert key1 == key2  # Same content should generate same key
        assert key1 != key3  # Different content should generate different key
    
    def test_cache_put_and_get(self):
        """Test cache put and get operations"""
        cache = ExecutionCache()
        
        request = SandboxExecutionRequest(
            code="print('hello')",
            language="python",
            execution_type="run"
        )
        
        response = SandboxExecutionResponse(
            execution_id="test-123",
            success=True,
            language="python",
            execution_type="run",
            exit_code=0,
            stdout="hello",
            execution_time=1.0
        )
        
        # Cache should be empty initially
        assert cache.get(request) is None
        
        # Put response in cache
        cache.put(request, response)
        
        # Should be able to retrieve it
        cached_response = cache.get(request)
        assert cached_response is not None
        assert cached_response.execution_id == "test-123"
        assert cached_response.success is True
        assert cached_response.stdout == "hello"
    
    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        cache = ExecutionCache(ttl_seconds=1)  # 1 second TTL
        
        request = SandboxExecutionRequest(
            code="print('hello')",
            language="python",
            execution_type="run"
        )
        
        response = SandboxExecutionResponse(
            execution_id="test-123",
            success=True,
            language="python",
            execution_type="run",
            exit_code=0,
            execution_time=1.0
        )
        
        cache.put(request, response)
        assert cache.get(request) is not None
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should be expired now
        assert cache.get(request) is None
    
    def test_cache_size_limit(self):
        """Test cache size limit"""
        cache = ExecutionCache(max_size=2)
        
        # Add 3 items (exceeds max size)
        for i in range(3):
            request = SandboxExecutionRequest(
                code=f"print('hello{i}')",
                language="python",
                execution_type="run"
            )
            
            response = SandboxExecutionResponse(
                execution_id=f"test-{i}",
                success=True,
                language="python",
                execution_type="run",
                exit_code=0,
                execution_time=1.0
            )
            
            cache.put(request, response)
        
        # Should only have 2 items (oldest removed)
        assert len(cache.cache) == 2
    
    def test_cache_clear(self):
        """Test cache clear operation"""
        cache = ExecutionCache()
        
        request = SandboxExecutionRequest(
            code="print('hello')",
            language="python",
            execution_type="run"
        )
        
        response = SandboxExecutionResponse(
            execution_id="test-123",
            success=True,
            language="python",
            execution_type="run",
            exit_code=0,
            execution_time=1.0
        )
        
        cache.put(request, response)
        assert len(cache.cache) == 1
        
        cache.clear()
        assert len(cache.cache) == 0
        assert len(cache.access_times) == 0
    
    def test_get_cache_stats(self):
        """Test cache statistics"""
        cache = ExecutionCache(max_size=100, ttl_seconds=3600)
        
        stats = cache.get_cache_stats()
        
        assert stats["size"] == 0
        assert stats["max_size"] == 100
        assert stats["ttl_seconds"] == 3600


class TestOptimizedSandboxService:
    """Test cases for Optimized Sandbox Service"""
    
    def test_optimized_sandbox_service_initialization(self, sandbox_config):
        """Test optimized sandbox service initialization"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=5)
        
        assert service.config == sandbox_config
        assert service.max_workers == 5
        assert service.resource_pool.max_workers == 5
        assert service.execution_cache.max_size == 1000
        assert service.metrics.total_executions == 0
        assert len(service.active_executions) == 0
        assert len(service.execution_history) == 0
    
    def test_optimized_sandbox_service_default_config(self):
        """Test optimized sandbox service with default config"""
        service = OptimizedSandboxService()
        
        assert service.config is not None
        assert service.max_workers == 10
        assert service.resource_pool.max_workers == 10
    
    @pytest.mark.asyncio
    async def test_execute_code_success(self, sandbox_config, sample_code):
        """Test successful code execution"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=2)
        
        request = SandboxExecutionRequest(
            code=sample_code["python"],
            language="python",
            test_code=sample_code["python"],
            execution_type="test",
            timeout=30
        )
        
        response = await service.execute_code(request)
        
        assert response.success is True
        assert response.execution_id is not None
        assert response.exit_code == 0
        assert "All tests passed!" in response.stdout
        assert response.execution_time > 0
        assert response.memory_usage_mb > 0
        assert response.security_scan_passed is True
        assert response.performance_test_passed is True
        assert response.code_quality_score > 0
    
    @pytest.mark.asyncio
    async def test_execute_code_caching(self, sandbox_config, sample_code):
        """Test execution result caching"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=2)
        
        request = SandboxExecutionRequest(
            code=sample_code["python"],
            language="python",
            execution_type="run"
        )
        
        # First execution
        start_time = time.time()
        response1 = await service.execute_code(request)
        first_execution_time = time.time() - start_time
        
        # Second execution (should be cached)
        start_time = time.time()
        response2 = await service.execute_code(request)
        second_execution_time = time.time() - start_time
        
        # Both should succeed
        assert response1.success is True
        assert response2.success is True
        
        # Second execution should be faster (cached)
        assert second_execution_time < first_execution_time
        
        # Cache should have the result
        cached_response = service.execution_cache.get(request)
        assert cached_response is not None
        assert cached_response.success is True
    
    @pytest.mark.asyncio
    async def test_execute_batch(self, sandbox_config, sample_code):
        """Test batch code execution"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=3)
        
        requests = [
            SandboxExecutionRequest(
                code=sample_code["python"],
                language="python",
                execution_type="run"
            ),
            SandboxExecutionRequest(
                code=sample_code["javascript"],
                language="javascript",
                execution_type="run"
            ),
            SandboxExecutionRequest(
                code="print('hello')",
                language="python",
                execution_type="run"
            )
        ]
        
        responses = await service.execute_batch(requests)
        
        assert len(responses) == 3
        for response in responses:
            assert response.success is True
            assert response.execution_id is not None
            assert response.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_resource_pool_utilization(self, sandbox_config, sample_code):
        """Test resource pool utilization"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=3)
        
        # Create multiple concurrent requests (within worker limit)
        requests = [
            SandboxExecutionRequest(
                code=sample_code["python"],
                language="python",
                execution_type="run"
            ) for _ in range(3)
        ]
        
        # Execute concurrently
        start_time = time.time()
        responses = await service.execute_batch(requests)
        execution_time = time.time() - start_time
        
        # All should succeed
        for response in responses:
            assert response.success is True
        
        # Check resource pool status
        pool_status = service.resource_pool.get_pool_status()
        assert pool_status["total_workers"] == 3
        assert pool_status["available_workers"] == 3  # All workers released
        assert pool_status["busy_workers"] == 0
    
    def test_get_performance_metrics(self, sandbox_config):
        """Test performance metrics collection"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=3)
        
        metrics = service.get_performance_metrics()
        
        assert "execution_metrics" in metrics
        assert "resource_pool" in metrics
        assert "cache_stats" in metrics
        assert "uptime_seconds" in metrics
        assert "executions_per_second" in metrics
        
        # Check execution metrics
        exec_metrics = metrics["execution_metrics"]
        assert exec_metrics["total_executions"] == 0
        assert exec_metrics["successful_executions"] == 0
        assert exec_metrics["failed_executions"] == 0
        assert exec_metrics["success_rate"] == 0.0
        assert exec_metrics["concurrent_executions"] == 0
        assert exec_metrics["max_concurrent_executions"] == 0
        
        # Check resource pool
        pool_metrics = metrics["resource_pool"]
        assert pool_metrics["total_workers"] == 3
        assert pool_metrics["available_workers"] == 3
        assert pool_metrics["busy_workers"] == 0
        assert pool_metrics["utilization_rate"] == 0.0
    
    @pytest.mark.asyncio
    async def test_performance_metrics_update(self, sandbox_config, sample_code):
        """Test performance metrics update after execution"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=2)
        
        request = SandboxExecutionRequest(
            code=sample_code["python"],
            language="python",
            execution_type="run"
        )
        
        # Execute code
        response = await service.execute_code(request)
        
        # Check metrics updated
        metrics = service.get_performance_metrics()
        exec_metrics = metrics["execution_metrics"]
        
        assert exec_metrics["total_executions"] == 1
        assert exec_metrics["successful_executions"] == 1
        assert exec_metrics["failed_executions"] == 0
        assert exec_metrics["success_rate"] == 1.0
        assert exec_metrics["average_execution_time"] > 0
        assert exec_metrics["concurrent_executions"] == 0  # Released after execution
    
    def test_clear_cache(self, sandbox_config):
        """Test cache clearing"""
        service = OptimizedSandboxService(config=sandbox_config)
        
        # Add something to cache
        request = SandboxExecutionRequest(
            code="print('hello')",
            language="python",
            execution_type="run"
        )
        
        response = SandboxExecutionResponse(
            execution_id="test-123",
            success=True,
            language="python",
            execution_type="run",
            exit_code=0,
            execution_time=1.0
        )
        
        service.execution_cache.put(request, response)
        assert service.execution_cache.get(request) is not None
        
        # Clear cache
        service.clear_cache()
        assert service.execution_cache.get(request) is None
    
    def test_shutdown(self, sandbox_config):
        """Test service shutdown"""
        service = OptimizedSandboxService(config=sandbox_config)
        
        # Add some data
        service.active_executions["test-123"] = {"status": "running"}
        service.execution_history.append({"execution_id": "test-123"})
        
        # Shutdown
        service.shutdown()
        
        # Should be cleaned up
        assert len(service.active_executions) == 0
        # History might still be there for debugging, but active executions should be cleared
    
    @pytest.mark.asyncio
    async def test_concurrent_execution_limits(self, sandbox_config, sample_code):
        """Test concurrent execution limits"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=2)
        
        # Create multiple requests (within worker limit)
        requests = [
            SandboxExecutionRequest(
                code=sample_code["python"],
                language="python",
                execution_type="run"
            ) for _ in range(2)
        ]
        
        # Execute concurrently (should be limited by max_workers=2)
        responses = await service.execute_batch(requests)
        
        # All should succeed (but may be serialized due to worker limit)
        for response in responses:
            assert response.success is True
        
        # Check that metrics show proper execution
        metrics = service.get_performance_metrics()
        assert metrics["execution_metrics"]["total_executions"] == 2
    
    @pytest.mark.asyncio
    async def test_error_handling_in_batch(self, sandbox_config):
        """Test error handling in batch execution"""
        service = OptimizedSandboxService(config=sandbox_config)
        
        # Create requests with one invalid
        requests = [
            SandboxExecutionRequest(
                code="print('hello')",
                language="python",
                execution_type="run"
            ),
            SandboxExecutionRequest(
                code="invalid code",
                language="python",
                execution_type="run"
            ),
            SandboxExecutionRequest(
                code="print('world')",
                language="python",
                execution_type="run"
            )
        ]
        
        responses = await service.execute_batch(requests)
        
        assert len(responses) == 3
        
        # First and third should succeed
        assert responses[0].success is True
        assert responses[2].success is True
        
        # Second should fail but not crash the batch
        assert responses[1].success is False
        assert responses[1].stderr is not None and len(responses[1].stderr) > 0
    
    def test_worker_metrics_tracking(self, sandbox_config):
        """Test worker metrics tracking"""
        service = OptimizedSandboxService(config=sandbox_config, max_workers=2)
        
        # Check initial worker metrics
        pool_status = service.resource_pool.get_pool_status()
        worker_metrics = pool_status["worker_metrics"]
        
        assert len(worker_metrics) == 2
        
        for worker_id, metrics in worker_metrics.items():
            assert metrics["total_executions"] == 0
            assert metrics["successful_executions"] == 0
            assert metrics["failed_executions"] == 0
            assert metrics["average_execution_time"] == 0.0
            assert metrics["last_used"] is None
