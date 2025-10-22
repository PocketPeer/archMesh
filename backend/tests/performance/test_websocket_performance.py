"""
Performance Tests for WebSocket Services

This module provides comprehensive performance testing for WebSocket services
including load testing, stress testing, and performance benchmarking.
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

from app.services.websocket.production_service import ProductionWebSocketService
from app.services.websocket.async_processor import ProcessingPriority
from app.schemas.websocket import WebSocketConfig


class PerformanceMetrics:
    """Performance metrics collector"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.throughput_measurements: List[float] = []
        self.error_count = 0
        self.success_count = 0
        self.start_time = None
        self.end_time = None
    
    def record_response_time(self, response_time: float):
        """Record response time"""
        self.response_times.append(response_time)
    
    def record_throughput(self, throughput: float):
        """Record throughput measurement"""
        self.throughput_measurements.append(throughput)
    
    def record_success(self):
        """Record successful operation"""
        self.success_count += 1
    
    def record_error(self):
        """Record failed operation"""
        self.error_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_operations = self.success_count + self.error_count
        success_rate = self.success_count / total_operations if total_operations > 0 else 0
        
        return {
            "total_operations": total_operations,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "response_times": {
                "min": min(self.response_times) if self.response_times else 0,
                "max": max(self.response_times) if self.response_times else 0,
                "mean": statistics.mean(self.response_times) if self.response_times else 0,
                "median": statistics.median(self.response_times) if self.response_times else 0,
                "p95": self._percentile(self.response_times, 95),
                "p99": self._percentile(self.response_times, 99)
            },
            "throughput": {
                "min": min(self.throughput_measurements) if self.throughput_measurements else 0,
                "max": max(self.throughput_measurements) if self.throughput_measurements else 0,
                "mean": statistics.mean(self.throughput_measurements) if self.throughput_measurements else 0,
                "median": statistics.median(self.throughput_measurements) if self.throughput_measurements else 0
            },
            "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


@pytest.fixture
def performance_config():
    """Performance test configuration"""
    return WebSocketConfig(
        max_connections=1000,
        max_message_size=4096,
        heartbeat_interval=30,
        connection_timeout=300,
        require_authentication=False
    )


@pytest.fixture
async def performance_service(performance_config):
    """Create performance test service"""
    service = ProductionWebSocketService(
        websocket_config=performance_config,
        redis_client=None,  # Disable Redis for performance tests
        enable_auto_scaling=True,
        enable_caching=False,  # Disable caching for performance tests
        enable_load_balancing=False,  # Disable load balancing for performance tests
        enable_monitoring=True
    )
    
    await service.start()
    yield service
    await service.stop()


class TestWebSocketPerformance:
    """Performance tests for WebSocket services"""
    
    @pytest.mark.asyncio
    async def test_connection_performance(self, performance_service):
        """Test connection establishment performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = datetime.utcnow()
        
        # Test 100 concurrent connections
        async def connect_client(client_id: int):
            start_time = time.time()
            try:
                await performance_service.connect(
                    session_id=f"client-{client_id}",
                    user_id=f"user-{client_id}"
                )
                response_time = time.time() - start_time
                metrics.record_response_time(response_time)
                metrics.record_success()
            except Exception as e:
                metrics.record_error()
                print(f"Connection error for client {client_id}: {e}")
        
        # Run concurrent connections
        tasks = [connect_client(i) for i in range(100)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics.end_time = datetime.utcnow()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["success_rate"] >= 0.95  # 95% success rate
        assert summary["response_times"]["p95"] < 1.0  # 95% under 1 second
        assert summary["response_times"]["mean"] < 0.5  # Average under 500ms
        
        print(f"Connection Performance: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_message_throughput(self, performance_service):
        """Test message processing throughput"""
        metrics = PerformanceMetrics()
        metrics.start_time = datetime.utcnow()
        
        # Establish connections first
        connections = []
        for i in range(50):
            await performance_service.connect(
                session_id=f"client-{i}",
                user_id=f"user-{i}"
            )
            connections.append(f"client-{i}")
        
        # Test message throughput
        async def send_messages(session_id: str, message_count: int):
            start_time = time.time()
            for i in range(message_count):
                try:
                    await performance_service.send_message(
                        session_id=session_id,
                        message={
                            "type": "test_message",
                            "id": i,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        priority=ProcessingPriority.NORMAL
                    )
                    metrics.record_success()
                except Exception as e:
                    metrics.record_error()
                    print(f"Message error for {session_id}: {e}")
            
            duration = time.time() - start_time
            throughput = message_count / duration
            metrics.record_throughput(throughput)
        
        # Send messages concurrently
        tasks = [send_messages(session_id, 20) for session_id in connections]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Wait for processing
        await asyncio.sleep(2)
        
        metrics.end_time = datetime.utcnow()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["success_rate"] >= 0.95  # 95% success rate
        assert summary["throughput"]["mean"] > 100  # At least 100 messages/second
        
        print(f"Message Throughput: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_priority_processing_performance(self, performance_service):
        """Test priority-based message processing performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = datetime.utcnow()
        
        # Establish connection
        session_id = "priority-test-client"
        await performance_service.connect(session_id=session_id, user_id="priority-user")
        
        # Send messages with different priorities
        priorities = [
            ProcessingPriority.LOW,
            ProcessingPriority.NORMAL,
            ProcessingPriority.HIGH,
            ProcessingPriority.CRITICAL
        ]
        
        async def send_priority_messages(priority: ProcessingPriority, count: int):
            start_time = time.time()
            for i in range(count):
                try:
                    await performance_service.send_message(
                        session_id=session_id,
                        message={
                            "type": "priority_test",
                            "priority": priority.value,
                            "id": i,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        priority=priority
                    )
                    metrics.record_success()
                except Exception as e:
                    metrics.record_error()
                    print(f"Priority message error: {e}")
            
            response_time = time.time() - start_time
            metrics.record_response_time(response_time)
        
        # Send messages with different priorities
        tasks = [send_priority_messages(priority, 25) for priority in priorities]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Wait for processing
        await asyncio.sleep(2)
        
        metrics.end_time = datetime.utcnow()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["success_rate"] >= 0.95  # 95% success rate
        assert summary["response_times"]["mean"] < 1.0  # Average under 1 second
        
        print(f"Priority Processing: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self, performance_service):
        """Test concurrent operations performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = datetime.utcnow()
        
        # Test concurrent operations
        async def perform_operations(client_id: int):
            session_id = f"concurrent-client-{client_id}"
            start_time = time.time()
            
            try:
                # Connect
                await performance_service.connect(session_id=session_id, user_id=f"user-{client_id}")
                
                # Send messages
                for i in range(10):
                    await performance_service.send_message(
                        session_id=session_id,
                        message={
                            "type": "concurrent_test",
                            "client_id": client_id,
                            "message_id": i
                        }
                    )
                
                # Disconnect
                await performance_service.disconnect(session_id)
                
                response_time = time.time() - start_time
                metrics.record_response_time(response_time)
                metrics.record_success()
                
            except Exception as e:
                metrics.record_error()
                print(f"Concurrent operation error for client {client_id}: {e}")
        
        # Run concurrent operations
        tasks = [perform_operations(i) for i in range(50)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics.end_time = datetime.utcnow()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["success_rate"] >= 0.90  # 90% success rate
        assert summary["response_times"]["p95"] < 2.0  # 95% under 2 seconds
        
        print(f"Concurrent Operations: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_memory_usage_performance(self, performance_service):
        """Test memory usage under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Establish many connections
        connections = []
        for i in range(200):
            session_id = f"memory-client-{i}"
            await performance_service.connect(session_id=session_id, user_id=f"user-{i}")
            connections.append(session_id)
        
        # Send many messages
        for session_id in connections:
            for i in range(5):
                await performance_service.send_message(
                    session_id=session_id,
                    message={
                        "type": "memory_test",
                        "data": "x" * 1000  # 1KB message
                    }
                )
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Check memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Performance assertions
        assert memory_increase < 100  # Less than 100MB increase
        assert final_memory < 500  # Less than 500MB total
        
        print(f"Memory Usage: Initial={initial_memory:.2f}MB, Final={final_memory:.2f}MB, Increase={memory_increase:.2f}MB")
    
    @pytest.mark.asyncio
    async def test_error_handling_performance(self, performance_service):
        """Test error handling performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = datetime.utcnow()
        
        # Test error scenarios
        async def test_error_scenario(scenario_id: int):
            start_time = time.time()
            
            try:
                if scenario_id % 3 == 0:
                    # Invalid session ID
                    await performance_service.send_message(
                        session_id="",  # Invalid
                        message={"type": "test"}
                    )
                elif scenario_id % 3 == 1:
                    # Non-existent session
                    await performance_service.send_message(
                        session_id="non-existent",
                        message={"type": "test"}
                    )
                else:
                    # Invalid message
                    await performance_service.send_message(
                        session_id="test-session",
                        message=None  # Invalid
                    )
                
                # If we get here, it's unexpected
                metrics.record_success()
                
            except Exception:
                # Expected to fail
                metrics.record_error()
            
            response_time = time.time() - start_time
            metrics.record_response_time(response_time)
        
        # Run error scenarios
        tasks = [test_error_scenario(i) for i in range(100)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics.end_time = datetime.utcnow()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["error_count"] > 0  # Should have errors
        assert summary["response_times"]["mean"] < 0.1  # Fast error handling
        
        print(f"Error Handling: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_health_check_performance(self, performance_service):
        """Test health check performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = datetime.utcnow()
        
        # Perform multiple health checks
        async def perform_health_check(check_id: int):
            start_time = time.time()
            try:
                health = await performance_service.health_check()
                response_time = time.time() - start_time
                metrics.record_response_time(response_time)
                metrics.record_success()
                
                # Verify health check structure
                assert "status" in health
                assert "uptime_seconds" in health
                assert "metrics" in health
                
            except Exception as e:
                metrics.record_error()
                print(f"Health check error {check_id}: {e}")
        
        # Run health checks concurrently
        tasks = [perform_health_check(i) for i in range(50)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics.end_time = datetime.utcnow()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["success_rate"] >= 0.95  # 95% success rate
        assert summary["response_times"]["p95"] < 0.5  # 95% under 500ms
        
        print(f"Health Check Performance: {json.dumps(summary, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_sustained_load_performance(self, performance_service):
        """Test sustained load performance"""
        metrics = PerformanceMetrics()
        metrics.start_time = datetime.utcnow()
        
        # Establish connections
        connections = []
        for i in range(100):
            session_id = f"sustained-client-{i}"
            await performance_service.connect(session_id=session_id, user_id=f"user-{i}")
            connections.append(session_id)
        
        # Send messages continuously for 30 seconds
        async def send_continuous_messages(session_id: str):
            message_count = 0
            start_time = time.time()
            
            while time.time() - start_time < 30:  # 30 seconds
                try:
                    await performance_service.send_message(
                        session_id=session_id,
                        message={
                            "type": "sustained_test",
                            "count": message_count,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    message_count += 1
                    metrics.record_success()
                    
                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    metrics.record_error()
                    print(f"Sustained load error for {session_id}: {e}")
            
            # Record throughput for this client
            duration = time.time() - start_time
            throughput = message_count / duration
            metrics.record_throughput(throughput)
        
        # Run sustained load
        tasks = [send_continuous_messages(session_id) for session_id in connections]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics.end_time = datetime.utcnow()
        summary = metrics.get_summary()
        
        # Performance assertions
        assert summary["success_rate"] >= 0.90  # 90% success rate
        assert summary["throughput"]["mean"] > 50  # At least 50 messages/second per client
        
        print(f"Sustained Load: {json.dumps(summary, indent=2)}")


# Performance test runner
async def run_performance_tests():
    """Run all performance tests"""
    print("Starting WebSocket Performance Tests...")
    
    config = WebSocketConfig(
        max_connections=1000,
        max_message_size=4096,
        heartbeat_interval=30,
        connection_timeout=300,
        require_authentication=False
    )
    
    service = ProductionWebSocketService(
        websocket_config=config,
        redis_client=None,
        enable_auto_scaling=True,
        enable_caching=False,
        enable_load_balancing=False,
        enable_monitoring=True
    )
    
    try:
        await service.start()
        print("Service started successfully")
        
        # Run performance tests
        test_instance = TestWebSocketPerformance()
        
        print("\n1. Testing Connection Performance...")
        await test_instance.test_connection_performance(service)
        
        print("\n2. Testing Message Throughput...")
        await test_instance.test_message_throughput(service)
        
        print("\n3. Testing Priority Processing...")
        await test_instance.test_priority_processing_performance(service)
        
        print("\n4. Testing Concurrent Operations...")
        await test_instance.test_concurrent_operations_performance(service)
        
        print("\n5. Testing Memory Usage...")
        await test_instance.test_memory_usage_performance(service)
        
        print("\n6. Testing Error Handling...")
        await test_instance.test_error_handling_performance(service)
        
        print("\n7. Testing Health Check Performance...")
        await test_instance.test_health_check_performance(service)
        
        print("\n8. Testing Sustained Load...")
        await test_instance.test_sustained_load_performance(service)
        
        print("\nPerformance tests completed successfully!")
        
    except Exception as e:
        print(f"Performance test error: {e}")
    finally:
        await service.stop()
        print("Service stopped")


if __name__ == "__main__":
    asyncio.run(run_performance_tests())

