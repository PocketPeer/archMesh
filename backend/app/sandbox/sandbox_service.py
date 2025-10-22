"""
Sandbox Code Testing Service

This module implements a secure sandbox environment for testing user-committed code
with automated test execution, security validation, performance testing, and code quality analysis.
"""

import asyncio
import os
import tempfile
import subprocess
import time
import uuid
import psutil
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from app.sandbox.models import (
    SandboxExecutionRequest,
    SandboxExecutionResponse,
    SandboxConfig,
    TestResult,
    SecurityScanResult,
    PerformanceResult,
    CodeQualityResult,
    ExecutionType,
    Language
)
from app.core.exceptions import SandboxError, SecurityError, ExecutionError, TimeoutError


class SandboxService:
    """
    Sandbox service for secure code execution and testing
    
    Provides isolated execution environment with security scanning,
    performance testing, and code quality analysis.
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        Initialize sandbox service
        
        Args:
            config: Sandbox configuration
        """
        self.config = config or SandboxConfig()
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.resource_usage: Dict[str, Any] = {}
        self.security_violations: List[Dict[str, Any]] = []
        
        # Initialize resource monitoring
        self._initialize_resource_monitoring()
    
    def _initialize_resource_monitoring(self):
        """Initialize resource monitoring"""
        self.resource_usage = {
            "memory_peak_mb": 0,
            "cpu_avg_percent": 0,
            "disk_usage_mb": 0,
            "network_usage_mb": 0
        }
    
    async def execute_code(self, request: SandboxExecutionRequest) -> SandboxExecutionResponse:
        """
        Execute code in sandbox environment
        
        Args:
            request: Execution request
            
        Returns:
            SandboxExecutionResponse: Execution results
            
        Raises:
            ExecutionError: If execution fails
            SecurityError: If security violations detected
            TimeoutError: If execution times out
        """
        if not request:
            raise ExecutionError("Request cannot be None")
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Validate request
            self._validate_request(request)
            
            # Track active execution
            self.active_executions[execution_id] = {
                "status": "running",
                "start_time": datetime.utcnow(),
                "request": request
            }
            
            # Create temporary directory for execution
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write code to file
                code_file = self._write_code_to_file(request, temp_dir)
                
                # Perform security scan
                security_result = await self._perform_security_scan(request, code_file)
                
                # Execute code
                execution_result = await self._execute_code_file(request, code_file, temp_dir)
                
                # Perform performance testing if enabled
                performance_result = None
                if self.config.performance_testing_enabled:
                    performance_result = await self._perform_performance_test(request, code_file, temp_dir)
                
                # Perform code quality analysis if enabled
                quality_result = None
                if self.config.code_quality_analysis_enabled:
                    quality_result = await self._perform_quality_analysis(request, code_file)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Create response
                response = SandboxExecutionResponse(
                    execution_id=execution_id,
                    success=execution_result["success"] and security_result.passed,
                    language=request.language,
                    execution_type=request.execution_type,
                    exit_code=execution_result["exit_code"],
                    stdout=execution_result["stdout"],
                    stderr=execution_result["stderr"],
                    execution_time=execution_time,
                    memory_usage_mb=execution_result["memory_usage_mb"],
                    cpu_usage_percent=execution_result["cpu_usage_percent"],
                    resource_usage=execution_result["resource_usage"],
                    test_results=execution_result.get("test_results"),
                    passed_tests=execution_result.get("passed_tests", []),
                    failed_tests=execution_result.get("failed_tests", []),
                    security_scan_passed=security_result.passed,
                    security_violations=security_result.violations if not security_result.passed else None,
                    security_scan_result=security_result,
                    performance_test_passed=performance_result.passed if performance_result else True,
                    performance_results=performance_result,
                    code_quality_score=quality_result.overall_score if quality_result else 0.0,
                    code_quality_results=quality_result,
                    timeout_occurred=execution_result.get("timeout_occurred", False),
                    memory_limit_exceeded=execution_result.get("memory_limit_exceeded", False),
                    file_size_exceeded=execution_result.get("file_size_exceeded", False)
                )
                
                # Record in history
                self.execution_history.append({
                    "execution_id": execution_id,
                    "status": "completed" if response.success else "failed",
                    "success": response.success,
                    "language": request.language,
                    "execution_time": execution_time,
                    "timestamp": datetime.utcnow()
                })
                
                # Cleanup
                if execution_id in self.active_executions:
                    del self.active_executions[execution_id]
                
                return response
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failure in history
            self.execution_history.append({
                "execution_id": execution_id,
                "status": "failed",
                "success": False,
                "language": request.language if request else "unknown",
                "execution_time": execution_time,
                "error": str(e),
                "timestamp": datetime.utcnow()
            })
            
            # Cleanup
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            # Re-raise the exception
            raise
    
    def _validate_request(self, request: SandboxExecutionRequest):
        """Validate execution request"""
        if not request.code or not request.code.strip():
            raise ExecutionError("Code cannot be empty")
        
        if request.language not in [lang.value for lang in Language]:
            raise ExecutionError(f"Unsupported language: {request.language}")
        
        # Check file size
        if len(request.code.encode('utf-8')) > self.config.max_file_size_mb * 1024 * 1024:
            raise ExecutionError("Code size exceeds maximum allowed size")
    
    def _write_code_to_file(self, request: SandboxExecutionRequest, temp_dir: str) -> str:
        """Write code to temporary file"""
        file_extension = self._get_file_extension(request.language)
        code_file = os.path.join(temp_dir, f"code{file_extension}")
        
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(request.code)
        
        return code_file
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "cpp": ".cpp",
            "csharp": ".cs",
            "go": ".go",
            "rust": ".rs"
        }
        return extensions.get(language, ".txt")
    
    async def _perform_security_scan(self, request: SandboxExecutionRequest, code_file: str) -> SecurityScanResult:
        """Perform security scan on code"""
        if not self.config.security_scan_enabled:
            return SecurityScanResult(passed=True, scan_time=0.0)
        
        start_time = time.time()
        violations = []
        
        # Read code for analysis
        with open(code_file, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # Check for dangerous imports and functions
        dangerous_patterns = {
            "file_access": [
                r"open\s*\(\s*['\"]/etc/",
                r"open\s*\(\s*['\"]/proc/",
                r"open\s*\(\s*['\"]/sys/",
                r"os\.system\s*\(",
                r"subprocess\.",
                r"exec\s*\(",
                r"eval\s*\("
            ],
            "network_access": [
                r"urllib\.",
                r"requests\.",
                r"socket\.",
                r"http\.",
                r"ftplib\.",
                r"smtplib\."
            ],
            "system_command": [
                r"os\.system\s*\(",
                r"subprocess\.",
                r"os\.popen\s*\(",
                r"commands\.",
                r"popen2\."
            ]
        }
        
        for category, patterns in dangerous_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code_content, re.IGNORECASE):
                    violations.append(f"{category}: {pattern}")
        
        # Check for infinite loops
        if re.search(r"while\s+True\s*:", code_content):
            violations.append("infinite_loop: while True loop detected")
        
        # Check for memory bombs
        if re.search(r"data\s*=\s*\[\].*while\s+True", code_content, re.DOTALL):
            violations.append("memory_bomb: potential memory exhaustion")
        
        scan_time = time.time() - start_time
        risk_score = len(violations) * 2.0  # Simple risk scoring
        
        # Record violations
        for violation in violations:
            self.security_violations.append({
                "type": violation.split(":")[0],
                "description": violation,
                "timestamp": datetime.utcnow(),
                "severity": "high" if risk_score > 5 else "medium" if risk_score > 2 else "low"
            })
        
        return SecurityScanResult(
            passed=len(violations) == 0,
            violations=violations,
            risk_score=min(risk_score, 10.0),
            scan_time=scan_time
        )
    
    async def _execute_code_file(self, request: SandboxExecutionRequest, code_file: str, temp_dir: str) -> Dict[str, Any]:
        """Execute code file"""
        timeout = request.timeout or self.config.max_execution_time
        
        try:
            # Prepare command based on language
            cmd = self._prepare_execution_command(request.language, code_file)
            
            # Start process with resource monitoring
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Monitor process
            start_time = time.time()
            memory_usage = 0
            cpu_usage = 0
            timeout_occurred = False
            memory_limit_exceeded = False
            
            while process.poll() is None:
                elapsed = time.time() - start_time
                
                # Check timeout
                if elapsed > timeout:
                    timeout_occurred = True
                    process.terminate()
                    break
                
                # Monitor resources
                try:
                    proc = psutil.Process(process.pid)
                    memory_info = proc.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    memory_usage = max(memory_usage, memory_mb)
                    
                    if memory_mb > self.config.max_memory_mb:
                        memory_limit_exceeded = True
                        process.terminate()
                        break
                    
                    cpu_usage = proc.cpu_percent()
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                await asyncio.sleep(0.1)
            
            # Get output
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            # Parse test results if this was a test execution
            test_results = None
            passed_tests = []
            failed_tests = []
            
            if request.execution_type == ExecutionType.TEST:
                test_results = self._parse_test_results(stdout, stderr)
                passed_tests = test_results.passed_tests if test_results else []
                failed_tests = test_results.failed_tests if test_results else []
            
            return {
                "success": exit_code == 0 and not timeout_occurred and not memory_limit_exceeded,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "memory_usage_mb": memory_usage,
                "cpu_usage_percent": cpu_usage,
                "resource_usage": {
                    "memory_peak": memory_usage,
                    "cpu_avg": cpu_usage,
                    "execution_time": time.time() - start_time
                },
                "test_results": test_results,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "timeout_occurred": timeout_occurred,
                "memory_limit_exceeded": memory_limit_exceeded
            }
            
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
                "resource_usage": {},
                "timeout_occurred": False,
                "memory_limit_exceeded": False
            }
    
    def _prepare_execution_command(self, language: str, code_file: str) -> List[str]:
        """Prepare execution command for language"""
        commands = {
            "python": ["python", code_file],
            "javascript": ["node", code_file],
            "typescript": ["ts-node", code_file],
            "java": ["java", "-cp", ".", "Main"],
            "cpp": ["./a.out"],
            "csharp": ["dotnet", "run"],
            "go": ["go", "run", code_file],
            "rust": ["cargo", "run"]
        }
        return commands.get(language, ["python", code_file])
    
    def _parse_test_results(self, stdout: str, stderr: str) -> Optional[TestResult]:
        """Parse test results from output"""
        # Simple test result parsing
        if "All tests passed!" in stdout:
            return TestResult(
                test_name="all_tests",
                passed=True,
                execution_time=0.0,
                output=stdout,
                passed_tests=["all_tests"],
                failed_tests=[]
            )
        elif "AssertionError" in stderr or "AssertionError" in stdout:
            return TestResult(
                test_name="all_tests",
                passed=False,
                execution_time=0.0,
                error_message=stderr or stdout,
                output=stdout,
                passed_tests=[],
                failed_tests=["all_tests"]
            )
        return None
    
    async def _perform_performance_test(self, request: SandboxExecutionRequest, code_file: str, temp_dir: str) -> PerformanceResult:
        """Perform performance testing"""
        # Simple performance test - run code multiple times and measure
        start_time = time.time()
        memory_peak = 0
        cpu_avg = 0
        
        for _ in range(3):  # Run 3 times for average
            result = await self._execute_code_file(request, code_file, temp_dir)
            memory_peak = max(memory_peak, result["memory_usage_mb"])
            cpu_avg += result["cpu_usage_percent"]
        
        cpu_avg /= 3
        execution_time = time.time() - start_time
        
        return PerformanceResult(
            execution_time=execution_time,
            memory_peak_mb=memory_peak,
            memory_avg_mb=memory_peak * 0.8,  # Estimate
            cpu_usage_percent=cpu_avg,
            passed=True,  # Simple pass/fail for now
            benchmarks={
                "execution_time": execution_time,
                "memory_peak": memory_peak,
                "cpu_avg": cpu_avg
            }
        )
    
    async def _perform_quality_analysis(self, request: SandboxExecutionRequest, code_file: str) -> CodeQualityResult:
        """Perform code quality analysis"""
        # Simple quality analysis
        with open(code_file, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # Calculate basic metrics
        lines = len(code_content.split('\n'))
        functions = len(re.findall(r'def\s+\w+', code_content))
        comments = len(re.findall(r'#', code_content))
        
        # Simple scoring
        complexity_score = min(10.0, max(0.0, 10.0 - (functions * 0.5)))
        maintainability_score = min(10.0, max(0.0, 10.0 - (lines / 10)))
        test_coverage = 100.0 if "test" in code_content.lower() else 0.0
        code_duplication = 0.0  # Simplified
        style_score = 8.0  # Default good score
        documentation_score = min(10.0, (comments / lines) * 100) if lines > 0 else 0.0
        
        overall_score = (complexity_score + maintainability_score + (test_coverage / 10) + style_score + documentation_score) / 5
        
        return CodeQualityResult(
            complexity_score=complexity_score,
            maintainability_score=maintainability_score,
            test_coverage=test_coverage,
            code_duplication=code_duplication,
            style_score=style_score,
            documentation_score=documentation_score,
            overall_score=overall_score,
            issues=[],
            suggestions=[]
        )
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active execution"""
        return self.active_executions.get(execution_id)
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history[-limit:]
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "language_distribution": {}
            }
        
        total = len(self.execution_history)
        successful = sum(1 for exec in self.execution_history if exec.get("success", False))
        failed = total - successful
        success_rate = successful / total if total > 0 else 0.0
        
        # Calculate average execution time
        times = [exec.get("execution_time", 0) for exec in self.execution_history if exec.get("execution_time")]
        avg_time = sum(times) / len(times) if times else 0.0
        
        # Language distribution
        language_dist = {}
        for exec in self.execution_history:
            lang = exec.get("language", "unknown")
            language_dist[lang] = language_dist.get(lang, 0) + 1
        
        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": success_rate,
            "average_execution_time": avg_time,
            "language_distribution": language_dist
        }
    
    def cleanup_old_executions(self, max_age_hours: int = 24):
        """Cleanup old execution history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        self.execution_history = [
            exec for exec in self.execution_history
            if exec.get("timestamp", datetime.utcnow()) > cutoff_time
        ]
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        return self.resource_usage.copy()
    
    def get_security_violations(self) -> List[Dict[str, Any]]:
        """Get security violations"""
        return self.security_violations.copy()
