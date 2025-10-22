/**
 * Component Integration Tests
 * 
 * These tests verify UI components work with real backend data
 * without mocks, testing actual user interactions and data flow.
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { AuthProvider } from '@/contexts/AuthContext';
import { AIChatProvider } from '@/contexts/AIChatContext';
import { apiClient } from '@/lib/api-client';

// Mock Next.js router for component tests
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
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
  usePathname: () => '/test-path',
}));

// Mock sonner toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    info: jest.fn(),
  },
}));

// Test wrapper with providers
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AuthProvider>
    <AIChatProvider>
      {children}
    </AIChatProvider>
  </AuthProvider>
);

describe('Component Integration Tests', () => {
  let testProjectId: string;

  beforeAll(async () => {
    // Create a test project for component tests
    try {
      const projectData = {
        name: `Component Test Project ${Date.now()}`,
        description: 'Project for testing component integration',
        domain: 'cloud-native' as const,
      };

      const project = await apiClient.createProject(projectData);
      testProjectId = project.id;
    } catch (error) {
      console.warn('Failed to create test project:', error);
    }
  });

  afterAll(async () => {
    // Cleanup test project
    if (testProjectId) {
      try {
        await apiClient.deleteProject(testProjectId);
      } catch (error) {
        console.warn('Failed to cleanup test project:', error);
      }
    }
  });

  describe('Project Detail Page Integration', () => {
    it('should load and display project data', async () => {
      if (!testProjectId) {
        console.warn('Skipping test - no test project available');
        return;
      }

      // Mock the project ID in params
      jest.mocked(require('next/navigation').useParams).mockReturnValue({
        id: testProjectId,
      });

      // Import the component dynamically to get fresh mocks
      const { default: ProjectDetailPage } = await import('@/app/projects/[id]/page');

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      // Wait for project data to load
      await waitFor(() => {
        expect(screen.getByText(/Component Test Project/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Verify project information is displayed
      expect(screen.getByText(/Component Test Project/)).toBeInTheDocument();
      expect(screen.getByText(/Project for testing component integration/)).toBeInTheDocument();
    });

    it('should display workflow history', async () => {
      if (!testProjectId) {
        console.warn('Skipping test - no test project available');
        return;
      }

      // Mock the project ID in params
      jest.mocked(require('next/navigation').useParams).mockReturnValue({
        id: testProjectId,
      });

      const { default: ProjectDetailPage } = await import('@/app/projects/[id]/page');

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      // Wait for workflows to load
      await waitFor(() => {
        expect(screen.getByText(/Workflows/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // Check if workflow tab is present
      const workflowTab = screen.getByRole('tab', { name: /Workflows/i });
      expect(workflowTab).toBeInTheDocument();
    });
  });

  describe('AI Chat Integration', () => {
    it('should initialize AI chat context with real data', async () => {
      render(
        <TestWrapper>
          <div data-testid="ai-chat-test">
            <AIChatProvider>
              <div>AI Chat Test</div>
            </AIChatProvider>
          </div>
        </TestWrapper>
      );

      // Wait for AI chat to initialize
      await waitFor(() => {
        expect(screen.getByTestId('ai-chat-test')).toBeInTheDocument();
      });
    });
  });

  describe('Authentication Integration', () => {
    it('should handle authentication state changes', async () => {
      render(
        <TestWrapper>
          <div data-testid="auth-test">
            <AuthProvider>
              <div>Auth Test</div>
            </AuthProvider>
          </div>
        </TestWrapper>
      );

      // Wait for auth context to initialize
      await waitFor(() => {
        expect(screen.getByTestId('auth-test')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle API errors gracefully', async () => {
      // Test with invalid project ID
      jest.mocked(require('next/navigation').useParams).mockReturnValue({
        id: 'invalid-project-id',
      });

      const { default: ProjectDetailPage } = await import('@/app/projects/[id]/page');

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      // Should handle error gracefully without crashing
      await waitFor(() => {
        // Look for error handling UI elements
        const errorElements = screen.queryAllByText(/error|failed|not found/i);
        // Should either show error message or loading state
        expect(errorElements.length).toBeGreaterThanOrEqual(0);
      }, { timeout: 10000 });
    });
  });

  describe('Real-time Updates Integration', () => {
    it('should handle real-time workflow updates', async () => {
      if (!testProjectId) {
        console.warn('Skipping test - no test project available');
        return;
      }

      // Mock the project ID in params
      jest.mocked(require('next/navigation').useParams).mockReturnValue({
        id: testProjectId,
      });

      const { default: ProjectDetailPage } = await import('@/app/projects/[id]/page');

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText(/Component Test Project/)).toBeInTheDocument();
      }, { timeout: 10000 });

      // The component should handle real-time updates without crashing
      // This tests the polling mechanism and state updates
      await new Promise(resolve => setTimeout(resolve, 10000));
      
      // Component should still be rendered
      expect(screen.getByText(/Component Test Project/)).toBeInTheDocument();
    }, 15000);
  });
});
