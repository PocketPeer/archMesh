#!/usr/bin/env python3
"""
Security Test Runner

This script runs security tests with configurable scenarios and generates reports.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.security.security_config import (
    SecurityTestConfig, VulnerabilitySeverity, VulnerabilityCategory,
    security_config, SecurityTestResult
)
from tests.security.test_security_vulnerabilities import TestSecurityVulnerabilities, SecurityTestResults


class SecurityTestRunner:
    """Security test runner with reporting capabilities."""
    
    def __init__(self, config: SecurityTestConfig = None):
        self.config = config or security_config
        self.results: List[SecurityTestResult] = []
        self.start_time = None
        self.end_time = None
    
    def run_security_tests(self, client, test_names: List[str] = None) -> SecurityTestResults:
        """Run security tests and return results."""
        if test_names is None:
            # Run all security tests
            test_names = [
                "test_sql_injection_projects_endpoint",
                "test_xss_vulnerabilities",
                "test_authentication_bypass",
                "test_csrf_vulnerabilities",
                "test_information_disclosure",
                "test_insecure_direct_object_references",
                "test_injection_attacks",
                "test_security_headers",
                "test_rate_limiting",
                "test_file_upload_security",
                "test_session_security",
                "test_crypto_weaknesses",
                "test_business_logic_vulnerabilities",
                "test_api_security"
            ]
        
        results = SecurityTestResults()
        test_instance = TestSecurityVulnerabilities()
        
        print(f"Running {len(test_names)} security tests...")
        
        for test_name in test_names:
            if hasattr(test_instance, test_name):
                print(f"Running {test_name}...")
                try:
                    # Run the test
                    test_method = getattr(test_instance, test_name)
                    test_method(client, results)
                except Exception as e:
                    print(f"Error running {test_name}: {e}")
                    results.add_vulnerability(
                        test_name,
                        "MEDIUM",
                        f"Test execution failed: {str(e)}",
                        f"Exception: {str(e)}",
                        "Fix test implementation"
                    )
            else:
                print(f"Test {test_name} not found")
        
        return results
    
    def run_scenario(self, scenario_name: str, client) -> SecurityTestResults:
        """Run a specific test scenario."""
        scenario = self.config.get_test_scenario(scenario_name)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        print(f"\n{'='*60}")
        print(f"Running scenario: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Severity: {scenario['severity'].value}")
        print(f"Tests: {', '.join(scenario['tests'])}")
        print(f"{'='*60}")
        
        return self.run_security_tests(client, scenario['tests'])
    
    def run_all_scenarios(self, client, scenario_names: List[str] = None):
        """Run all or specified scenarios."""
        if scenario_names is None:
            scenario_names = list(self.config.test_scenarios.keys())
        
        self.start_time = datetime.now()
        print(f"Starting security tests at {self.start_time}")
        print(f"Running {len(scenario_names)} scenarios")
        
        all_results = SecurityTestResults()
        
        for scenario_name in scenario_names:
            try:
                scenario_results = self.run_scenario(scenario_name, client)
                # Merge results
                all_results.vulnerabilities.extend(scenario_results.vulnerabilities)
                all_results.passed_tests += scenario_results.passed_tests
                all_results.failed_tests += scenario_results.failed_tests
                all_results.total_tests += scenario_results.total_tests
            except Exception as e:
                print(f"❌ Error running scenario '{scenario_name}': {e}")
        
        self.end_time = datetime.now()
        self._print_summary(all_results)
        
        return all_results
    
    def _print_summary(self, results: SecurityTestResults):
        """Print security test summary."""
        summary = results.get_summary()
        
        print(f"\n{'='*80}")
        print(f"SECURITY TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Start time: {self.start_time}")
        print(f"End time: {self.end_time}")
        print(f"Total duration: {(self.end_time - self.start_time).total_seconds():.2f}s")
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed tests: {summary['passed_tests']}")
        print(f"Failed tests: {summary['failed_tests']}")
        print(f"Vulnerabilities found: {summary['vulnerabilities_found']}")
        print(f"Security score: {summary['security_score']:.1f}%")
        
        if results.vulnerabilities:
            print(f"\nVULNERABILITIES FOUND:")
            # Group by severity
            by_severity = {}
            for vuln in results.vulnerabilities:
                severity = vuln['severity']
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(vuln)
            
            # Print by severity (critical first)
            severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
            for severity in severity_order:
                if severity in by_severity:
                    print(f"\n{severity} SEVERITY:")
                    for vuln in by_severity[severity]:
                        print(f"  - {vuln['test']}: {vuln['description']}")
                        if vuln['evidence']:
                            print(f"    Evidence: {vuln['evidence'][:100]}...")
                        if vuln['recommendation']:
                            print(f"    Recommendation: {vuln['recommendation']}")
        
        # Security recommendations
        print(f"\nSECURITY RECOMMENDATIONS:")
        if summary['security_score'] < 80:
            print("  - Security score is below 80%. Review and fix vulnerabilities.")
        if any(v['severity'] == 'CRITICAL' for v in results.vulnerabilities):
            print("  - CRITICAL vulnerabilities found. Address immediately.")
        if any(v['severity'] == 'HIGH' for v in results.vulnerabilities):
            print("  - HIGH severity vulnerabilities found. Address as soon as possible.")
        if summary['vulnerabilities_found'] == 0:
            print("  - No vulnerabilities found. Continue regular security testing.")
        
        print(f"{'='*80}")
    
    def save_report(self, results: SecurityTestResults, filename: str):
        """Save security test results to JSON file."""
        report_data = {
            "summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_tests": results.total_tests,
                "passed_tests": results.passed_tests,
                "failed_tests": results.failed_tests,
                "vulnerabilities_found": len(results.vulnerabilities),
                "security_score": results.get_summary()['security_score']
            },
            "vulnerabilities": results.vulnerabilities,
            "owasp_top_10_summary": self.config.get_owasp_top_10_summary(),
            "severity_summary": self.config.get_severity_summary(),
            "category_summary": self.config.get_category_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Security report saved to {filename}")
    
    def generate_owasp_report(self, results: SecurityTestResults) -> str:
        """Generate OWASP Top 10 compliance report."""
        owasp_summary = self.config.get_owasp_top_10_summary()
        
        report = []
        report.append("# OWASP Top 10 Security Assessment Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Summary
        summary = results.get_summary()
        report.append("## Executive Summary")
        report.append(f"- **Total Tests**: {summary['total_tests']}")
        report.append(f"- **Passed Tests**: {summary['passed_tests']}")
        report.append(f"- **Failed Tests**: {summary['failed_tests']}")
        report.append(f"- **Vulnerabilities Found**: {summary['vulnerabilities_found']}")
        report.append(f"- **Security Score**: {summary['security_score']:.1f}%")
        report.append("")
        
        # OWASP Top 10 Analysis
        report.append("## OWASP Top 10 Analysis")
        for owasp_id, vulnerabilities in owasp_summary.items():
            report.append(f"### {owasp_id}")
            report.append(f"**Vulnerabilities**: {len(vulnerabilities)}")
            for vuln in vulnerabilities:
                report.append(f"- **{vuln.name}** ({vuln.severity.value})")
                report.append(f"  - {vuln.description}")
                report.append(f"  - **Impact**: {vuln.impact}")
                report.append(f"  - **Remediation**: {vuln.remediation}")
                if vuln.cwe_id:
                    report.append(f"  - **CWE**: {vuln.cwe_id}")
            report.append("")
        
        # Detailed Findings
        if results.vulnerabilities:
            report.append("## Detailed Findings")
            by_severity = {}
            for vuln in results.vulnerabilities:
                severity = vuln['severity']
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(vuln)
            
            severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
            for severity in severity_order:
                if severity in by_severity:
                    report.append(f"### {severity} Severity Issues")
                    for vuln in by_severity[severity]:
                        report.append(f"#### {vuln['test']}")
                        report.append(f"**Description**: {vuln['description']}")
                        if vuln['evidence']:
                            report.append(f"**Evidence**: {vuln['evidence']}")
                        if vuln['recommendation']:
                            report.append(f"**Recommendation**: {vuln['recommendation']}")
                        report.append("")
        
        # Recommendations
        report.append("## Security Recommendations")
        if summary['security_score'] < 80:
            report.append("- Security score is below 80%. Review and fix vulnerabilities.")
        if any(v['severity'] == 'CRITICAL' for v in results.vulnerabilities):
            report.append("- **CRITICAL**: Address critical vulnerabilities immediately.")
        if any(v['severity'] == 'HIGH' for v in results.vulnerabilities):
            report.append("- **HIGH**: Address high severity vulnerabilities as soon as possible.")
        if summary['vulnerabilities_found'] == 0:
            report.append("- No vulnerabilities found. Continue regular security testing.")
        
        report.append("")
        report.append("## Next Steps")
        report.append("1. Review all identified vulnerabilities")
        report.append("2. Prioritize fixes based on severity and impact")
        report.append("3. Implement security controls and best practices")
        report.append("4. Schedule regular security testing")
        report.append("5. Consider penetration testing for critical applications")
        
        return "\n".join(report)


def main():
    """Main function for running security tests."""
    parser = argparse.ArgumentParser(description="Run security tests")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to run")
    parser.add_argument("--tests", nargs="+", help="Specific tests to run")
    parser.add_argument("--severity", choices=[s.value for s in VulnerabilitySeverity], 
                       help="Run tests for specific severity level")
    parser.add_argument("--category", choices=[c.value for c in VulnerabilityCategory], 
                       help="Run tests for specific vulnerability category")
    parser.add_argument("--output", "-o", help="Output file for JSON report")
    parser.add_argument("--owasp-report", help="Generate OWASP Top 10 report")
    parser.add_argument("--list", action="store_true", help="List available scenarios and tests")
    
    args = parser.parse_args()
    
    # Create test client
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    # Create runner
    runner = SecurityTestRunner()
    
    if args.list:
        # List available scenarios and tests
        print("Available scenarios:")
        for name, scenario in runner.config.get_all_test_scenarios().items():
            print(f"  - {name}: {scenario['name']}")
        
        print("\nAvailable vulnerability definitions:")
        for name, vuln in runner.config.vulnerabilities.items():
            print(f"  - {name}: {vuln.name} ({vuln.severity.value})")
        return
    
    # Determine what to run
    if args.tests:
        # Run specific tests
        results = runner.run_security_tests(client, args.tests)
    elif args.scenarios:
        # Run specific scenarios
        results = runner.run_all_scenarios(client, args.scenarios)
    else:
        # Run all scenarios
        results = runner.run_all_scenarios(client)
    
    # Save reports
    if args.output:
        runner.save_report(results, args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        runner.save_report(results, f"security_report_{timestamp}.json")
    
    if args.owasp_report:
        owasp_report = runner.generate_owasp_report(results)
        with open(args.owasp_report, 'w') as f:
            f.write(owasp_report)
        print(f"OWASP Top 10 report saved to {args.owasp_report}")


if __name__ == "__main__":
    main()

