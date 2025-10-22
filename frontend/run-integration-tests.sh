#!/bin/bash

# Integration Test Runner
# This script runs integration tests against real backend services

set -e

echo "🚀 Starting Integration Tests"
echo "=============================="

# Check if backend is running
echo "🔍 Checking backend availability..."
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "❌ Backend is not running on http://localhost:8000"
    echo "Please start the backend server first:"
    echo "  cd ../backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

echo "✅ Backend is running"

# Check if frontend is running
echo "🔍 Checking frontend availability..."
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend is not running on http://localhost:3000"
    echo "Please start the frontend server first:"
    echo "  npm run dev"
    exit 1
fi

echo "✅ Frontend is running"

# Set environment variables
export NODE_ENV=test
export NEXT_PUBLIC_API_BASE=http://localhost:8000

echo ""
echo "🧪 Running Integration Tests"
echo "=============================="

# Run API integration tests
echo "📡 Testing API Client Integration..."
npm run test:integration:api

# Run workflow integration tests
echo "⚙️  Testing Workflow Integration..."
npm run test:integration:workflow

# Run component integration tests
echo "🧩 Testing Component Integration..."
npm run test:integration:components

# Run all integration tests
echo "🔄 Running All Integration Tests..."
npm run test:integration

echo ""
echo "✅ All Integration Tests Completed Successfully!"
echo "🎉 Real functionality verified!"
