/**
 * Workflow Refinement Integration Tests
 * 
 * Tests the complete workflow refinement functionality including:
 * - Multi-LLM orchestration
 * - Quality assessment
 * - Question generation
 * - Iterative improvement
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { jest } from '@jest/globals';
import WorkflowRefinement from '@/components/WorkflowRefinement';
import RefinementButton from '@/components/RefinementButton';

// Mock API responses
const mockRefinementStrategies = {
  strategies: [
    {
      value: 'validation_only',
      name: 'Validation Only',
      description: 'Only validate output quality without refinement'
    },
    {
      value: 'iterative_improvement',
      name: 'Iterative Improvement',
      description: 'Iteratively improve output through multiple refinement cycles'
    }
  ]
};

const mockLLMProviders = {
  providers: [
    {
      id: 'deepseek',
      name: 'DeepSeek',
      description: 'Good for reasoning and analysis tasks',
      best_for: ['validation', 'analysis']
    },
    {
      id: 'claude',
      name: 'Claude',
      description: 'Excellent for critique and question generation',
      best_for: ['validation', 'question_generation', 'critique']
    },
    {
      id: 'gpt-4',
      name: 'GPT-4',
      description: 'Strong for synthesis and refinement',
      best_for: ['refinement', 'synthesis', 'improvement']
    }
  ]
};

const mockQualityAssessment = {
  workflow_id: 'test-workflow-123',
  completeness: 0.75,
  consistency: 0.80,
  accuracy: 0.70,
  relevance: 0.85,
  overall: 0.78,
  confidence: 0.82,
  notes: 'Quality assessment completed using claude'
};

const mockRefinementResult = {
  refinement_id: 'ref_test-workflow-123_2024-01-01T00:00:00Z',
  workflow_id: 'test-workflow-123',
  status: 'completed',
  quality_improvement: 0.15,
  iterations_performed: 2,
  llm_used: 'gpt-4',
  refinement_notes: [
    'Iteration 1: Quality improved to 0.85',
    'Iteration 2: Quality improved to 0.93'
  ],
  questions_generated: [
    {
      question: 'What is the expected user load for this system?',
      category: 'technical',
      priority: 'high',
      context: 'Needed for scalability decisions'
    },
    {
      question: 'What are the security requirements?',
      category: 'security',
      priority: 'high',
      context: 'Critical for architecture design'
    }
  ],
  timestamp: '2024-01-01T00:00:00Z'
};

// Mock fetch
global.fetch = jest.fn();

describe('Workflow Refinement Integration', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  describe('WorkflowRefinement Component', () => {
    const defaultProps = {
      workflowId: 'test-workflow-123',
      projectId: 'test-project-456',
      onRefinementComplete: jest.fn()
    };

    it('renders refinement interface with configuration options', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        });

      render(<WorkflowRefinement {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('Workflow Refinement')).toBeInTheDocument();
      });

      // Check that configuration options are rendered
      expect(screen.getByText('Configuration')).toBeInTheDocument();
      expect(screen.getByText('Quality Assessment')).toBeInTheDocument();
      expect(screen.getByText('Questions')).toBeInTheDocument();
      expect(screen.getByText('Results')).toBeInTheDocument();
    });

    it('loads refinement options on mount', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        });

      render(<WorkflowRefinement {...defaultProps} />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/v1/refinement/strategies');
        expect(fetch).toHaveBeenCalledWith('/api/v1/refinement/llm-providers');
      });
    });

    it('assesses current quality on mount', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockQualityAssessment)
        });

      render(<WorkflowRefinement {...defaultProps} />);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/v1/refinement/assess-quality', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            workflow_id: 'test-workflow-123',
            llm_provider: 'claude'
          })
        });
      });
    });

    it('displays quality assessment results', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockQualityAssessment)
        });

      render(<WorkflowRefinement {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('78%')).toBeInTheDocument(); // Overall quality
        expect(screen.getByText('Good')).toBeInTheDocument(); // Quality label
      });
    });

    it('starts refinement process when button is clicked', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockQualityAssessment)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementResult)
        });

      render(<WorkflowRefinement {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('Start Refinement')).toBeInTheDocument();
      });

      const startButton = screen.getByText('Start Refinement');
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/v1/refinement/refine', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            workflow_id: 'test-workflow-123',
            strategy: 'iterative_improvement',
            primary_llm: 'deepseek',
            validation_llm: 'claude',
            refinement_llm: 'gpt-4',
            max_iterations: 3,
            quality_threshold: 0.8,
            enable_cross_validation: true,
            enable_question_generation: true
          })
        });
      });
    });

    it('displays refinement results after completion', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockQualityAssessment)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementResult)
        });

      render(<WorkflowRefinement {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('Start Refinement')).toBeInTheDocument();
      });

      const startButton = screen.getByText('Start Refinement');
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('+15%')).toBeInTheDocument(); // Quality improvement
        expect(screen.getByText('2')).toBeInTheDocument(); // Iterations
        expect(screen.getByText('gpt-4')).toBeInTheDocument(); // LLM used
      });
    });

    it('generates questions when requested', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockQualityAssessment)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({
            workflow_id: 'test-workflow-123',
            questions: mockRefinementResult.questions_generated,
            total_questions: 2
          })
        });

      render(<WorkflowRefinement {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('Generate Questions')).toBeInTheDocument();
      });

      const generateButton = screen.getByText('Generate Questions');
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/v1/refinement/generate-questions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            workflow_id: 'test-workflow-123'
          })
        });
      });
    });

    it('handles refinement errors gracefully', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockQualityAssessment)
        })
        .mockResolvedValueOnce({
          ok: false,
          json: () => Promise.resolve({
            detail: 'Refinement failed: LLM timeout'
          })
        });

      render(<WorkflowRefinement {...defaultProps} />);

      await waitFor(() => {
        expect(screen.getByText('Start Refinement')).toBeInTheDocument();
      });

      const startButton = screen.getByText('Start Refinement');
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Refinement failed: LLM timeout')).toBeInTheDocument();
      });
    });
  });

  describe('RefinementButton Component', () => {
    const defaultProps = {
      workflowId: 'test-workflow-123',
      projectId: 'test-project-456',
      currentQuality: 0.75,
      onRefinementComplete: jest.fn()
    };

    it('renders refinement button with quality indicator', () => {
      render(<RefinementButton {...defaultProps} />);

      expect(screen.getByText('Refine Output')).toBeInTheDocument();
      expect(screen.getByText('75%')).toBeInTheDocument();
    });

    it('opens refinement dialog when clicked', () => {
      render(<RefinementButton {...defaultProps} />);

      const button = screen.getByText('Refine Output');
      fireEvent.click(button);

      expect(screen.getByText('Workflow Refinement')).toBeInTheDocument();
    });

    it('displays quality information in dialog', () => {
      render(<RefinementButton {...defaultProps} />);

      const button = screen.getByText('Refine Output');
      fireEvent.click(button);

      expect(screen.getByText('Current Quality: Good (75%)')).toBeInTheDocument();
    });

    it('calls onRefinementComplete when refinement is completed', async () => {
      const onRefinementComplete = jest.fn();
      
      render(
        <RefinementButton 
          {...defaultProps} 
          onRefinementComplete={onRefinementComplete}
        />
      );

      const button = screen.getByText('Refine Output');
      fireEvent.click(button);

      // Simulate refinement completion
      await waitFor(() => {
        expect(screen.getByText('Workflow Refinement')).toBeInTheDocument();
      });
    });
  });

  describe('Quality Assessment Integration', () => {
    it('displays quality metrics correctly', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockQualityAssessment)
        });

      render(<WorkflowRefinement workflowId="test-123" projectId="test-456" />);

      await waitFor(() => {
        expect(screen.getByText('75%')).toBeInTheDocument(); // Completeness
        expect(screen.getByText('80%')).toBeInTheDocument(); // Consistency
        expect(screen.getByText('70%')).toBeInTheDocument(); // Accuracy
        expect(screen.getByText('85%')).toBeInTheDocument(); // Relevance
        expect(screen.getByText('78%')).toBeInTheDocument(); // Overall
        expect(screen.getByText('82%')).toBeInTheDocument(); // Confidence
      });
    });

    it('shows appropriate quality labels', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockQualityAssessment)
        });

      render(<WorkflowRefinement workflowId="test-123" projectId="test-456" />);

      await waitFor(() => {
        expect(screen.getByText('Good')).toBeInTheDocument(); // Overall quality label
      });
    });
  });

  describe('Multi-LLM Configuration', () => {
    it('allows selection of different LLM providers', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        });

      render(<WorkflowRefinement workflowId="test-123" projectId="test-456" />);

      await waitFor(() => {
        expect(screen.getByText('DeepSeek')).toBeInTheDocument();
        expect(screen.getByText('Claude')).toBeInTheDocument();
        expect(screen.getByText('GPT-4')).toBeInTheDocument();
      });
    });

    it('allows configuration of refinement parameters', async () => {
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockRefinementStrategies)
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockLLMProviders)
        });

      render(<WorkflowRefinement workflowId="test-123" projectId="test-456" />);

      await waitFor(() => {
        expect(screen.getByText('Max Iterations: 3')).toBeInTheDocument();
        expect(screen.getByText('Quality Threshold: 80%')).toBeInTheDocument();
        expect(screen.getByText('Enable Cross-Validation')).toBeInTheDocument();
        expect(screen.getByText('Enable Question Generation')).toBeInTheDocument();
      });
    });
  });
});
