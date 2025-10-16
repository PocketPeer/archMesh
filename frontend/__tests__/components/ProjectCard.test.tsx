/**
 * Tests for ProjectCard component.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ProjectCard } from '@/components/ProjectCard';
import { Project } from '@/types';

// Mock data
const mockProject: Project = {
  id: 'test-project-id',
  name: 'Test Project',
  description: 'A test project for unit testing',
  domain: 'cloud-native',
  status: 'pending',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

describe('ProjectCard', () => {
  it('renders project information correctly', () => {
    render(<ProjectCard project={mockProject} />);
    
    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('A test project for unit testing')).toBeInTheDocument();
    expect(screen.getByText('Cloud Native')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  it('displays correct status badge color', () => {
    render(<ProjectCard project={mockProject} />);
    
    const statusBadge = screen.getByText('Pending');
    expect(statusBadge).toHaveClass('bg-yellow-100', 'text-yellow-800');
  });

  it('displays correct domain badge', () => {
    render(<ProjectCard project={mockProject} />);
    
    const domainBadge = screen.getByText('Cloud Native');
    expect(domainBadge).toHaveClass('bg-blue-100', 'text-blue-800');
  });

  it('calls onEdit when edit button is clicked', () => {
    const mockOnEdit = jest.fn();
    render(<ProjectCard project={mockProject} onEdit={mockOnEdit} />);
    
    const editButton = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editButton);
    
    expect(mockOnEdit).toHaveBeenCalledWith(mockProject);
  });

  it('calls onDelete when delete button is clicked', () => {
    const mockOnDelete = jest.fn();
    render(<ProjectCard project={mockProject} onDelete={mockOnDelete} />);
    
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);
    
    expect(mockOnDelete).toHaveBeenCalledWith(mockProject);
  });

  it('renders without onEdit and onDelete callbacks', () => {
    render(<ProjectCard project={mockProject} />);
    
    expect(screen.getByText('Test Project')).toBeInTheDocument();
    // Should not crash when callbacks are not provided
  });

  it('displays different status badge colors for different statuses', () => {
    const statuses = [
      { status: 'pending', expectedClass: 'bg-yellow-100' },
      { status: 'processing', expectedClass: 'bg-blue-100' },
      { status: 'completed', expectedClass: 'bg-green-100' },
      { status: 'failed', expectedClass: 'bg-red-100' },
    ];

    statuses.forEach(({ status, expectedClass }) => {
      const projectWithStatus = { ...mockProject, status: status as Project['status'] };
      const { unmount } = render(<ProjectCard project={projectWithStatus} />);
      
      const statusBadge = screen.getByText(status.charAt(0).toUpperCase() + status.slice(1));
      expect(statusBadge).toHaveClass(expectedClass);
      
      unmount();
    });
  });

  it('displays different domain badge colors for different domains', () => {
    const domains = [
      { domain: 'cloud-native', expectedClass: 'bg-blue-100' },
      { domain: 'data-platform', expectedClass: 'bg-green-100' },
      { domain: 'enterprise', expectedClass: 'bg-purple-100' },
    ];

    domains.forEach(({ domain, expectedClass }) => {
      const projectWithDomain = { ...mockProject, domain: domain as Project['domain'] };
      const { unmount } = render(<ProjectCard project={projectWithDomain} />);
      
      const domainBadge = screen.getByText(domain.split('-').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' '));
      expect(domainBadge).toHaveClass(expectedClass);
      
      unmount();
    });
  });
});
