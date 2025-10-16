/**
 * Tests for ProjectDetailPage component.
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { useParams, useSearchParams } from 'next/navigation';
import ProjectDetailPage from '@/app/projects/[id]/page';
import { apiClient } from '@/lib/api-client';
import { Project, WorkflowSession, WorkflowStatus } from '@/types';

// Mock Next.js hooks
jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    getProject: jest.fn(),
    listWorkflows: jest.fn(),
    getWorkflowStatus: jest.fn(),
    getRequirements: jest.fn(),
    getArchitecture: jest.fn(),
  },
}));

const mockProject: Project = {
  id: 'test-project-id',
  name: 'Test Project',
  description: 'A test project for unit testing',
  domain: 'cloud-native',
  status: 'pending',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockWorkflowSession: WorkflowSession = {
  id: 'test-session-id',
  project_id: 'test-project-id',
  current_stage: 'starting',
  status: 'starting',
  is_active: true,
  started_at: '2024-01-01T00:00:00Z',
  last_activity: '2024-01-01T00:00:00Z',
};

const mockWorkflowStatus: WorkflowStatus = {
  session_id: 'test-session-id',
  current_stage: 'requirements_review',
  stage_progress: 0.5,
  is_active: true,
  last_updated: '2024-01-01T00:00:00Z',
};

describe('ProjectDetailPage', () => {
  beforeEach(() => {
    (useParams as jest.Mock).mockReturnValue({ id: 'test-project-id' });
    (useSearchParams as jest.Mock).mockReturnValue({ get: jest.fn() });
    (apiClient.getProject as jest.Mock).mockResolvedValue(mockProject);
    (apiClient.listWorkflows as jest.Mock).mockResolvedValue({ items: [mockWorkflowSession] });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders project information correctly', async () => {
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
      expect(screen.getByText('A test project for unit testing')).toBeInTheDocument();
    });
  });

  it('displays project stats correctly', async () => {
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Workflows')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument(); // One workflow
      expect(screen.getByText('Active Workflows')).toBeInTheDocument();
    });
  });

  it('shows current workflow status when workflow ID is provided', async () => {
    (useSearchParams as jest.Mock).mockReturnValue({ 
      get: jest.fn().mockReturnValue('test-session-id') 
    });
    (apiClient.getWorkflowStatus as jest.Mock).mockResolvedValue(mockWorkflowStatus);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Current Workflow Status')).toBeInTheDocument();
      expect(screen.getByText('REQUIREMENTS REVIEW')).toBeInTheDocument();
    });
  });

  it('shows requirements review notification when in requirements_review stage', async () => {
    (useSearchParams as jest.Mock).mockReturnValue({ 
      get: jest.fn().mockReturnValue('test-session-id') 
    });
    (apiClient.getWorkflowStatus as jest.Mock).mockResolvedValue(mockWorkflowStatus);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Requirements Review Required')).toBeInTheDocument();
      expect(screen.getByText('Please review and approve the extracted requirements before the architecture design begins.')).toBeInTheDocument();
    });
  });

  it('shows architecture review notification when in architecture_review stage', async () => {
    const architectureReviewStatus = { ...mockWorkflowStatus, current_stage: 'architecture_review' };
    (useSearchParams as jest.Mock).mockReturnValue({ 
      get: jest.fn().mockReturnValue('test-session-id') 
    });
    (apiClient.getWorkflowStatus as jest.Mock).mockResolvedValue(architectureReviewStatus);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Architecture Review Required')).toBeInTheDocument();
      expect(screen.getByText('Please review and approve the generated architecture design.')).toBeInTheDocument();
    });
  });

  it('displays workflow results when available', async () => {
    const completedStatus = { ...mockWorkflowStatus, current_stage: 'completed' };
    const mockRequirements = {
      structured_requirements: {
        business_goals: ['Launch online marketplace'],
        functional_requirements: ['User registration'],
        non_functional_requirements: {
          performance: ['Handle 1000 users'],
          security: ['Encrypt data']
        }
      }
    };
    const mockArchitecture = {
      overview: 'Microservices-based e-commerce platform',
      technology_stack: ['Node.js', 'PostgreSQL'],
      components: [
        { name: 'User Service', description: 'Handles user authentication' }
      ]
    };

    (useSearchParams as jest.Mock).mockReturnValue({ 
      get: jest.fn().mockReturnValue('test-session-id') 
    });
    (apiClient.getWorkflowStatus as jest.Mock).mockResolvedValue(completedStatus);
    (apiClient.getRequirements as jest.Mock).mockResolvedValue(mockRequirements);
    (apiClient.getArchitecture as jest.Mock).mockResolvedValue(mockArchitecture);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Workflow Results')).toBeInTheDocument();
      expect(screen.getByText('Requirements')).toBeInTheDocument();
      expect(screen.getByText('Architecture')).toBeInTheDocument();
    });
  });

  it('handles loading state correctly', () => {
    (apiClient.getProject as jest.Mock).mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<ProjectDetailPage />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('handles error state correctly', async () => {
    (apiClient.getProject as jest.Mock).mockRejectedValue(new Error('Failed to load project'));
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Project Not Found')).toBeInTheDocument();
    });
  });

  it('refreshes workflow status periodically for active workflows', async () => {
    jest.useFakeTimers();
    
    (useSearchParams as jest.Mock).mockReturnValue({ 
      get: jest.fn().mockReturnValue('test-session-id') 
    });
    (apiClient.getWorkflowStatus as jest.Mock).mockResolvedValue(mockWorkflowStatus);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(apiClient.getWorkflowStatus).toHaveBeenCalledTimes(1);
    });
    
    // Fast-forward time to trigger polling
    jest.advanceTimersByTime(5000);
    
    await waitFor(() => {
      expect(apiClient.getWorkflowStatus).toHaveBeenCalledTimes(2);
    });
    
    jest.useRealTimers();
  });

  it('stops polling when workflow is completed', async () => {
    jest.useFakeTimers();
    
    const completedStatus = { ...mockWorkflowStatus, current_stage: 'completed' };
    (useSearchParams as jest.Mock).mockReturnValue({ 
      get: jest.fn().mockReturnValue('test-session-id') 
    });
    (apiClient.getWorkflowStatus as jest.Mock).mockResolvedValue(completedStatus);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(apiClient.getWorkflowStatus).toHaveBeenCalledTimes(1);
    });
    
    // Fast-forward time - should not trigger more polling
    jest.advanceTimersByTime(10000);
    
    await waitFor(() => {
      expect(apiClient.getWorkflowStatus).toHaveBeenCalledTimes(1);
    });
    
    jest.useRealTimers();
  });
});
