"""
Unit Tests for Sandbox Code Testing Service

This module tests the Sandbox Code Testing service using TDD methodology
with comprehensive test coverage for secure code execution and testing.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from app.sandbox.models import (
    SandboxExecutionRequest, 
    SandboxExecutionResponse, 
    TestResult, 
    SecurityScanResult,
    PerformanceResult,
    CodeQualityResult
)
from app.sandbox.sandbox_service import SandboxService, SandboxConfig
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
""",
        "typescript": """
function add(a: number, b: number): number {
    return a + b;
}

function testAdd(): void {
    console.assert(add(2, 3) === 5);
    console.assert(add(-1, 1) === 0);
    console.assert(add(0, 0) === 0);
    console.log("All tests passed!");
}

testAdd();
"""
    }


@pytest.fixture
def malicious_code():
    """Malicious code samples for security testing"""
    return {
        "file_access": """
import os
with open('/etc/passwd', 'r') as f:
    print(f.read())
""",
        "network_access": """
import urllib.request
response = urllib.request.urlopen('http://malicious-site.com')
print(response.read())
""",
        "system_command": """
import subprocess
subprocess.run(['rm', '-rf', '/'])
""",
        "infinite_loop": """
while True:
    pass
""",
        "memory_bomb": """
data = []
while True:
    data.append('x' * 1000000)
"""
    }


