"""
Security Hardening Components for Sandbox Service

This module implements enhanced security features for the sandbox service including
advanced isolation, sophisticated security scanning, audit logging, rate limiting,
and comprehensive input sanitization.
"""

import os
import re
import time
import hashlib
import logging
import threading
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import json
import ast
import subprocess
import tempfile
from pathlib import Path

from app.core.exceptions import SecurityError, SandboxError


class SecurityLevel(Enum):
    """Security isolation levels"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    STRICT = "strict"
    PARANOID = "paranoid"


class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityViolation:
    """Security violation record"""
    violation_id: str
    violation_type: str
    threat_level: ThreatLevel
    description: str
    code_snippet: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    mitigated: bool = False
    mitigation_action: Optional[str] = None


@dataclass
class AuditLogEntry:
    """Audit log entry for security events"""
    log_id: str
    event_type: str
    user_id: Optional[str]
    action: str
    resource: str
    result: str
    session_id: Optional[str] = None
    execution_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    rule_id: str
    name: str
    pattern: str
    max_requests: int
    time_window_seconds: int
    action: str  # "block", "throttle", "log"
    enabled: bool = True


class SecurityPatterns:
    """Security pattern definitions for code analysis"""
    
    # File system access patterns
    FILE_ACCESS_PATTERNS = {
        "dangerous_paths": [
            r"['\"]/etc/",
            r"['\"]/proc/",
            r"['\"]/sys/",
            r"['\"]/dev/",
            r"['\"]/root/",
            r"['\"]/home/",
            r"['\"]/var/log/",
            r"['\"]/usr/bin/",
            r"['\"]/bin/",
            r"['\"]/sbin/"
        ],
        "file_operations": [
            r"open\s*\(",
            r"file\s*\(",
            r"with\s+open\s*\(",
            r"os\.remove\s*\(",
            r"os\.unlink\s*\(",
            r"shutil\.rmtree\s*\(",
            r"os\.makedirs\s*\(",
            r"os\.mkdir\s*\(",
            r"os\.chmod\s*\(",
            r"os\.chown\s*\("
        ]
    }
    
    # Network access patterns
    NETWORK_PATTERNS = {
        "network_imports": [
            r"import\s+urllib",
            r"import\s+requests",
            r"import\s+socket",
            r"import\s+http",
            r"import\s+ftplib",
            r"import\s+smtplib",
            r"import\s+telnetlib",
            r"import\s+poplib",
            r"import\s+imaplib"
        ],
        "network_functions": [
            r"urllib\.",
            r"requests\.",
            r"socket\.",
            r"http\.",
            r"ftplib\.",
            r"smtplib\.",
            r"telnetlib\.",
            r"poplib\.",
            r"imaplib\."
        ]
    }
    
    # System command patterns
    SYSTEM_COMMAND_PATTERNS = {
        "dangerous_commands": [
            r"os\.system\s*\(",
            r"subprocess\.",
            r"os\.popen\s*\(",
            r"commands\.",
            r"popen2\.",
            r"os\.exec\w*\s*\(",
            r"os\.spawn\w*\s*\(",
            r"os\.fork\s*\(",
            r"os\.kill\s*\(",
            r"signal\."
        ],
        "shell_operations": [
            r"shell\s*=\s*True",
            r"shell\s*=\s*1",
            r"bash\s+",
            r"sh\s+",
            r"cmd\s+",
            r"powershell\s+"
        ]
    }
    
    # Code injection patterns
    INJECTION_PATTERNS = {
        "code_injection": [
            r"exec\s*\(",
            r"eval\s*\(",
            r"compile\s*\(",
            r"__import__\s*\(",
            r"getattr\s*\(",
            r"setattr\s*\(",
            r"delattr\s*\(",
            r"globals\s*\(",
            r"locals\s*\(",
            r"vars\s*\("
        ],
        "reflection": [
            r"getattr\s*\(",
            r"setattr\s*\(",
            r"hasattr\s*\(",
            r"delattr\s*\(",
            r"dir\s*\(",
            r"type\s*\(",
            r"isinstance\s*\(",
            r"issubclass\s*\("
        ]
    }
    
    # Resource exhaustion patterns
    RESOURCE_EXHAUSTION_PATTERNS = {
        "infinite_loops": [
            r"while\s+True\s*:",
            r"while\s+1\s*:",
            r"for\s+\w+\s+in\s+range\s*\(\s*float\s*\(\s*['\"]inf['\"]\s*\)\s*\)",
            r"for\s+\w+\s+in\s+itertools\.cycle\s*\("
        ],
        "memory_bombs": [
            r"data\s*=\s*\[\].*while\s+True",
            r"data\s*=\s*\{\}.*while\s+True",
            r"data\s*=\s*\[\].*for\s+\w+\s+in\s+range\s*\(\s*\d{6,}\s*\)",
            r"\.append\s*\(.*\)\s*for\s+\w+\s+in\s+range\s*\(\s*\d{6,}\s*\)"
        ],
        "recursion_bombs": [
            r"def\s+\w+\s*\([^)]*\)\s*:\s*\n\s*\w+\s*\([^)]*\)",
            r"def\s+\w+\s*\([^)]*\)\s*:\s*\n\s*return\s+\w+\s*\([^)]*\)"
        ]
    }


class RateLimiter:
    """Rate limiting implementation for sandbox requests"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.rules: Dict[str, RateLimitRule] = {}
        self.blocked_ips: Set[str] = set()
        self._lock = threading.Lock()
    
    def add_rule(self, rule: RateLimitRule):
        """Add a rate limiting rule"""
        with self._lock:
            self.rules[rule.rule_id] = rule
    
    def check_rate_limit(self, identifier: str, rule_id: str) -> Tuple[bool, str]:
        """
        Check if request is within rate limit
        
        Returns:
            (allowed, message)
        """
        with self._lock:
            if rule_id not in self.rules:
                return True, "No rule found"
            
            rule = self.rules[rule_id]
            if not rule.enabled:
                return True, "Rule disabled"
            
            now = time.time()
            window_start = now - rule.time_window_seconds
            
            # Clean old requests
            requests = self.requests[identifier]
            while requests and requests[0] < window_start:
                requests.popleft()
            
            # Check limit
            if len(requests) >= rule.max_requests:
                if rule.action == "block":
                    self.blocked_ips.add(identifier)
                    return False, f"Rate limit exceeded: {rule.name}"
                elif rule.action == "throttle":
                    return False, f"Rate limit exceeded: {rule.name}"
                else:  # log
                    return True, f"Rate limit exceeded: {rule.name} (logged)"
            
            # Add current request
            requests.append(now)
            return True, "Request allowed"
    
    def is_blocked(self, identifier: str) -> bool:
        """Check if identifier is blocked"""
        with self._lock:
            return identifier in self.blocked_ips
    
    def unblock(self, identifier: str):
        """Unblock an identifier"""
        with self._lock:
            self.blocked_ips.discard(identifier)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        with self._lock:
            return {
                "total_rules": len(self.rules),
                "active_rules": sum(1 for rule in self.rules.values() if rule.enabled),
                "blocked_identifiers": len(self.blocked_ips),
                "tracked_identifiers": len(self.requests)
            }


