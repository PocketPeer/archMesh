#!/bin/bash

# E2E Test Execution Script
# This script runs comprehensive E2E tests that would have caught recent integration issues

set -e  # Exit on any error

echo "🚀 Starting E2E Test Execution"
echo "================================"

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

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the frontend directory."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_status "Installing dependencies..."
npm install

print_status "Installing Playwright browsers..."
npx playwright install

# Check if backend is running
print_status "Checking backend health..."
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    print_success "Backend is running and healthy"
else
    print_warning "Backend is not running. Starting backend..."
    
    # Try to start backend
    cd ../backend
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
        
        print_status "Starting backend server..."
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        
        # Wait for backend to start
        print_status "Waiting for backend to start..."
        for i in {1..30}; do
            if curl -s http://localhost:8000/api/v1/health > /dev/null; then
                print_success "Backend started successfully"
                break
            fi
            sleep 2
        done
        
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start within 60 seconds"
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
    else
        print_error "Backend requirements.txt not found"
        exit 1
    fi
    
    cd ../frontend
fi

# Check if frontend is running
print_status "Checking frontend health..."
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Frontend is running"
else
    print_warning "Frontend is not running. Starting frontend..."
    
    print_status "Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null; then
            print_success "Frontend started successfully"
            break
        fi
        sleep 2
    done
    
    if [ $i -eq 30 ]; then
        print_error "Frontend failed to start within 60 seconds"
        kill $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
fi

# Create test results directory
mkdir -p test-results

print_status "Running E2E tests..."
echo "================================"

# Run different test suites
test_suites=(
    "critical-user-journeys"
    "api-integration" 
    "websocket-integration"
)

total_tests=0
passed_tests=0
failed_tests=0

for suite in "${test_suites[@]}"; do
    print_status "Running $suite tests..."
    
    if npx playwright test __tests__/e2e/$suite.test.ts --reporter=json --output-dir=test-results/$suite; then
        print_success "$suite tests passed"
        ((passed_tests++))
    else
        print_error "$suite tests failed"
        ((failed_tests++))
    fi
    
    ((total_tests++))
done

# Generate comprehensive report
print_status "Generating test report..."
npx playwright show-report --host 0.0.0.0 --port 9323 &
REPORT_PID=$!

# Summary
echo "================================"
echo "E2E Test Execution Summary"
echo "================================"
print_status "Total test suites: $total_tests"
print_success "Passed: $passed_tests"
if [ $failed_tests -gt 0 ]; then
    print_error "Failed: $failed_tests"
else
    print_success "Failed: $failed_tests"
fi

# Cleanup
print_status "Cleaning up..."
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null || true
fi

if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null || true
fi

if [ ! -z "$REPORT_PID" ]; then
    print_status "Test report available at: http://localhost:9323"
    print_status "Press Ctrl+C to stop the report server"
    wait $REPORT_PID
fi

# Exit with appropriate code
if [ $failed_tests -gt 0 ]; then
    print_error "Some tests failed. Check the test report for details."
    exit 1
else
    print_success "All E2E tests passed! 🎉"
    exit 0
fi
