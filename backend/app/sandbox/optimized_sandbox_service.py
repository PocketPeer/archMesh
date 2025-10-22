"""
Optimized Sandbox Code Testing Service

This module implements an optimized version of the sandbox service with
enhanced performance, resource management, and scalability features.
"""

import asyncio
import os
import tempfile
import subprocess
import time
import uuid
import psutil
import re
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import queue
import weakref

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


@dataclass
class ExecutionMetrics:
    """Metrics for execution performance tracking"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0
    peak_memory_usage: float = 0.0
    peak_cpu_usage: float = 0.0
    concurrent_executions: int = 0
    max_concurrent_executions: int = 0


class ResourcePool:
    """Resource pool for managing execution resources"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.available_workers: Set[str] = set()
        self.busy_workers: Set[str] = set()
        self.worker_metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
        # Initialize worker pool
        for i in range(max_workers):
            worker_id = f"worker-{i}"
            self.available_workers.add(worker_id)
            self.worker_metrics[worker_id] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0.0,
                "last_used": None
            }
    
    def acquire_worker(self) -> Optional[str]:
        """Acquire an available worker"""
        with self._lock:
            if self.available_workers:
                worker_id = self.available_workers.pop()
                self.busy_workers.add(worker_id)
                self.worker_metrics[worker_id]["last_used"] = datetime.utcnow()
                return worker_id
            return None
    
    def release_worker(self, worker_id: str, execution_time: float, success: bool):
        """Release a worker and update metrics"""
        with self._lock:
            if worker_id in self.busy_workers:
                self.busy_workers.remove(worker_id)
                self.available_workers.add(worker_id)
                
                # Update metrics
                metrics = self.worker_metrics[worker_id]
                metrics["total_executions"] += 1
                if success:
                    metrics["successful_executions"] += 1
                else:
                    metrics["failed_executions"] += 1
                
                # Update average execution time
                total = metrics["total_executions"]
                current_avg = metrics["average_execution_time"]
                metrics["average_execution_time"] = (current_avg * (total - 1) + execution_time) / total
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status"""
        with self._lock:
            return {
                "available_workers": len(self.available_workers),
                "busy_workers": len(self.busy_workers),
                "total_workers": self.max_workers,
                "utilization_rate": len(self.busy_workers) / self.max_workers,
                "worker_metrics": self.worker_metrics.copy()
            }


class ExecutionCache:
    """Cache for execution results to improve performance"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        self._lock = threading.Lock()
    
    def _generate_cache_key(self, request: SandboxExecutionRequest) -> str:
        """Generate cache key for request"""
        import hashlib
        key_data = f"{request.language}:{request.code}:{request.execution_type}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, request: SandboxExecutionRequest) -> Optional[SandboxExecutionResponse]:
        """Get cached result for request"""
        cache_key = self._generate_cache_key(request)
        
        with self._lock:
            if cache_key in self.cache:
                # Check TTL
                if datetime.utcnow() - self.access_times[cache_key] < timedelta(seconds=self.ttl_seconds):
                    self.access_times[cache_key] = datetime.utcnow()
                    return SandboxExecutionResponse(**self.cache[cache_key])
                else:
                    # Expired, remove from cache
                    del self.cache[cache_key]
                    del self.access_times[cache_key]
        
        return None
    
    def put(self, request: SandboxExecutionRequest, response: SandboxExecutionResponse):
        """Put result in cache"""
        cache_key = self._generate_cache_key(request)
        
        with self._lock:
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[cache_key] = response.dict()
            self.access_times[cache_key] = datetime.utcnow()
    
    def clear(self):
        """Clear cache"""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": 0.0,  # Would need to track hits/misses
                "ttl_seconds": self.ttl_seconds
            }