class SecurityScanner:
    """Advanced security scanner for code analysis"""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.ENHANCED):
        self.security_level = security_level
        self.violations: List[SecurityViolation] = []
        self.patterns = SecurityPatterns()
        self._lock = threading.Lock()
    
    def scan_code(self, code: str, language: str = "python") -> List[SecurityViolation]:
        """Perform comprehensive security scan on code"""
        violations = []
        
        # Basic syntax and structure analysis
        violations.extend(self._scan_syntax_issues(code, language))
        
        # Pattern-based scanning
        violations.extend(self._scan_dangerous_patterns(code, language))
        
        # AST-based analysis for Python
        if language == "python":
            violations.extend(self._scan_ast_patterns(code))
        
        # Resource exhaustion detection
        violations.extend(self._scan_resource_exhaustion(code))
        
        # Store violations
        with self._lock:
            self.violations.extend(violations)
        
        return violations
    
    def _scan_syntax_issues(self, code: str, language: str) -> List[SecurityViolation]:
        """Scan for syntax and basic security issues"""
        violations = []
        
        # Check for suspicious imports
        import_lines = [line for line in code.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]
        
        for i, line in enumerate(import_lines):
            if any(pattern in line.lower() for pattern in ['os', 'sys', 'subprocess', 'socket', 'urllib', 'requests']):
                violations.append(SecurityViolation(
                    violation_id=f"syntax_import_{i}",
                    violation_type="dangerous_import",
                    threat_level=ThreatLevel.MEDIUM,
                    description=f"Dangerous import detected: {line.strip()}",
                    code_snippet=line.strip(),
                    line_number=i + 1
                ))
        
        return violations
    
    def _scan_dangerous_patterns(self, code: str, language: str) -> List[SecurityViolation]:
        """Scan for dangerous code patterns"""
        violations = []
        lines = code.split('\n')
        
        # File access patterns
        for pattern in self.patterns.FILE_ACCESS_PATTERNS["dangerous_paths"]:
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(SecurityViolation(
                        violation_id=f"file_access_{i}",
                        violation_type="file_access_violation",
                        threat_level=ThreatLevel.HIGH,
                        description=f"Dangerous file path access: {pattern}",
                        code_snippet=line.strip(),
                        line_number=i + 1
                    ))
        
        # Network access patterns
        for pattern in self.patterns.NETWORK_PATTERNS["network_functions"]:
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(SecurityViolation(
                        violation_id=f"network_access_{i}",
                        violation_type="network_access_violation",
                        threat_level=ThreatLevel.HIGH,
                        description=f"Network access detected: {pattern}",
                        code_snippet=line.strip(),
                        line_number=i + 1
                    ))
        
        # System command patterns
        for pattern in self.patterns.SYSTEM_COMMAND_PATTERNS["dangerous_commands"]:
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(SecurityViolation(
                        violation_id=f"system_command_{i}",
                        violation_type="system_command_violation",
                        threat_level=ThreatLevel.CRITICAL,
                        description=f"System command execution: {pattern}",
                        code_snippet=line.strip(),
                        line_number=i + 1
                    ))
        
        # Code injection patterns
        for pattern in self.patterns.INJECTION_PATTERNS["code_injection"]:
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(SecurityViolation(
                        violation_id=f"code_injection_{i}",
                        violation_type="code_injection_violation",
                        threat_level=ThreatLevel.CRITICAL,
                        description=f"Code injection detected: {pattern}",
                        code_snippet=line.strip(),
                        line_number=i + 1
                    ))
        
        return violations
    
    def _scan_ast_patterns(self, code: str) -> List[SecurityViolation]:
        """Perform AST-based security analysis for Python code"""
        violations = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in ['exec', 'eval', 'compile', '__import__']:
                            violations.append(SecurityViolation(
                                violation_id=f"ast_injection_{node.lineno}",
                                violation_type="code_injection_violation",
                                threat_level=ThreatLevel.CRITICAL,
                                description=f"Dangerous function call: {func_name}",
                                code_snippet=ast.get_source_segment(code, node) or f"{func_name}(...)",
                                line_number=node.lineno,
                                column_number=node.col_offset
                            ))
                
                # Check for dangerous attribute access
                elif isinstance(node, ast.Attribute):
                    if node.attr in ['system', 'popen', 'exec', 'eval']:
                        violations.append(SecurityViolation(
                            violation_id=f"ast_attribute_{node.lineno}",
                            violation_type="system_command_violation",
                            threat_level=ThreatLevel.HIGH,
                            description=f"Dangerous attribute access: {node.attr}",
                            code_snippet=ast.get_source_segment(code, node) or f".{node.attr}",
                            line_number=node.lineno,
                            column_number=node.col_offset
                        ))
        
        except SyntaxError as e:
            violations.append(SecurityViolation(
                violation_id=f"syntax_error_{e.lineno}",
                violation_type="syntax_error",
                threat_level=ThreatLevel.MEDIUM,
                description=f"Syntax error: {e.msg}",
                code_snippet=code.split('\n')[e.lineno - 1] if e.lineno else "",
                line_number=e.lineno,
                column_number=e.offset
            ))
        
        return violations
    
    def _scan_resource_exhaustion(self, code: str) -> List[SecurityViolation]:
        """Scan for resource exhaustion patterns"""
        violations = []
        lines = code.split('\n')
        
        # Infinite loop detection
        for pattern in self.patterns.RESOURCE_EXHAUSTION_PATTERNS["infinite_loops"]:
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(SecurityViolation(
                        violation_id=f"infinite_loop_{i}",
                        violation_type="resource_exhaustion",
                        threat_level=ThreatLevel.HIGH,
                        description=f"Infinite loop detected: {pattern}",
                        code_snippet=line.strip(),
                        line_number=i + 1
                    ))
        
        # Memory bomb detection
        for pattern in self.patterns.RESOURCE_EXHAUSTION_PATTERNS["memory_bombs"]:
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE | re.DOTALL):
                    violations.append(SecurityViolation(
                        violation_id=f"memory_bomb_{i}",
                        violation_type="resource_exhaustion",
                        threat_level=ThreatLevel.HIGH,
                        description=f"Memory bomb detected: {pattern}",
                        code_snippet=line.strip(),
                        line_number=i + 1
                    ))
        
        return violations
    
    def get_violation_summary(self) -> Dict[str, Any]:
        """Get summary of security violations"""
        with self._lock:
            summary = {
                "total_violations": len(self.violations),
                "by_type": defaultdict(int),
                "by_threat_level": defaultdict(int),
                "recent_violations": []
            }
            
            for violation in self.violations:
                summary["by_type"][violation.violation_type] += 1
                summary["by_threat_level"][violation.threat_level.value] += 1
                
                # Recent violations (last 24 hours)
                if violation.timestamp > datetime.utcnow() - timedelta(hours=24):
                    summary["recent_violations"].append({
                        "id": violation.violation_id,
                        "type": violation.violation_type,
                        "threat_level": violation.threat_level.value,
                        "timestamp": violation.timestamp.isoformat()
                    })
            
            return dict(summary)


