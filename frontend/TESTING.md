# Testing Strategy - Real Functionality

This document outlines the comprehensive testing strategy for ArchMesh, focusing on real functionality testing without mocks.

## Test Categories

### 1. Unit Tests (`npm test`)
- **Purpose**: Test individual components and functions in isolation
- **Scope**: React components, utility functions, hooks
- **Mocks**: Minimal mocking of external dependencies
- **Speed**: Fast (< 1 second per test)

### 2. Integration Tests (`npm run test:integration`)
- **Purpose**: Test real functionality with actual backend services
- **Scope**: API client, workflow execution, component integration
- **Mocks**: No API mocking, real backend calls
- **Speed**: Medium (30 seconds - 2 minutes per test)

### 3. E2E Tests (`npm run test:e2e`)
- **Purpose**: Test complete user journeys in real browser
- **Scope**: Full application workflow from UI to backend
- **Mocks**: None - real browser, real backend
- **Speed**: Slow (1-5 minutes per test)

## Running Tests

### Quick Start
```bash
# Run all tests
npm run test:all:real

# Run specific test categories
npm run test:integration
npm run test:e2e:real
```

### Individual Test Suites
```bash
# Unit tests
npm test
npm run test:watch

# Integration tests
npm run test:integration
npm run test:integration:api
npm run test:integration:workflow
npm run test:integration:components

# E2E tests
npm run test:e2e
npm run test:e2e:real
npm run test:e2e:ui
```

### Using the Test Runner Script
```bash
# Run integration tests with backend checks
./run-integration-tests.sh
```

## What Each Test Type Verifies

### Unit Tests
- ✅ Component rendering and behavior
- ✅ User interactions (clicks, form submissions)
- ✅ State management and context
- ✅ Error handling in components
- ✅ Utility function correctness

### Integration Tests
- ✅ Real API communication
- ✅ Database operations
- ✅ Authentication flows
- ✅ Workflow execution
- ✅ Error handling across services
- ✅ Data persistence
- ✅ Real-time updates

### E2E Tests
- ✅ Complete user journeys
- ✅ Cross-browser compatibility
- ✅ Performance under load
- ✅ Real user scenarios
- ✅ End-to-end data flow
- ✅ UI/UX validation

## Test Data Management

### Automatic Cleanup
- All tests automatically clean up created data
- Projects, workflows, and sessions are deleted after tests
- No test data pollution between runs

### Test Data Isolation
- Each test uses unique identifiers (timestamps)
- Tests run sequentially to avoid conflicts
- Independent test data per test suite

### Realistic Test Data
- Tests use realistic project names and descriptions
- Real requirement documents for workflow testing
- Authentic error scenarios and edge cases

## Prerequisites

### For Integration Tests
1. **Backend Server**: Must be running on `http://localhost:8000`
2. **Database**: Must be initialized and accessible
3. **Services**: Ollama, Redis, etc. must be available
4. **Environment**: All required environment variables set

### For E2E Tests
1. **Frontend Server**: Must be running on `http://localhost:3000`
2. **Backend Server**: Must be running on `http://localhost:8000`
3. **Browser**: Chrome/Chromium installed for Playwright
4. **Network**: Local network accessible

## Test Configuration

### Timeouts
- **Unit Tests**: 5 seconds
- **Integration Tests**: 2 minutes
- **E2E Tests**: 5 minutes

### Retries
- **Unit Tests**: No retries
- **Integration Tests**: 1 retry on failure
- **E2E Tests**: 2 retries on failure

### Parallel Execution
- **Unit Tests**: Parallel (fast)
- **Integration Tests**: Sequential (avoid conflicts)
- **E2E Tests**: Sequential (browser resources)

## Debugging Tests

### Verbose Output
```bash
npm run test:integration -- --verbose
npm run test:e2e -- --verbose
```

### Debug Mode
```bash
# Integration tests with watch mode
npm run test:integration:watch

# E2E tests with UI
npm run test:e2e:ui

# E2E tests with headed browser
npm run test:e2e:headed
```

### Single Test Execution
```bash
# Run specific test
npm run test:integration -- --testNamePattern="should create a new project"
npm run test:e2e -- --grep="Complete User Journey"
```

## Continuous Integration

### CI Pipeline
1. **Unit Tests**: Run first, fast feedback
2. **Integration Tests**: Run against test backend
3. **E2E Tests**: Run against staging environment
4. **Performance Tests**: Run on dedicated infrastructure

### Test Reports
- **Coverage**: Generated for unit tests
- **Screenshots**: Captured for failed E2E tests
- **Videos**: Recorded for complex E2E scenarios
- **Logs**: Detailed logs for debugging failures

## Best Practices

### Writing Tests
1. **Test Real Functionality**: Avoid excessive mocking
2. **Use Real Data**: Test with realistic scenarios
3. **Clean Up**: Always clean up test data
4. **Isolate Tests**: Each test should be independent
5. **Clear Names**: Use descriptive test names

### Maintaining Tests
1. **Update Tests**: Keep tests in sync with code changes
2. **Fix Flaky Tests**: Address unstable tests immediately
3. **Monitor Performance**: Keep test execution times reasonable
4. **Review Coverage**: Ensure adequate test coverage
5. **Document Changes**: Update test documentation

### Debugging Failures
1. **Check Logs**: Review detailed error logs
2. **Verify Prerequisites**: Ensure all services are running
3. **Test Isolation**: Run tests individually
4. **Environment Check**: Verify environment variables
5. **Network Issues**: Check connectivity and ports

## Expected Results

When all tests pass, you can be confident that:

### ✅ Functionality
- All features work as expected
- User journeys complete successfully
- Error handling is robust
- Performance meets requirements

### ✅ Integration
- Frontend and backend communicate correctly
- Database operations succeed
- External services integrate properly
- Real-time features function

### ✅ User Experience
- UI is responsive and intuitive
- Error messages are helpful
- Loading states are appropriate
- Navigation works smoothly

### ✅ Reliability
- System handles errors gracefully
- Data is persisted correctly
- Concurrent users are supported
- System recovers from failures

## Troubleshooting

### Common Issues

#### Backend Not Running
```
Error: Backend not available at http://localhost:8000
```
**Solution**: Start backend with `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

#### Database Connection Issues
```
Error: Failed to create project
```
**Solution**: Check database connection and initialization

#### Test Timeouts
```
Error: Test timeout exceeded
```
**Solution**: Check service performance, increase timeout if needed

#### Flaky Tests
```
Error: Test passes sometimes, fails other times
```
**Solution**: Add proper waits, fix race conditions, improve test isolation

### Getting Help

1. **Check Logs**: Review test output and error messages
2. **Verify Setup**: Ensure all prerequisites are met
3. **Run Individually**: Test specific components in isolation
4. **Check Documentation**: Review test documentation and examples
5. **Ask for Help**: Contact team for assistance with complex issues

## Conclusion

This testing strategy ensures that ArchMesh works correctly in real-world scenarios by testing actual functionality rather than mocked behavior. The combination of unit, integration, and E2E tests provides comprehensive coverage and confidence in the application's reliability and performance.
