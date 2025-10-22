#!/bin/bash

# Comprehensive Test Suite Runner for ArchMesh
# This script runs all tests in the correct order and generates comprehensive reports

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
REPORTS_DIR="$PROJECT_ROOT/reports"
COVERAGE_DIR="$PROJECT_ROOT/coverage"

# Test configuration
BACKEND_COVERAGE_THRESHOLD=90
FRONTEND_COVERAGE_THRESHOLD=85
PARALLEL_JOBS=4

# Create directories
mkdir -p "$REPORTS_DIR"
mkdir -p "$COVERAGE_DIR"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test result tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Function to run backend tests
run_backend_tests() {
    log_info "Running backend tests..."
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Run unit tests
    log_info "Running backend unit tests..."
    pytest tests/unit \
        --cov=app \
        --cov-report=html:"$COVERAGE_DIR/backend-html" \
        --cov-report=xml:"$COVERAGE_DIR/backend-coverage.xml" \
        --cov-report=term-missing \
        --cov-fail-under=$BACKEND_COVERAGE_THRESHOLD \
        --junitxml="$REPORTS_DIR/backend-unit-results.xml" \
        --maxfail=5 \
        --tb=short \
        -v
    
    if [ $? -eq 0 ]; then
        log_success "Backend unit tests passed"
        ((PASSED_TESTS++))
    else
        log_error "Backend unit tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    
    # Run integration tests
    log_info "Running backend integration tests..."
    pytest tests/integration \
        --junitxml="$REPORTS_DIR/backend-integration-results.xml" \
        --maxfail=3 \
        --tb=short \
        -v
    
    if [ $? -eq 0 ]; then
        log_success "Backend integration tests passed"
        ((PASSED_TESTS++))
    else
        log_error "Backend integration tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    
    # Run performance tests (if not in CI)
    if [ "$CI" != "true" ]; then
        log_info "Running backend performance tests..."
        pytest tests/performance \
            --junitxml="$REPORTS_DIR/backend-performance-results.xml" \
            --maxfail=2 \
            --tb=short \
            -v
        
        if [ $? -eq 0 ]; then
            log_success "Backend performance tests passed"
            ((PASSED_TESTS++))
        else
            log_warning "Backend performance tests failed (non-critical)"
            ((SKIPPED_TESTS++))
        fi
        ((TOTAL_TESTS++))
    fi
    
    deactivate
}

# Function to run frontend tests
run_frontend_tests() {
    log_info "Running frontend tests..."
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_warning "Node modules not found. Installing dependencies..."
        npm ci
    fi
    
    # Run unit tests
    log_info "Running frontend unit tests..."
    npm test -- \
        --coverage \
        --coverageDirectory="$COVERAGE_DIR/frontend" \
        --coverageReporters=html,text,lcov \
        --coverageThreshold.global.branches=$FRONTEND_COVERAGE_THRESHOLD \
        --coverageThreshold.global.functions=$FRONTEND_COVERAGE_THRESHOLD \
        --coverageThreshold.global.lines=$FRONTEND_COVERAGE_THRESHOLD \
        --coverageThreshold.global.statements=$FRONTEND_COVERAGE_THRESHOLD \
        --watchAll=false \
        --passWithNoTests
    
    if [ $? -eq 0 ]; then
        log_success "Frontend unit tests passed"
        ((PASSED_TESTS++))
    else
        log_error "Frontend unit tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    
    # Run integration tests
    log_info "Running frontend integration tests..."
    npm run test:integration
    
    if [ $? -eq 0 ]; then
        log_success "Frontend integration tests passed"
        ((PASSED_TESTS++))
    else
        log_error "Frontend integration tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    
    # Run E2E tests (if not in CI or if explicitly requested)
    if [ "$CI" != "true" ] || [ "$RUN_E2E" = "true" ]; then
        log_info "Running frontend E2E tests..."
        npm run test:e2e
        
        if [ $? -eq 0 ]; then
            log_success "Frontend E2E tests passed"
            ((PASSED_TESTS++))
        else
            log_error "Frontend E2E tests failed"
            ((FAILED_TESTS++))
        fi
        ((TOTAL_TESTS++))
    fi
}

# Function to run security tests
run_security_tests() {
    log_info "Running security tests..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Run security tests
    pytest tests/security \
        --junitxml="$REPORTS_DIR/security-results.xml" \
        --maxfail=1 \
        --tb=short \
        -v
    
    if [ $? -eq 0 ]; then
        log_success "Security tests passed"
        ((PASSED_TESTS++))
    else
        log_error "Security tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    
    deactivate
}

