/**
 * Integration Test Setup
 * 
 * This setup file is specifically for integration tests that use real backend services.
 * It provides minimal mocking and focuses on testing actual functionality.
 */

import React from 'react';
import '@testing-library/jest-dom';

// Mock Next.js router (minimal mocking)
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    prefetch: jest.fn(),
  }),
  useParams: () => ({
    id: 'test-project-id',
    sessionId: 'test-session-id',
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
  usePathname: () => '/test-path',
}));

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: any) {
    return React.createElement('a', { href, ...props }, children);
  };
});

// Mock sonner toast (minimal mocking)
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    info: jest.fn(),
  },
}));

// DO NOT mock the API client - we want to test real functionality
// jest.mock('@/lib/api-client') - REMOVED

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock WebSocket for integration tests
global.WebSocket = jest.fn().mockImplementation(() => ({
  close: jest.fn(),
  send: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  readyState: WebSocket.OPEN,
}));

// Set up test environment variables
process.env.NEXT_PUBLIC_API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
process.env.NODE_ENV = 'test';

// Global test utilities
global.testUtils = {
  // Helper to wait for API calls to complete
  waitForApiCall: async (timeout = 5000) => {
    return new Promise(resolve => setTimeout(resolve, timeout));
  },
  
  // Helper to create test data
  createTestProject: () => ({
    name: `Test Project ${Date.now()}`,
    description: 'Test project for integration testing',
    domain: 'cloud-native',
  }),
  
  // Helper to create test file
  createTestFile: (content = 'Test content', name = 'test.txt', type = 'text/plain') => {
    return new File([content], name, { type });
  },
};

// Console configuration for integration tests
const originalConsoleError = console.error;
console.error = (...args) => {
  // Filter out known test warnings
  const message = args[0];
  if (
    typeof message === 'string' &&
    (message.includes('Warning: ReactDOM.render is no longer supported') ||
     message.includes('Warning: validateDOMNesting') ||
     message.includes('act() is not supported'))
  ) {
    return;
  }
  originalConsoleError(...args);
};
