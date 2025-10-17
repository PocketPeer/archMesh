#!/bin/bash

# Frontend Test Runner Script
# This script runs different types of tests for the frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install dependencies if needed
install_dependencies() {
    if [ ! -d "node_modules" ]; then
        print_status "Installing dependencies..."
        npm install
    fi
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    npm run test:unit
    print_success "Unit tests completed"
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    npm run test:integration
    print_success "Integration tests completed"
}

# Function to run brownfield tests
run_brownfield_tests() {
    print_status "Running brownfield tests..."
    npm run test:brownfield
    print_success "Brownfield tests completed"
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    npm run test
    print_success "All tests completed"
}

# Function to run tests with coverage
run_coverage_tests() {
    print_status "Running tests with coverage..."
    npm run test:coverage
    print_success "Coverage tests completed"
}

# Function to run tests in watch mode
run_watch_tests() {
    print_status "Running tests in watch mode..."
    npm run test:watch
}

# Function to run CI tests
run_ci_tests() {
    print_status "Running CI tests..."
    npm run test:ci
    print_success "CI tests completed"
}

# Function to lint code
run_lint() {
    print_status "Running linter..."
    if command_exists eslint; then
        npx eslint src --ext .ts,.tsx --fix
        print_success "Linting completed"
    else
        print_warning "ESLint not found, skipping linting"
    fi
}

# Function to type check
run_type_check() {
    print_status "Running TypeScript type check..."
    npx tsc --noEmit
    print_success "Type check completed"
}

# Function to show help
show_help() {
    echo "Frontend Test Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  unit          Run unit tests only"
    echo "  integration   Run integration tests only"
    echo "  brownfield    Run brownfield tests only"
    echo "  all           Run all tests (default)"
    echo "  coverage      Run tests with coverage report"
    echo "  watch         Run tests in watch mode"
    echo "  ci            Run tests for CI environment"
    echo "  lint          Run linter"
    echo "  type-check    Run TypeScript type check"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 unit       # Run only unit tests"
    echo "  $0 coverage   # Run tests with coverage"
    echo "  $0 watch      # Run tests in watch mode"
}

# Main script logic
main() {
    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run this script from the frontend directory."
        exit 1
    fi

    # Install dependencies if needed
    install_dependencies

    # Parse command line arguments
    case "${1:-all}" in
        "unit")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "brownfield")
            run_brownfield_tests
            ;;
        "all")
            run_all_tests
            ;;
        "coverage")
            run_coverage_tests
            ;;
        "watch")
            run_watch_tests
            ;;
        "ci")
            run_ci_tests
            ;;
        "lint")
            run_lint
            ;;
        "type-check")
            run_type_check
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
