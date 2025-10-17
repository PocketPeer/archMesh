#!/usr/bin/env python3
"""
Test runner script for the ArchMesh backend.

This script provides a convenient way to run different types of tests
with appropriate configurations and reporting.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Run ArchMesh backend tests')
    parser.add_argument(
        '--type',
        choices=['unit', 'integration', 'e2e', 'api', 'all', 'brownfield'],
        default='all',
        help='Type of tests to run'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run tests in parallel'
    )
    parser.add_argument(
        '--file',
        help='Run specific test file'
    )
    parser.add_argument(
        '--function',
        help='Run specific test function'
    )
    parser.add_argument(
        '--markers',
        help='Run tests with specific markers'
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ['python', '-m', 'pytest']
    
    # Add verbosity
    if args.verbose:
        base_cmd.append('-v')
    
    # Add parallel execution
    if args.parallel:
        base_cmd.extend(['-n', 'auto'])
    
    # Add coverage
    if args.coverage:
        base_cmd.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-report=xml:coverage.xml',
            '--cov-fail-under=80'
        ])
    
    # Determine test path based on type
    test_paths = []
    if args.type == 'unit':
        test_paths = ['tests/unit/']
    elif args.type == 'integration':
        test_paths = ['tests/integration/']
    elif args.type == 'e2e':
        test_paths = ['tests/e2e/']
    elif args.type == 'api':
        test_paths = ['tests/api/']
    elif args.type == 'brownfield':
        test_paths = [
            'tests/unit/test_architecture_agent_brownfield.py',
            'tests/unit/test_knowledge_base_service.py',
            'tests/integration/test_brownfield_workflow.py',
            'tests/api/test_brownfield_api.py',
            'tests/e2e/test_brownfield_e2e.py'
        ]
    elif args.type == 'all':
        test_paths = ['tests/']
    
    # Add specific file or function
    if args.file:
        test_paths = [args.file]
    elif args.function:
        test_paths = [f'{args.function}']
    
    # Add markers
    if args.markers:
        base_cmd.extend(['-m', args.markers])
    
    # Add test paths
    base_cmd.extend(test_paths)
    
    # Run the tests
    success = run_command(base_cmd, f"{args.type.title()} tests")
    
    if not success:
        sys.exit(1)
    
    # Additional reporting for coverage
    if args.coverage:
        print(f"\n{'='*60}")
        print("Coverage reports generated:")
        print("- Terminal: Displayed above")
        print("- HTML: htmlcov/index.html")
        print("- XML: coverage.xml")
        print(f"{'='*60}")
    
    print(f"\n✅ All {args.type} tests completed successfully!")


if __name__ == '__main__':
    main()
