"""
Performance Testing Configuration

This module provides configuration and utilities for performance testing,
including test scenarios, thresholds, and reporting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class TestType(Enum):
    """Types of performance tests."""
    LOAD = "load"
    STRESS = "stress"
    SPIKE = "spike"
    VOLUME = "volume"
    ENDURANCE = "endurance"
    MEMORY = "memory"
    CPU = "cpu"


class TestSeverity(Enum):
    """Test severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    max_response_time_ms: float
    min_throughput_rps: float
    max_cpu_percent: float
    max_memory_mb: float
    min_success_rate_percent: float
    max_error_rate_percent: float = 5.0


@dataclass
class TestScenario:
    """Performance test scenario configuration."""
    name: str
    description: str
    test_type: TestType
    severity: TestSeverity
    endpoint: str
    method: str = "GET"
    data: Optional[Dict] = None
    headers: Optional[Dict] = None
    concurrent_users: int = 10
    requests_per_user: int = 10
    duration_seconds: Optional[int] = None
    thresholds: Optional[PerformanceThreshold] = None
    warmup_requests: int = 5
    cooldown_seconds: int = 2


@dataclass
class PerformanceReport:
    """Performance test report."""
    scenario_name: str
    test_type: TestType
    severity: TestSeverity
    start_time: str
    end_time: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate_percent: float
    average_response_time_ms: float
    median_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    max_response_time_ms: float
    min_response_time_ms: float
    requests_per_second: float
    average_cpu_percent: float
    max_cpu_percent: float
    average_memory_mb: float
    max_memory_mb: float
    errors: List[str] = field(default_factory=list)
    threshold_violations: List[str] = field(default_factory=list)
    passed: bool = True


