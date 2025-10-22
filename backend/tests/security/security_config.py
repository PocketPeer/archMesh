"""
Security Testing Configuration

This module provides configuration and utilities for security testing,
including vulnerability definitions, severity levels, and test scenarios.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityCategory(Enum):
    """Vulnerability categories."""
    INJECTION = "injection"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_EXPOSURE = "data_exposure"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    VULNERABLE_COMPONENTS = "vulnerable_components"
    IDENTIFICATION_FAILURES = "identification_failures"
    LOGGING_MONITORING = "logging_monitoring"
    CRYPTOGRAPHIC_FAILURES = "cryptographic_failures"
    SOFTWARE_DATA_INTEGRITY = "software_data_integrity"
    SERVER_SIDE_REQUEST_FORGERY = "server_side_request_forgery"


@dataclass
class VulnerabilityDefinition:
    """Definition of a security vulnerability."""
    name: str
    category: VulnerabilityCategory
    severity: VulnerabilitySeverity
    description: str
    impact: str
    remediation: str
    references: List[str] = field(default_factory=list)
    cwe_id: Optional[str] = None
    owasp_top_10: Optional[str] = None


@dataclass
class SecurityTestResult:
    """Result of a security test."""
    test_name: str
    vulnerability: Optional[VulnerabilityDefinition]
    passed: bool
    evidence: str = ""
    recommendation: str = ""
    timestamp: str = ""


class SecurityTestConfig:
    """Security testing configuration manager."""
    
    def __init__(self):
        self.vulnerabilities: Dict[str, VulnerabilityDefinition] = {}
        self.test_scenarios: Dict[str, Dict[str, Any]] = {}
        self._setup_vulnerability_definitions()
        self._setup_test_scenarios()
    
    def _setup_vulnerability_definitions(self):
        """Setup vulnerability definitions based on OWASP Top 10 and CWE."""
        
        # A01:2021 – Broken Access Control
        self.vulnerabilities["idor"] = VulnerabilityDefinition(
            name="Insecure Direct Object References",
            category=VulnerabilityCategory.AUTHORIZATION,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Application exposes direct references to internal implementation objects",
            impact="Attackers can manipulate references to access unauthorized data",
            remediation="Implement proper authorization checks and use indirect references",
            cwe_id="CWE-639",
            owasp_top_10="A01:2021"
        )
        
        # A02:2021 – Cryptographic Failures
        self.vulnerabilities["weak_crypto"] = VulnerabilityDefinition(
            name="Weak Cryptographic Implementation",
            category=VulnerabilityCategory.CRYPTOGRAPHIC_FAILURES,
            severity=VulnerabilitySeverity.HIGH,
            description="Use of weak cryptographic algorithms or improper implementation",
            impact="Sensitive data can be compromised through cryptographic attacks",
            remediation="Use strong cryptographic algorithms and proper key management",
            cwe_id="CWE-327",
            owasp_top_10="A02:2021"
        )
        
        # A03:2021 – Injection
        self.vulnerabilities["sql_injection"] = VulnerabilityDefinition(
            name="SQL Injection",
            category=VulnerabilityCategory.INJECTION,
            severity=VulnerabilitySeverity.CRITICAL,
            description="Untrusted data is sent to an interpreter as part of a command or query",
            impact="Attackers can execute arbitrary SQL commands and access sensitive data",
            remediation="Use parameterized queries and input validation",
            cwe_id="CWE-89",
            owasp_top_10="A03:2021"
        )
        
        self.vulnerabilities["xss"] = VulnerabilityDefinition(
            name="Cross-Site Scripting (XSS)",
            category=VulnerabilityCategory.INJECTION,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Untrusted data is included in web page output without proper validation",
            impact="Attackers can execute malicious scripts in users' browsers",
            remediation="Implement proper input validation and output encoding",
            cwe_id="CWE-79",
            owasp_top_10="A03:2021"
        )
        
        self.vulnerabilities["command_injection"] = VulnerabilityDefinition(
            name="Command Injection",
            category=VulnerabilityCategory.INJECTION,
            severity=VulnerabilitySeverity.CRITICAL,
            description="Untrusted data is used to construct system commands",
            impact="Attackers can execute arbitrary system commands",
            remediation="Avoid system commands or use proper input validation and escaping",
            cwe_id="CWE-78",
            owasp_top_10="A03:2021"
        )
        
        # A04:2021 – Insecure Design
        self.vulnerabilities["business_logic"] = VulnerabilityDefinition(
            name="Business Logic Flaw",
            category=VulnerabilityCategory.AUTHORIZATION,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Application logic allows unauthorized actions or data access",
            impact="Attackers can exploit business logic to gain unauthorized access",
            remediation="Implement proper business logic validation and authorization",
            cwe_id="CWE-840",
            owasp_top_10="A04:2021"
        )
        
        # A05:2021 – Security Misconfiguration
        self.vulnerabilities["security_headers"] = VulnerabilityDefinition(
            name="Missing Security Headers",
            category=VulnerabilityCategory.SECURITY_MISCONFIGURATION,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Application is missing important security headers",
            impact="Application is vulnerable to various attacks like clickjacking, XSS",
            remediation="Implement all required security headers",
            cwe_id="CWE-693",
            owasp_top_10="A05:2021"
        )
        
        # A06:2021 – Vulnerable and Outdated Components
        self.vulnerabilities["vulnerable_components"] = VulnerabilityDefinition(
            name="Vulnerable Components",
            category=VulnerabilityCategory.VULNERABLE_COMPONENTS,
            severity=VulnerabilitySeverity.HIGH,
            description="Application uses components with known vulnerabilities",
            impact="Attackers can exploit known vulnerabilities in components",
            remediation="Keep all components updated and scan for vulnerabilities",
            cwe_id="CWE-1104",
            owasp_top_10="A06:2021"
        )
        
        # A07:2021 – Identification and Authentication Failures
        self.vulnerabilities["auth_bypass"] = VulnerabilityDefinition(
            name="Authentication Bypass",
            category=VulnerabilityCategory.AUTHENTICATION,
            severity=VulnerabilitySeverity.CRITICAL,
            description="Authentication mechanisms can be bypassed or broken",
            impact="Attackers can gain unauthorized access to the application",
            remediation="Implement strong authentication and session management",
            cwe_id="CWE-287",
            owasp_top_10="A07:2021"
        )
        
        # A08:2021 – Software and Data Integrity Failures
        self.vulnerabilities["file_upload"] = VulnerabilityDefinition(
            name="Insecure File Upload",
            category=VulnerabilityCategory.SOFTWARE_DATA_INTEGRITY,
            severity=VulnerabilitySeverity.HIGH,
            description="File upload functionality allows malicious files",
            impact="Attackers can upload malicious files and execute code",
            remediation="Implement file type validation, size limits, and content scanning",
            cwe_id="CWE-434",
            owasp_top_10="A08:2021"
        )
        
        # A09:2021 – Security Logging and Monitoring Failures
        self.vulnerabilities["logging_monitoring"] = VulnerabilityDefinition(
            name="Insufficient Logging and Monitoring",
            category=VulnerabilityCategory.LOGGING_MONITORING,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Application lacks proper logging and monitoring",
            impact="Security incidents may go undetected",
            remediation="Implement comprehensive logging and monitoring",
            cwe_id="CWE-778",
            owasp_top_10="A09:2021"
        )
        
        # A10:2021 – Server-Side Request Forgery (SSRF)
        self.vulnerabilities["ssrf"] = VulnerabilityDefinition(
            name="Server-Side Request Forgery",
            category=VulnerabilityCategory.SERVER_SIDE_REQUEST_FORGERY,
            severity=VulnerabilitySeverity.HIGH,
            description="Application makes requests to arbitrary URLs",
            impact="Attackers can make requests to internal services or external systems",
            remediation="Implement URL validation and network segmentation",
            cwe_id="CWE-918",
            owasp_top_10="A10:2021"
        )
        
        # Additional vulnerabilities
        self.vulnerabilities["csrf"] = VulnerabilityDefinition(
            name="Cross-Site Request Forgery",
            category=VulnerabilityCategory.AUTHORIZATION,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Application allows unauthorized actions via forged requests",
            impact="Attackers can perform actions on behalf of authenticated users",
            remediation="Implement CSRF tokens and SameSite cookie attributes",
            cwe_id="CWE-352",
            owasp_top_10="A01:2021"
        )
        
        self.vulnerabilities["information_disclosure"] = VulnerabilityDefinition(
            name="Information Disclosure",
            category=VulnerabilityCategory.DATA_EXPOSURE,
            severity=VulnerabilitySeverity.LOW,
            description="Application discloses sensitive information",
            impact="Attackers can gather information about the application",
            remediation="Implement proper error handling and information filtering",
            cwe_id="CWE-200",
            owasp_top_10="A05:2021"
        )
        
        self.vulnerabilities["rate_limiting"] = VulnerabilityDefinition(
            name="Missing Rate Limiting",
            category=VulnerabilityCategory.SECURITY_MISCONFIGURATION,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Application lacks rate limiting protection",
            impact="Application is vulnerable to abuse and DoS attacks",
            remediation="Implement rate limiting and request throttling",
            cwe_id="CWE-770",
            owasp_top_10="A05:2021"
        )
        
        self.vulnerabilities["session_security"] = VulnerabilityDefinition(
            name="Insecure Session Management",
            category=VulnerabilityCategory.AUTHENTICATION,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Session management is insecure or missing",
            impact="Attackers can hijack or manipulate user sessions",
            remediation="Implement secure session management with proper flags",
            cwe_id="CWE-613",
            owasp_top_10="A07:2021"
        )
    
    def _setup_test_scenarios(self):
        """Setup security test scenarios."""
        
        self.test_scenarios = {
            "injection_tests": {
                "name": "Injection Attack Tests",
                "description": "Test for various injection vulnerabilities",
                "tests": [
                    "test_sql_injection_projects_endpoint",
                    "test_xss_vulnerabilities",
                    "test_injection_attacks"
                ],
                "severity": VulnerabilitySeverity.CRITICAL
            },
            
            "authentication_tests": {
                "name": "Authentication Security Tests",
                "description": "Test authentication mechanisms",
                "tests": [
                    "test_authentication_bypass",
                    "test_session_security"
                ],
                "severity": VulnerabilitySeverity.CRITICAL
            },
            
            "authorization_tests": {
                "name": "Authorization Security Tests",
                "description": "Test authorization mechanisms",
                "tests": [
                    "test_insecure_direct_object_references",
                    "test_csrf_vulnerabilities",
                    "test_business_logic_vulnerabilities"
                ],
                "severity": VulnerabilitySeverity.MEDIUM
            },
            
            "data_protection_tests": {
                "name": "Data Protection Tests",
                "description": "Test data protection mechanisms",
                "tests": [
                    "test_information_disclosure",
                    "test_crypto_weaknesses"
                ],
                "severity": VulnerabilitySeverity.MEDIUM
            },
            
            "configuration_tests": {
                "name": "Security Configuration Tests",
                "description": "Test security configuration",
                "tests": [
                    "test_security_headers",
                    "test_rate_limiting"
                ],
                "severity": VulnerabilitySeverity.MEDIUM
            },
            
            "file_security_tests": {
                "name": "File Security Tests",
                "description": "Test file handling security",
                "tests": [
                    "test_file_upload_security"
                ],
                "severity": VulnerabilitySeverity.HIGH
            },
            
            "api_security_tests": {
                "name": "API Security Tests",
                "description": "Test API-specific security",
                "tests": [
                    "test_api_security"
                ],
                "severity": VulnerabilitySeverity.MEDIUM
            }
        }
    
    def get_vulnerability(self, name: str) -> Optional[VulnerabilityDefinition]:
        """Get vulnerability definition by name."""
        return self.vulnerabilities.get(name)
    
    def get_vulnerabilities_by_category(self, category: VulnerabilityCategory) -> List[VulnerabilityDefinition]:
        """Get vulnerabilities by category."""
        return [vuln for vuln in self.vulnerabilities.values() if vuln.category == category]
    
    def get_vulnerabilities_by_severity(self, severity: VulnerabilitySeverity) -> List[VulnerabilityDefinition]:
        """Get vulnerabilities by severity."""
        return [vuln for vuln in self.vulnerabilities.values() if vuln.severity == severity]
    
    def get_test_scenario(self, name: str) -> Optional[Dict[str, Any]]:
        """Get test scenario by name."""
        return self.test_scenarios.get(name)
    
    def get_all_test_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Get all test scenarios."""
        return self.test_scenarios
    
    def get_owasp_top_10_summary(self) -> Dict[str, List[VulnerabilityDefinition]]:
        """Get summary of vulnerabilities by OWASP Top 10."""
        owasp_summary = {}
        for vuln in self.vulnerabilities.values():
            if vuln.owasp_top_10:
                if vuln.owasp_top_10 not in owasp_summary:
                    owasp_summary[vuln.owasp_top_10] = []
                owasp_summary[vuln.owasp_top_10].append(vuln)
        return owasp_summary
    
    def get_severity_summary(self) -> Dict[str, int]:
        """Get summary of vulnerabilities by severity."""
        severity_counts = {}
        for severity in VulnerabilitySeverity:
            severity_counts[severity.value] = len(self.get_vulnerabilities_by_severity(severity))
        return severity_counts
    
    def get_category_summary(self) -> Dict[str, int]:
        """Get summary of vulnerabilities by category."""
        category_counts = {}
        for category in VulnerabilityCategory:
            category_counts[category.value] = len(self.get_vulnerabilities_by_category(category))
        return category_counts


# Global security configuration instance
security_config = SecurityTestConfig()

