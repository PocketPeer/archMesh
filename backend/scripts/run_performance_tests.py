#!/usr/bin/env python3
"""
Performance Test Runner

This script runs performance tests with configurable scenarios and generates reports.
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

from tests.performance.performance_config import (
    PerformanceConfig, TestType, TestSeverity, 
    performance_config, PerformanceReport
)
from tests.performance.test_load_testing import TestLoadTesting, LoadTestResults
from tests.performance.test_performance_monitoring import TestPerformanceMonitoring, PerformanceMonitor


class PerformanceTestRunner:
    """Performance test runner with reporting capabilities."""
    
    def __init__(self, config: PerformanceConfig = None):
        self.config = config or performance_config
        self.results: List[PerformanceReport] = []
        self.start_time = None
        self.end_time = None
    
    def run_scenario(self, scenario_name: str, client) -> PerformanceReport:
        """Run a specific test scenario."""
        scenario = self.config.get_scenario(scenario_name)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        print(f"\n{'='*60}")
        print(f"Running scenario: {scenario.name}")
        print(f"Type: {scenario.test_type.value}")
        print(f"Severity: {scenario.severity.value}")
        print(f"Endpoint: {scenario.endpoint}")
        print(f"Concurrent users: {scenario.concurrent_users}")
        print(f"Requests per user: {scenario.requests_per_user}")
        print(f"{'='*60}")
        
        # Initialize monitoring
        monitor = PerformanceMonitor()
        monitor.start_monitoring(interval=0.05)
        
        # Run the test
        test_start_time = datetime.now()
        
        try:
            # Import and run the appropriate test
            if scenario.test_type == TestType.LOAD:
                results = self._run_load_test(client, scenario, monitor)
            elif scenario.test_type == TestType.STRESS:
                results = self._run_stress_test(client, scenario, monitor)
            elif scenario.test_type == TestType.SPIKE:
                results = self._run_spike_test(client, scenario, monitor)
            elif scenario.test_type == TestType.VOLUME:
                results = self._run_volume_test(client, scenario, monitor)
            elif scenario.test_type == TestType.ENDURANCE:
                results = self._run_endurance_test(client, scenario, monitor)
            elif scenario.test_type == TestType.MEMORY:
                results = self._run_memory_test(client, scenario, monitor)
            elif scenario.test_type == TestType.CPU:
                results = self._run_cpu_test(client, scenario, monitor)
            else:
                raise ValueError(f"Unsupported test type: {scenario.test_type}")
            
        finally:
            monitor.stop_monitoring()
        
        test_end_time = datetime.now()
        
        # Create performance report
        report = self._create_report(scenario, results, monitor, test_start_time, test_end_time)
        
        # Validate against thresholds
        self._validate_thresholds(report, scenario.thresholds)
        
        # Print results
        self._print_scenario_results(report)
        
        return report
    
    def _run_load_test(self, client, scenario, monitor) -> LoadTestResults:
        """Run load test scenario."""
        from tests.performance.test_load_testing import TestLoadTesting
        
        test_instance = TestLoadTesting()
        return test_instance._run_load_test(
            client, scenario.endpoint, scenario.method,
            scenario.data, scenario.headers,
            scenario.concurrent_users, scenario.requests_per_user
        )
    
    def _run_stress_test(self, client, scenario, monitor) -> LoadTestResults:
        """Run stress test scenario."""
        # Stress test is similar to load test but with higher thresholds
        return self._run_load_test(client, scenario, monitor)
    
    def _run_spike_test(self, client, scenario, monitor) -> LoadTestResults:
        """Run spike test scenario."""
        from tests.performance.test_load_testing import TestLoadTesting
        
        test_instance = TestLoadTesting()
        return test_instance._run_load_test(
            client, scenario.endpoint, scenario.method,
            scenario.data, scenario.headers,
            scenario.concurrent_users, scenario.requests_per_user
        )
    
    def _run_volume_test(self, client, scenario, monitor) -> LoadTestResults:
        """Run volume test scenario."""
        return self._run_load_test(client, scenario, monitor)
    
    def _run_endurance_test(self, client, scenario, monitor) -> LoadTestResults:
        """Run endurance test scenario."""
        # Endurance test runs for a specific duration
        if scenario.duration_seconds:
            # Calculate requests per user based on duration
            requests_per_second = scenario.concurrent_users * 2  # 2 RPS per user
            total_requests = requests_per_second * scenario.duration_seconds
            requests_per_user = max(1, total_requests // scenario.concurrent_users)
            
            # Create modified scenario
            modified_scenario = scenario
            modified_scenario.requests_per_user = requests_per_user
            
            return self._run_load_test(client, modified_scenario, monitor)
        else:
            return self._run_load_test(client, scenario, monitor)
    
    def _run_memory_test(self, client, scenario, monitor) -> LoadTestResults:
        """Run memory test scenario."""
        return self._run_load_test(client, scenario, monitor)
    
    def _run_cpu_test(self, client, scenario, monitor) -> LoadTestResults:
        """Run CPU test scenario."""
        return self._run_load_test(client, scenario, monitor)
    
    def _create_report(self, scenario, results: LoadTestResults, monitor: PerformanceMonitor,
                      start_time: datetime, end_time: datetime) -> PerformanceReport:
        """Create performance report from test results."""
        duration = (end_time - start_time).total_seconds()
        
        # Get monitoring stats
        cpu_stats = monitor.get_cpu_stats()
        memory_stats = monitor.get_memory_stats()
        response_stats = monitor.get_response_time_stats(scenario.endpoint)
        success_rate = monitor.get_success_rate(scenario.endpoint)
        
        return PerformanceReport(
            scenario_name=scenario.name,
            test_type=scenario.test_type,
            severity=scenario.severity,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            total_requests=results.total_requests,
            successful_requests=results.successful_requests,
            failed_requests=results.failed_requests,
            success_rate_percent=success_rate,
            average_response_time_ms=response_stats.get('avg', 0) * 1000,
            median_response_time_ms=response_stats.get('median', 0) * 1000,
            p95_response_time_ms=response_stats.get('p95', 0) * 1000,
            p99_response_time_ms=response_stats.get('p99', 0) * 1000,
            max_response_time_ms=response_stats.get('max', 0) * 1000,
            min_response_time_ms=response_stats.get('min', 0) * 1000,
            requests_per_second=results.requests_per_second,
            average_cpu_percent=cpu_stats.get('avg', 0),
            max_cpu_percent=cpu_stats.get('max', 0),
            average_memory_mb=memory_stats.get('avg', 0),
            max_memory_mb=memory_stats.get('max', 0),
            errors=results.errors
        )
    
    def _validate_thresholds(self, report: PerformanceReport, thresholds):
        """Validate report against performance thresholds."""
        if not thresholds:
            return
        
        violations = []
        
        if report.average_response_time_ms > thresholds.max_response_time_ms:
            violations.append(f"Average response time {report.average_response_time_ms:.2f}ms exceeds threshold {thresholds.max_response_time_ms}ms")
        
        if report.requests_per_second < thresholds.min_throughput_rps:
            violations.append(f"Throughput {report.requests_per_second:.2f} RPS below threshold {thresholds.min_throughput_rps} RPS")
        
        if report.max_cpu_percent > thresholds.max_cpu_percent:
            violations.append(f"Max CPU usage {report.max_cpu_percent:.2f}% exceeds threshold {thresholds.max_cpu_percent}%")
        
        if report.max_memory_mb > thresholds.max_memory_mb:
            violations.append(f"Max memory usage {report.max_memory_mb:.2f}MB exceeds threshold {thresholds.max_memory_mb}MB")
        
        if report.success_rate_percent < thresholds.min_success_rate_percent:
            violations.append(f"Success rate {report.success_rate_percent:.2f}% below threshold {thresholds.min_success_rate_percent}%")
        
        report.threshold_violations = violations
        report.passed = len(violations) == 0
    
    def _print_scenario_results(self, report: PerformanceReport):
        """Print scenario test results."""
        print(f"\nResults for {report.scenario_name}:")
        print(f"  Duration: {report.duration_seconds:.2f}s")
        print(f"  Total requests: {report.total_requests}")
        print(f"  Successful requests: {report.successful_requests}")
        print(f"  Failed requests: {report.failed_requests}")
        print(f"  Success rate: {report.success_rate_percent:.2f}%")
        print(f"  Average response time: {report.average_response_time_ms:.2f}ms")
        print(f"  P95 response time: {report.p95_response_time_ms:.2f}ms")
        print(f"  P99 response time: {report.p99_response_time_ms:.2f}ms")
        print(f"  Throughput: {report.requests_per_second:.2f} RPS")
        print(f"  Max CPU usage: {report.max_cpu_percent:.2f}%")
        print(f"  Max memory usage: {report.max_memory_mb:.2f}MB")
        
        if report.threshold_violations:
            print(f"  ❌ FAILED - Threshold violations:")
            for violation in report.threshold_violations:
                print(f"    - {violation}")
        else:
            print(f"  ✅ PASSED - All thresholds met")
        
        if report.errors:
            print(f"  Errors: {len(report.errors)}")
            for error in report.errors[:5]:  # Show first 5 errors
                print(f"    - {error}")
    
    def run_all_scenarios(self, client, scenario_names: List[str] = None):
        """Run all or specified scenarios."""
        if scenario_names is None:
            scenario_names = list(self.config.scenarios.keys())
        
        self.start_time = datetime.now()
        print(f"Starting performance tests at {self.start_time}")
        print(f"Running {len(scenario_names)} scenarios")
        
        for scenario_name in scenario_names:
            try:
                report = self.run_scenario(scenario_name, client)
                self.results.append(report)
            except Exception as e:
                print(f"❌ Error running scenario '{scenario_name}': {e}")
                # Create a failed report
                failed_report = PerformanceReport(
                    scenario_name=scenario_name,
                    test_type=TestType.LOAD,
                    severity=TestSeverity.MEDIUM,
                    start_time=datetime.now().isoformat(),
                    end_time=datetime.now().isoformat(),
                    duration_seconds=0,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    success_rate_percent=0,
                    average_response_time_ms=0,
                    median_response_time_ms=0,
                    p95_response_time_ms=0,
                    p99_response_time_ms=0,
                    max_response_time_ms=0,
                    min_response_time_ms=0,
                    requests_per_second=0,
                    average_cpu_percent=0,
                    max_cpu_percent=0,
                    average_memory_mb=0,
                    max_memory_mb=0,
                    errors=[str(e)],
                    threshold_violations=[f"Test execution failed: {e}"],
                    passed=False
                )
                self.results.append(failed_report)
        
        self.end_time = datetime.now()
        self._print_summary()
    
    def _print_summary(self):
        """Print test summary."""
        print(f"\n{'='*80}")
        print(f"PERFORMANCE TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Start time: {self.start_time}")
        print(f"End time: {self.end_time}")
        print(f"Total duration: {(self.end_time - self.start_time).total_seconds():.2f}s")
        print(f"Total scenarios: {len(self.results)}")
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(passed / len(self.results) * 100):.1f}%")
        
        if failed > 0:
            print(f"\nFailed scenarios:")
            for report in self.results:
                if not report.passed:
                    print(f"  - {report.scenario_name}: {', '.join(report.threshold_violations)}")
        
        print(f"{'='*80}")
    
    def save_report(self, filename: str):
        """Save test results to JSON file."""
        report_data = {
            "summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_scenarios": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed)
            },
            "scenarios": []
        }
        
        for report in self.results:
            scenario_data = {
                "name": report.scenario_name,
                "type": report.test_type.value,
                "severity": report.severity.value,
                "passed": report.passed,
                "duration_seconds": report.duration_seconds,
                "total_requests": report.total_requests,
                "success_rate_percent": report.success_rate_percent,
                "average_response_time_ms": report.average_response_time_ms,
                "p95_response_time_ms": report.p95_response_time_ms,
                "requests_per_second": report.requests_per_second,
                "max_cpu_percent": report.max_cpu_percent,
                "max_memory_mb": report.max_memory_mb,
                "threshold_violations": report.threshold_violations,
                "errors": report.errors
            }
            report_data["scenarios"].append(scenario_data)
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Report saved to {filename}")


def main():
    """Main function for running performance tests."""
    parser = argparse.ArgumentParser(description="Run performance tests")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenarios to run")
    parser.add_argument("--type", choices=[t.value for t in TestType], help="Run scenarios of specific type")
    parser.add_argument("--severity", choices=[s.value for s in TestSeverity], help="Run scenarios of specific severity")
    parser.add_argument("--output", "-o", help="Output file for JSON report")
    parser.add_argument("--list", action="store_true", help="List available scenarios")
    
    args = parser.parse_args()
    
    # Create test client
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    # Create runner
    runner = PerformanceTestRunner()
    
    if args.list:
        # List available scenarios
        summary = runner.config.get_scenario_summary()
        print("Available scenarios:")
        for scenario in summary["scenarios"]:
            print(f"  - {scenario['name']} ({scenario['type']}, {scenario['severity']})")
        return
    
    # Determine scenarios to run
    scenario_names = None
    if args.scenarios:
        scenario_names = args.scenarios
    elif args.type:
        scenarios = runner.config.get_scenarios_by_type(TestType(args.type))
        scenario_names = [s.name for s in scenarios]
    elif args.severity:
        scenarios = runner.config.get_scenarios_by_severity(TestSeverity(args.severity))
        scenario_names = [s.name for s in scenarios]
    
    # Run tests
    runner.run_all_scenarios(client, scenario_names)
    
    # Save report
    if args.output:
        runner.save_report(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        runner.save_report(f"performance_report_{timestamp}.json")


if __name__ == "__main__":
    main()

