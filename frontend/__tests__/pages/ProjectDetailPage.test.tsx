import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useParams, useSearchParams } from 'next/navigation';
import ProjectDetailPage from '@/app/projects/[id]/page';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    getProject: jest.fn(),
    listWorkflows: jest.fn(),
    getWorkflowStatus: jest.fn(),
    getRequirements: jest.fn(),
    getArchitecture: jest.fn(),
  },
}));

// Mock the toast function
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock the components
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
            services: [],
            dependencies: [],
            technology_stack: {},
            quality_score: 0.8,
            analysis_metadata: {
              analyzed_at: new Date().toISOString(),
              services_count: 0,
              dependencies_count: 0,
              technologies_detected: []
            }
          })}
        >
          Analyze Repository
        </button>
      </div>
    );
  };
});

jest.mock('@/src/components/architecture/ArchitectureComparison', () => {
  return function MockArchitectureComparison({ onApprove, onReject }: any) {
    return (
      <div data-testid="architecture-comparison">
        <button onClick={() => onApprove({ approved: true })}>Approve</button>
        <button onClick={() => onReject('Not suitable')}>Reject</button>
      </div>
    );
  };
});

describe('ProjectDetailPage', () => {
  const mockProject = {
    id: 'test-project',
    name: 'Test Project',
    description: 'Test Description',
    domain: 'cloud-native' as const,
    mode: 'greenfield' as const,
    status: 'pending' as const,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  };

  const mockWorkflows = [
    {
      session_id: 'session-1',
      project_id: 'test-project',
      current_stage: 'completed',
      state_data: {
        current_stage: 'completed',
        stage_progress: 1.0,
        completed_stages: ['starting', 'document_analysis', 'requirements_review', 'architecture_design', 'architecture_review'],
        stage_results: {},
        pending_tasks: [],
        errors: [],
        metadata: {},
      },
      is_active: false,
      started_at: '2023-01-01T00:00:00Z',
      last_activity_at: '2023-01-01T00:00:00Z',
      completed_at: '2023-01-01T00:00:00Z',
      agent_executions: [],
      human_feedback: [],
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    
    (useParams as jest.Mock).mockReturnValue({ id: 'test-project' });
    (useSearchParams as jest.Mock).mockReturnValue(new URLSearchParams());
    
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockResolvedValue(mockProject);
    apiClient.listWorkflows.mockResolvedValue({ items: mockWorkflows });
  });

  it('renders project details', async () => {
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Test Project' })).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });
  });

  it('shows mode selector', async () => {
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('mode-selector')).toBeInTheDocument();
    });
  });

  it('switches to brownfield mode', async () => {
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('mode-selector')).toBeInTheDocument();
    });
    
    const switchButton = screen.getByText('Switch to Brownfield');
    fireEvent.click(switchButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('github-connector')).toBeInTheDocument();
    });
  });

  it('shows GitHub connector in brownfield mode', async () => {
    const brownfieldProject = { ...mockProject, mode: 'brownfield' };
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockResolvedValue(brownfieldProject);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('github-connector')).toBeInTheDocument();
    });
  });

  it('handles GitHub analysis completion', async () => {
    const brownfieldProject = { ...mockProject, mode: 'brownfield' };
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockResolvedValue(brownfieldProject);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('github-connector')).toBeInTheDocument();
    });
    
    const analyzeButton = screen.getByText('Analyze Repository');
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText('Current Architecture')).toBeInTheDocument();
    });
  });

  it('shows existing architecture after analysis', async () => {
    const brownfieldProject = { 
      ...mockProject, 
      mode: 'brownfield',
      existing_architecture: {
        repository_url: 'https://github.com/test/repo',
        branch: 'main',
        services: [
          {
            id: 'user-service',
            name: 'User Service',
            type: 'service',
            technology: 'Node.js',
            description: 'User management service',
          }
        ],
        dependencies: [],
        technology_stack: { 'Node.js': 1 },
        quality_score: 0.8,
        analysis_metadata: {
          analyzed_at: new Date().toISOString(),
          services_count: 1,
          dependencies_count: 0,
          technologies_detected: ['Node.js']
        }
      }
    };
    
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockResolvedValue(brownfieldProject);
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Current Architecture')).toBeInTheDocument();
      expect(screen.getByText('User Service')).toBeInTheDocument();
    });
  });

  it('shows architecture comparison when both architectures exist', async () => {
    const brownfieldProject = { 
      ...mockProject, 
      mode: 'brownfield',
      existing_architecture: {
        repository_url: 'https://github.com/test/repo',
        branch: 'main',
        services: [],
        dependencies: [],
        technology_stack: {},
        quality_score: 0.8,
        analysis_metadata: {
          analyzed_at: new Date().toISOString(),
          services_count: 0,
          dependencies_count: 0,
          technologies_detected: []
        }
      },
      proposed_architecture: {
        architecture_overview: {
          style: 'microservices',
          integration_approach: 'event-driven',
          rationale: 'Test rationale'
        },
        new_services: [],
        modified_services: [],
        integration_points: [],
        impact_analysis: {
          risk_level: 'low',
          breaking_changes: false,
          downtime_required: false
        }
      },
      changes: []
    };
    
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockResolvedValue(brownfieldProject);
    apiClient.listWorkflows.mockResolvedValue({ items: [] });
    
    render(<ProjectDetailPage />);
    
    // Wait for project to load first
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Test Project' })).toBeInTheDocument();
    });
    
    // Then check for architecture comparison
    await waitFor(() => {
      expect(screen.getByText('Architecture Comparison')).toBeInTheDocument();
    });
  });

  it('handles architecture approval', async () => {
    const brownfieldProject = { 
      ...mockProject, 
      mode: 'brownfield',
      existing_architecture: {
        repository_url: 'https://github.com/test/repo',
        branch: 'main',
        services: [],
        dependencies: [],
        technology_stack: {},
        quality_score: 0.8,
        analysis_metadata: {
          analyzed_at: new Date().toISOString(),
          services_count: 0,
          dependencies_count: 0,
          technologies_detected: []
        }
      },
      proposed_architecture: {
        architecture_overview: {
          style: 'microservices',
          integration_approach: 'event-driven',
          rationale: 'Test rationale'
        },
        new_services: [],
        modified_services: [],
        integration_points: [],
        impact_analysis: {
          risk_level: 'low',
          breaking_changes: false,
          downtime_required: false
        }
      },
      changes: []
    };
    
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockResolvedValue(brownfieldProject);
    apiClient.listWorkflows.mockResolvedValue({ items: [] });
    
    render(<ProjectDetailPage />);
    
    // Wait for project to load first
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Test Project' })).toBeInTheDocument();
    });
    
    // Then check for architecture comparison
    await waitFor(() => {
      expect(screen.getByText('Architecture Comparison')).toBeInTheDocument();
    });
    
    const approveButton = screen.getByText('Approve');
    fireEvent.click(approveButton);
    
    // Should not throw any errors
    await waitFor(() => {
      expect(approveButton).toBeInTheDocument();
    });
  });

  it('handles architecture rejection', async () => {
    const brownfieldProject = { 
      ...mockProject, 
      mode: 'brownfield',
      existing_architecture: {
        repository_url: 'https://github.com/test/repo',
        branch: 'main',
        services: [],
        dependencies: [],
        technology_stack: {},
        quality_score: 0.8,
        analysis_metadata: {
          analyzed_at: new Date().toISOString(),
          services_count: 0,
          dependencies_count: 0,
          technologies_detected: []
        }
      },
      proposed_architecture: {
        architecture_overview: {
          style: 'microservices',
          integration_approach: 'event-driven',
          rationale: 'Test rationale'
        },
        new_services: [],
        modified_services: [],
        integration_points: [],
        impact_analysis: {
          risk_level: 'low',
          breaking_changes: false,
          downtime_required: false
        }
      },
      changes: []
    };
    
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockResolvedValue(brownfieldProject);
    apiClient.listWorkflows.mockResolvedValue({ items: [] });
    
    render(<ProjectDetailPage />);
    
    // Wait for project to load first
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Test Project' })).toBeInTheDocument();
    });
    
    // Then check for architecture comparison
    await waitFor(() => {
      expect(screen.getByText('Architecture Comparison')).toBeInTheDocument();
    });
    
    const rejectButton = screen.getByText('Reject');
    fireEvent.click(rejectButton);
    
    // Should not throw any errors
    await waitFor(() => {
      expect(rejectButton).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<ProjectDetailPage />);
    
    // Check for loading skeleton elements
    expect(screen.queryByText('Test Project')).not.toBeInTheDocument();
    // The component shows a loading skeleton with animate-pulse class
    expect(screen.getByText((content, element) => {
      return element?.classList.contains('animate-pulse') || false;
    })).toBeInTheDocument();
  });

  it('shows error state when project not found', async () => {
    const { apiClient } = require('@/lib/api-client');
    apiClient.getProject.mockRejectedValue(new Error('Project not found'));
    
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Project Not Found')).toBeInTheDocument();
    });
  });

  it('shows workflow statistics', async () => {
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Workflows')).toBeInTheDocument();
      expect(screen.getAllByText('1')).toHaveLength(2); // Appears in multiple places
    });
  });

  it('shows project information', async () => {
    render(<ProjectDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Project Information')).toBeInTheDocument();
      expect(screen.getByText('test-project')).toBeInTheDocument();
    });
  });
});