class TestSandboxService:
    """Test cases for Sandbox Service"""
    
    def test_sandbox_service_initialization(self, sandbox_config):
        """Test sandbox service initialization"""
        sandbox = SandboxService(config=sandbox_config)
        
        assert sandbox.config == sandbox_config
        assert sandbox.active_executions == {}
        assert sandbox.execution_history == []
        assert len(sandbox.resource_usage) > 0  # Should be initialized with default values
        assert sandbox.security_violations == []
    
    def test_sandbox_service_initialization_with_default_config(self):
        """Test sandbox service initialization with default config"""
        sandbox = SandboxService()
        
        assert sandbox.config is not None
        assert sandbox.config.max_execution_time == 60
        assert sandbox.config.max_memory_mb == 1024
        assert sandbox.config.enable_network_access is False
        assert sandbox.config.security_scan_enabled is True
    
    @pytest.mark.asyncio
    async def test_execute_code_success(self, sandbox_config, sample_code):
        """Test successful code execution"""
        sandbox = SandboxService(config=sandbox_config)
        
        request = SandboxExecutionRequest(
            code=sample_code["python"],
            language="python",
            test_code=sample_code["python"],
            execution_type="test",
            timeout=30
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is True
        assert response.execution_id is not None
        assert response.exit_code == 0
        assert "All tests passed!" in response.stdout
        assert response.stderr == ""
        assert response.execution_time > 0
        assert response.memory_usage_mb > 0
        assert response.cpu_usage_percent >= 0
        assert response.security_scan_passed is True
        assert response.performance_test_passed is True
        assert response.code_quality_score > 0
    
    @pytest.mark.asyncio
    async def test_execute_code_with_test_failure(self, sandbox_config):
        """Test code execution with test failure"""
        sandbox = SandboxService(config=sandbox_config)
        
        failing_code = """
def add(a, b):
    return a - b  # Wrong implementation

def test_add():
    assert add(2, 3) == 5  # This will fail

if __name__ == "__main__":
    test_add()
"""
        
        request = SandboxExecutionRequest(
            code=failing_code,
            language="python",
            test_code=failing_code,
            execution_type="test"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is False
        assert response.exit_code != 0
        assert "AssertionError" in response.stderr or "AssertionError" in response.stdout
        assert response.test_results is not None
        assert len(response.test_results.failed_tests) > 0
    
    @pytest.mark.asyncio
    async def test_execute_code_security_violation(self, sandbox_config, malicious_code):
        """Test code execution with security violation"""
        sandbox = SandboxService(config=sandbox_config)
        
        request = SandboxExecutionRequest(
            code=malicious_code["file_access"],
            language="python",
            execution_type="run"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is False
        assert response.security_scan_passed is False
        assert response.security_violations is not None
        assert len(response.security_violations) > 0
        assert any("file_access" in violation.lower() for violation in response.security_violations)
    
    @pytest.mark.asyncio
    async def test_execute_code_network_violation(self, sandbox_config, malicious_code):
        """Test code execution with network access violation"""
        sandbox = SandboxService(config=sandbox_config)
        
        request = SandboxExecutionRequest(
            code=malicious_code["network_access"],
            language="python",
            execution_type="run"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is False
        assert response.security_scan_passed is False
        assert response.security_violations is not None
        assert len(response.security_violations) > 0
        assert any("network" in violation.lower() for violation in response.security_violations)
    
    @pytest.mark.asyncio
    async def test_execute_code_system_command_violation(self, sandbox_config, malicious_code):
        """Test code execution with system command violation"""
        sandbox = SandboxService(config=sandbox_config)
        
        request = SandboxExecutionRequest(
            code=malicious_code["system_command"],
            language="python",
            execution_type="run"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is False
        assert response.security_scan_passed is False
        assert response.security_violations is not None
        assert len(response.security_violations) > 0
        assert any("system" in violation.lower() or "command" in violation.lower() for violation in response.security_violations)
    
    @pytest.mark.asyncio
    async def test_execute_code_timeout(self, sandbox_config, malicious_code):
        """Test code execution timeout"""
        sandbox = SandboxService(config=sandbox_config)
        
        request = SandboxExecutionRequest(
            code=malicious_code["infinite_loop"],
            language="python",
            execution_type="run",
            timeout=5
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is False
        assert response.timeout_occurred is True
        assert response.execution_time >= 5
        assert response.execution_time < 30  # Should timeout within reasonable time
    
    @pytest.mark.asyncio
    async def test_execute_code_memory_limit(self, sandbox_config, malicious_code):
        """Test code execution memory limit"""
        sandbox = SandboxService(config=sandbox_config)
        
        request = SandboxExecutionRequest(
            code=malicious_code["memory_bomb"],
            language="python",
            execution_type="run"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is False
        assert response.memory_limit_exceeded is True
        assert response.memory_usage_mb >= sandbox_config.max_memory_mb
    
    @pytest.mark.asyncio
    async def test_execute_code_multiple_languages(self, sandbox_config, sample_code):
        """Test code execution for multiple languages"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Test only languages that are likely to be available
        languages = ["python", "javascript"]  # Removed typescript as ts-node may not be installed
        
        for language in languages:
            request = SandboxExecutionRequest(
                code=sample_code[language],
                language=language,
                execution_type="run"
            )
            
            response = await sandbox.execute_code(request)
            
            assert response.success is True
            assert response.language == language
            assert response.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_execute_code_with_dependencies(self, sandbox_config):
        """Test code execution with external dependencies"""
        sandbox = SandboxService(config=sandbox_config)
        
        code_with_deps = """
import requests
import json

def fetch_data():
    response = requests.get('https://api.github.com/users/octocat')
    return response.json()

if __name__ == "__main__":
    data = fetch_data()
    print(f"User: {data.get('login', 'Unknown')}")
"""
        
        request = SandboxExecutionRequest(
            code=code_with_deps,
            language="python",
            execution_type="run",
            dependencies=["requests"]
        )
        
        response = await sandbox.execute_code(request)
        
        # Should fail due to network access being disabled
        assert response.success is False
        assert response.security_scan_passed is False
    
    @pytest.mark.asyncio
    async def test_execute_code_performance_testing(self, sandbox_config):
        """Test code execution with performance testing"""
        sandbox = SandboxService(config=sandbox_config)
        
        performance_code = """
import time

def slow_function():
    time.sleep(0.1)
    return sum(range(1000))

def test_performance():
    start_time = time.time()
    result = slow_function()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.3f}s")
    return execution_time

if __name__ == "__main__":
    test_performance()
"""
        
        request = SandboxExecutionRequest(
            code=performance_code,
            language="python",
            execution_type="performance_test"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is True
        assert response.performance_test_passed is True
        assert response.performance_results is not None
        assert response.performance_results.execution_time > 0
        assert response.performance_results.memory_peak_mb > 0
        assert response.performance_results.cpu_usage_percent >= 0
    
    @pytest.mark.asyncio
    async def test_execute_code_quality_analysis(self, sandbox_config):
        """Test code execution with quality analysis"""
        sandbox = SandboxService(config=sandbox_config)
        
        quality_code = """
def calculate_fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def test_fibonacci():
    assert calculate_fibonacci(0) == 0
    assert calculate_fibonacci(1) == 1
    assert calculate_fibonacci(10) == 55

if __name__ == "__main__":
    test_fibonacci()
    print("Fibonacci tests passed!")
"""
        
        request = SandboxExecutionRequest(
            code=quality_code,
            language="python",
            execution_type="quality_analysis"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is True
        assert response.code_quality_score > 0
        assert response.code_quality_results is not None
        assert response.code_quality_results.complexity_score >= 0
        assert response.code_quality_results.maintainability_score >= 0
        assert response.code_quality_results.test_coverage >= 0
    
    @pytest.mark.asyncio
    async def test_execute_code_concurrent_executions(self, sandbox_config, sample_code):
        """Test concurrent code executions"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Create multiple execution requests
        requests = []
        for i in range(5):
            request = SandboxExecutionRequest(
                code=sample_code["python"],
                language="python",
                execution_type="test"
            )
            requests.append(request)
        
        # Execute all requests concurrently
        responses = await asyncio.gather(*[sandbox.execute_code(req) for req in requests])
        
        # All should succeed
        for response in responses:
            assert response.success is True
            assert response.execution_id is not None
        
        # Check that all executions are tracked
        assert len(sandbox.active_executions) == 0  # Should be cleaned up
        assert len(sandbox.execution_history) == 5
    
    @pytest.mark.asyncio
    async def test_execute_code_resource_monitoring(self, sandbox_config, sample_code):
        """Test resource monitoring during execution"""
        sandbox = SandboxService(config=sandbox_config)
        
        request = SandboxExecutionRequest(
            code=sample_code["python"],
            language="python",
            execution_type="test"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is True
        assert response.memory_usage_mb > 0
        assert response.cpu_usage_percent >= 0
        assert response.execution_time > 0
        assert response.resource_usage is not None
        assert "memory_peak" in response.resource_usage
        assert "cpu_avg" in response.resource_usage
    
    @pytest.mark.asyncio
    async def test_execute_code_error_handling(self, sandbox_config):
        """Test error handling for invalid requests"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Test with invalid request
        with pytest.raises(ExecutionError):
            await sandbox.execute_code(None)
        
        # Test with invalid language
        request = SandboxExecutionRequest(
            code="print('hello')",
            language="invalid_language",
            execution_type="run"
        )
        
        with pytest.raises(ExecutionError):
            await sandbox.execute_code(request)
    
    def test_validate_request_validation(self, sandbox_config):
        """Test request validation logic"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Test with invalid language
        with pytest.raises(ExecutionError, match="Unsupported language"):
            sandbox._validate_request(SandboxExecutionRequest(
                code="print('hello')",
                language="invalid_language",
                execution_type="run"
            ))
        
        # Test with valid request (should not raise)
        try:
            sandbox._validate_request(SandboxExecutionRequest(
                code="print('hello')",
                language="python",
                execution_type="run"
            ))
        except ExecutionError:
            pytest.fail("Valid request should not raise ExecutionError")
    
    @pytest.mark.asyncio
    async def test_execute_code_cleanup(self, sandbox_config, sample_code):
        """Test cleanup after execution"""
        sandbox = SandboxService(config=sandbox_config)
        
        request = SandboxExecutionRequest(
            code=sample_code["python"],
            language="python",
            execution_type="test"
        )
        
        response = await sandbox.execute_code(request)
        
        assert response.success is True
        
        # Check that cleanup was performed
        assert response.execution_id not in sandbox.active_executions
        assert response.execution_id in [exec["execution_id"] for exec in sandbox.execution_history]
    
    def test_get_execution_status(self, sandbox_config, sample_code):
        """Test getting execution status"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Add a mock execution to active executions
        execution_id = "test-execution-123"
        sandbox.active_executions[execution_id] = {
            "status": "running",
            "start_time": datetime.utcnow(),
            "request": SandboxExecutionRequest(
                code=sample_code["python"],
                language="python",
                execution_type="test"
            )
        }
        
        status = sandbox.get_execution_status(execution_id)
        
        assert status is not None
        assert status["status"] == "running"
        assert "start_time" in status
    
    def test_get_execution_status_not_found(self, sandbox_config):
        """Test getting status for non-existent execution"""
        sandbox = SandboxService(config=sandbox_config)
        
        status = sandbox.get_execution_status("non-existent-id")
        
        assert status is None
    
    def test_get_execution_history(self, sandbox_config):
        """Test getting execution history"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Add some mock history
        sandbox.execution_history = [
            {
                "execution_id": "exec-1",
                "status": "completed",
                "success": True,
                "timestamp": datetime.utcnow()
            },
            {
                "execution_id": "exec-2",
                "status": "failed",
                "success": False,
                "timestamp": datetime.utcnow()
            }
        ]
        
        history = sandbox.get_execution_history(limit=10)
        
        assert len(history) == 2
        assert history[0]["execution_id"] == "exec-1"
        assert history[1]["execution_id"] == "exec-2"
    
    def test_get_execution_statistics(self, sandbox_config):
        """Test getting execution statistics"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Add some mock history
        sandbox.execution_history = [
            {"success": True, "language": "python", "execution_time": 1.0},
            {"success": False, "language": "python", "execution_time": 0.5},
            {"success": True, "language": "javascript", "execution_time": 1.5}
        ]
        
        stats = sandbox.get_execution_statistics()
        
        assert stats["total_executions"] == 3
        assert stats["successful_executions"] == 2
        assert stats["failed_executions"] == 1
        assert stats["success_rate"] == 2/3
        assert stats["average_execution_time"] == 1.0
        assert stats["language_distribution"]["python"] == 2
        assert stats["language_distribution"]["javascript"] == 1
    
    def test_cleanup_old_executions(self, sandbox_config):
        """Test cleanup of old executions"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Add old executions
        old_time = datetime.utcnow() - timedelta(hours=2)
        sandbox.execution_history = [
            {
                "execution_id": "old-exec",
                "timestamp": old_time,
                "status": "completed"
            },
            {
                "execution_id": "recent-exec",
                "timestamp": datetime.utcnow(),
                "status": "completed"
            }
        ]
        
        sandbox.cleanup_old_executions(max_age_hours=1)
        
        assert len(sandbox.execution_history) == 1
        assert sandbox.execution_history[0]["execution_id"] == "recent-exec"
    
    def test_get_resource_usage(self, sandbox_config):
        """Test getting resource usage statistics"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Add some mock resource usage
        sandbox.resource_usage = {
            "memory_peak_mb": 256,
            "cpu_avg_percent": 45.5,
            "disk_usage_mb": 1024,
            "network_usage_mb": 0
        }
        
        usage = sandbox.get_resource_usage()
        
        assert usage["memory_peak_mb"] == 256
        assert usage["cpu_avg_percent"] == 45.5
        assert usage["disk_usage_mb"] == 1024
        assert usage["network_usage_mb"] == 0
    
    def test_get_security_violations(self, sandbox_config):
        """Test getting security violations"""
        sandbox = SandboxService(config=sandbox_config)
        
        # Add some mock violations
        sandbox.security_violations = [
            {
                "type": "file_access",
                "description": "Attempted to access /etc/passwd",
                "timestamp": datetime.utcnow(),
                "severity": "high"
            },
            {
                "type": "network_access",
                "description": "Attempted to connect to external host",
                "timestamp": datetime.utcnow(),
                "severity": "medium"
            }
        ]
        
        violations = sandbox.get_security_violations()
        
        assert len(violations) == 2
        assert violations[0]["type"] == "file_access"
        assert violations[1]["type"] == "network_access"
