"""
Models for Sandbox Code Testing

This module defines the data models for sandbox code execution,
testing, security scanning, and performance analysis.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ExecutionType(str, Enum):
    """Types of code execution"""
    RUN = "run"
    TEST = "test"
    PERFORMANCE_TEST = "performance_test"
    QUALITY_ANALYSIS = "quality_analysis"
    SECURITY_SCAN = "security_scan"


class Language(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"


class SecurityViolationType(str, Enum):
    """Types of security violations"""
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"
    SYSTEM_COMMAND = "system_command"
    MEMORY_VIOLATION = "memory_violation"
    CPU_VIOLATION = "cpu_violation"
    TIMEOUT_VIOLATION = "timeout_violation"
    UNAUTHORIZED_IMPORT = "unauthorized_import"
    DANGEROUS_FUNCTION = "dangerous_function"


class TestResult(BaseModel):
    """Result of test execution"""
    
    test_name: str = Field(..., description="Name of the test")
    passed: bool = Field(..., description="Whether the test passed")
    execution_time: float = Field(..., description="Time taken to execute the test")
    error_message: Optional[str] = Field(None, description="Error message if test failed")
    output: Optional[str] = Field(None, description="Test output")
    passed_tests: List[str] = Field(default_factory=list, description="List of passed tests")
    failed_tests: List[str] = Field(default_factory=list, description="List of failed tests")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SecurityScanResult(BaseModel):
    """Result of security scan"""
    
    passed: bool = Field(..., description="Whether security scan passed")
    violations: List[str] = Field(default_factory=list, description="List of security violations")
    risk_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Risk score from 0-10")
    scan_time: float = Field(..., description="Time taken for security scan")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed scan results")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PerformanceResult(BaseModel):
    """Result of performance testing"""
    
    execution_time: float = Field(..., description="Total execution time in seconds")
    memory_peak_mb: float = Field(..., description="Peak memory usage in MB")
    memory_avg_mb: float = Field(..., description="Average memory usage in MB")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")
    io_operations: int = Field(default=0, description="Number of I/O operations")
    network_requests: int = Field(default=0, description="Number of network requests")
    passed: bool = Field(..., description="Whether performance test passed")
    benchmarks: Dict[str, float] = Field(default_factory=dict, description="Performance benchmarks")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CodeQualityResult(BaseModel):
    """Result of code quality analysis"""
    
    complexity_score: float = Field(..., ge=0.0, le=10.0, description="Code complexity score")
    maintainability_score: float = Field(..., ge=0.0, le=10.0, description="Maintainability score")
    test_coverage: float = Field(..., ge=0.0, le=100.0, description="Test coverage percentage")
    code_duplication: float = Field(..., ge=0.0, le=100.0, description="Code duplication percentage")
    style_score: float = Field(..., ge=0.0, le=10.0, description="Code style score")
    documentation_score: float = Field(..., ge=0.0, le=10.0, description="Documentation score")
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall quality score")
    issues: List[str] = Field(default_factory=list, description="List of quality issues")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SandboxConfig(BaseModel):
    """Configuration for sandbox environment"""
    
    max_execution_time: int = Field(default=60, ge=1, le=300, description="Maximum execution time in seconds")
    max_memory_mb: int = Field(default=1024, ge=64, le=8192, description="Maximum memory usage in MB")
    max_cpu_percent: int = Field(default=80, ge=10, le=100, description="Maximum CPU usage percentage")
    enable_network_access: bool = Field(default=False, description="Whether to allow network access")
    enable_file_system_access: bool = Field(default=True, description="Whether to allow file system access")
    allowed_file_extensions: List[str] = Field(
        default_factory=lambda: [".py", ".js", ".ts", ".java", ".cpp", ".cs", ".go", ".rs"],
        description="Allowed file extensions"
    )
    max_file_size_mb: int = Field(default=10, ge=1, le=100, description="Maximum file size in MB")
    security_scan_enabled: bool = Field(default=True, description="Whether to enable security scanning")
    performance_testing_enabled: bool = Field(default=True, description="Whether to enable performance testing")
    code_quality_analysis_enabled: bool = Field(default=True, description="Whether to enable code quality analysis")
    isolation_level: str = Field(default="container", description="Isolation level: container, process, thread")
    cleanup_after_execution: bool = Field(default=True, description="Whether to cleanup after execution")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SandboxExecutionRequest(BaseModel):
    """Request for sandbox code execution"""
    
    code: str = Field(..., min_length=1, max_length=100000, description="Code to execute")
    language: str = Field(..., description="Programming language")
    test_code: Optional[str] = Field(None, description="Test code to run")
    execution_type: ExecutionType = Field(default=ExecutionType.RUN, description="Type of execution")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="Execution timeout in seconds")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    input_data: Optional[str] = Field(None, description="Input data for the code")
    expected_output: Optional[str] = Field(None, description="Expected output")
    performance_thresholds: Dict[str, float] = Field(default_factory=dict, description="Performance thresholds")
    security_requirements: List[str] = Field(default_factory=list, description="Security requirements")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SandboxExecutionResponse(BaseModel):
    """Response from sandbox code execution"""
    
    execution_id: str = Field(..., description="Unique execution identifier")
    success: bool = Field(..., description="Whether execution was successful")
    language: str = Field(..., description="Programming language used")
    execution_type: ExecutionType = Field(..., description="Type of execution performed")
    
    # Execution results
    exit_code: int = Field(..., description="Exit code of the execution")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error output")
    execution_time: float = Field(..., description="Total execution time in seconds")
    
    # Resource usage
    memory_usage_mb: float = Field(default=0.0, description="Memory usage in MB")
    cpu_usage_percent: float = Field(default=0.0, description="CPU usage percentage")
    resource_usage: Dict[str, Any] = Field(default_factory=dict, description="Detailed resource usage")
    
    # Test results
    test_results: Optional[TestResult] = Field(None, description="Test execution results")
    passed_tests: List[str] = Field(default_factory=list, description="List of passed tests")
    failed_tests: List[str] = Field(default_factory=list, description="List of failed tests")
    
    # Security results
    security_scan_passed: bool = Field(default=True, description="Whether security scan passed")
    security_violations: Optional[List[str]] = Field(None, description="List of security violations")
    security_scan_result: Optional[SecurityScanResult] = Field(None, description="Detailed security scan results")
    
    # Performance results
    performance_test_passed: bool = Field(default=True, description="Whether performance test passed")
    performance_results: Optional[PerformanceResult] = Field(None, description="Performance test results")
    
    # Code quality results
    code_quality_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Code quality score")
    code_quality_results: Optional[CodeQualityResult] = Field(None, description="Code quality analysis results")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    timeout_occurred: bool = Field(default=False, description="Whether execution timed out")
    memory_limit_exceeded: bool = Field(default=False, description="Whether memory limit was exceeded")
    file_size_exceeded: bool = Field(default=False, description="Whether file size limit was exceeded")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")
    sandbox_version: str = Field(default="1.0.0", description="Sandbox service version")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
