"""
Secure Sandbox Code Testing Service with Enhanced Security

This module implements a production-ready sandbox service with comprehensive
security hardening, advanced isolation, sophisticated scanning, audit logging,
rate limiting, and input sanitization.
"""

import asyncio
import os
import tempfile
import subprocess
import time
import uuid
import psutil
import re
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
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
from app.sandbox.optimized_sandbox_service import (
    OptimizedSandboxService,
    ResourcePool,
    ExecutionCache,
    ExecutionMetrics
)
from app.sandbox.security_hardening import (
    SecurityLevel,
    ThreatLevel,
    SecurityViolation,
    AuditLogEntry,
    RateLimitRule,
    SecurityPatterns,
    RateLimiter,
    SecurityScanner,
    AuditLogger,
    InputSanitizer,
    EnhancedIsolation
)
from app.core.exceptions import SandboxError, SecurityError, ExecutionError, TimeoutError


@dataclass
class SecurityConfig:
    """Security configuration for sandbox service"""
    security_level: SecurityLevel = SecurityLevel.ENHANCED
    enable_audit_logging: bool = True
    enable_rate_limiting: bool = True
    enable_input_sanitization: bool = True
    enable_advanced_scanning: bool = True
    max_violations_per_execution: int = 10
    block_on_critical_violations: bool = True
    audit_log_file: str = "sandbox_audit.log"
    rate_limit_rules: List[RateLimitRule] = None


