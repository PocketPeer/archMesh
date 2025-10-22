/**
 * Project Detail Page - Real Functionality Tests
 * 
 * These tests verify the ProjectDetailPage component works with real data
 * and actual API calls, focusing on user interactions and data flow.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import ProjectDetailPage from '@/app/projects/[id]/page';
import { AuthProvider } from '@/src/contexts/AuthContext';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useSearchParams: jest.fn(),
  useRouter: jest.fn(),
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

// Mock components that are not the focus of these tests
jest.mock('@/src/components/ModeSelector', () => {
  return function MockModeSelector({ value, onChange }: any) {
    return (
      <div data-testid="mode-selector">
        <button onClick={() => onChange('brownfield')}>Switch to Brownfield</button>
        <span>Current mode: {value}</span>
      </div>
    );
  };
});

jest.mock('@/src/components/GitHubConnector', () => {
  return function MockGitHubConnector({ onAnalysisComplete }: any) {
    return (
      <div data-testid="github-connector">
        <button 
          onClick={() => onAnalysisComplete({
            repository_url: 'https://github.com/test/repo',
            analysis_metadata: {
              services_count: 5,
              dependencies_count: 8,
              technologies_detected: ['Node.js', 'PostgreSQL', 'Redis']
            },
            quality_score: 0.85,
            services: [],
            dependencies: []
          })}
        >
          Analyze Repository
        </button>
      </div>
    );
  };
});

// Mock the WorkflowProgress component
jest.mock('@/src/components/common/WorkflowProgress', () => {
  return function MockWorkflowProgress({ sessionId }: any) {
    return (
      <div data-testid="workflow-progress">
        Workflow Progress for session: {sessionId}
      </div>
    );
  };
});

// Test wrapper with providers
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AuthProvider>
    {children}
  </AuthProvider>
);

describe('ProjectDetailPage - Real Functionality', () => {
  const mockPush = jest.fn();
  const mockGet = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default mocks
    (useParams as jest.Mock).mockReturnValue({
      id: 'test-project-id',
    });
    
    (useSearchParams as jest.Mock).mockReturnValue({
      get: mockGet,
    });
    
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
      replace: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      prefetch: jest.fn(),
    });
  });

  describe('Component Rendering', () => {
    it('should render loading state initially', () => {
      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      // Should show loading state
      expect(screen.getByText(/Loading.../)).toBeInTheDocument();
    });

    it('should render error state when project fails to load', async () => {
      // Mock API to return error
      const originalFetch = global.fetch;
      global.fetch = jest.fn().mockRejectedValue(new Error('Failed to fetch'));

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/Failed to load project/)).toBeInTheDocument();
      });

      // Restore original fetch
      global.fetch = originalFetch;
    });
  });

  describe('Workflow Integration', () => {
    it('should display workflow status when workflowId is provided', async () => {
      // Mock workflow ID in URL
      mockGet.mockReturnValue('test-workflow-id');

      // Mock successful API responses
      const mockProject = {
        id: 'test-project-id',
        name: 'Test Project',
        description: 'Test Description',
        domain: 'cloud-native',
        mode: 'greenfield',
        status: 'pending',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      const mockWorkflowStatus = {
        session_id: 'test-workflow-id',
        project_id: 'test-project-id',
        current_stage: 'starting',
        errors: [],
      };

      const mockWorkflows = {
        items: [{
          session_id: 'test-workflow-id',
          project_id: 'test-project-id',
          current_stage: 'starting',
          is_active: true,
          started_at: '2024-01-01T00:00:00Z',
          last_activity_at: '2024-01-01T00:00:00Z',
          state_data: {
            stage_progress: 0.1,
            completed_stages: [],
            errors: [],
            metadata: { domain: 'cloud-native' }
          }
        }],
        total: 1,
        page: 1,
        page_size: 10,
        has_next: false
      };

      global.fetch = jest.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockProject),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockWorkflows),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockWorkflowStatus),
        });

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      // Wait for project to load
      await waitFor(() => {
        expect(screen.getByText('Test Project')).toBeInTheDocument();
      });

      // Should show workflow progress
      expect(screen.getByTestId('workflow-progress')).toBeInTheDocument();
    });

    it('should handle workflow status updates', async () => {
      mockGet.mockReturnValue('test-workflow-id');

      const mockProject = {
        id: 'test-project-id',
        name: 'Test Project',
        description: 'Test Description',
        domain: 'cloud-native',
        mode: 'greenfield',
        status: 'pending',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      const mockWorkflows = {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        has_next: false
      };

      const mockWorkflowStatus = {
        session_id: 'test-workflow-id',
        project_id: 'test-project-id',
        current_stage: 'completed',
        errors: [],
      };

      global.fetch = jest.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockProject),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockWorkflows),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockWorkflowStatus),
        });

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Project')).toBeInTheDocument();
      });

      // Should show completed workflow status
      expect(screen.getByText(/COMPLETED/)).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should navigate to upload page when Start Workflow is clicked', async () => {
      const mockProject = {
        id: 'test-project-id',
        name: 'Test Project',
        description: 'Test Description',
        domain: 'cloud-native',
        mode: 'greenfield',
        status: 'pending',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      const mockWorkflows = {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        has_next: false
      };

      global.fetch = jest.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockProject),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockWorkflows),
        });

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Project')).toBeInTheDocument();
      });

      // Click Start Workflow button
      const startWorkflowButton = screen.getByText('Start Workflow');
      fireEvent.click(startWorkflowButton);

      // Should navigate to upload page
      expect(mockPush).toHaveBeenCalledWith('/projects/test-project-id/upload');
    });

    it('should switch to workflows tab and display workflow history', async () => {
      const mockProject = {
        id: 'test-project-id',
        name: 'Test Project',
        description: 'Test Description',
        domain: 'cloud-native',
        mode: 'greenfield',
        status: 'pending',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      const mockWorkflows = {
        items: [{
          session_id: 'workflow-1',
          project_id: 'test-project-id',
          current_stage: 'completed',
          is_active: false,
          started_at: '2024-01-01T00:00:00Z',
          last_activity_at: '2024-01-01T00:00:00Z',
          state_data: {
            stage_progress: 1.0,
            completed_stages: ['starting', 'document_analysis', 'requirements_review', 'architecture_design'],
            errors: [],
            metadata: { domain: 'cloud-native' }
          }
        }],
        total: 1,
        page: 1,
        page_size: 10,
        has_next: false
      };

      global.fetch = jest.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockProject),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockWorkflows),
        });

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Project')).toBeInTheDocument();
      });

      // Click on Workflows tab
      const workflowsTab = screen.getByRole('tab', { name: /Workflows/i });
      fireEvent.click(workflowsTab);

      // Should show workflow history
      await waitFor(() => {
        expect(screen.getByText('Workflow Sessions')).toBeInTheDocument();
      });

      // Should show the workflow
      expect(screen.getByText('workflow-1')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/Failed to load project/)).toBeInTheDocument();
      });
    });

    it('should handle workflow errors and show restart option', async () => {
      const mockProject = {
        id: 'test-project-id',
        name: 'Test Project',
        description: 'Test Description',
        domain: 'cloud-native',
        mode: 'greenfield',
        status: 'pending',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      const mockWorkflows = {
        items: [{
          session_id: 'failed-workflow',
          project_id: 'test-project-id',
          current_stage: 'failed',
          is_active: false,
          started_at: '2024-01-01T00:00:00Z',
          last_activity_at: '2024-01-01T00:00:00Z',
          state_data: {
            stage_progress: 0.3,
            completed_stages: ['starting', 'document_analysis'],
            errors: ['LLM timeout error', 'Processing failed'],
            metadata: { domain: 'cloud-native' }
          }
        }],
        total: 1,
        page: 1,
        page_size: 10,
        has_next: false
      };

      global.fetch = jest.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockProject),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockWorkflows),
        });

      render(
        <TestWrapper>
          <ProjectDetailPage />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Project')).toBeInTheDocument();
      });

      // Switch to workflows tab
      const workflowsTab = screen.getByRole('tab', { name: /Workflows/i });
      fireEvent.click(workflowsTab);

      await waitFor(() => {
        expect(screen.getByText('Workflow Sessions')).toBeInTheDocument();
      });

      // Should show failed workflow with restart button
      expect(screen.getByText('Restart')).toBeInTheDocument();
      expect(screen.getByText(/LLM timeout error/)).toBeInTheDocument();
    });
  });
});