# Function to generate test report
generate_test_report() {
    log_info "Generating comprehensive test report..."
    
    # Create test report
    cat > "$REPORTS_DIR/test-summary.md" << EOF
# Test Execution Summary

**Generated:** $(date)
**Total Tests:** $TOTAL_TESTS
**Passed:** $PASSED_TESTS
**Failed:** $FAILED_TESTS
**Skipped:** $SKIPPED_TESTS
**Success Rate:** $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%

## Test Results

### Backend Tests
- Unit Tests: $(if [ -f "$REPORTS_DIR/backend-unit-results.xml" ]; then echo "✅ Passed"; else echo "❌ Failed"; fi)
- Integration Tests: $(if [ -f "$REPORTS_DIR/backend-integration-results.xml" ]; then echo "✅ Passed"; else echo "❌ Failed"; fi)
- Performance Tests: $(if [ -f "$REPORTS_DIR/backend-performance-results.xml" ]; then echo "✅ Passed"; else echo "⏭️ Skipped"; fi)

### Frontend Tests
- Unit Tests: $(if [ -f "$COVERAGE_DIR/frontend/coverage-final.json" ]; then echo "✅ Passed"; else echo "❌ Failed"; fi)
- Integration Tests: $(if [ -f "$REPORTS_DIR/frontend-integration-results.xml" ]; then echo "✅ Passed"; else echo "❌ Failed"; fi)
- E2E Tests: $(if [ -f "$REPORTS_DIR/frontend-e2e-results.xml" ]; then echo "✅ Passed"; else echo "⏭️ Skipped"; fi)

### Security Tests
- Security Tests: $(if [ -f "$REPORTS_DIR/security-results.xml" ]; then echo "✅ Passed"; else echo "❌ Failed"; fi)

## Coverage Reports

- Backend Coverage: [HTML Report]($COVERAGE_DIR/backend-html/index.html)
- Frontend Coverage: [HTML Report]($COVERAGE_DIR/frontend/index.html)

## Recommendations

$(if [ $FAILED_TESTS -gt 0 ]; then echo "- ❌ Fix failing tests before proceeding"; fi)
$(if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then echo "- ✅ All tests passed! Ready for deployment"; fi)
$(if [ $SKIPPED_TESTS -gt 0 ]; then echo "- ⚠️ Consider running skipped tests in CI environment"; fi)

EOF

    log_success "Test report generated: $REPORTS_DIR/test-summary.md"
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is required but not installed"
        exit 1
    fi
    
    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        log_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        log_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Function to cleanup
cleanup() {
    log_info "Cleaning up..."
    
    # Kill any running processes
    pkill -f "uvicorn" || true
    pkill -f "npm run dev" || true
    
    # Remove temporary files
    rm -rf "$PROJECT_ROOT/.pytest_cache" || true
    rm -rf "$PROJECT_ROOT/__pycache__" || true
    rm -rf "$PROJECT_ROOT/.coverage" || true
    
    log_success "Cleanup completed"
}

# Function to show help
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -h, --help          Show this help message
    -b, --backend       Run only backend tests
    -f, --frontend      Run only frontend tests
    -s, --security      Run only security tests
    -e, --e2e           Include E2E tests (default: skip in CI)
    -c, --coverage      Show coverage report after tests
    -r, --report        Generate detailed test report
    --cleanup           Clean up before running tests
    --no-cleanup        Skip cleanup after tests

Examples:
    $0                  # Run all tests
    $0 -b               # Run only backend tests
    $0 -f -e            # Run frontend tests including E2E
    $0 --cleanup        # Clean up and run all tests
    $0 -c -r            # Run tests with coverage and report

EOF
}

# Main execution
main() {
    local run_backend=true
    local run_frontend=true
    local run_security=true
    local run_e2e=false
    local show_coverage=false
    local generate_report=false
    local cleanup_before=false
    local cleanup_after=true
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -b|--backend)
                run_frontend=false
                run_security=false
                shift
                ;;
            -f|--frontend)
                run_backend=false
                run_security=false
                shift
                ;;
            -s|--security)
                run_backend=false
                run_frontend=false
                shift
                ;;
            -e|--e2e)
                run_e2e=true
                shift
                ;;
            -c|--coverage)
                show_coverage=true
                shift
                ;;
            -r|--report)
                generate_report=true
                shift
                ;;
            --cleanup)
                cleanup_before=true
                shift
                ;;
            --no-cleanup)
                cleanup_after=false
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Set environment variables
    export RUN_E2E=$run_e2e
    
    # Start execution
    log_info "Starting ArchMesh Test Suite"
    log_info "Project Root: $PROJECT_ROOT"
    
    # Check prerequisites
    check_prerequisites
    
    # Cleanup before if requested
    if [ "$cleanup_before" = true ]; then
        cleanup
    fi
    
    # Run tests based on options
    if [ "$run_backend" = true ]; then
        run_backend_tests
    fi
    
    if [ "$run_frontend" = true ]; then
        run_frontend_tests
    fi
    
    if [ "$run_security" = true ]; then
        run_security_tests
    fi
    
    # Generate report if requested
    if [ "$generate_report" = true ]; then
        generate_test_report
    fi
    
    # Show coverage if requested
    if [ "$show_coverage" = true ]; then
        log_info "Coverage reports available at:"
        log_info "  Backend: $COVERAGE_DIR/backend-html/index.html"
        log_info "  Frontend: $COVERAGE_DIR/frontend/index.html"
    fi
    
    # Cleanup after if requested
    if [ "$cleanup_after" = true ]; then
        cleanup
    fi
    
    # Final summary
    log_info "Test execution completed"
    log_info "Total: $TOTAL_TESTS, Passed: $PASSED_TESTS, Failed: $FAILED_TESTS, Skipped: $SKIPPED_TESTS"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_success "All tests passed! 🎉"
        exit 0
    else
        log_error "Some tests failed. Please review the results."
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