class PerformanceConfig:
    """Performance testing configuration manager."""
    
    def __init__(self):
        self.scenarios: Dict[str, TestScenario] = {}
        self.default_thresholds: Dict[TestType, PerformanceThreshold] = {}
        self._setup_default_thresholds()
        self._setup_default_scenarios()
    
    def _setup_default_thresholds(self):
        """Setup default performance thresholds."""
        self.default_thresholds = {
            TestType.LOAD: PerformanceThreshold(
                max_response_time_ms=1000,
                min_throughput_rps=10,
                max_cpu_percent=70,
                max_memory_mb=200,
                min_success_rate_percent=95
            ),
            TestType.STRESS: PerformanceThreshold(
                max_response_time_ms=2000,
                min_throughput_rps=5,
                max_cpu_percent=90,
                max_memory_mb=300,
                min_success_rate_percent=90
            ),
            TestType.SPIKE: PerformanceThreshold(
                max_response_time_ms=3000,
                min_throughput_rps=2,
                max_cpu_percent=95,
                max_memory_mb=400,
                min_success_rate_percent=80
            ),
            TestType.VOLUME: PerformanceThreshold(
                max_response_time_ms=2000,
                min_throughput_rps=5,
                max_cpu_percent=80,
                max_memory_mb=500,
                min_success_rate_percent=90
            ),
            TestType.ENDURANCE: PerformanceThreshold(
                max_response_time_ms=1500,
                min_throughput_rps=8,
                max_cpu_percent=75,
                max_memory_mb=250,
                min_success_rate_percent=95
            ),
            TestType.MEMORY: PerformanceThreshold(
                max_response_time_ms=1000,
                min_throughput_rps=10,
                max_cpu_percent=70,
                max_memory_mb=150,
                min_success_rate_percent=95
            ),
            TestType.CPU: PerformanceThreshold(
                max_response_time_ms=1000,
                min_throughput_rps=10,
                max_cpu_percent=60,
                max_memory_mb=200,
                min_success_rate_percent=95
            )
        }
    
    def _setup_default_scenarios(self):
        """Setup default test scenarios."""
        # Health endpoint scenarios
        self.scenarios["health_load"] = TestScenario(
            name="Health Endpoint Load Test",
            description="Test health endpoint under normal load",
            test_type=TestType.LOAD,
            severity=TestSeverity.MEDIUM,
            endpoint="/api/v1/health",
            concurrent_users=20,
            requests_per_user=50,
            thresholds=self.default_thresholds[TestType.LOAD]
        )
        
        self.scenarios["health_stress"] = TestScenario(
            name="Health Endpoint Stress Test",
            description="Test health endpoint under high stress",
            test_type=TestType.STRESS,
            severity=TestSeverity.HIGH,
            endpoint="/api/v1/health",
            concurrent_users=50,
            requests_per_user=100,
            thresholds=self.default_thresholds[TestType.STRESS]
        )
        
        self.scenarios["health_spike"] = TestScenario(
            name="Health Endpoint Spike Test",
            description="Test health endpoint under sudden load spikes",
            test_type=TestType.SPIKE,
            severity=TestSeverity.HIGH,
            endpoint="/api/v1/health",
            concurrent_users=100,
            requests_per_user=50,
            thresholds=self.default_thresholds[TestType.SPIKE]
        )
        
        # Projects endpoint scenarios
        self.scenarios["projects_load"] = TestScenario(
            name="Projects Endpoint Load Test",
            description="Test projects list endpoint under normal load",
            test_type=TestType.LOAD,
            severity=TestSeverity.MEDIUM,
            endpoint="/api/v1/projects",
            concurrent_users=15,
            requests_per_user=20,
            thresholds=self.default_thresholds[TestType.LOAD]
        )
        
        self.scenarios["projects_volume"] = TestScenario(
            name="Projects Endpoint Volume Test",
            description="Test projects endpoint with large dataset",
            test_type=TestType.VOLUME,
            severity=TestSeverity.MEDIUM,
            endpoint="/api/v1/projects",
            concurrent_users=10,
            requests_per_user=30,
            thresholds=self.default_thresholds[TestType.VOLUME]
        )
        
        # Project creation scenarios
        self.scenarios["project_creation_load"] = TestScenario(
            name="Project Creation Load Test",
            description="Test project creation under load",
            test_type=TestType.LOAD,
            severity=TestSeverity.HIGH,
            endpoint="/api/v1/projects",
            method="POST",
            data={
                "name": "Load Test Project",
                "description": "Project created during load testing",
                "domain": "cloud-native"
            },
            concurrent_users=10,
            requests_per_user=5,
            thresholds=self.default_thresholds[TestType.LOAD]
        )
        
        # Workflow scenarios
        self.scenarios["workflow_load"] = TestScenario(
            name="Workflow Endpoint Load Test",
            description="Test workflow endpoints under load",
            test_type=TestType.LOAD,
            severity=TestSeverity.HIGH,
            endpoint="/api/v1/workflows",
            concurrent_users=8,
            requests_per_user=10,
            thresholds=self.default_thresholds[TestType.LOAD]
        )
        
        # Endurance scenarios
        self.scenarios["endurance_test"] = TestScenario(
            name="Endurance Test",
            description="Test system stability over extended period",
            test_type=TestType.ENDURANCE,
            severity=TestSeverity.CRITICAL,
            endpoint="/api/v1/health",
            concurrent_users=5,
            requests_per_user=100,
            duration_seconds=60,
            thresholds=self.default_thresholds[TestType.ENDURANCE]
        )
        
        # Memory scenarios
        self.scenarios["memory_test"] = TestScenario(
            name="Memory Usage Test",
            description="Test memory usage patterns under load",
            test_type=TestType.MEMORY,
            severity=TestSeverity.MEDIUM,
            endpoint="/api/v1/health",
            concurrent_users=20,
            requests_per_user=100,
            thresholds=self.default_thresholds[TestType.MEMORY]
        )
        
        # CPU scenarios
        self.scenarios["cpu_test"] = TestScenario(
            name="CPU Usage Test",
            description="Test CPU usage patterns under load",
            test_type=TestType.CPU,
            severity=TestSeverity.MEDIUM,
            endpoint="/api/v1/health",
            concurrent_users=25,
            requests_per_user=80,
            thresholds=self.default_thresholds[TestType.CPU]
        )
    
    def get_scenario(self, name: str) -> Optional[TestScenario]:
        """Get a test scenario by name."""
        return self.scenarios.get(name)
    
    def get_scenarios_by_type(self, test_type: TestType) -> List[TestScenario]:
        """Get all scenarios of a specific type."""
        return [scenario for scenario in self.scenarios.values() if scenario.test_type == test_type]
    
    def get_scenarios_by_severity(self, severity: TestSeverity) -> List[TestScenario]:
        """Get all scenarios of a specific severity."""
        return [scenario for scenario in self.scenarios.values() if scenario.severity == severity]
    
    def add_scenario(self, scenario: TestScenario):
        """Add a new test scenario."""
        self.scenarios[scenario.name] = scenario
    
    def remove_scenario(self, name: str):
        """Remove a test scenario."""
        if name in self.scenarios:
            del self.scenarios[name]
    
    def get_threshold(self, test_type: TestType) -> PerformanceThreshold:
        """Get performance threshold for a test type."""
        return self.default_thresholds.get(test_type, self.default_thresholds[TestType.LOAD])
    
    def set_threshold(self, test_type: TestType, threshold: PerformanceThreshold):
        """Set performance threshold for a test type."""
        self.default_thresholds[test_type] = threshold
    
    def validate_scenario(self, scenario: TestScenario) -> List[str]:
        """Validate a test scenario configuration."""
        errors = []
        
        if not scenario.name:
            errors.append("Scenario name is required")
        
        if not scenario.endpoint:
            errors.append("Scenario endpoint is required")
        
        if scenario.concurrent_users <= 0:
            errors.append("Concurrent users must be positive")
        
        if scenario.requests_per_user <= 0:
            errors.append("Requests per user must be positive")
        
        if scenario.duration_seconds is not None and scenario.duration_seconds <= 0:
            errors.append("Duration must be positive")
        
        if scenario.thresholds:
            if scenario.thresholds.max_response_time_ms <= 0:
                errors.append("Max response time must be positive")
            
            if scenario.thresholds.min_throughput_rps <= 0:
                errors.append("Min throughput must be positive")
            
            if scenario.thresholds.max_cpu_percent <= 0 or scenario.thresholds.max_cpu_percent > 100:
                errors.append("Max CPU percent must be between 0 and 100")
            
            if scenario.thresholds.max_memory_mb <= 0:
                errors.append("Max memory must be positive")
            
            if scenario.thresholds.min_success_rate_percent < 0 or scenario.thresholds.min_success_rate_percent > 100:
                errors.append("Min success rate must be between 0 and 100")
        
        return errors
    
    def get_scenario_summary(self) -> Dict[str, Any]:
        """Get a summary of all scenarios."""
        summary = {
            "total_scenarios": len(self.scenarios),
            "by_type": {},
            "by_severity": {},
            "scenarios": []
        }
        
        # Count by type
        for test_type in TestType:
            count = len(self.get_scenarios_by_type(test_type))
            summary["by_type"][test_type.value] = count
        
        # Count by severity
        for severity in TestSeverity:
            count = len(self.get_scenarios_by_severity(severity))
            summary["by_severity"][severity.value] = count
        
        # List all scenarios
        for scenario in self.scenarios.values():
            summary["scenarios"].append({
                "name": scenario.name,
                "type": scenario.test_type.value,
                "severity": scenario.severity.value,
                "endpoint": scenario.endpoint,
                "concurrent_users": scenario.concurrent_users,
                "requests_per_user": scenario.requests_per_user
            })
        
        return summary


# Global configuration instance
performance_config = PerformanceConfig()

