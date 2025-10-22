"""
Security Vulnerability Testing Suite

This module provides comprehensive security testing for common web application
vulnerabilities including SQL injection, XSS, CSRF, authentication bypass,
and other security issues.
"""

import pytest
import json
import base64
import hashlib
import hmac
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


class SecurityTestResults:
    """Container for security test results."""
    
    def __init__(self):
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.passed_tests: int = 0
        self.failed_tests: int = 0
        self.total_tests: int = 0
    
    def add_vulnerability(self, test_name: str, severity: str, description: str, 
                         evidence: str = "", recommendation: str = ""):
        """Add a discovered vulnerability."""
        self.vulnerabilities.append({
            "test": test_name,
            "severity": severity,
            "description": description,
            "evidence": evidence,
            "recommendation": recommendation
        })
        self.failed_tests += 1
    
    def add_passed_test(self, test_name: str):
        """Add a passed security test."""
        self.passed_tests += 1
    
    def increment_total(self):
        """Increment total test count."""
        self.total_tests += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get security test summary."""
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "vulnerabilities_found": len(self.vulnerabilities),
            "security_score": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        }


class TestSecurityVulnerabilities:
    """Comprehensive security vulnerability testing."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def results(self):
        """Create security test results container."""
        return SecurityTestResults()
    
    def test_sql_injection_projects_endpoint(self, client, results):
        """Test for SQL injection vulnerabilities in projects endpoint."""
        results.increment_total()
        
        # Common SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE projects; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO projects (name) VALUES ('hacked'); --",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "' OR 1=1#",
            "') OR ('1'='1"
        ]
        
        vulnerable = False
        for payload in sql_payloads:
            try:
                # Test in query parameters
                response = client.get(f"/api/v1/projects?name={payload}")
                if response.status_code == 200:
                    # Check if response contains error messages or unexpected data
                    response_text = response.text.lower()
                    if any(keyword in response_text for keyword in 
                          ['error', 'sql', 'database', 'mysql', 'postgresql', 'sqlite']):
                        vulnerable = True
                        results.add_vulnerability(
                            "SQL Injection - Projects Query",
                            "HIGH",
                            f"SQL injection vulnerability detected in projects query parameter",
                            f"Payload: {payload}, Response: {response.text[:200]}",
                            "Implement parameterized queries and input validation"
                        )
                        break
                
                # Test in request body
                response = client.post("/api/v1/projects", json={
                    "name": payload,
                    "description": "Test description",
                    "domain": "cloud-native"
                })
                if response.status_code in [200, 201]:
                    response_text = response.text.lower()
                    if any(keyword in response_text for keyword in 
                          ['error', 'sql', 'database', 'mysql', 'postgresql', 'sqlite']):
                        vulnerable = True
                        results.add_vulnerability(
                            "SQL Injection - Projects Body",
                            "HIGH",
                            f"SQL injection vulnerability detected in projects request body",
                            f"Payload: {payload}, Response: {response.text[:200]}",
                            "Implement parameterized queries and input validation"
                        )
                        break
                        
            except Exception as e:
                # Exception might indicate successful injection
                if "sql" in str(e).lower() or "database" in str(e).lower():
                    vulnerable = True
                    results.add_vulnerability(
                        "SQL Injection - Exception",
                        "HIGH",
                        f"SQL injection vulnerability detected via exception",
                        f"Payload: {payload}, Exception: {str(e)}",
                        "Implement parameterized queries and input validation"
                    )
                    break
        
        if not vulnerable:
            results.add_passed_test("SQL Injection - Projects Endpoint")
    
    def test_xss_vulnerabilities(self, client, results):
        """Test for Cross-Site Scripting (XSS) vulnerabilities."""
        results.increment_total()
        
        # Common XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>"
        ]
        
        vulnerable = False
        for payload in xss_payloads:
            try:
                # Test in project name
                response = client.post("/api/v1/projects", json={
                    "name": payload,
                    "description": "Test description",
                    "domain": "cloud-native"
                })
                
                if response.status_code in [200, 201]:
                    response_text = response.text
                    # Check if payload is reflected without proper escaping
                    if payload in response_text and not any(escaped in response_text for escaped in 
                                                          ['&lt;', '&gt;', '&amp;', '&quot;', '&#x27;']):
                        vulnerable = True
                        results.add_vulnerability(
                            "XSS - Project Name",
                            "MEDIUM",
                            f"XSS vulnerability detected in project name field",
                            f"Payload: {payload}, Response contains unescaped payload",
                            "Implement proper input sanitization and output encoding"
                        )
                        break
                
                # Test in project description
                response = client.post("/api/v1/projects", json={
                    "name": "Test Project",
                    "description": payload,
                    "domain": "cloud-native"
                })
                
                if response.status_code in [200, 201]:
                    response_text = response.text
                    if payload in response_text and not any(escaped in response_text for escaped in 
                                                          ['&lt;', '&gt;', '&amp;', '&quot;', '&#x27;']):
                        vulnerable = True
                        results.add_vulnerability(
                            "XSS - Project Description",
                            "MEDIUM",
                            f"XSS vulnerability detected in project description field",
                            f"Payload: {payload}, Response contains unescaped payload",
                            "Implement proper input sanitization and output encoding"
                        )
                        break
                        
            except Exception as e:
                # Check if exception indicates XSS vulnerability
                if "script" in str(e).lower() or "javascript" in str(e).lower():
                    vulnerable = True
                    results.add_vulnerability(
                        "XSS - Exception",
                        "MEDIUM",
                        f"XSS vulnerability detected via exception",
                        f"Payload: {payload}, Exception: {str(e)}",
                        "Implement proper input sanitization and output encoding"
                    )
                    break
        
        if not vulnerable:
            results.add_passed_test("XSS - Input Fields")
    
    def test_authentication_bypass(self, client, results):
        """Test for authentication bypass vulnerabilities."""
        results.increment_total()
        
        # Test various authentication bypass techniques
        bypass_attempts = [
            # No authentication
            {"headers": {}},
            
            # Empty authorization header
            {"headers": {"Authorization": ""}},
            
            # Invalid authorization header
            {"headers": {"Authorization": "Bearer invalid_token"}},
            
            # SQL injection in authorization
            {"headers": {"Authorization": "Bearer ' OR '1'='1"}},
            
            # JWT manipulation attempts
            {"headers": {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.invalid"}},
            
            # Basic auth bypass attempts
            {"headers": {"Authorization": "Basic " + base64.b64encode(b"admin:admin").decode()}},
            {"headers": {"Authorization": "Basic " + base64.b64encode(b"admin:").decode()}},
            {"headers": {"Authorization": "Basic " + base64.b64encode(b":admin").decode()}},
        ]
        
        vulnerable = False
        for attempt in bypass_attempts:
            try:
                # Test protected endpoints
                response = client.get("/api/v1/projects", **attempt)
                
                # If we get a successful response without proper authentication, it's a vulnerability
                if response.status_code == 200:
                    vulnerable = True
                    results.add_vulnerability(
                        "Authentication Bypass",
                        "CRITICAL",
                        f"Authentication bypass vulnerability detected",
                        f"Headers: {attempt['headers']}, Status: {response.status_code}",
                        "Implement proper authentication and authorization checks"
                    )
                    break
                    
            except Exception as e:
                # Check if exception indicates authentication issue
                if "unauthorized" not in str(e).lower() and "forbidden" not in str(e).lower():
                    vulnerable = True
                    results.add_vulnerability(
                        "Authentication Bypass - Exception",
                        "CRITICAL",
                        f"Authentication bypass vulnerability detected via exception",
                        f"Headers: {attempt['headers']}, Exception: {str(e)}",
                        "Implement proper authentication and authorization checks"
                    )
                    break
        
        if not vulnerable:
            results.add_passed_test("Authentication Bypass")
    
    def test_csrf_vulnerabilities(self, client, results):
        """Test for Cross-Site Request Forgery (CSRF) vulnerabilities."""
        results.increment_total()
        
        # Test CSRF by making requests without proper CSRF tokens
        csrf_tests = [
            # POST request without CSRF token
            {"method": "POST", "url": "/api/v1/projects", "data": {
                "name": "CSRF Test Project",
                "description": "Test description",
                "domain": "cloud-native"
            }},
            
            # PUT request without CSRF token
            {"method": "PUT", "url": "/api/v1/projects/test-id", "data": {
                "name": "Updated Project",
                "description": "Updated description"
            }},
            
            # DELETE request without CSRF token
            {"method": "DELETE", "url": "/api/v1/projects/test-id"},
        ]
        
        vulnerable = False
        for test in csrf_tests:
            try:
                if test["method"] == "POST":
                    response = client.post(test["url"], json=test["data"])
                elif test["method"] == "PUT":
                    response = client.put(test["url"], json=test["data"])
                elif test["method"] == "DELETE":
                    response = client.delete(test["url"])
                
                # If request succeeds without CSRF protection, it's a vulnerability
                if response.status_code in [200, 201, 204]:
                    vulnerable = True
                    results.add_vulnerability(
                        "CSRF Vulnerability",
                        "MEDIUM",
                        f"CSRF vulnerability detected in {test['method']} request",
                        f"URL: {test['url']}, Status: {response.status_code}",
                        "Implement CSRF tokens and SameSite cookie attributes"
                    )
                    break
                    
            except Exception as e:
                # Check if exception indicates CSRF protection
                if "csrf" not in str(e).lower() and "forbidden" not in str(e).lower():
                    vulnerable = True
                    results.add_vulnerability(
                        "CSRF Vulnerability - Exception",
                        "MEDIUM",
                        f"CSRF vulnerability detected via exception",
                        f"URL: {test['url']}, Exception: {str(e)}",
                        "Implement CSRF tokens and SameSite cookie attributes"
                    )
                    break
        
        if not vulnerable:
            results.add_passed_test("CSRF Protection")
    
    def test_information_disclosure(self, client, results):
        """Test for information disclosure vulnerabilities."""
        results.increment_total()
        
        # Test various endpoints for information disclosure
        disclosure_tests = [
            # Test error messages
            {"url": "/api/v1/projects/invalid-id", "expected_info": ["error", "traceback", "stack"]},
            {"url": "/api/v1/nonexistent-endpoint", "expected_info": ["error", "traceback", "stack"]},
            {"url": "/api/v1/projects?invalid_param=test", "expected_info": ["error", "traceback", "stack"]},
        ]
        
        vulnerable = False
        for test in disclosure_tests:
            try:
                response = client.get(test["url"])
                
                if response.status_code >= 400:
                    response_text = response.text.lower()
                    
                    # Check for sensitive information in error responses
                    for info_type in test["expected_info"]:
                        if info_type in response_text:
                            vulnerable = True
                            results.add_vulnerability(
                                "Information Disclosure",
                                "LOW",
                                f"Information disclosure in error response",
                                f"URL: {test['url']}, Disclosed info: {info_type}",
                                "Implement generic error messages and proper error handling"
                            )
                            break
                    
                    if vulnerable:
                        break
                        
            except Exception as e:
                # Check if exception contains sensitive information
                exception_text = str(e).lower()
                if any(info in exception_text for info in ["password", "token", "key", "secret"]):
                    vulnerable = True
                    results.add_vulnerability(
                        "Information Disclosure - Exception",
                        "MEDIUM",
                        f"Sensitive information disclosed in exception",
                        f"URL: {test['url']}, Exception: {str(e)[:200]}",
                        "Implement proper exception handling and logging"
                    )
                    break
        
        if not vulnerable:
            results.add_passed_test("Information Disclosure")
    
    def test_insecure_direct_object_references(self, client, results):
        """Test for Insecure Direct Object References (IDOR)."""
        results.increment_total()
        
        # Test IDOR by accessing resources with different IDs
        idor_tests = [
            # Test with different project IDs
            {"url": "/api/v1/projects/1", "description": "Project ID 1"},
            {"url": "/api/v1/projects/2", "description": "Project ID 2"},
            {"url": "/api/v1/projects/999", "description": "Project ID 999"},
            {"url": "/api/v1/projects/admin", "description": "Project ID admin"},
            {"url": "/api/v1/projects/../etc/passwd", "description": "Path traversal attempt"},
        ]
        
        vulnerable = False
        for test in idor_tests:
            try:
                response = client.get(test["url"])
                
                # If we can access resources without proper authorization, it's IDOR
                if response.status_code == 200:
                    vulnerable = True
                    results.add_vulnerability(
                        "IDOR Vulnerability",
                        "MEDIUM",
                        f"Insecure Direct Object Reference detected",
                        f"URL: {test['url']}, Status: {response.status_code}",
                        "Implement proper authorization checks for resource access"
                    )
                    break
                    
            except Exception as e:
                # Check if exception indicates IDOR vulnerability
                if "unauthorized" not in str(e).lower() and "forbidden" not in str(e).lower():
                    vulnerable = True
                    results.add_vulnerability(
                        "IDOR Vulnerability - Exception",
                        "MEDIUM",
                        f"IDOR vulnerability detected via exception",
                        f"URL: {test['url']}, Exception: {str(e)}",
                        "Implement proper authorization checks for resource access"
                    )
                    break
        
        if not vulnerable:
            results.add_passed_test("IDOR Protection")
    
    def test_injection_attacks(self, client, results):
        """Test for various injection attacks."""
        results.increment_total()
        
        # Test different types of injection attacks
        injection_payloads = [
            # Command injection
            {"type": "Command Injection", "payloads": [
                "; ls -la",
                "| cat /etc/passwd",
                "&& whoami",
                "`id`",
                "$(whoami)",
                "; rm -rf /",
                "| nc -l 4444"
            ]},
            
            # LDAP injection
            {"type": "LDAP Injection", "payloads": [
                "*",
                "*)(&",
                "*)(|",
                "*)(uid=*",
                "*)(|(uid=*",
                "*)(|(objectClass=*"
            ]},
            
            # NoSQL injection
            {"type": "NoSQL Injection", "payloads": [
                '{"$ne": null}',
                '{"$gt": ""}',
                '{"$where": "this.username == this.password"}',
                '{"$regex": ".*"}',
                '{"$exists": true}'
            ]},
        ]
        
        vulnerable = False
        for injection_type in injection_payloads:
            for payload in injection_type["payloads"]:
                try:
                    # Test in query parameters
                    response = client.get(f"/api/v1/projects?search={payload}")
                    
                    if response.status_code == 200:
                        response_text = response.text.lower()
                        # Check for signs of successful injection
                        if any(keyword in response_text for keyword in 
                              ['error', 'exception', 'command', 'ldap', 'mongodb', 'nosql']):
                            vulnerable = True
                            results.add_vulnerability(
                                f"{injection_type['type']}",
                                "HIGH",
                                f"{injection_type['type']} vulnerability detected",
                                f"Payload: {payload}, Response: {response.text[:200]}",
                                "Implement proper input validation and parameterized queries"
                            )
                            break
                    
                    # Test in request body
                    response = client.post("/api/v1/projects", json={
                        "name": payload,
                        "description": "Test description",
                        "domain": "cloud-native"
                    })
                    
                    if response.status_code in [200, 201]:
                        response_text = response.text.lower()
                        if any(keyword in response_text for keyword in 
                              ['error', 'exception', 'command', 'ldap', 'mongodb', 'nosql']):
                            vulnerable = True
                            results.add_vulnerability(
                                f"{injection_type['type']} - Body",
                                "HIGH",
                                f"{injection_type['type']} vulnerability detected in request body",
                                f"Payload: {payload}, Response: {response.text[:200]}",
                                "Implement proper input validation and parameterized queries"
                            )
                            break
                            
                except Exception as e:
                    # Check if exception indicates successful injection
                    exception_text = str(e).lower()
                    if any(keyword in exception_text for keyword in 
                          ['command', 'ldap', 'mongodb', 'nosql', 'injection']):
                        vulnerable = True
                        results.add_vulnerability(
                            f"{injection_type['type']} - Exception",
                            "HIGH",
                            f"{injection_type['type']} vulnerability detected via exception",
                            f"Payload: {payload}, Exception: {str(e)}",
                            "Implement proper input validation and parameterized queries"
                        )
                        break
                
                if vulnerable:
                    break
            
            if vulnerable:
                break
        
        if not vulnerable:
            results.add_passed_test("Injection Attacks")
    
    def test_security_headers(self, client, results):
        """Test for missing security headers."""
        results.increment_total()
        
        # Required security headers
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        try:
            response = client.get("/api/v1/health")
            missing_headers = []
            
            for header in required_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if missing_headers:
                results.add_vulnerability(
                    "Missing Security Headers",
                    "MEDIUM",
                    f"Missing security headers detected",
                    f"Missing headers: {', '.join(missing_headers)}",
                    "Implement all required security headers"
                )
            else:
                results.add_passed_test("Security Headers")
                
        except Exception as e:
            results.add_vulnerability(
                "Security Headers - Exception",
                "MEDIUM",
                f"Error checking security headers",
                f"Exception: {str(e)}",
                "Implement proper error handling for security header checks"
            )
    
    def test_rate_limiting(self, client, results):
        """Test for rate limiting vulnerabilities."""
        results.increment_total()
        
        try:
            # Make rapid requests to test rate limiting
            responses = []
            for i in range(100):  # Make 100 rapid requests
                response = client.get("/api/v1/health")
                responses.append(response.status_code)
            
            # Check if rate limiting is implemented
            rate_limited = any(status == 429 for status in responses)  # 429 = Too Many Requests
            
            if not rate_limited:
                results.add_vulnerability(
                    "Rate Limiting",
                    "MEDIUM",
                    f"Rate limiting not implemented",
                    f"Made 100 requests, no rate limiting detected",
                    "Implement rate limiting to prevent abuse"
                )
            else:
                results.add_passed_test("Rate Limiting")
                
        except Exception as e:
            results.add_vulnerability(
                "Rate Limiting - Exception",
                "MEDIUM",
                f"Error testing rate limiting",
                f"Exception: {str(e)}",
                "Implement proper rate limiting and error handling"
            )
    
    def test_file_upload_security(self, client, results):
        """Test for file upload security vulnerabilities."""
        results.increment_total()
        
        # Test malicious file uploads
        malicious_files = [
            # Executable files
            {"filename": "malicious.exe", "content": b"MZ\x90\x00", "type": "application/x-msdownload"},
            {"filename": "script.php", "content": b"<?php system($_GET['cmd']); ?>", "type": "application/x-php"},
            {"filename": "shell.jsp", "content": b"<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>", "type": "application/x-jsp"},
            
            # Script files
            {"filename": "script.js", "content": b"alert('XSS')", "type": "application/javascript"},
            {"filename": "script.vbs", "content": b"MsgBox \"Hello World\"", "type": "application/x-vbs"},
            
            # Large files (DoS attempt)
            {"filename": "large.txt", "content": b"X" * (10 * 1024 * 1024), "type": "text/plain"},  # 10MB file
        ]
        
        vulnerable = False
        for file_test in malicious_files:
            try:
                # Test file upload endpoint
                files = {"file": (file_test["filename"], file_test["content"], file_test["type"])}
                response = client.post("/api/v1/workflows/upload", files=files)
                
                # If malicious file is accepted, it's a vulnerability
                if response.status_code in [200, 201]:
                    vulnerable = True
                    results.add_vulnerability(
                        "File Upload Security",
                        "HIGH",
                        f"Malicious file upload accepted",
                        f"File: {file_test['filename']}, Type: {file_test['type']}, Status: {response.status_code}",
                        "Implement file type validation, size limits, and content scanning"
                    )
                    break
                    
            except Exception as e:
                # Check if exception indicates security issue
                if "forbidden" not in str(e).lower() and "invalid" not in str(e).lower():
                    vulnerable = True
                    results.add_vulnerability(
                        "File Upload Security - Exception",
                        "HIGH",
                        f"File upload security issue detected via exception",
                        f"File: {file_test['filename']}, Exception: {str(e)}",
                        "Implement proper file upload validation and error handling"
                    )
                    break
        
        if not vulnerable:
            results.add_passed_test("File Upload Security")
    
    def test_session_security(self, client, results):
        """Test for session security vulnerabilities."""
        results.increment_total()
        
        try:
            # Test session-related endpoints
            response = client.get("/api/v1/health")
            
            # Check for secure session cookies
            cookies = response.cookies
            session_cookies = [cookie for cookie in cookies if 'session' in cookie.lower() or 'auth' in cookie.lower()]
            
            vulnerable = False
            for cookie in session_cookies:
                # Check if session cookie is secure
                if not cookie.get('secure', False):
                    vulnerable = True
                    results.add_vulnerability(
                        "Session Security",
                        "MEDIUM",
                        f"Insecure session cookie detected",
                        f"Cookie: {cookie.name}, Secure flag missing",
                        "Set Secure flag on session cookies"
                    )
                    break
                
                # Check if session cookie has HttpOnly flag
                if not cookie.get('httponly', False):
                    vulnerable = True
                    results.add_vulnerability(
                        "Session Security",
                        "MEDIUM",
                        f"Session cookie without HttpOnly flag",
                        f"Cookie: {cookie.name}, HttpOnly flag missing",
                        "Set HttpOnly flag on session cookies"
                    )
                    break
            
            if not vulnerable and session_cookies:
                results.add_passed_test("Session Security")
            elif not session_cookies:
                # No session cookies found, which might be expected
                results.add_passed_test("Session Security")
                
        except Exception as e:
            results.add_vulnerability(
                "Session Security - Exception",
                "MEDIUM",
                f"Error testing session security",
                f"Exception: {str(e)}",
                "Implement proper session management and error handling"
            )
    
    def test_crypto_weaknesses(self, client, results):
        """Test for cryptographic weaknesses."""
        results.increment_total()
        
        try:
            # Test for weak cryptographic implementations
            response = client.get("/api/v1/health")
            
            # Check for weak hash algorithms in response
            response_text = response.text.lower()
            weak_hashes = ['md5', 'sha1', 'des', 'rc4']
            
            vulnerable = False
            for weak_hash in weak_hashes:
                if weak_hash in response_text:
                    vulnerable = True
                    results.add_vulnerability(
                        "Weak Cryptography",
                        "MEDIUM",
                        f"Weak cryptographic algorithm detected",
                        f"Algorithm: {weak_hash}",
                        "Use strong cryptographic algorithms (SHA-256, AES-256)"
                    )
                    break
            
            # Check for hardcoded secrets or keys
            if any(secret in response_text for secret in ['password', 'secret', 'key', 'token']):
                vulnerable = True
                results.add_vulnerability(
                    "Information Disclosure",
                    "HIGH",
                    f"Potential secret disclosure in response",
                    f"Response contains sensitive keywords",
                    "Remove sensitive information from responses"
                )
            
            if not vulnerable:
                results.add_passed_test("Cryptographic Security")
                
        except Exception as e:
            results.add_vulnerability(
                "Cryptographic Security - Exception",
                "MEDIUM",
                f"Error testing cryptographic security",
                f"Exception: {str(e)}",
                "Implement proper cryptographic practices and error handling"
            )
    
    def test_business_logic_vulnerabilities(self, client, results):
        """Test for business logic vulnerabilities."""
        results.increment_total()
        
        try:
            # Test for business logic flaws
            # Example: Test if users can access/modify other users' data
            
            # Test project access with different IDs
            test_ids = ["1", "2", "999", "admin", "test"]
            vulnerable = False
            
            for test_id in test_ids:
                response = client.get(f"/api/v1/projects/{test_id}")
                
                # If we can access any project without proper authorization, it's a vulnerability
                if response.status_code == 200:
                    vulnerable = True
                    results.add_vulnerability(
                        "Business Logic Flaw",
                        "MEDIUM",
                        f"Unauthorized access to project data",
                        f"Project ID: {test_id}, Status: {response.status_code}",
                        "Implement proper authorization checks for business logic"
                    )
                    break
            
            # Test for privilege escalation
            # Example: Try to create admin projects
            admin_data = {
                "name": "Admin Project",
                "description": "This should require admin privileges",
                "domain": "admin",
                "role": "admin"
            }
            
            response = client.post("/api/v1/projects", json=admin_data)
            if response.status_code in [200, 201]:
                vulnerable = True
                results.add_vulnerability(
                    "Privilege Escalation",
                    "HIGH",
                    f"Privilege escalation vulnerability detected",
                    f"Admin data accepted, Status: {response.status_code}",
                    "Implement proper privilege checks and role-based access control"
                )
            
            if not vulnerable:
                results.add_passed_test("Business Logic Security")
                
        except Exception as e:
            results.add_vulnerability(
                "Business Logic Security - Exception",
                "MEDIUM",
                f"Error testing business logic security",
                f"Exception: {str(e)}",
                "Implement proper business logic validation and error handling"
            )
    
    def test_api_security(self, client, results):
        """Test for API-specific security vulnerabilities."""
        results.increment_total()
        
        try:
            # Test for API security issues
            
            # Test for missing API versioning
            response = client.get("/api/v1/health")
            if "api-version" not in response.headers and "version" not in response.headers:
                results.add_vulnerability(
                    "API Versioning",
                    "LOW",
                    f"Missing API versioning headers",
                    f"No version headers found",
                    "Implement API versioning for better security and compatibility"
                )
            
            # Test for excessive data exposure
            response = client.get("/api/v1/projects")
            if response.status_code == 200:
                response_data = response.json()
                # Check if response contains sensitive fields
                sensitive_fields = ['password', 'secret', 'key', 'token', 'ssn', 'credit_card']
                for field in sensitive_fields:
                    if field in str(response_data).lower():
                        results.add_vulnerability(
                            "Data Exposure",
                            "MEDIUM",
                            f"Sensitive data exposure in API response",
                            f"Sensitive field: {field}",
                            "Remove sensitive fields from API responses"
                        )
                        break
            
            # Test for missing input validation
            invalid_data = {
                "name": "A" * 1000,  # Very long name
                "description": "B" * 10000,  # Very long description
                "domain": "invalid_domain_that_should_not_exist"
            }
            
            response = client.post("/api/v1/projects", json=invalid_data)
            if response.status_code in [200, 201]:
                results.add_vulnerability(
                    "Input Validation",
                    "MEDIUM",
                    f"Missing input validation",
                    f"Invalid data accepted, Status: {response.status_code}",
                    "Implement proper input validation and length limits"
                )
            
            results.add_passed_test("API Security")
            
        except Exception as e:
            results.add_vulnerability(
                "API Security - Exception",
                "MEDIUM",
                f"Error testing API security",
                f"Exception: {str(e)}",
                "Implement proper API security practices and error handling"
            )
    
    def test_security_summary(self, client, results):
        """Generate security test summary."""
        summary = results.get_summary()
        
        print(f"\n{'='*60}")
        print(f"SECURITY TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed tests: {summary['passed_tests']}")
        print(f"Failed tests: {summary['failed_tests']}")
        print(f"Vulnerabilities found: {summary['vulnerabilities_found']}")
        print(f"Security score: {summary['security_score']:.1f}%")
        
        if results.vulnerabilities:
            print(f"\nVULNERABILITIES FOUND:")
            for vuln in results.vulnerabilities:
                print(f"  [{vuln['severity']}] {vuln['test']}: {vuln['description']}")
        
        print(f"{'='*60}")
        
        # Assert that we have a reasonable security score
        assert summary['security_score'] >= 70, f"Security score too low: {summary['security_score']:.1f}%"

