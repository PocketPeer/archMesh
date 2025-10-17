import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import GitHubConnector from '@/src/components/GitHubConnector';

// Mock the toast function
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('GitHubConnector', () => {
  const defaultProps = {
    projectId: 'test-project',
    onAnalysisComplete: jest.fn(),
    onError: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with initial form', () => {
    render(<GitHubConnector {...defaultProps} />);
    
    expect(screen.getByText('GitHub Repository Analysis')).toBeInTheDocument();
    expect(screen.getByLabelText('Repository URL *')).toBeInTheDocument();
    expect(screen.getByLabelText('Branch')).toBeInTheDocument();
    expect(screen.getByLabelText('GitHub Token (Optional)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /analyze/i })).toBeInTheDocument();
  });

  it('validates repository URL format', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    // Test invalid URL
    fireEvent.change(urlInput, { target: { value: 'invalid-url' } });
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Please enter a valid GitHub repository URL/)).toBeInTheDocument();
    });
  });

  it('requires repository URL', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    fireEvent.click(analyzeButton);
    
    // The button should be disabled when URL is empty, so no error message is shown
    expect(analyzeButton).toBeDisabled();
  });

  it('starts analysis with valid URL', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // The component shows some progress message
    await waitFor(() => {
      expect(screen.getByText(/Starting repository analysis|Cloning repository|Analyzing file structure/)).toBeInTheDocument();
    });
  });

  it('shows analysis progress', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // Check that progress is shown
    await waitFor(() => {
      expect(screen.getByText(/Starting repository analysis|Cloning repository|Analyzing file structure/)).toBeInTheDocument();
    });
  });

  it('completes analysis and shows results', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // Wait for analysis to complete (it takes 5 seconds in the component)
    await waitFor(() => {
      expect(screen.getByText('Analysis Complete')).toBeInTheDocument();
    }, { timeout: 10000 });
    
    expect(screen.getByText('Repository: https://github.com/owner/repo')).toBeInTheDocument();
  });

  it('calls onAnalysisComplete with results', async () => {
    const onAnalysisComplete = jest.fn();
    render(<GitHubConnector {...defaultProps} onAnalysisComplete={onAnalysisComplete} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // Wait for analysis to complete
    await waitFor(() => {
      expect(onAnalysisComplete).toHaveBeenCalledWith(
        expect.objectContaining({
          repository_url: 'https://github.com/owner/repo',
          services: expect.any(Array),
          dependencies: expect.any(Array),
          technology_stack: expect.any(Object),
          quality_score: expect.any(Number),
        })
      );
    }, { timeout: 10000 });
  });

  it('shows analysis results with correct metrics', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // Wait for analysis to complete
    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument(); // Services count
      expect(screen.getByText('2')).toBeInTheDocument(); // Dependencies count
      expect(screen.getByText('85%')).toBeInTheDocument(); // Quality score
    }, { timeout: 10000 });
  });

  it('shows technologies detected', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // Wait for analysis to complete
    await waitFor(() => {
      expect(screen.getByText('Node.js')).toBeInTheDocument();
      expect(screen.getByText('Java')).toBeInTheDocument();
      expect(screen.getAllByText('PostgreSQL')).toHaveLength(2); // Appears in both technologies and services
    }, { timeout: 15000 });
  }, 20000);

  it('shows services found', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // Wait for analysis to complete
    await waitFor(() => {
      expect(screen.getByText('User Service')).toBeInTheDocument();
      expect(screen.getByText('User Database')).toBeInTheDocument();
      expect(screen.getByText('Payment Service')).toBeInTheDocument();
    }, { timeout: 10000 });
  });

  it('allows resetting analysis', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // Wait for analysis to complete
    await waitFor(() => {
      expect(screen.getByText('Analysis Complete')).toBeInTheDocument();
    }, { timeout: 10000 });
    
    const resetButton = screen.getByText('Analyze Different Repository');
    fireEvent.click(resetButton);
    
    await waitFor(() => {
      expect(screen.getByLabelText('Repository URL *')).toHaveValue('');
    });
  });

  it('handles branch input', () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const branchInput = screen.getByLabelText('Branch');
    fireEvent.change(branchInput, { target: { value: 'develop' } });
    
    expect(branchInput).toHaveValue('develop');
  });

  it('handles GitHub token input', () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const tokenInput = screen.getByLabelText('GitHub Token (Optional)');
    fireEvent.change(tokenInput, { target: { value: 'ghp_token123' } });
    
    expect(tokenInput).toHaveValue('ghp_token123');
  });

  it('disables form during analysis', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(urlInput).toBeDisabled();
      expect(analyzeButton).toBeDisabled();
    });
  });

  it('applies custom className', () => {
    const { container } = render(<GitHubConnector {...defaultProps} className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('shows progress percentage', async () => {
    render(<GitHubConnector {...defaultProps} />);
    
    const urlInput = screen.getByLabelText('Repository URL *');
    const analyzeButton = screen.getByRole('button', { name: /analyze/i });
    
    fireEvent.change(urlInput, { target: { value: 'https://github.com/owner/repo' } });
    fireEvent.click(analyzeButton);
    
    // Check that progress percentage is shown
    await waitFor(() => {
      expect(screen.getByText(/0%|20%|40%/)).toBeInTheDocument();
    });
  });
});
