/**
 * Jest configuration for integration tests
 * 
 * These tests run against real backend services without mocks.
 */

module.exports = {
  displayName: 'Integration Tests',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/setup.ts'],
  testMatch: [
    '<rootDir>/**/*.integration.test.ts',
    '<rootDir>/**/*.integration.test.tsx',
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/../../$1',
    '^@/contexts/(.*)$': '<rootDir>/../../src/contexts/$1',
  },
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
      },
    }],
  },
  testTimeout: 120000, // 2 minutes for integration tests
  maxWorkers: 1, // Run integration tests sequentially to avoid conflicts
  collectCoverage: false, // Disable coverage for integration tests
  verbose: true,
  // Don't mock anything - use real implementations
  clearMocks: true,
  resetMocks: false,
  restoreMocks: false,
};
