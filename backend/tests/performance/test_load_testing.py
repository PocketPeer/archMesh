"""
Advanced Load Testing Suite

This module provides comprehensive load testing capabilities for the ArchMesh API,
including stress testing, spike testing, volume testing, and endurance testing.
"""

import pytest
import asyncio
import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app


class LoadTestResults:
    """Container for load test results and metrics."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        self.start_time: float = 0
        self.end_time: float = 0
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
    
    @property
    def duration(self) -> float:
        """Total test duration in seconds."""
        return self.end_time - self.start_time
    
    @property
    def requests_per_second(self) -> float:
        """Requests per second throughput."""
        return self.total_requests / self.duration if self.duration > 0 else 0
    
    @property
    def success_rate(self) -> float:
        """Percentage of successful requests."""
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
    
    @property
    def average_response_time(self) -> float:
        """Average response time in seconds."""
        return statistics.mean(self.response_times) if self.response_times else 0
    
    @property
    def median_response_time(self) -> float:
        """Median response time in seconds."""
        return statistics.median(self.response_times) if self.response_times else 0
    
    @property
    def p95_response_time(self) -> float:
        """95th percentile response time in seconds."""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    @property
    def p99_response_time(self) -> float:
        """99th percentile response time in seconds."""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of test results."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{self.success_rate:.2f}%",
            "duration": f"{self.duration:.2f}s",
            "requests_per_second": f"{self.requests_per_second:.2f}",
            "average_response_time": f"{self.average_response_time:.3f}s",
            "median_response_time": f"{self.median_response_time:.3f}s",
            "p95_response_time": f"{self.p95_response_time:.3f}s",
            "p99_response_time": f"{self.p99_response_time:.3f}s",
            "error_count": len(self.errors)
        }


class TestLoadTesting:
    """Comprehensive load testing suite."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def _make_request(self, client: TestClient, endpoint: str, method: str = "GET", 
                     data: Dict = None, headers: Dict = None) -> Tuple[float, int, str]:
        """Make a single request and return timing, status code, and error."""
        start_time = time.time()
        try:
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            elif method == "POST":
                response = client.post(endpoint, json=data, headers=headers)
            elif method == "PUT":
                response = client.put(endpoint, json=data, headers=headers)
            elif method == "DELETE":
                response = client.delete(endpoint, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = end_time - start_time
            return response_time, response.status_code, ""
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return response_time, 0, str(e)
    
    def _run_load_test(self, client: TestClient, endpoint: str, method: str = "GET",
                      data: Dict = None, headers: Dict = None, 
                      concurrent_users: int = 10, requests_per_user: int = 10) -> LoadTestResults:
        """Run a load test with specified parameters."""
        results = LoadTestResults()
        results.start_time = time.time()
        
        def user_worker():
            """Worker function for each concurrent user."""
            user_results = []
            for _ in range(requests_per_user):
                response_time, status_code, error = self._make_request(
                    client, endpoint, method, data, headers
                )
                user_results.append((response_time, status_code, error))
            return user_results
        
        # Run concurrent users
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_worker) for _ in range(concurrent_users)]
            
            for future in as_completed(futures):
                user_results = future.result()
                for response_time, status_code, error in user_results:
                    results.response_times.append(response_time)
                    results.status_codes.append(status_code)
                    results.total_requests += 1
                    
                    if status_code >= 200 and status_code < 400:
                        results.successful_requests += 1
                    else:
                        results.failed_requests += 1
                        if error:
                            results.errors.append(error)
        
        results.end_time = time.time()
        return results
    
    def test_health_endpoint_load(self, client):
        """Test health endpoint under load."""
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            results = self._run_load_test(
                client, "/api/v1/health", 
                concurrent_users=20, 
                requests_per_user=50
            )
            
            summary = results.get_summary()
            print(f"Health endpoint load test results: {summary}")
            
            # Assertions
            assert results.success_rate >= 95.0, f"Success rate too low: {results.success_rate}%"
            assert results.requests_per_second >= 50, f"Throughput too low: {results.requests_per_second} RPS"
            assert results.average_response_time <= 0.5, f"Response time too high: {results.average_response_time}s"
            assert results.p95_response_time <= 1.0, f"P95 response time too high: {results.p95_response_time}s"
    
    def test_projects_list_load(self, client):
        """Test projects list endpoint under load."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock projects list
            mock_projects = [
                Mock(
                    id=str(uuid4()),
                    name=f"Project {i}",
                    description=f"Description {i}",
                    domain="cloud-native",
                    status="processing",
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z"
                )
                for i in range(100)
            ]
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_projects
            mock_result.scalar.return_value = 100
            mock_db.execute.return_value = mock_result
            
            results = self._run_load_test(
                client, "/api/v1/projects",
                concurrent_users=15,
                requests_per_user=20
            )
            
            summary = results.get_summary()
            print(f"Projects list load test results: {summary}")
            
            # Assertions
            assert results.success_rate >= 90.0, f"Success rate too low: {results.success_rate}%"
            assert results.requests_per_second >= 20, f"Throughput too low: {results.requests_per_second} RPS"
            assert results.average_response_time <= 1.0, f"Response time too high: {results.average_response_time}s"
    
    def test_project_creation_load(self, client):
        """Test project creation under load."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            def mock_refresh(project):
                project.id = uuid4()
                project.created_at = "2023-01-01T00:00:00Z"
                project.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            project_data = {
                "name": "Load Test Project",
                "description": "Project created during load testing",
                "domain": "cloud-native"
            }
            
            results = self._run_load_test(
                client, "/api/v1/projects", "POST",
                data=project_data,
                concurrent_users=10,
                requests_per_user=5
            )
            
            summary = results.get_summary()
            print(f"Project creation load test results: {summary}")
            
            # Assertions
            assert results.success_rate >= 80.0, f"Success rate too low: {results.success_rate}%"
            assert results.requests_per_second >= 10, f"Throughput too low: {results.requests_per_second} RPS"
            assert results.average_response_time <= 2.0, f"Response time too high: {results.average_response_time}s"
    
    def test_spike_testing(self, client):
        """Test system behavior under sudden load spikes."""
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Normal load
            normal_results = self._run_load_test(
                client, "/api/v1/health",
                concurrent_users=5,
                requests_per_user=10
            )
            
            # Spike load
            spike_results = self._run_load_test(
                client, "/api/v1/health",
                concurrent_users=50,
                requests_per_user=20
            )
            
            print(f"Normal load results: {normal_results.get_summary()}")
            print(f"Spike load results: {spike_results.get_summary()}")
            
            # Assertions
            assert spike_results.success_rate >= 80.0, f"Spike success rate too low: {spike_results.success_rate}%"
            assert spike_results.average_response_time <= 2.0, f"Spike response time too high: {spike_results.average_response_time}s"
            
            # System should recover from spike
            recovery_results = self._run_load_test(
                client, "/api/v1/health",
                concurrent_users=5,
                requests_per_user=10
            )
            
            assert recovery_results.success_rate >= 95.0, f"Recovery success rate too low: {recovery_results.success_rate}%"
            assert recovery_results.average_response_time <= 1.0, f"Recovery response time too high: {recovery_results.average_response_time}s"
    
    def test_volume_testing(self, client):
        """Test system behavior with large volumes of data."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock large dataset (1000 projects)
            mock_projects = [
                Mock(
                    id=str(uuid4()),
                    name=f"Volume Test Project {i}",
                    description=f"Large description for project {i}" * 10,  # Large description
                    domain="cloud-native",
                    status="processing",
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z"
                )
                for i in range(1000)
            ]
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_projects
            mock_result.scalar.return_value = 1000
            mock_db.execute.return_value = mock_result
            
            results = self._run_load_test(
                client, "/api/v1/projects",
                concurrent_users=5,
                requests_per_user=10
            )
            
            summary = results.get_summary()
            print(f"Volume test results: {summary}")
            
            # Assertions
            assert results.success_rate >= 90.0, f"Volume test success rate too low: {results.success_rate}%"
            assert results.average_response_time <= 3.0, f"Volume test response time too high: {results.average_response_time}s"
    
    def test_endurance_testing(self, client):
        """Test system stability over extended period."""
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Run for 30 seconds with moderate load
            start_time = time.time()
            results = LoadTestResults()
            results.start_time = start_time
            
            def endurance_worker():
                """Worker for endurance testing."""
                worker_results = []
                while time.time() - start_time < 30:  # 30 seconds
                    response_time, status_code, error = self._make_request(client, "/api/v1/health")
                    worker_results.append((response_time, status_code, error))
                    time.sleep(0.1)  # Small delay between requests
                return worker_results
            
            # Run 5 concurrent workers
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(endurance_worker) for _ in range(5)]
                
                for future in as_completed(futures):
                    worker_results = future.result()
                    for response_time, status_code, error in worker_results:
                        results.response_times.append(response_time)
                        results.status_codes.append(status_code)
                        results.total_requests += 1
                        
                        if status_code >= 200 and status_code < 400:
                            results.successful_requests += 1
                        else:
                            results.failed_requests += 1
                            if error:
                                results.errors.append(error)
            
            results.end_time = time.time()
            summary = results.get_summary()
            print(f"Endurance test results: {summary}")
            
            # Assertions
            assert results.success_rate >= 95.0, f"Endurance test success rate too low: {results.success_rate}%"
            assert results.average_response_time <= 1.0, f"Endurance test response time too high: {results.average_response_time}s"
            assert len(results.errors) == 0, f"Endurance test had errors: {results.errors}"
    
    def test_memory_usage_under_load(self, client):
        """Test memory usage patterns under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            # Run load test
            results = self._run_load_test(
                client, "/api/v1/health",
                concurrent_users=20,
                requests_per_user=100
            )
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"Memory usage - Initial: {initial_memory:.2f}MB, Final: {final_memory:.2f}MB, Increase: {memory_increase:.2f}MB")
            
            # Assertions
            assert results.success_rate >= 90.0, f"Memory test success rate too low: {results.success_rate}%"
            assert memory_increase < 100, f"Memory increase too high: {memory_increase:.2f}MB"  # Less than 100MB increase
    
    def test_concurrent_different_endpoints(self, client):
        """Test concurrent requests to different endpoints."""
        # Mock Redis for health checks
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis), \
             patch('app.api.v1.projects.get_db') as mock_get_db:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock projects list
            mock_projects = [Mock(id=str(uuid4()), name=f"Project {i}", domain="cloud-native", status="processing") for i in range(10)]
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_projects
            mock_result.scalar.return_value = 10
            mock_db.execute.return_value = mock_result
            
            def endpoint_worker(endpoint: str, method: str = "GET", data: Dict = None):
                """Worker for specific endpoint."""
                worker_results = []
                for _ in range(20):
                    response_time, status_code, error = self._make_request(client, endpoint, method, data)
                    worker_results.append((response_time, status_code, error))
                return worker_results
            
            # Run concurrent requests to different endpoints
            with ThreadPoolExecutor(max_workers=15) as executor:
                futures = []
                
                # Health endpoint
                for _ in range(5):
                    futures.append(executor.submit(endpoint_worker, "/api/v1/health"))
                
                # Projects endpoint
                for _ in range(5):
                    futures.append(executor.submit(endpoint_worker, "/api/v1/projects"))
                
                # Mixed endpoints
                for _ in range(5):
                    futures.append(executor.submit(endpoint_worker, "/api/v1/health"))
                
                # Collect results
                all_results = []
                for future in as_completed(futures):
                    worker_results = future.result()
                    all_results.extend(worker_results)
            
            # Analyze results
            total_requests = len(all_results)
            successful_requests = sum(1 for _, status_code, _ in all_results if 200 <= status_code < 400)
            response_times = [response_time for response_time, _, _ in all_results]
            
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            print(f"Concurrent endpoints test - Total: {total_requests}, Success: {successful_requests}, Success Rate: {success_rate:.2f}%, Avg Response: {avg_response_time:.3f}s")
            
            # Assertions
            assert success_rate >= 90.0, f"Concurrent endpoints success rate too low: {success_rate}%"
            assert avg_response_time <= 1.5, f"Concurrent endpoints response time too high: {avg_response_time}s"
    
    def test_error_recovery_under_load(self, client):
        """Test system recovery from errors under load."""
        # First, test with failing Redis
        with patch('app.api.v1.health.get_redis', side_effect=Exception("Redis connection failed")):
            error_results = self._run_load_test(
                client, "/api/v1/health",
                concurrent_users=10,
                requests_per_user=5
            )
            
            print(f"Error condition results: {error_results.get_summary()}")
            
            # System should handle errors gracefully
            assert error_results.total_requests > 0, "No requests were processed during error condition"
        
        # Then test recovery with working Redis
        mock_redis = Mock()
        mock_redis.ping = AsyncMock(return_value=True)
        
        with patch('app.api.v1.health.get_redis', return_value=mock_redis):
            recovery_results = self._run_load_test(
                client, "/api/v1/health",
                concurrent_users=10,
                requests_per_user=5
            )
            
            print(f"Recovery results: {recovery_results.get_summary()}")
            
            # System should recover
            assert recovery_results.success_rate >= 95.0, f"Recovery success rate too low: {recovery_results.success_rate}%"
            assert recovery_results.average_response_time <= 1.0, f"Recovery response time too high: {recovery_results.average_response_time}s"