class AuditLogger:
    """Comprehensive audit logging for security events"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "sandbox_audit.log"
        self.logs: List[AuditLogEntry] = []
        self._lock = threading.Lock()
        
        # Setup logging
        self.logger = logging.getLogger("sandbox_audit")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_event(self, entry: AuditLogEntry):
        """Log a security event"""
        with self._lock:
            self.logs.append(entry)
            
            # Log to file
            log_message = json.dumps({
                "log_id": entry.log_id,
                "event_type": entry.event_type,
                "user_id": entry.user_id,
                "session_id": entry.session_id,
                "execution_id": entry.execution_id,
                "action": entry.action,
                "resource": entry.resource,
                "result": entry.result,
                "details": entry.details,
                "timestamp": entry.timestamp.isoformat(),
                "ip_address": entry.ip_address,
                "user_agent": entry.user_agent
            })
            
            self.logger.info(log_message)
    
    def log_execution_start(self, execution_id: str, user_id: str, code_hash: str, 
                           language: str, ip_address: Optional[str] = None):
        """Log execution start event"""
        entry = AuditLogEntry(
            log_id=f"exec_start_{execution_id}",
            event_type="execution_start",
            user_id=user_id,
            execution_id=execution_id,
            action="execute_code",
            resource="sandbox",
            result="started",
            details={
                "code_hash": code_hash,
                "language": language,
                "code_length": len(code_hash)
            },
            ip_address=ip_address
        )
        self.log_event(entry)
    
    def log_execution_end(self, execution_id: str, user_id: str, success: bool, 
                         execution_time: float, violations: List[SecurityViolation]):
        """Log execution end event"""
        entry = AuditLogEntry(
            log_id=f"exec_end_{execution_id}",
            event_type="execution_end",
            user_id=user_id,
            execution_id=execution_id,
            action="execute_code",
            resource="sandbox",
            result="completed" if success else "failed",
            details={
                "success": success,
                "execution_time": execution_time,
                "violations_count": len(violations),
                "violations": [
                    {
                        "type": v.violation_type,
                        "threat_level": v.threat_level.value,
                        "description": v.description
                    } for v in violations
                ]
            }
        )
        self.log_event(entry)
    
    def log_security_violation(self, execution_id: str, user_id: str, 
                              violation: SecurityViolation):
        """Log security violation event"""
        entry = AuditLogEntry(
            log_id=f"violation_{violation.violation_id}",
            event_type="security_violation",
            user_id=user_id,
            execution_id=execution_id,
            action="security_scan",
            resource="code",
            result="violation_detected",
            details={
                "violation_type": violation.violation_type,
                "threat_level": violation.threat_level.value,
                "description": violation.description,
                "line_number": violation.line_number,
                "code_snippet": violation.code_snippet
            }
        )
        self.log_event(entry)
    
    def log_rate_limit_exceeded(self, identifier: str, rule_id: str, 
                               user_id: Optional[str] = None):
        """Log rate limit exceeded event"""
        entry = AuditLogEntry(
            log_id=f"rate_limit_{int(time.time())}",
            event_type="rate_limit_exceeded",
            user_id=user_id,
            action="rate_limit_check",
            resource="sandbox",
            result="blocked",
            details={
                "identifier": identifier,
                "rule_id": rule_id
            }
        )
        self.log_event(entry)
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit log summary for specified time period"""
        with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_logs = [log for log in self.logs if log.timestamp > cutoff_time]
            
            summary = {
                "total_events": len(recent_logs),
                "by_event_type": defaultdict(int),
                "by_result": defaultdict(int),
                "by_user": defaultdict(int),
                "security_violations": 0,
                "rate_limit_violations": 0,
                "execution_events": 0
            }
            
            for log in recent_logs:
                summary["by_event_type"][log.event_type] += 1
                summary["by_result"][log.result] += 1
                if log.user_id:
                    summary["by_user"][log.user_id] += 1
                
                if log.event_type == "security_violation":
                    summary["security_violations"] += 1
                elif log.event_type == "rate_limit_exceeded":
                    summary["rate_limit_violations"] += 1
                elif log.event_type in ["execution_start", "execution_end"]:
                    summary["execution_events"] += 1
            
            return dict(summary)


