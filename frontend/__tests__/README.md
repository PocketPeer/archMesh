# Frontend Test Suite

This directory contains comprehensive tests for the frontend brownfield functionality.

## Test Structure

```
__tests__/
├── components/           # Component unit tests
│   ├── ModeSelector.test.tsx
│   └── GitHubConnector.test.tsx
├── pages/               # Page integration tests
│   ├── ProjectDetailPage.test.tsx
│   └── BrownfieldDemoPage.test.tsx
├── utils/               # Test utilities and helpers
│   └── test-utils.tsx
└── README.md           # This file
```

## Test Types

### 1. Unit Tests
- **Purpose**: Test individual components in isolation
- **Location**: `components/`
- **Coverage**: Component rendering, props handling, user interactions
- **Examples**: ModeSelector, GitHubConnector

### 2. Integration Tests
- **Purpose**: Test component interactions and data flow
- **Location**: `pages/`
- **Coverage**: Page rendering, API integration, state management
- **Examples**: ProjectDetailPage, BrownfieldDemoPage

### 3. UI Tests
- **Purpose**: Test user interface and user experience
- **Location**: `pages/`
- **Coverage**: Visual rendering, accessibility, responsive design
- **Examples**: BrownfieldDemoPage

## Test Utilities

### test-utils.tsx
Provides common testing utilities:
- Custom render function with providers
- Mock data generators
- Helper functions for async operations
- Re-exports from testing-library

### Mock Data
- `mockProject`: Complete project object with brownfield data
- `mockWorkflowSession`: Workflow session data
- `mockArchitectureGraph`: Architecture visualization data
- `mockImpactAnalysis`: Impact analysis data

## Running Tests

### Using npm scripts:
```bash
# Run all tests
npm test

# Run specific test types
npm run test:unit
npm run test:integration
npm run test:brownfield

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run for CI
npm run test:ci
```

### Using the test runner script:
```bash
# Make executable
chmod +x run_tests.sh

# Run all tests
./run_tests.sh

# Run specific test types
./run_tests.sh unit
./run_tests.sh integration
./run_tests.sh brownfield

# Run with coverage
./run_tests.sh coverage

# Run in watch mode
./run_tests.sh watch
```

## Test Configuration

### Jest Configuration (jest.config.js)
- TypeScript support with ts-jest
- JSDOM environment for DOM testing
- Setup file for global mocks
- Coverage reporting
- Test file patterns

### Setup File (jest.setup.js)
- Global mocks for Next.js components
- API client mocking
- Browser API mocks
- Console warning suppression

## Mocking Strategy

### Next.js Components
- Router hooks (useRouter, useParams, useSearchParams)
- Link component
- Navigation functions

### API Client
- All API methods mocked
- Configurable responses
- Error simulation support

### External Libraries
- UUID generation
- Toast notifications
- Browser APIs (ResizeObserver, IntersectionObserver)

## Test Coverage

### Components
- ✅ ModeSelector: Rendering, mode changes, callbacks
- ✅ GitHubConnector: Input handling, API calls, error states

### Pages
- ✅ ProjectDetailPage: Rendering, data loading, mode switching
- ✅ BrownfieldDemoPage: Demo functionality, component integration

### Utilities
- ✅ test-utils: Mock data, helper functions, custom render

## Best Practices

### 1. Test Structure
- Use descriptive test names
- Group related tests with `describe`
- Use `beforeEach` for setup
- Clean up after tests

### 2. Mocking
- Mock external dependencies
- Use realistic mock data
- Test error scenarios
- Verify mock calls

### 3. Assertions
- Test user interactions
- Verify component state
- Check API calls
- Validate error handling

### 4. Accessibility
- Test keyboard navigation
- Verify ARIA attributes
- Check screen reader compatibility
- Test focus management

## Continuous Integration

### GitHub Actions
Tests run automatically on:
- Pull requests
- Push to main branch
- Scheduled runs

### Coverage Requirements
- Minimum 80% line coverage
- Minimum 70% branch coverage
- Minimum 60% function coverage

## Debugging Tests

### Common Issues
1. **Async operations**: Use `waitFor` and `findBy` queries
2. **Mock data**: Ensure mocks match expected interfaces
3. **Component state**: Wait for state updates
4. **API calls**: Mock responses properly

### Debug Commands
```bash
# Run specific test file
npm test -- ModeSelector.test.tsx

# Run with verbose output
npm test -- --verbose

# Run with coverage
npm test -- --coverage

# Debug mode
npm test -- --detectOpenHandles
```

## Future Enhancements

### Planned Tests
- [ ] E2E tests with Playwright
- [ ] Visual regression tests
- [ ] Performance tests
- [ ] Accessibility tests

### Test Improvements
- [ ] Better error simulation
- [ ] More realistic mock data
- [ ] Enhanced coverage reporting
- [ ] Parallel test execution

## Contributing

### Adding New Tests
1. Create test file in appropriate directory
2. Use existing test utilities
3. Follow naming conventions
4. Add to appropriate test script
5. Update documentation

### Test Guidelines
- Write tests before implementation (TDD)
- Keep tests simple and focused
- Use descriptive test names
- Mock external dependencies
- Test both success and error cases
