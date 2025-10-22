# E2E Testing Strategy - Comprehensive Customer Journey

## Overview

This E2E testing suite implements a comprehensive TDD approach to catch integration issues that unit tests alone cannot detect. The recent homepage errors (database schema, WebSocket endpoints, enum conversion) demonstrate why these tests are critical.

## Test Categories

### 1. Critical User Journeys (`critical-user-journeys.test.ts`)
Tests the most important user workflows that would have caught recent issues:

- **Homepage loads without errors** - Would have caught API fetch errors
- **WebSocket connection establishes** - Would have caught missing WebSocket endpoint
- **Project list displays correctly** - Would have caught database schema issues
- **Complete project creation workflow**
- **Document upload and processing**
- **Architecture workflow execution**
- **Real-time notifications**
- **Error handling and recovery**
- **Navigation and routing**
- **Mobile responsiveness**
- **Performance requirements**

### 2. API Integration Tests (`api-integration.test.ts`)
Tests API endpoints and would have caught specific recent issues:

- **Projects API returns valid data structure** - Would have caught enum conversion issue
- **Database schema validation** - Would have caught missing owner_id column
- **WebSocket endpoint accepts connections** - Would have caught missing endpoint
- **Error handling and status codes**
- **Performance and concurrency**
- **CORS configuration**

### 3. WebSocket Integration Tests (`websocket-integration.test.ts`)
Tests WebSocket functionality comprehensively:

- **Connection establishment**
- **Ping/pong mechanism**
- **Multiple connections**
- **Connection drops and reconnection**
- **Message handling**
- **Error handling**
- **Performance testing**

## TDD Approach

### RED Phase (Current)
✅ **COMPLETED**: Created comprehensive failing tests that would have caught recent issues

### GREEN Phase (Next)
🔄 **IN PROGRESS**: Run tests and fix issues to make them pass

### REFACTOR Phase (Future)
⏳ **PENDING**: Optimize tests and improve maintainability

## Running Tests

### Prerequisites
1. Install dependencies:
   ```bash
   npm install
   ```

2. Install Playwright browsers:
   ```bash
   npx playwright install
   ```

3. Ensure backend is running:
   ```bash
   cd ../backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Test Commands

```bash
# Run all E2E tests
npm run test:e2e

# Run tests with UI
npm run test:e2e:ui

# Run tests in headed mode (see browser)
npm run test:e2e:headed

# Debug tests
npm run test:e2e:debug

# View test report
npm run test:e2e:report

# Run all tests (unit + E2E)
npm run test:all
```

### Test Configuration

Tests are configured in `playwright.config.ts`:
- **Base URL**: `http://localhost:3000`
- **Backend URL**: `http://localhost:8000`
- **Browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari
- **Parallel execution**: Enabled
- **Retries**: 2 on CI, 0 locally
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On retry

## Test Data Management

### Global Setup (`global-setup.ts`)
- Sets up test database
- Creates test data
- Verifies backend health

### Global Teardown (`global-teardown.ts`)
- Cleans up test data
- Generates test reports

### Test Utilities (`test-utils.ts`)
- Common test helpers
- API test helpers
- WebSocket test helpers
- Performance test helpers

## Issues These Tests Would Have Caught

### 1. Database Schema Issues
**Problem**: Missing `owner_id` column in `projects` table
**Test**: `database schema validation` in API integration tests
**Detection**: Would have failed with SQLAlchemy error about missing column

### 2. Enum Conversion Issues
**Problem**: SQLAlchemy enum to Pydantic enum conversion
**Test**: `Projects API returns valid data structure` in API integration tests
**Detection**: Would have failed with enum validation error

### 3. Missing WebSocket Endpoint
**Problem**: No WebSocket endpoint configured in FastAPI
**Test**: `WebSocket endpoint accepts connections` in API integration tests
**Detection**: Would have failed with 404 error

### 4. Frontend-Backend Integration
**Problem**: API client expecting different response format
**Test**: `Homepage loads without errors` in critical user journeys
**Detection**: Would have failed with console errors

## Test Coverage

### Critical User Journeys: 11 tests
- Homepage loading
- WebSocket connection
- Project management
- Document upload
- Architecture workflow
- Notifications
- Error handling
- Navigation
- Mobile responsiveness
- Performance

### API Integration: 12 tests
- Data structure validation
- Pagination
- Filtering
- CRUD operations
- Error handling
- CORS
- Performance
- Concurrency
- Schema validation
- Status codes

### WebSocket Integration: 10 tests
- Connection establishment
- Ping/pong
- Multiple connections
- Reconnection
- Message handling
- Error handling
- Performance
- Message types
- Headers
- Concurrent messaging

**Total: 33 comprehensive E2E tests**

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- **Parallel execution** for speed
- **Retry logic** for flaky tests
- **Artifact collection** (screenshots, videos, traces)
- **Test reporting** with HTML and JSON output
- **Performance monitoring**

## Maintenance

### Adding New Tests
1. Follow the existing pattern in test files
2. Use test utilities for common operations
3. Add appropriate data-testid attributes to components
4. Update this README with new test descriptions

### Updating Tests
1. Keep tests focused on user behavior, not implementation
2. Use page objects for complex interactions
3. Maintain test data isolation
4. Update utilities as needed

### Debugging Failed Tests
1. Check test artifacts (screenshots, videos, traces)
2. Use `npm run test:e2e:debug` for step-by-step debugging
3. Verify backend is running and accessible
4. Check console logs for errors

## Success Metrics

- **Test Coverage**: 100% of critical user journeys
- **Performance**: Page loads < 3 seconds, API responses < 2 seconds
- **Reliability**: < 5% flaky test rate
- **Maintenance**: Tests updated within 24 hours of feature changes

This comprehensive E2E testing strategy ensures that integration issues like the recent homepage errors are caught early in the development process, maintaining a robust and functioning UI.
