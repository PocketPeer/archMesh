# E2E Test Documentation

## Overview

This document describes the E2E testing strategy, patterns, and best practices for the ArchMesh application.

## Test Structure

### Test Categories

1. **Authentication Flow Tests** (`authentication-flow.test.ts`)
   - User registration and login
   - Session management
   - Authentication error handling

2. **Real Functionality Tests** (`real-functionality.test.ts`)
   - Complete user journeys
   - Workflow execution
   - Integration with backend services

3. **User Workflow Tests** (`user-workflows.test.ts`)
   - Realistic user scenarios
   - Business process validation
   - User experience testing

4. **Feature Implementation Tests** (`feature-implementation.test.ts`)
   - Specific feature validation
   - UI component testing
   - Integration testing

5. **Team Collaboration Tests** (`team-collaboration.test.ts`)
   - Multi-user scenarios
   - Permission testing
   - Collaboration features

## Test Configuration

### Centralized Configuration (`test-config.ts`)

```typescript
export const E2E_CONFIG = {
  baseUrl: 'http://localhost:3000',
  apiBaseUrl: 'http://localhost:8000',
  timeouts: {
    test: 180000,        // 3 minutes
    workflow: 120000,     // 2 minutes
    navigation: 15000,   // 15 seconds
    element: 10000,      // 10 seconds
  },
  polling: {
    workflow: 3000,      // 3 seconds
    ui: 1000,           // 1 second
  }
};
```

### Test Utilities (`test-utils.ts`)

Optimized utilities for common test operations:

- `waitForElement()` - Smart element waiting with retry logic
- `waitForWorkflowStatus()` - Workflow completion monitoring
- `fillFormField()` - Form filling with retry logic
- `clickElement()` - Element clicking with retry logic
- `createTestUser()` - Dynamic test user creation
- `retryOperation()` - Retry mechanism for flaky operations

## Test Patterns

### 1. User Journey Testing

```typescript
test('Complete User Journey', async () => {
  // Step 1: Navigate to homepage
  await page.goto(E2E_CONFIG.baseUrl);
  await waitForPageLoad(page);
  
  // Step 2: User registration
  await clickElement(page, 'text=Sign Up');
  await waitForNavigation(page, '**/register');
  
  // Step 3: Fill registration form
  await fillFormField(page, 'input[name="email"]', testUser.email);
  await fillFormField(page, 'input[name="password"]', testUser.password);
  
  // Step 4: Submit and verify
  await clickElement(page, 'button[type="submit"]');
  await waitForElement(page, 'text=Registration successful');
});
```

### 2. Workflow Testing

```typescript
test('Workflow Execution', async () => {
  // Start workflow
  await clickElement(page, 'text=Start Workflow');
  await waitForNavigation(page, '**/upload');
  
  // Upload file and context
  await fileInput.setInputFiles(filePath);
  await fillFormField(page, 'textarea[placeholder*="context"]', context);
  
  // Submit and monitor
  await clickElement(page, 'button[type="submit"]');
  await waitForNavigation(page, /\/projects\/[^\/]+/);
  
  // Wait for completion
  const status = await waitForWorkflowStatus(page, ['completed', 'failed']);
  expect(status).toBeDefined();
});
```

### 3. Error Handling Testing

```typescript
test('Error Recovery', async () => {
  // Simulate error condition
  await page.goto('/projects/invalid-id');
  
  // Verify error handling
  await expect(page.locator('text=Project not found')).toBeVisible();
  
  // Test recovery
  await clickElement(page, 'text=Go Back');
  await waitForNavigation(page, '**/projects');
});
```

## Best Practices

### 1. Test Data Management

```typescript
// ✅ Good: Dynamic test data
const testUser = createTestUser();
const testProject = createTestProject();

// ❌ Bad: Static test data
const testUser = { email: 'test@example.com', password: 'password' };
```

### 2. Wait Strategies

```typescript
// ✅ Good: Smart waits
await waitForElement(page, '[data-testid="workflow-status"]');
await waitForWorkflowStatus(page, ['completed', 'failed']);

// ❌ Bad: Fixed timeouts
await page.waitForTimeout(5000);
```

### 3. Error Handling

```typescript
// ✅ Good: Retry logic
await retryOperation(async () => {
  await clickElement(page, 'button[type="submit"]');
});

// ❌ Bad: No error handling
await page.click('button[type="submit"]');
```

### 4. Test Isolation

```typescript
// ✅ Good: Clean setup/teardown
test.beforeEach(async ({ browser }) => {
  page = await browser.newPage();
  testUser = createTestUser();
});

test.afterEach(async () => {
  await page.close();
  // Cleanup test data
});
```

## Performance Monitoring

### Metrics Tracked

- **Execution Time**: Test duration
- **Success Rate**: Pass/fail ratio
- **Flakiness Score**: Intermittent failure rate
- **Resource Usage**: Memory and CPU consumption
- **Network Requests**: API call count

### Performance Report

```typescript
import { PerformanceMonitor } from './performance-monitor';

const monitor = new PerformanceMonitor(page);

test('Performance Test', async () => {
  monitor.startTest('User Registration');
  
  // Test operations...
  
  const metrics = monitor.endTest();
  console.log(`Test completed in ${metrics.duration}ms`);
});
```

## Debugging

### Screenshots on Failure

```typescript
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === 'failed') {
    await page.screenshot({ 
      path: `test-results/failure-${testInfo.title}.png`,
      fullPage: true 
    });
  }
});
```

### Console Logging

```typescript
// Enable console logging for debugging
test.beforeEach(async ({ page }) => {
  page.on('console', msg => console.log(msg.text()));
});
```

### Network Monitoring

```typescript
// Monitor API calls
page.on('request', request => {
  console.log(`API Request: ${request.method()} ${request.url()}`);
});

page.on('response', response => {
  console.log(`API Response: ${response.status()} ${response.url()}`);
});
```

## Maintenance

### Regular Tasks

1. **Update Test Data**: Keep test data current with application changes
2. **Review Flaky Tests**: Identify and fix intermittent failures
3. **Performance Analysis**: Monitor test execution times
4. **Selector Updates**: Update selectors when UI changes

### Test Maintenance Checklist

- [ ] All tests use centralized configuration
- [ ] Test data is dynamic and unique
- [ ] Wait strategies are optimized
- [ ] Error handling is comprehensive
- [ ] Performance is monitored
- [ ] Screenshots are captured on failure
- [ ] Tests are isolated and independent

## Troubleshooting

### Common Issues

1. **Timeout Errors**: Increase timeout or improve wait strategy
2. **Element Not Found**: Update selectors or add retry logic
3. **Flaky Tests**: Add proper wait conditions
4. **Slow Tests**: Optimize wait strategies and reduce unnecessary operations

### Debug Commands

```bash
# Run specific test with debug output
npx playwright test --debug user-workflows.test.ts

# Run tests with headed browser
npx playwright test --headed

# Generate test report
npx playwright show-report
```

## Future Improvements

1. **Parallel Execution**: Run independent tests in parallel
2. **Visual Testing**: Add screenshot comparison tests
3. **API Testing**: Separate API tests from UI tests
4. **Mobile Testing**: Add mobile device testing
5. **Accessibility Testing**: Add a11y test coverage
