# Integration Tests

These tests verify the complete application functionality using real backend services without mocks.

## Prerequisites

Before running integration tests, ensure:

1. **Backend Server Running**: The backend must be running on `http://localhost:8000`
2. **Database Initialized**: The database should be set up with all required tables
3. **Services Available**: All required services (Ollama, etc.) should be running
4. **Environment Variables**: Ensure all required environment variables are set

## Running Integration Tests

### All Integration Tests
```bash
npm run test:integration
```

### Specific Test Categories
```bash
# API Client tests
npm run test:integration:api

# Workflow tests
npm run test:integration:workflow

# Component tests
npm run test:integration:components
```

### Watch Mode
```bash
npm run test:integration:watch
```

## Test Structure

### API Client Integration Tests (`api-client.integration.test.ts`)
- Tests real API calls to backend
- Verifies authentication and token refresh
- Tests project CRUD operations
- Tests workflow management
- Tests error handling

### Workflow Integration Tests (`workflow.integration.test.ts`)
- Tests complete workflow lifecycle
- Tests document upload and processing
- Tests real-time status updates
- Tests timeout handling
- Tests results retrieval

### Component Integration Tests (`components.integration.test.tsx`)
- Tests UI components with real data
- Tests context providers
- Tests error handling in components
- Tests real-time updates

## Test Configuration

### Timeouts
- Default timeout: 2 minutes (120,000ms)
- Workflow tests: Up to 2 minutes for processing
- API tests: 30 seconds for individual calls

### Test Data
- Tests create real projects and workflows
- Automatic cleanup after each test
- Unique test data using timestamps

### Environment
- Uses real backend API
- No mocking of API client
- Minimal mocking of Next.js components
- Real database operations

## What These Tests Verify

### ✅ Real Functionality
- Actual API calls work correctly
- Database operations succeed
- Authentication flows properly
- Workflow execution completes

### ✅ Integration Issues
- API endpoint compatibility
- Data format consistency
- Error handling robustness
- Performance under load

### ✅ User Experience
- Complete user journeys work
- Error messages are helpful
- Loading states are appropriate
- Real-time updates function

## Troubleshooting

### Backend Not Running
```
Error: Backend not available at http://localhost:8000
```
**Solution**: Start the backend server with `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Database Issues
```
Error: Failed to create project
```
**Solution**: Ensure database is initialized and accessible

### Timeout Issues
```
Error: Test timeout exceeded
```
**Solution**: Check if backend services are responding slowly, increase timeout if needed

### Workflow Failures
```
Error: Workflow failed with errors
```
**Solution**: Check Ollama service, LLM configuration, and backend logs

## Best Practices

1. **Run tests in sequence**: Integration tests should run one at a time to avoid conflicts
2. **Clean up data**: Tests automatically clean up created data
3. **Check logs**: Monitor backend logs during test execution
4. **Verify services**: Ensure all required services are running before tests
5. **Use real data**: Tests use realistic test data to catch real issues

## Continuous Integration

These tests are designed to run in CI environments:

- Tests are deterministic and repeatable
- Automatic cleanup prevents data pollution
- Clear error messages for debugging
- Appropriate timeouts for CI environments

## Debugging

### Enable Verbose Logging
```bash
npm run test:integration -- --verbose
```

### Run Single Test
```bash
npm run test:integration -- --testNamePattern="should create a new project"
```

### Debug Mode
```bash
npm run test:integration:watch
```

## Expected Results

When all tests pass, you can be confident that:

- ✅ Frontend and backend communicate correctly
- ✅ All API endpoints work as expected
- ✅ Workflow processing functions properly
- ✅ Error handling is robust
- ✅ User experience is smooth
- ✅ Real-time features work correctly
