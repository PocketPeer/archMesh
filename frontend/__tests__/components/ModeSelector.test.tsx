import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ModeSelector from '@/src/components/ModeSelector';

describe('ModeSelector', () => {
  const defaultProps = {
    value: 'greenfield' as const,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default options', () => {
    render(<ModeSelector {...defaultProps} />);
    
    expect(screen.getByText('Project Type')).toBeInTheDocument();
    expect(screen.getByText('New Project (Greenfield)')).toBeInTheDocument();
    expect(screen.getByText('Existing System (Brownfield)')).toBeInTheDocument();
  });

  it('shows correct selected mode', () => {
    render(<ModeSelector {...defaultProps} value="brownfield" />);
    
    const brownfieldContainer = screen.getByText('Existing System (Brownfield)').closest('div[class*="border-2"]');
    expect(brownfieldContainer).toHaveClass('border-blue-500');
  });

  it('calls onChange when mode is selected', async () => {
    const onChange = jest.fn();
    render(<ModeSelector {...defaultProps} onChange={onChange} />);
    
    const brownfieldOption = screen.getByText('Existing System (Brownfield)').closest('div');
    fireEvent.click(brownfieldOption!);
    
    await waitFor(() => {
      expect(onChange).toHaveBeenCalledWith('brownfield');
    });
  });

  it('shows mode-specific features', () => {
    render(<ModeSelector {...defaultProps} value="greenfield" />);
    
    expect(screen.getByText('Clean slate design')).toBeInTheDocument();
    expect(screen.getByText('Latest technologies')).toBeInTheDocument();
    expect(screen.getByText('No legacy constraints')).toBeInTheDocument();
  });

  it('shows brownfield-specific features when brownfield is selected', () => {
    render(<ModeSelector {...defaultProps} value="brownfield" />);
    
    expect(screen.getByText('GitHub integration')).toBeInTheDocument();
    expect(screen.getByText('Existing architecture analysis')).toBeInTheDocument();
    expect(screen.getByText('Integration planning')).toBeInTheDocument();
  });

  it('disables interaction when disabled prop is true', () => {
    render(<ModeSelector {...defaultProps} disabled={true} />);
    
    const greenfieldContainer = screen.getByText('New Project (Greenfield)').closest('div[class*="border-2"]');
    expect(greenfieldContainer).toHaveClass('opacity-50', 'cursor-not-allowed');
  });

  it('does not call onChange when disabled', async () => {
    const onChange = jest.fn();
    render(<ModeSelector {...defaultProps} onChange={onChange} disabled={true} />);
    
    const brownfieldOption = screen.getByText('Existing System (Brownfield)').closest('div');
    fireEvent.click(brownfieldOption!);
    
    await waitFor(() => {
      expect(onChange).not.toHaveBeenCalled();
    });
  });

  it('applies custom className', () => {
    const { container } = render(<ModeSelector {...defaultProps} className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('shows help text', () => {
    render(<ModeSelector {...defaultProps} />);
    
    expect(screen.getByText('Need help choosing?')).toBeInTheDocument();
    expect(screen.getByText(/Perfect for new applications/)).toBeInTheDocument();
    expect(screen.getByText(/Ideal when you need to add features/)).toBeInTheDocument();
  });

  it('renders with custom options', () => {
    const customOptions = [
      {
        value: 'greenfield' as const,
        label: 'Custom Greenfield',
        description: 'Custom greenfield description',
        icon: '🚀'
      },
      {
        value: 'brownfield' as const,
        label: 'Custom Brownfield',
        description: 'Custom brownfield description',
        icon: '🔧'
      }
    ];

    render(<ModeSelector {...defaultProps} options={customOptions} />);
    
    expect(screen.getByText('Custom Greenfield')).toBeInTheDocument();
    expect(screen.getByText('Custom Brownfield')).toBeInTheDocument();
    expect(screen.getByText('Custom greenfield description')).toBeInTheDocument();
    expect(screen.getByText('Custom brownfield description')).toBeInTheDocument();
  });

  it('handles keyboard navigation', async () => {
    const onChange = jest.fn();
    render(<ModeSelector {...defaultProps} onChange={onChange} />);
    
    const brownfieldOption = screen.getByText('Existing System (Brownfield)').closest('div')?.parentElement;
    fireEvent.click(brownfieldOption!);
    
    await waitFor(() => {
      expect(onChange).toHaveBeenCalledWith('brownfield');
    });
  });

  it('shows selection indicator for selected option', () => {
    render(<ModeSelector {...defaultProps} value="brownfield" />);
    
    const brownfieldContainer = screen.getByText('Existing System (Brownfield)').closest('div[class*="border-2"]');
    const checkIcon = brownfieldContainer!.querySelector('svg');
    expect(checkIcon).toBeInTheDocument();
  });
});