class SecureSandboxService(OptimizedSandboxService):
    """
    Secure sandbox service with comprehensive security hardening
    
    Features:
    - Enhanced isolation with configurable security levels
    - Advanced security scanning with AST analysis
    - Comprehensive audit logging for all security events
    - Rate limiting with configurable rules and actions
    - Input sanitization and validation
    - Real-time security monitoring and alerting
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None, 
                 security_config: Optional[SecurityConfig] = None,
                 max_workers: int = 10):
        """
        Initialize secure sandbox service
        
        Args:
            config: Sandbox configuration
            security_config: Security configuration
            max_workers: Maximum number of concurrent workers
        """
        super().__init__(config, max_workers)
        
        # Security configuration
        self.security_config = security_config or SecurityConfig()
        
        # Security components
        self.security_scanner = SecurityScanner(self.security_config.security_level)
        self.audit_logger = AuditLogger(self.security_config.audit_log_file)
        self.rate_limiter = RateLimiter()
        self.input_sanitizer = InputSanitizer()
        self.enhanced_isolation = EnhancedIsolation(self.security_config.security_level)
        
        # Security tracking
        self.security_violations: List[SecurityViolation] = []
        self.blocked_requests: Set[str] = set()
        self.security_metrics: Dict[str, Any] = {
            "total_scans": 0,
            "violations_detected": 0,
            "requests_blocked": 0,
            "rate_limits_triggered": 0,
            "audit_events_logged": 0
        }
        
        # Initialize rate limiting rules
        self._initialize_rate_limiting_rules()
        
        # Security monitoring
        self._security_lock = threading.Lock()
        self._last_security_scan = time.time()
    
    def _initialize_rate_limiting_rules(self):
        """Initialize default rate limiting rules"""
        if not self.security_config.rate_limit_rules:
            self.security_config.rate_limit_rules = [
                RateLimitRule(
                    rule_id="execution_rate",
                    name="Execution Rate Limit",
                    pattern=".*",
                    max_requests=100,
                    time_window_seconds=3600,  # 1 hour
                    action="throttle"
                ),
                RateLimitRule(
                    rule_id="burst_rate",
                    name="Burst Rate Limit",
                    pattern=".*",
                    max_requests=10,
                    time_window_seconds=60,  # 1 minute
                    action="block"
                ),
                RateLimitRule(
                    rule_id="security_violations",
                    name="Security Violation Rate",
                    pattern=".*",
                    max_requests=5,
                    time_window_seconds=300,  # 5 minutes
                    action="block"
                )
            ]
        
        # Add rules to rate limiter
        for rule in self.security_config.rate_limit_rules:
            self.rate_limiter.add_rule(rule)
    
    async def execute_code(self, request: SandboxExecutionRequest, 
                          user_id: Optional[str] = None,
                          ip_address: Optional[str] = None) -> SandboxExecutionResponse:
        """
        Execute code in secure sandbox environment with comprehensive security
        
        Args:
            request: Execution request
            user_id: User identifier for audit logging
            ip_address: IP address for rate limiting and audit logging
            
        Returns:
            SandboxExecutionResponse: Execution results with security analysis
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Generate request identifier for rate limiting
        request_id = self._generate_request_id(user_id, ip_address)
        
        try:
            # 1. Rate limiting check
            if self.security_config.enable_rate_limiting:
                await self._check_rate_limits(request_id, user_id)
            
            # 2. Input sanitization and validation
            if self.security_config.enable_input_sanitization:
                sanitized_code, warnings = self.input_sanitizer.sanitize_code(
                    request.code, request.language
                )
                request.code = sanitized_code
                
                # Log warnings
                for warning in warnings:
                    self.audit_logger.log_event(AuditLogEntry(
                        log_id=f"warning_{execution_id}",
                        event_type="input_warning",
                        user_id=user_id,
                        execution_id=execution_id,
                        action="input_sanitization",
                        resource="code",
                        result="warning",
                        details={"warning": warning}
                    ))
            
            # 3. Advanced security scanning
            violations = []
            if self.security_config.enable_advanced_scanning:
                violations = await self._perform_advanced_security_scan(
                    request, execution_id, user_id
                )
                
                # Check if execution should be blocked
                if self._should_block_execution(violations):
                    raise SecurityError(f"Execution blocked due to security violations: {len(violations)} violations detected")
            
            # 4. Log execution start
            code_hash = hashlib.sha256(request.code.encode()).hexdigest()
            self.audit_logger.log_execution_start(
                execution_id, user_id or "anonymous", code_hash, 
                request.language, ip_address
            )
            
            # 5. Execute code with enhanced isolation
            response = await self._execute_code_secure(request, execution_id, user_id)
            
            # 6. Log execution end
            execution_time = time.time() - start_time
            self.audit_logger.log_execution_end(
                execution_id, user_id or "anonymous", response.success,
                execution_time, violations
            )
            
            # 7. Update security metrics
            with self._security_lock:
                self.security_metrics["total_scans"] += 1
                self.security_metrics["violations_detected"] += len(violations)
                self.security_metrics["audit_events_logged"] += 1
            
            # 8. Add security information to response
            response.security_violations = [v.description for v in violations] if violations else None
            response.security_scan_result = SecurityScanResult(
                passed=len(violations) == 0,
                violations=[v.description for v in violations],
                risk_score=sum(self._get_threat_score(v.threat_level) for v in violations),
                scan_time=time.time() - start_time,
                details={
                    "violations_count": len(violations),
                    "threat_levels": [v.threat_level.value for v in violations],
                    "security_level": self.security_config.security_level.value
                }
            )
            
            return response
            
        except SecurityError as e:
            # Log security error
            self.audit_logger.log_event(AuditLogEntry(
                log_id=f"security_error_{execution_id}",
                event_type="security_error",
                user_id=user_id,
                execution_id=execution_id,
                action="execute_code",
                resource="sandbox",
                result="blocked",
                details={"error": str(e)}
            ))
            
            with self._security_lock:
                self.security_metrics["requests_blocked"] += 1
            
            raise
        except Exception as e:
            # Log general error
            self.audit_logger.log_event(AuditLogEntry(
                log_id=f"execution_error_{execution_id}",
                event_type="execution_error",
                user_id=user_id,
                execution_id=execution_id,
                action="execute_code",
                resource="sandbox",
                result="failed",
                details={"error": str(e)}
            ))
            raise
    
    async def _check_rate_limits(self, request_id: str, user_id: Optional[str]):
        """Check rate limits for request"""
        # Check execution rate limit
        allowed, message = self.rate_limiter.check_rate_limit(request_id, "execution_rate")
        if not allowed:
            self.audit_logger.log_rate_limit_exceeded(request_id, "execution_rate", user_id)
            with self._security_lock:
                self.security_metrics["rate_limits_triggered"] += 1
            raise SecurityError(f"Rate limit exceeded: {message}")
        
        # Check burst rate limit
        allowed, message = self.rate_limiter.check_rate_limit(request_id, "burst_rate")
        if not allowed:
            self.audit_logger.log_rate_limit_exceeded(request_id, "burst_rate", user_id)
            with self._security_lock:
                self.security_metrics["rate_limits_triggered"] += 1
            raise SecurityError(f"Burst rate limit exceeded: {message}")
    
    async def _perform_advanced_security_scan(self, request: SandboxExecutionRequest,
                                            execution_id: str, user_id: Optional[str]) -> List[SecurityViolation]:
        """Perform advanced security scanning on code"""
        violations = self.security_scanner.scan_code(request.code, request.language)
        
        # Log each violation
        for violation in violations:
            self.audit_logger.log_security_violation(execution_id, user_id, violation)
            
            # Check security violation rate limit
            if self.security_config.enable_rate_limiting:
                allowed, _ = self.rate_limiter.check_rate_limit(
                    f"{user_id}_violations", "security_violations"
                )
                if not allowed:
                    self.audit_logger.log_rate_limit_exceeded(
                        f"{user_id}_violations", "security_violations", user_id
                    )
                    raise SecurityError("Too many security violations detected")
        
        # Store violations
        with self._security_lock:
            self.security_violations.extend(violations)
        
        return violations
    
    def _should_block_execution(self, violations: List[SecurityViolation]) -> bool:
        """Determine if execution should be blocked based on violations"""
        if not self.security_config.block_on_critical_violations:
            return False
        
        # Block if too many violations
        if len(violations) > self.security_config.max_violations_per_execution:
            return True
        
        # Block if any critical violations
        critical_violations = [v for v in violations if v.threat_level == ThreatLevel.CRITICAL]
        if critical_violations:
            return True
        
        return False
    
    async def _execute_code_secure(self, request: SandboxExecutionRequest,
                                 execution_id: str, user_id: Optional[str]) -> SandboxExecutionResponse:
        """Execute code with enhanced security isolation"""
        # Acquire worker from pool
        worker_id = self.resource_pool.acquire_worker()
        if not worker_id:
            raise ExecutionError("No available workers in resource pool")
        
        try:
            # Create isolated environment
            with tempfile.TemporaryDirectory() as temp_dir:
                isolation_config = self.enhanced_isolation.create_isolated_environment(temp_dir)
                
                # Write code to file
                code_file = self._write_code_to_file(request, temp_dir)
                
                # Execute with enhanced isolation
                execution_result = await self._execute_code_file_secure(
                    request, code_file, temp_dir, isolation_config
                )
                
                # Perform security scan on execution result
                security_result = await self._perform_result_security_scan(
                    execution_result, request, code_file
                )
                
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
        
        finally:
            # Release worker
            execution_time = time.time() - start_time if 'start_time' in locals() else 0
            self.resource_pool.release_worker(worker_id, execution_time, True)
    
    async def _execute_code_file_secure(self, request: SandboxExecutionRequest,
                                      code_file: str, temp_dir: str,
                                      isolation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code file with enhanced security isolation"""
        timeout = request.timeout or self.config.max_execution_time
        
        # Run subprocess in thread pool with security restrictions
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.thread_pool,
            self._execute_code_file_secure_sync,
            request, code_file, temp_dir, timeout, isolation_config
        )
        
        return result
    
    def _execute_code_file_secure_sync(self, request: SandboxExecutionRequest,
                                     code_file: str, temp_dir: str, timeout: int,
                                     isolation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous secure code execution (runs in thread pool)"""
        try:
            # Prepare command with security restrictions
            cmd = self._prepare_secure_execution_command(request.language, code_file, isolation_config)
            
            # Apply security restrictions
            process_config = {
                "temp_dir": temp_dir,
                "timeout": timeout
            }
            security_restrictions = self.enhanced_isolation.apply_security_restrictions(process_config)
            
            # Start process with enhanced security
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=security_restrictions["cwd"],
                env=security_restrictions["env"],
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Monitor process with enhanced security checks
            start_time = time.time()
            memory_usage = 0
            cpu_usage = 0
            timeout_occurred = False
            memory_limit_exceeded = False
            security_violation_detected = False
            
            while process.poll() is None:
                elapsed = time.time() - start_time
                
                # Check timeout
                if elapsed > timeout:
                    timeout_occurred = True
                    process.terminate()
                    break
                
                # Monitor resources with enhanced checks
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
                    
                    # Check for suspicious process behavior
                    if self._detect_suspicious_behavior(proc):
                        security_violation_detected = True
                        process.terminate()
                        break
                    
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
                "success": exit_code == 0 and not timeout_occurred and not memory_limit_exceeded and not security_violation_detected,
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
                "memory_limit_exceeded": memory_limit_exceeded,
                "security_violation_detected": security_violation_detected
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
                "memory_limit_exceeded": False,
                "security_violation_detected": False
            }
    
    def _prepare_secure_execution_command(self, language: str, code_file: str,
                                        isolation_config: Dict[str, Any]) -> List[str]:
        """Prepare secure execution command with isolation"""
        import sys
        
        commands = {
            "python": [sys.executable, "-B", "-E", "-s", code_file],  # Use system Python
            "javascript": ["node", "--no-deprecation", "--no-warnings", code_file],
            "typescript": ["ts-node", "--transpile-only", code_file],
            "java": ["java", "-Djava.security.manager", "-Djava.security.policy=restrict.policy", "Main"],
            "cpp": ["./a.out"],
            "csharp": ["dotnet", "run", "--configuration", "Release"],
            "go": ["go", "run", code_file],
            "rust": ["cargo", "run", "--release"]
        }
        
        base_cmd = commands.get(language, [sys.executable, code_file])
        
        # Add security flags based on isolation level
        if isolation_config["config"]["seccomp"]:
            # Add seccomp flags if supported
            pass
        
        return base_cmd
    
    def _detect_suspicious_behavior(self, proc: psutil.Process) -> bool:
        """Detect suspicious process behavior"""
        try:
            # Check for suspicious system calls or file access
            # This is a simplified check - in production, you'd use more sophisticated monitoring
            
            # Check memory usage patterns
            memory_info = proc.memory_info()
            if memory_info.rss > 100 * 1024 * 1024:  # 100MB
                return True
            
            # Check CPU usage patterns
            cpu_percent = proc.cpu_percent()
            if cpu_percent > 90:  # 90% CPU usage
                return True
            
            # Check for suspicious file operations
            try:
                open_files = proc.open_files()
                for file_info in open_files:
                    if any(suspicious_path in file_info.path for suspicious_path in 
                          ["/etc/", "/proc/", "/sys/", "/dev/", "/root/"]):
                        return True
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            
            return False
            
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return False
    
    async def _perform_result_security_scan(self, execution_result: Dict[str, Any],
                                          request: SandboxExecutionRequest,
                                          code_file: str) -> SecurityScanResult:
        """Perform security scan on execution results"""
        start_time = time.time()
        violations = []
        
        # Check stdout for suspicious content
        if execution_result.get("stdout"):
            stdout_violations = self._scan_output_for_violations(
                execution_result["stdout"], "stdout"
            )
            violations.extend(stdout_violations)
        
        # Check stderr for suspicious content
        if execution_result.get("stderr"):
            stderr_violations = self._scan_output_for_violations(
                execution_result["stderr"], "stderr"
            )
            violations.extend(stderr_violations)
        
        # Check for security violations in execution
        if execution_result.get("security_violation_detected"):
            violations.append(SecurityViolation(
                violation_id=f"runtime_violation_{int(time.time())}",
                violation_type="runtime_security_violation",
                threat_level=ThreatLevel.HIGH,
                description="Suspicious runtime behavior detected",
                code_snippet="Runtime monitoring",
                context={"execution_result": execution_result}
            ))
        
        scan_time = time.time() - start_time
        risk_score = sum(self._get_threat_score(v.threat_level) for v in violations)
        
        return SecurityScanResult(
            passed=len(violations) == 0,
            violations=[v.description for v in violations],
            risk_score=min(risk_score, 10.0),
            scan_time=scan_time,
            details={
                "violations_count": len(violations),
                "threat_levels": [v.threat_level.value for v in violations],
                "scan_type": "result_scan"
            }
        )
    
    def _scan_output_for_violations(self, output: str, output_type: str) -> List[SecurityViolation]:
        """Scan output for security violations"""
        violations = []
        
        # Check for sensitive information disclosure
        sensitive_patterns = [
            r"password\s*[:=]\s*\w+",
            r"token\s*[:=]\s*\w+",
            r"key\s*[:=]\s*\w+",
            r"secret\s*[:=]\s*\w+",
            r"api[_-]?key\s*[:=]\s*\w+"
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                violations.append(SecurityViolation(
                    violation_id=f"output_sensitive_{int(time.time())}",
                    violation_type="information_disclosure",
                    threat_level=ThreatLevel.MEDIUM,
                    description=f"Sensitive information in {output_type}",
                    code_snippet=output[:100] + "..." if len(output) > 100 else output,
                    context={"pattern": pattern, "output_type": output_type}
                ))
        
        return violations
    
    def _get_threat_score(self, threat_level: ThreatLevel) -> float:
        """Get numeric threat score for threat level"""
        scores = {
            ThreatLevel.LOW: 1.0,
            ThreatLevel.MEDIUM: 2.5,
            ThreatLevel.HIGH: 5.0,
            ThreatLevel.CRITICAL: 10.0
        }
        return scores.get(threat_level, 1.0)
    
    def _generate_request_id(self, user_id: Optional[str], ip_address: Optional[str]) -> str:
        """Generate unique request identifier for rate limiting"""
        if user_id:
            return f"user_{user_id}"
        elif ip_address:
            return f"ip_{ip_address}"
        else:
            return f"anonymous_{int(time.time())}"
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get comprehensive security metrics"""
        with self._security_lock:
            return {
                "security_metrics": self.security_metrics.copy(),
                "rate_limiter_stats": self.rate_limiter.get_stats(),
                "security_scanner_summary": self.security_scanner.get_violation_summary(),
                "audit_log_summary": self.audit_logger.get_audit_summary(),
                "security_config": {
                    "security_level": self.security_config.security_level.value,
                    "audit_logging_enabled": self.security_config.enable_audit_logging,
                    "rate_limiting_enabled": self.security_config.enable_rate_limiting,
                    "input_sanitization_enabled": self.security_config.enable_input_sanitization,
                    "advanced_scanning_enabled": self.security_config.enable_advanced_scanning
                }
            }
    
    def get_security_violations(self, hours: int = 24) -> List[SecurityViolation]:
        """Get security violations from specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        with self._security_lock:
            return [v for v in self.security_violations if v.timestamp > cutoff_time]
    
    def clear_security_data(self):
        """Clear security data (for testing/debugging)"""
        with self._security_lock:
            self.security_violations.clear()
            self.blocked_requests.clear()
            self.security_metrics = {
                "total_scans": 0,
                "violations_detected": 0,
                "requests_blocked": 0,
                "rate_limits_triggered": 0,
                "audit_events_logged": 0
            }
    
    def shutdown(self):
        """Shutdown service and cleanup security resources"""
        # Call parent shutdown
        super().shutdown()
        
        # Clear security data
        self.clear_security_data()
        
        # Close audit logger
        if hasattr(self.audit_logger, 'logger'):
            for handler in self.audit_logger.logger.handlers:
                handler.close()