class OptimizedSandboxService:
    """
    Optimized sandbox service with enhanced performance and resource management
    
    Features:
    - Resource pooling for efficient worker management
    - Execution result caching for improved performance
    - Async process management for better concurrency
    - Advanced metrics collection and monitoring
    - Batch execution support for high throughput
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None, max_workers: int = 10):
        """
        Initialize optimized sandbox service
        
        Args:
            config: Sandbox configuration
            max_workers: Maximum number of concurrent workers
        """
        self.config = config or SandboxConfig()
        self.max_workers = max_workers
        
        # Core components
        self.resource_pool = ResourcePool(max_workers)
        self.execution_cache = ExecutionCache()
        self.metrics = ExecutionMetrics()
        
        # Execution tracking
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.security_violations: List[Dict[str, Any]] = []
        
        # Thread pools for async operations
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        
        # Performance tracking
        self._performance_lock = threading.Lock()
        self._start_time = time.time()
        
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
        Execute code in optimized sandbox environment
        
        Args:
            request: Execution request
            
        Returns:
            SandboxExecutionResponse: Execution results
        """
        # Check cache first
        cached_result = self.execution_cache.get(request)
        if cached_result:
            return cached_result
        
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Acquire worker from pool
        worker_id = self.resource_pool.acquire_worker()
        if not worker_id:
            raise ExecutionError("No available workers in resource pool")
        
        try:
            # Validate request
            self._validate_request(request)
            
            # Track active execution
            self.active_executions[execution_id] = {
                "status": "running",
                "start_time": datetime.utcnow(),
                "request": request,
                "worker_id": worker_id
            }
            
            # Update concurrent execution metrics
            with self._performance_lock:
                self.metrics.concurrent_executions += 1
                self.metrics.max_concurrent_executions = max(
                    self.metrics.max_concurrent_executions,
                    self.metrics.concurrent_executions
                )
            
            # Execute code with optimized process management
            response = await self._execute_code_optimized(request, execution_id, worker_id)
            
            # Cache successful results
            if response.success:
                self.execution_cache.put(request, response)
            
            # Update metrics
            execution_time = time.time() - start_time
            with self._performance_lock:
                self.metrics.total_executions += 1
                if response.success:
                    self.metrics.successful_executions += 1
                else:
                    self.metrics.failed_executions += 1
                
                # Update average execution time
                total = self.metrics.total_executions
                current_avg = self.metrics.average_execution_time
                self.metrics.average_execution_time = (current_avg * (total - 1) + execution_time) / total
                
                # Update peak resource usage
                self.metrics.peak_memory_usage = max(
                    self.metrics.peak_memory_usage,
                    response.memory_usage_mb
                )
                self.metrics.peak_cpu_usage = max(
                    self.metrics.peak_cpu_usage,
                    response.cpu_usage_percent
                )
            
            # Record in history
            self.execution_history.append({
                "execution_id": execution_id,
                "status": "completed" if response.success else "failed",
                "success": response.success,
                "language": request.language,
                "execution_time": execution_time,
                "worker_id": worker_id,
                "timestamp": datetime.utcnow()
            })
            
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
                "worker_id": worker_id,
                "error": str(e),
                "timestamp": datetime.utcnow()
            })
            
            # Update metrics
            with self._performance_lock:
                self.metrics.total_executions += 1
                self.metrics.failed_executions += 1
            
            raise
        finally:
            # Release worker and update metrics
            self.resource_pool.release_worker(worker_id, execution_time, response.success if 'response' in locals() else False)
            
            # Update concurrent execution metrics
            with self._performance_lock:
                self.metrics.concurrent_executions -= 1
            
            # Cleanup
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _execute_code_optimized(self, request: SandboxExecutionRequest, execution_id: str, worker_id: str) -> SandboxExecutionResponse:
        """Execute code with optimized process management"""
        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write code to file
            code_file = self._write_code_to_file(request, temp_dir)
            
            # Perform security scan
            security_result = await self._perform_security_scan(request, code_file)
            
            # Execute code with async process management
            execution_result = await self._execute_code_file_async(request, code_file, temp_dir)
            
            # Perform performance testing if enabled
            performance_result = None
            if self.config.performance_testing_enabled:
                performance_result = await self._perform_performance_test(request, code_file, temp_dir)
            
            # Perform code quality analysis if enabled
            quality_result = None
            if self.config.code_quality_analysis_enabled:
                quality_result = await self._perform_quality_analysis(request, code_file)
            
            # Create response
            response = SandboxExecutionResponse(
                execution_id=execution_id,
                success=execution_result["success"] and security_result.passed,
                language=request.language,
                execution_type=request.execution_type,
                exit_code=execution_result["exit_code"],
                stdout=execution_result["stdout"],
                stderr=execution_result["stderr"],
                execution_time=execution_result["execution_time"],
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
            
            return response
    
    async def _execute_code_file_async(self, request: SandboxExecutionRequest, code_file: str, temp_dir: str) -> Dict[str, Any]:
        """Execute code file with async process management"""
        timeout = request.timeout or self.config.max_execution_time
        
        # Run subprocess in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.thread_pool,
            self._execute_code_file_sync,
            request, code_file, temp_dir, timeout
        )
        
        return result
    
    def _execute_code_file_sync(self, request: SandboxExecutionRequest, code_file: str, temp_dir: str, timeout: int) -> Dict[str, Any]:
        """Synchronous code execution (runs in thread pool)"""
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
                
                time.sleep(0.1)
            
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
                "execution_time": time.time() - start_time,
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
                "execution_time": 0,
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
                "resource_usage": {},
                "timeout_occurred": False,
                "memory_limit_exceeded": False
            }
    
    async def execute_batch(self, requests: List[SandboxExecutionRequest]) -> List[SandboxExecutionResponse]:
        """Execute multiple code requests in batch"""
        tasks = [self.execute_code(request) for request in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                # Create error response
                error_response = SandboxExecutionResponse(
                    execution_id=str(uuid.uuid4()),
                    success=False,
                    language=requests[i].language,
                    execution_type=requests[i].execution_type,
                    exit_code=-1,
                    stderr=str(response),
                    execution_time=0,
                    error_message=str(response)
                )
                results.append(error_response)
            else:
                results.append(response)
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        with self._performance_lock:
            uptime = time.time() - self._start_time
            return {
                "execution_metrics": {
                    "total_executions": self.metrics.total_executions,
                    "successful_executions": self.metrics.successful_executions,
                    "failed_executions": self.metrics.failed_executions,
                    "success_rate": self.metrics.successful_executions / max(1, self.metrics.total_executions),
                    "average_execution_time": self.metrics.average_execution_time,
                    "peak_memory_usage": self.metrics.peak_memory_usage,
                    "peak_cpu_usage": self.metrics.peak_cpu_usage,
                    "concurrent_executions": self.metrics.concurrent_executions,
                    "max_concurrent_executions": self.metrics.max_concurrent_executions
                },
                "resource_pool": self.resource_pool.get_pool_status(),
                "cache_stats": self.execution_cache.get_cache_stats(),
                "uptime_seconds": uptime,
                "executions_per_second": self.metrics.total_executions / max(1, uptime)
            }
    
    def clear_cache(self):
        """Clear execution cache"""
        self.execution_cache.clear()
    
    def shutdown(self):
        """Shutdown service and cleanup resources"""
        # Shutdown thread pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        # Clear cache
        self.clear_cache()
        
        # Clear active executions
        self.active_executions.clear()
    
    # Include all the helper methods from the original service
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
    
    async def _perform_performance_test(self, request: SandboxExecutionRequest, code_file: str, temp_dir: str) -> PerformanceResult:
        """Perform performance testing"""
        # Simple performance test - run code multiple times and measure
        start_time = time.time()
        memory_peak = 0
        cpu_avg = 0
        
        for _ in range(3):  # Run 3 times for average
            result = await self._execute_code_file_async(request, code_file, temp_dir)
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
    
    # Include all the management methods from the original service
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

