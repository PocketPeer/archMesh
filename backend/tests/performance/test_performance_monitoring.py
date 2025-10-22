"""
Performance Monitoring and Benchmarking

This module provides comprehensive performance monitoring capabilities including
CPU usage, memory usage, response time tracking, and performance regression detection.
"""

import pytest
import time
import psutil
import os
import threading
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from dataclasses import dataclass, field
from datetime import datetime

from app.main import app


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    response_time_ms: float = 0.0
    status_code: int = 0
    endpoint: str = ""
    error: Optional[str] = None


@dataclass
class PerformanceBenchmark:
    """Container for performance benchmarks."""
    endpoint: str
    max_response_time_ms: float
    min_throughput_rps: float
    max_cpu_percent: float
    max_memory_mb: float
    min_success_rate_percent: float


class PerformanceMonitor:
    """Performance monitoring utility."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process(os.getpid())
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def start_monitoring(self, interval: float = 0.1):
        """Start continuous performance monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval: float):
        """Monitoring loop running in separate thread."""
        while self.monitoring:
            try:
                cpu_percent = self.process.cpu_percent()
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                metric = PerformanceMetrics(
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb
                )
                self.metrics.append(metric)
                
                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def record_request(self, endpoint: str, response_time_ms: float, status_code: int, error: str = None):
        """Record a request metric."""
        metric = PerformanceMetrics(
            endpoint=endpoint,
            response_time_ms=response_time_ms,
            status_code=status_code,
            error=error
        )
        self.metrics.append(metric)
    
    def get_cpu_stats(self) -> Dict[str, float]:
        """Get CPU usage statistics."""
        cpu_values = [m.cpu_percent for m in self.metrics if m.cpu_percent > 0]
        if not cpu_values:
            return {"avg": 0, "max": 0, "min": 0}
        
        return {
            "avg": sum(cpu_values) / len(cpu_values),
            "max": max(cpu_values),
            "min": min(cpu_values)
        }
    
    def get_memory_stats(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        memory_values = [m.memory_mb for m in self.metrics if m.memory_mb > 0]
        if not memory_values:
            return {"avg": 0, "max": 0, "min": 0}
        
        return {
            "avg": sum(memory_values) / len(memory_values),
            "max": max(memory_values),
            "min": min(memory_values)
        }
    
    def get_response_time_stats(self, endpoint: str = None) -> Dict[str, float]:
        """Get response time statistics."""
        response_times = [m.response_time_ms for m in self.metrics 
                         if m.response_time_ms > 0 and (endpoint is None or m.endpoint == endpoint)]
        if not response_times:
            return {"avg": 0, "max": 0, "min": 0, "p95": 0, "p99": 0}
        
        sorted_times = sorted(response_times)
        return {
            "avg": sum(response_times) / len(response_times),
            "max": max(response_times),
            "min": min(response_times),
            "p95": sorted_times[int(len(sorted_times) * 0.95)],
            "p99": sorted_times[int(len(sorted_times) * 0.99)]
        }
    
    def get_success_rate(self, endpoint: str = None) -> float:
        """Get success rate percentage."""
        requests = [m for m in self.metrics 
                   if m.status_code > 0 and (endpoint is None or m.endpoint == endpoint)]
        if not requests:
            return 0.0
        
        successful = sum(1 for m in requests if 200 <= m.status_code < 400)
        return (successful / len(requests)) * 100
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics.clear()


class TestPerformanceMonitoring:
    """Performance monitoring and benchmarking tests."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def monitor(self):
        """Create performance monitor."""
        return PerformanceMonitor()
    
    def test_cpu_monitoring(self, client, monitor):
        """Test CPU usage monitoring."""
        monitor.start_monitoring(interval=0.05)
        
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Generate some load
            for _ in range(50):
                start_time = time.time()
                response = client.get("/api/v1/health")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                monitor.record_request("/api/v1/health", response_time_ms, response.status_code)
                
                time.sleep(0.01)  # Small delay
        
        monitor.stop_monitoring()
        
        cpu_stats = monitor.get_cpu_stats()
        print(f"CPU stats: {cpu_stats}")
        
        # Assertions
        assert cpu_stats["avg"] >= 0, "CPU average should be non-negative"
        assert cpu_stats["max"] >= 0, "CPU max should be non-negative"
        assert len(monitor.metrics) > 0, "Should have collected metrics"
    
    def test_memory_monitoring(self, client, monitor):
        """Test memory usage monitoring."""
        monitor.start_monitoring(interval=0.05)
        
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Generate some load
            for _ in range(30):
                start_time = time.time()
                response = client.get("/api/v1/health")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                monitor.record_request("/api/v1/health", response_time_ms, response.status_code)
                
                time.sleep(0.02)
        
        monitor.stop_monitoring()
        
        memory_stats = monitor.get_memory_stats()
        print(f"Memory stats: {memory_stats}")
        
        # Assertions
        assert memory_stats["avg"] > 0, "Memory average should be positive"
        assert memory_stats["max"] > 0, "Memory max should be positive"
        assert memory_stats["max"] >= memory_stats["avg"], "Max should be >= average"
    
    def test_response_time_monitoring(self, client, monitor):
        """Test response time monitoring."""
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Record multiple requests
            for i in range(20):
                start_time = time.time()
                response = client.get("/api/v1/health")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                monitor.record_request("/api/v1/health", response_time_ms, response.status_code)
                
                time.sleep(0.01)
        
        response_stats = monitor.get_response_time_stats("/api/v1/health")
        print(f"Response time stats: {response_stats}")
        
        # Assertions
        assert response_stats["avg"] > 0, "Average response time should be positive"
        assert response_stats["max"] >= response_stats["avg"], "Max should be >= average"
        assert response_stats["min"] <= response_stats["avg"], "Min should be <= average"
        assert response_stats["p95"] >= response_stats["avg"], "P95 should be >= average"
        assert response_stats["p99"] >= response_stats["p95"], "P99 should be >= P95"
    
    def test_success_rate_monitoring(self, client, monitor):
        """Test success rate monitoring."""
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Record successful requests
            for _ in range(15):
                start_time = time.time()
                response = client.get("/api/v1/health")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                monitor.record_request("/api/v1/health", response_time_ms, response.status_code)
        
        # Record some failed requests
        with patch('app.api.v1.health.get_redis', side_effect=Exception("Redis error")):
            for _ in range(5):
                start_time = time.time()
                try:
                    response = client.get("/api/v1/health")
                    status_code = response.status_code
                except:
                    status_code = 500
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                monitor.record_request("/api/v1/health", response_time_ms, status_code)
        
        success_rate = monitor.get_success_rate("/api/v1/health")
        print(f"Success rate: {success_rate}%")
        
        # Assertions
        assert 0 <= success_rate <= 100, "Success rate should be between 0 and 100"
        assert success_rate >= 70, f"Success rate should be at least 70%, got {success_rate}%"
    
    def test_performance_benchmarking(self, client, monitor):
        """Test performance benchmarking against defined thresholds."""
        # Define benchmarks
        benchmarks = [
            PerformanceBenchmark(
                endpoint="/api/v1/health",
                max_response_time_ms=500,
                min_throughput_rps=10,
                max_cpu_percent=80,
                max_memory_mb=200,
                min_success_rate_percent=95
            )
        ]
        
        monitor.start_monitoring(interval=0.05)
        
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Run benchmark test
            start_time = time.time()
            request_count = 0
            
            while time.time() - start_time < 5:  # Run for 5 seconds
                request_start = time.time()
                response = client.get("/api/v1/health")
                request_end = time.time()
                
                response_time_ms = (request_end - request_start) * 1000
                monitor.record_request("/api/v1/health", response_time_ms, response.status_code)
                request_count += 1
                
                time.sleep(0.1)
        
        monitor.stop_monitoring()
        
        # Evaluate benchmarks
        benchmark = benchmarks[0]
        response_stats = monitor.get_response_time_stats("/api/v1/health")
        cpu_stats = monitor.get_cpu_stats()
        memory_stats = monitor.get_memory_stats()
        success_rate = monitor.get_success_rate("/api/v1/health")
        duration = 5.0  # seconds
        throughput = request_count / duration
        
        print(f"Benchmark results:")
        print(f"  Response time: {response_stats['avg']:.2f}ms (max: {benchmark.max_response_time_ms}ms)")
        print(f"  Throughput: {throughput:.2f} RPS (min: {benchmark.min_throughput_rps} RPS)")
        print(f"  CPU: {cpu_stats['max']:.2f}% (max: {benchmark.max_cpu_percent}%)")
        print(f"  Memory: {memory_stats['max']:.2f}MB (max: {benchmark.max_memory_mb}MB)")
        print(f"  Success rate: {success_rate:.2f}% (min: {benchmark.min_success_rate_percent}%)")
        
        # Assertions
        assert response_stats['avg'] <= benchmark.max_response_time_ms, f"Response time too high: {response_stats['avg']}ms"
        assert throughput >= benchmark.min_throughput_rps, f"Throughput too low: {throughput} RPS"
        assert cpu_stats['max'] <= benchmark.max_cpu_percent, f"CPU usage too high: {cpu_stats['max']}%"
        assert memory_stats['max'] <= benchmark.max_memory_mb, f"Memory usage too high: {memory_stats['max']}MB"
        assert success_rate >= benchmark.min_success_rate_percent, f"Success rate too low: {success_rate}%"
    
    def test_performance_regression_detection(self, client, monitor):
        """Test performance regression detection."""
        # Baseline performance measurement
        monitor.start_monitoring(interval=0.05)
        
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Measure baseline
            baseline_times = []
            for _ in range(20):
                start_time = time.time()
                response = client.get("/api/v1/health")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                baseline_times.append(response_time_ms)
                monitor.record_request("/api/v1/health", response_time_ms, response.status_code)
        
        monitor.stop_monitoring()
        
        baseline_avg = sum(baseline_times) / len(baseline_times)
        print(f"Baseline average response time: {baseline_avg:.2f}ms")
        
        # Simulate performance regression (slower responses)
        monitor.clear_metrics()
        monitor.start_monitoring(interval=0.05)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Add artificial delay to simulate regression
            def slow_health_check():
                time.sleep(0.1)  # 100ms delay
                return True
            
            mock_redis.ping = AsyncMock(side_effect=slow_health_check)
            
            regression_times = []
            for _ in range(20):
                start_time = time.time()
                response = client.get("/api/v1/health")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                regression_times.append(response_time_ms)
                monitor.record_request("/api/v1/health", response_time_ms, response.status_code)
        
        monitor.stop_monitoring()
        
        regression_avg = sum(regression_times) / len(regression_times)
        regression_factor = regression_avg / baseline_avg
        
        print(f"Regression average response time: {regression_avg:.2f}ms")
        print(f"Regression factor: {regression_factor:.2f}x")
        
        # Assertions
        assert regression_avg > baseline_avg, "Regression should be slower than baseline"
        assert regression_factor > 1.5, f"Regression factor should be > 1.5x, got {regression_factor:.2f}x"
    
    def test_memory_leak_detection(self, client, monitor):
        """Test memory leak detection."""
        monitor.start_monitoring(interval=0.1)
        
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Run multiple cycles of requests
            for cycle in range(5):
                print(f"Memory leak test cycle {cycle + 1}")
                
                for _ in range(20):
                    start_time = time.time()
                    response = client.get("/api/v1/health")
                    end_time = time.time()
                    
                    response_time_ms = (end_time - start_time) * 1000
                    monitor.record_request("/api/v1/health", response_time_ms, response.status_code)
                
                time.sleep(0.5)  # Allow system to settle
        
        monitor.stop_monitoring()
        
        memory_stats = monitor.get_memory_stats()
        print(f"Memory leak test results: {memory_stats}")
        
        # Check for significant memory growth
        memory_growth = memory_stats["max"] - memory_stats["min"]
        memory_growth_percent = (memory_growth / memory_stats["min"]) * 100 if memory_stats["min"] > 0 else 0
        
        print(f"Memory growth: {memory_growth:.2f}MB ({memory_growth_percent:.2f}%)")
        
        # Assertions
        assert memory_growth_percent < 50, f"Memory growth too high: {memory_growth_percent:.2f}%"
        assert memory_stats["max"] < 500, f"Maximum memory usage too high: {memory_stats['max']:.2f}MB"
    
    def test_concurrent_monitoring(self, client, monitor):
        """Test monitoring under concurrent load."""
        import threading
        from concurrent.futures import ThreadPoolExecutor
        
        monitor.start_monitoring(interval=0.05)
        
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        def worker_thread(thread_id: int):
            """Worker thread for concurrent testing."""
            with patch('app.api.v1.health.get_redis', return_value=mock_redis):
                for _ in range(10):
                    start_time = time.time()
                    response = client.get("/api/v1/health")
                    end_time = time.time()
                    
                    response_time_ms = (end_time - start_time) * 1000
                    monitor.record_request(f"/api/v1/health-thread-{thread_id}", response_time_ms, response.status_code)
                    
                    time.sleep(0.05)
        
        # Run concurrent threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(5)]
            
            for future in futures:
                future.result()
        
        monitor.stop_monitoring()
        
        # Analyze results
        cpu_stats = monitor.get_cpu_stats()
        memory_stats = monitor.get_memory_stats()
        total_requests = len([m for m in monitor.metrics if m.status_code > 0])
        
        print(f"Concurrent monitoring results:")
        print(f"  Total requests: {total_requests}")
        print(f"  CPU stats: {cpu_stats}")
        print(f"  Memory stats: {memory_stats}")
        
        # Assertions
        assert total_requests >= 50, f"Should have at least 50 requests, got {total_requests}"
        assert cpu_stats["max"] < 100, f"CPU usage too high: {cpu_stats['max']}%"
        assert memory_stats["max"] < 300, f"Memory usage too high: {memory_stats['max']}MB"

