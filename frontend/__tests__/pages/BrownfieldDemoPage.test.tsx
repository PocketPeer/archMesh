import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import BrownfieldDemoPage from '@/app/demo-brownfield/page';

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
        <button onClick={() => onChange('greenfield')}>Switch to Greenfield</button>
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
            repository_url: 'https://github.com/example/e-commerce-platform',
            services: [],
            dependencies: [],
            technology_stack: {},
            quality_score: 0.85,
            analysis_metadata: {
              analyzed_at: new Date().toISOString(),
              services_count: 4,
              dependencies_count: 3,
              technologies_detected: ['Node.js', 'Java', 'PostgreSQL']
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
        <button onClick={() => onApprove({ approved: true })}>Approve Integration</button>
        <button onClick={() => onReject('Not suitable')}>Reject Integration</button>
      </div>
    );
  };
});

describe('BrownfieldDemoPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders demo page with title and description', () => {
    render(<BrownfieldDemoPage />);
    
    expect(screen.getByText('Brownfield Project Demo')).toBeInTheDocument();
    expect(screen.getByText(/Experience how ArchMesh handles existing system integration/)).toBeInTheDocument();
  });

  it('shows mode selector', () => {
    render(<BrownfieldDemoPage />);
    
    expect(screen.getByTestId('mode-selector')).toBeInTheDocument();
  });

  it('shows demo controls', () => {
    render(<BrownfieldDemoPage />);
    
    expect(screen.getByText('Demo Controls')).toBeInTheDocument();
    expect(screen.getByText('Load Mock Data')).toBeInTheDocument();
    expect(screen.getByText('Clear Data')).toBeInTheDocument();
  });

  it('loads mock data when button is clicked', async () => {
    render(<BrownfieldDemoPage />);
    
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByText('Current Architecture')).toBeInTheDocument();
      expect(screen.getByText('Architecture Comparison')).toBeInTheDocument();
    });
  });

  it('clears data when clear button is clicked', async () => {
    render(<BrownfieldDemoPage />);
    
    // First load mock data
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByText('Current Architecture')).toBeInTheDocument();
    });
    
    // Then clear data
    const clearButton = screen.getByText('Clear Data');
    fireEvent.click(clearButton);
    
    await waitFor(() => {
      expect(screen.queryByText('Current Architecture')).not.toBeInTheDocument();
    });
  });

  it('shows GitHub connector in brownfield mode', () => {
    render(<BrownfieldDemoPage />);
    
    expect(screen.getByTestId('github-connector')).toBeInTheDocument();
  });

  it('handles GitHub analysis completion', async () => {
    render(<BrownfieldDemoPage />);
    
    const analyzeButton = screen.getByText('Analyze Repository');
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText('Current Architecture')).toBeInTheDocument();
      expect(screen.getByText('4')).toBeInTheDocument(); // Services count
      expect(screen.getByText('3')).toBeInTheDocument(); // Dependencies count
      expect(screen.getByText('85%')).toBeInTheDocument(); // Quality score
    });
  });

  it('shows existing architecture after analysis', async () => {
    render(<BrownfieldDemoPage />);
    
    const analyzeButton = screen.getByText('Analyze Repository');
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText('Current Architecture')).toBeInTheDocument();
      expect(screen.getByText('Technologies Detected')).toBeInTheDocument();
      expect(screen.getByText('Services Found')).toBeInTheDocument();
    });
  });

  it('shows architecture comparison after loading mock data', async () => {
    render(<BrownfieldDemoPage />);
    
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('architecture-comparison')).toBeInTheDocument();
    });
  });

  it('handles integration approval', async () => {
    render(<BrownfieldDemoPage />);
    
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('architecture-comparison')).toBeInTheDocument();
    });
    
    const approveButton = screen.getByText('Approve Integration');
    fireEvent.click(approveButton);
    
    // Should not throw any errors
    await waitFor(() => {
      expect(approveButton).toBeInTheDocument();
    });
  });

  it('handles integration rejection', async () => {
    render(<BrownfieldDemoPage />);
    
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByTestId('architecture-comparison')).toBeInTheDocument();
    });
    
    const rejectButton = screen.getByText('Reject Integration');
    fireEvent.click(rejectButton);
    
    // Should not throw any errors
    await waitFor(() => {
      expect(rejectButton).toBeInTheDocument();
    });
  });

  it('shows next steps after loading mock data', async () => {
    render(<BrownfieldDemoPage />);
    
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByText('Next Steps')).toBeInTheDocument();
      expect(screen.getByText('Repository Analysis Complete')).toBeInTheDocument();
      expect(screen.getByText('Integration Design Ready')).toBeInTheDocument();
      expect(screen.getByText('Ready for Implementation')).toBeInTheDocument();
    });
  });

  it('switches to greenfield mode', () => {
    render(<BrownfieldDemoPage />);
    
    const switchButton = screen.getByText('Switch to Greenfield');
    fireEvent.click(switchButton);
    
    expect(screen.getByText('Greenfield Mode')).toBeInTheDocument();
    expect(screen.getByText('Building a new system from scratch')).toBeInTheDocument();
  });

  it('shows greenfield mode info when in greenfield mode', () => {
    render(<BrownfieldDemoPage />);
    
    const switchButton = screen.getByText('Switch to Greenfield');
    fireEvent.click(switchButton);
    
    expect(screen.getByText('New Project Mode')).toBeInTheDocument();
    expect(screen.getByText(/In greenfield mode, you can design a completely new system/)).toBeInTheDocument();
    expect(screen.getByText('Switch to Brownfield Mode')).toBeInTheDocument();
  });

  it('switches back to brownfield mode from greenfield', () => {
    render(<BrownfieldDemoPage />);
    
    // Switch to greenfield first
    const switchToGreenfield = screen.getByText('Switch to Greenfield');
    fireEvent.click(switchToGreenfield);
    
    // Then switch back to brownfield
    const switchToBrownfield = screen.getByText('Switch to Brownfield Mode');
    fireEvent.click(switchToBrownfield);
    
    expect(screen.getByTestId('github-connector')).toBeInTheDocument();
  });

  it('shows technologies in existing architecture', async () => {
    render(<BrownfieldDemoPage />);
    
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByText('Node.js')).toBeInTheDocument();
      expect(screen.getByText('Java')).toBeInTheDocument();
      expect(screen.getAllByText('PostgreSQL')).toHaveLength(3); // Appears in technologies and services
      expect(screen.getByText('Express')).toBeInTheDocument();
      expect(screen.getByText('Spring Boot')).toBeInTheDocument();
    });
  });

  it('shows services in existing architecture', async () => {
    render(<BrownfieldDemoPage />);
    
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByText('User Service')).toBeInTheDocument();
      expect(screen.getByText('User Database')).toBeInTheDocument();
      expect(screen.getByText('Payment Service')).toBeInTheDocument();
      expect(screen.getByText('Payment Database')).toBeInTheDocument();
    });
  });

  it('shows service descriptions and technologies', async () => {
    render(<BrownfieldDemoPage />);
    
    const loadButton = screen.getByText('Load Mock Data');
    fireEvent.click(loadButton);
    
    await waitFor(() => {
      expect(screen.getByText('Handles user authentication and profiles')).toBeInTheDocument();
      expect(screen.getByText('Stores user data and authentication info')).toBeInTheDocument();
      expect(screen.getByText('Node.js + Express')).toBeInTheDocument();
      expect(screen.getAllByText('PostgreSQL')).toHaveLength(3); // Appears in technologies and services
    });
  });
});