class InputSanitizer:
    """Advanced input sanitization and validation"""
    
    def __init__(self):
        self.max_code_length = 100000  # 100KB
        self.max_line_length = 1000
        self.allowed_languages = {"python", "javascript", "typescript", "java", "cpp", "csharp", "go", "rust"}
        self.dangerous_keywords = {
            "python": ["__import__", "exec", "eval", "compile", "globals", "locals", "vars"],
            "javascript": ["eval", "Function", "setTimeout", "setInterval", "document", "window"],
            "typescript": ["eval", "Function", "setTimeout", "setInterval", "document", "window"],
            "java": ["Runtime", "ProcessBuilder", "System", "Class", "Method"],
            "cpp": ["system", "exec", "popen", "fork", "execv"],
            "csharp": ["Process", "ProcessStartInfo", "Assembly", "Type"],
            "go": ["os/exec", "syscall", "unsafe", "reflect"],
            "rust": ["std::process", "std::thread", "std::sync"]
        }
    
    def sanitize_code(self, code: str, language: str) -> Tuple[str, List[str]]:
        """
        Sanitize and validate code input
        
        Returns:
            (sanitized_code, warnings)
        """
        warnings = []
        
        # Basic validation
        if not code or not code.strip():
            raise SecurityError("Code cannot be empty")
        
        if len(code) > self.max_code_length:
            raise SecurityError(f"Code too long: {len(code)} > {self.max_code_length}")
        
        if language not in self.allowed_languages:
            raise SecurityError(f"Unsupported language: {language}")
        
        # Line length validation
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if len(line) > self.max_line_length:
                warnings.append(f"Line {i+1} too long: {len(line)} > {self.max_line_length}")
        
        # Language-specific sanitization
        if language in self.dangerous_keywords:
            for keyword in self.dangerous_keywords[language]:
                if keyword in code:
                    warnings.append(f"Potentially dangerous keyword detected: {keyword}")
        
        # Remove null bytes and control characters
        sanitized_code = ''.join(char for char in code if ord(char) >= 32 or char in '\n\r\t')
        
        # Normalize line endings
        sanitized_code = sanitized_code.replace('\r\n', '\n').replace('\r', '\n')
        
        return sanitized_code, warnings
    
    def validate_execution_request(self, request_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate execution request data"""
        errors = []
        
        # Required fields
        required_fields = ["code", "language"]
        for field in required_fields:
            if field not in request_data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate language
        language = request_data.get("language")
        if language not in self.allowed_languages:
            errors.append(f"Unsupported language: {language}")
        
        # Validate code
        code = request_data.get("code", "")
        if not isinstance(code, str):
            errors.append("Code must be a string")
        elif len(code) > self.max_code_length:
            errors.append(f"Code too long: {len(code)} > {self.max_code_length}")
        
        # Validate timeout
        timeout = request_data.get("timeout")
        if timeout is not None:
            if not isinstance(timeout, (int, float)) or timeout <= 0 or timeout > 300:
                errors.append("Timeout must be a positive number <= 300 seconds")
        
        return len(errors) == 0, errors


class EnhancedIsolation:
    """Enhanced isolation mechanisms for sandbox execution"""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.ENHANCED):
        self.security_level = security_level
        self.isolation_config = self._get_isolation_config()
    
    def _get_isolation_config(self) -> Dict[str, Any]:
        """Get isolation configuration based on security level"""
        configs = {
            SecurityLevel.BASIC: {
                "chroot": False,
                "namespace": False,
                "cgroup": False,
                "seccomp": False,
                "capabilities": ["CHOWN", "DAC_OVERRIDE", "FOWNER", "FSETID", "KILL", "SETGID", "SETUID", "SETPCAP", "NET_BIND_SERVICE", "NET_RAW", "SYS_CHROOT", "MKNOD", "AUDIT_WRITE", "SETFCAP"]
            },
            SecurityLevel.ENHANCED: {
                "chroot": True,
                "namespace": True,
                "cgroup": True,
                "seccomp": True,
                "capabilities": ["CHOWN", "DAC_OVERRIDE", "FOWNER", "FSETID", "KILL", "SETGID", "SETUID", "SETPCAP", "NET_BIND_SERVICE", "NET_RAW", "SYS_CHROOT", "MKNOD", "AUDIT_WRITE", "SETFCAP"]
            },
            SecurityLevel.STRICT: {
                "chroot": True,
                "namespace": True,
                "cgroup": True,
                "seccomp": True,
                "capabilities": ["CHOWN", "DAC_OVERRIDE", "FOWNER", "FSETID", "KILL", "SETGID", "SETUID", "SETPCAP", "NET_BIND_SERVICE", "NET_RAW", "SYS_CHROOT", "MKNOD", "AUDIT_WRITE", "SETFCAP"]
            },
            SecurityLevel.PARANOID: {
                "chroot": True,
                "namespace": True,
                "cgroup": True,
                "seccomp": True,
                "capabilities": []
            }
        }
        return configs.get(self.security_level, configs[SecurityLevel.ENHANCED])
    
    def create_isolated_environment(self, temp_dir: str) -> Dict[str, Any]:
        """Create isolated execution environment"""
        env_config = {
            "temp_dir": temp_dir,
            "isolation_level": self.security_level.value,
            "config": self.isolation_config.copy()
        }
        
        # Create restricted directory structure
        restricted_dirs = ["bin", "lib", "usr", "tmp"]
        for dir_name in restricted_dirs:
            dir_path = os.path.join(temp_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)
        
        # Set up restricted permissions
        os.chmod(temp_dir, 0o755)
        
        return env_config
    
    def apply_security_restrictions(self, process_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply security restrictions to process configuration"""
        restrictions = process_config.copy()
        
        # Environment restrictions
        restrictions["env"] = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": "/tmp",
            "USER": "sandbox",
            "SHELL": "/bin/sh"
        }
        
        # Working directory restrictions
        restrictions["cwd"] = restrictions.get("temp_dir", "/tmp")
        
        # Process restrictions
        if self.isolation_config["seccomp"]:
            restrictions["seccomp"] = self._get_seccomp_profile()
        
        return restrictions
    
    def _get_seccomp_profile(self) -> Dict[str, Any]:
        """Get seccomp profile for process restrictions"""
        return {
            "defaultAction": "SCMP_ACT_ERRNO",
            "architectures": ["SCMP_ARCH_X86_64"],
            "syscalls": [
                {
                    "names": ["read", "write", "open", "close", "stat", "fstat", "lstat", "poll", "lseek", "mmap", "mprotect", "munmap", "brk", "rt_sigaction", "rt_sigprocmask", "rt_sigreturn", "ioctl", "pread64", "pwrite64", "readv", "writev", "access", "pipe", "select", "sched_yield", "mremap", "msync", "mincore", "madvise", "shmget", "shmat", "shmctl", "dup", "dup2", "pause", "nanosleep", "getitimer", "alarm", "setitimer", "getpid", "sendfile", "socket", "connect", "accept", "sendto", "recvfrom", "sendmsg", "recvmsg", "shutdown", "bind", "listen", "getsockname", "getpeername", "socketpair", "setsockopt", "getsockopt", "clone", "fork", "vfork", "execve", "exit", "wait4", "kill", "uname", "semget", "semop", "semctl", "shmdt", "msgget", "msgsnd", "msgrcv", "msgctl", "fcntl", "flock", "fsync", "fdatasync", "truncate", "ftruncate", "getdents", "getcwd", "chdir", "fchdir", "rename", "mkdir", "rmdir", "creat", "link", "unlink", "symlink", "readlink", "chmod", "fchmod", "chown", "fchown", "lchown", "umask", "gettimeofday", "getrlimit", "getrusage", "sysinfo", "times", "ptrace", "getuid", "syslog", "getgid", "setuid", "setgid", "geteuid", "getegid", "setpgid", "getppid", "getpgrp", "setsid", "setreuid", "setregid", "getgroups", "setgroups", "setresuid", "getresuid", "setresgid", "getresgid", "getpgid", "setfsuid", "setfsgid", "getsid", "capget", "capset", "rt_sigpending", "rt_sigtimedwait", "rt_sigqueueinfo", "rt_sigsuspend", "sigaltstack", "utime", "mknod", "uselib", "personality", "ustat", "statfs", "fstatfs", "sysfs", "getpriority", "setpriority", "sched_setparam", "sched_getparam", "sched_setscheduler", "sched_getscheduler", "sched_get_priority_max", "sched_get_priority_min", "sched_rr_get_interval", "mlock", "munlock", "mlockall", "munlockall", "vhangup", "modify_ldt", "pivot_root", "_sysctl", "prctl", "arch_prctl", "adjtimex", "setrlimit", "chroot", "sync", "acct", "settimeofday", "mount", "umount2", "swapon", "swapoff", "reboot", "sethostname", "setdomainname", "iopl", "ioperm", "create_module", "init_module", "delete_module", "get_kernel_syms", "query_module", "quotactl", "nfsservctl", "getpmsg", "putpmsg", "afs_syscall", "tuxcall", "security", "gettid", "readahead", "setxattr", "lsetxattr", "fsetxattr", "getxattr", "lgetxattr", "fgetxattr", "listxattr", "llistxattr", "flistxattr", "removexattr", "lremovexattr", "fremovexattr", "tkill", "time", "futex", "sched_setaffinity", "sched_getaffinity", "set_thread_area", "io_setup", "io_destroy", "io_getevents", "io_submit", "io_cancel", "get_thread_area", "lookup_dcookie", "epoll_create", "epoll_ctl_old", "epoll_wait_old", "remap_file_pages", "getdents64", "set_tid_address", "restart_syscall", "semtimedop", "fadvise64", "timer_create", "timer_settime", "timer_gettime", "timer_getoverrun", "timer_delete", "clock_settime", "clock_gettime", "clock_getres", "clock_nanosleep", "exit_group", "epoll_wait", "epoll_ctl", "tgkill", "utimes", "vserver", "mbind", "set_mempolicy", "get_mempolicy", "mq_open", "mq_unlink", "mq_timedsend", "mq_timedreceive", "mq_notify", "mq_getsetattr", "kexec_load", "waitid", "add_key", "request_key", "keyctl", "ioprio_set", "ioprio_get", "inotify_init", "inotify_add_watch", "inotify_rm_watch", "migrate_pages", "openat", "mkdirat", "mknodat", "fchownat", "futimesat", "newfstatat", "unlinkat", "renameat", "linkat", "symlinkat", "readlinkat", "fchmodat", "faccessat", "pselect6", "ppoll", "unshare", "set_robust_list", "get_robust_list", "splice", "tee", "sync_file_range", "vmsplice", "move_pages", "utimensat", "epoll_pwait", "signalfd", "timerfd_create", "eventfd", "fallocate", "timerfd_settime", "timerfd_gettime", "accept4", "signalfd4", "eventfd2", "epoll_create1", "dup3", "pipe2", "inotify_init1", "preadv", "pwritev", "rt_tgsigqueueinfo", "perf_event_open", "recvmmsg", "fanotify_init", "fanotify_mark", "prlimit64", "name_to_handle_at", "open_by_handle_at", "clock_adjtime", "syncfs", "sendmmsg", "setns", "getcpu", "process_vm_readv", "process_vm_writev", "kcmp", "finit_module", "sched_setattr", "sched_getattr", "renameat2", "seccomp", "getrandom", "memfd_create", "kexec_file_load", "bpf", "execveat", "userfaultfd", "membarrier", "mlock2", "copy_file_range", "preadv2", "pwritev2", "pkey_mprotect", "pkey_alloc", "pkey_free", "statx", "io_pgetevents", "rseq"],
                    "action": "SCMP_ACT_ALLOW"
                }
            ]
        }
