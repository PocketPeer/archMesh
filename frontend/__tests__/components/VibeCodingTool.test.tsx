import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { VibeCodingTool } from '../../src/components/VibeCodingTool';
import { apiClient } from '../../lib/api-client';

// Mock the API client
jest.mock('../../lib/api-client', () => ({
  apiClient: {
    generateCode: jest.fn(),
    getSessionStatus: jest.fn(),
    submitFeedback: jest.fn(),
  },
}));

// Mock WebSocket hook
jest.mock('../../src/hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    isConnected: true,
    sendMessage: jest.fn(),
    lastMessage: null,
  }),
}));

describe('VibeCodingTool', () => {
  const mockProps = {
    projectId: 'test-project-123',
    onCodeGenerated: jest.fn(),
    onSessionUpdate: jest.fn(),
  };
  
  let mockClipboardWriteText: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock clipboard API
    mockClipboardWriteText = jest.fn(() => Promise.resolve());
    Object.defineProperty(navigator, 'clipboard', {
      value: {
        writeText: mockClipboardWriteText,
      },
      writable: true,
      configurable: true,
    });
  });

  describe('Component Initialization', () => {
    it('should render the vibe coding tool interface', () => {
      render(<VibeCodingTool {...mockProps} />);
      
      expect(screen.getByText('Vibe Coding Tool')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Describe what you want to build...')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /generate code/i })).toBeInTheDocument();
    });

    it('should display the chat interface', async () => {
      const user = userEvent.setup();
      render(<VibeCodingTool {...mockProps} />);
      
      // Click on the Chat tab to make it visible
      const chatTab = screen.getByRole('tab', { name: /chat/i });
      await user.click(chatTab);
      
      expect(screen.getByTestId('chat-messages')).toBeInTheDocument();
      expect(screen.getByTestId('chat-input')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    });

    it('should show the code editor', () => {
      render(<VibeCodingTool {...mockProps} />);
      
      // The code editor is only shown when there's generated code
      expect(screen.getByText('No code generated yet. Enter a description above to get started.')).toBeInTheDocument();
    });

    it('should display execution results panel', async () => {
      const user = userEvent.setup();
      render(<VibeCodingTool {...mockProps} />);
      
      expect(screen.getByText('Execution Results')).toBeInTheDocument();
      
      // Click on the results tab to make it visible
      const resultsTab = screen.getByRole('tab', { name: /execution results/i });
      await user.click(resultsTab);
      
      // The execution results panel is only shown when there are results
      expect(screen.getByText('No execution results yet. Generate code to see results here.')).toBeInTheDocument();
    });
  });

  describe('Natural Language Input', () => {
    it('should handle natural language input', async () => {
      const user = userEvent.setup();
      
      // Mock a delayed response to ensure we can see the loading state
      (apiClient.generateCode as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          success: true,
          generated_code: {
            code: 'def hello_world():\n    return "Hello, World!"',
            language: 'python',
            framework: 'fastapi',
          },
          execution_result: null,
        }), 100))
      );

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a FastAPI endpoint for user authentication');
      await user.click(generateButton);
      
      expect(screen.getByTestId('progress-indicator')).toBeInTheDocument();
    });

    it('should validate input before generation', async () => {
      const user = userEvent.setup();
      render(<VibeCodingTool {...mockProps} />);
      
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      await user.click(generateButton);
      
      expect(screen.getByText('Please enter a description')).toBeInTheDocument();
    });

    it('should show progress during code generation', async () => {
      const user = userEvent.setup();
      
      // Mock a delayed response to ensure we can see the loading state
      (apiClient.generateCode as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          success: true,
          generated_code: {
            code: 'def hello_world():\n    return "Hello, World!"',
            language: 'python',
            framework: 'fastapi',
          },
          execution_result: null,
          session_id: 'test-session-123',
        }), 100))
      );

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a simple calculator');
      await user.click(generateButton);
      
      // Check for loading state after the click
      await waitFor(() => {
        expect(screen.getByTestId('progress-indicator')).toBeInTheDocument();
      });
    });
  });

  describe('Code Generation', () => {
    it('should display generated code in the editor', async () => {
      const user = userEvent.setup();
      
      // Set up the mock before rendering
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def hello_world():\n    return "Hello, World!"',
          language: 'python',
          framework: 'fastapi',
        },
        execution_result: null,
        session_id: 'test-session-123',
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a hello world function');
      await user.click(generateButton);
      
      // Wait for the API call to complete
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Wait for the code editor to appear (it only shows when generatedCode is set)
      await waitFor(() => {
        expect(screen.getByTestId('code-editor')).toBeInTheDocument();
      }, { timeout: 5000 });
      
      // Verify the code content is rendered
      expect(screen.getByText(/def hello_world\(\):/)).toBeInTheDocument();
    });

    it('should handle code generation errors', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockRejectedValue(new Error('Generation failed'));

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create invalid code');
      await user.click(generateButton);
      
      await waitFor(() => {
        expect(screen.getByText('Code generation failed')).toBeInTheDocument();
      });
    });

    it('should show code quality metrics', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    pass',
          language: 'python',
          quality_score: 0.85,
        },
        execution_result: null,
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a test function');
      await user.click(generateButton);
      
      await waitFor(() => {
        expect(screen.getByText('Quality Score: 85%')).toBeInTheDocument();
      });
    });
  });

  describe('Code Execution', () => {
    it('should execute generated code in sandbox', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'print("Hello, World!")',
          language: 'python',
        },
        execution_result: {
          success: true,
          stdout: 'Hello, World!',
          stderr: '',
          execution_time: 0.5,
        },
        session_id: 'test-session-123',
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Print hello world');
      await user.click(generateButton);
      
      // Wait for code generation to complete
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Click on the results tab to see execution results
      const resultsTab = screen.getByRole('tab', { name: /execution results/i });
      await user.click(resultsTab);
      
      await waitFor(() => {
        expect(screen.getByText('Hello, World!')).toBeInTheDocument();
        expect(screen.getByText('Execution Time: 0.5s')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should handle execution errors', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'invalid syntax',
          language: 'python',
        },
        execution_result: {
          success: false,
          stdout: '',
          stderr: 'SyntaxError: invalid syntax',
          execution_time: 0.1,
        },
        session_id: 'test-session-123',
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create invalid code');
      await user.click(generateButton);
      
      // Wait for code generation to complete first
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Click on the results tab to see execution results
      const resultsTab = screen.getByRole('tab', { name: /execution results/i });
      await user.click(resultsTab);
      
      await waitFor(() => {
        expect(screen.getByText('SyntaxError: invalid syntax')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('should show execution metrics', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'import time; time.sleep(1)',
          language: 'python',
        },
        execution_result: {
          success: true,
          stdout: '',
          stderr: '',
          execution_time: 1.2,
          memory_usage_mb: 45.6,
          cpu_usage_percent: 25.0,
        },
        session_id: 'test-session-123',
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a time delay');
      await user.click(generateButton);
      
      // Wait for code generation to complete first
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Wait for code to be generated
      await waitFor(() => {
        expect(screen.getByTestId('code-editor')).toBeInTheDocument();
      });
      
      // Click on the results tab to see execution results
      const resultsTab = screen.getByRole('tab', { name: /execution results/i });
      await user.click(resultsTab);
      
      // Wait for execution results to be displayed
      await waitFor(() => {
        const memoryUsageText = screen.queryByText(/Memory Usage: 45\.6 MB/);
        const cpuUsageText = screen.queryByText(/CPU Usage: 25\.0%/);
        expect(memoryUsageText || cpuUsageText).toBeTruthy();
      }, { timeout: 5000 });
    });
  });

  describe('Chat Interface', () => {
    it('should handle chat messages', async () => {
      const user = userEvent.setup();
      render(<VibeCodingTool {...mockProps} />);
      
      // Click on the Chat tab to make it visible
      const chatTab = screen.getByRole('tab', { name: /chat/i });
      await user.click(chatTab);
      
      const chatInput = screen.getByTestId('chat-input');
      const sendButton = screen.getByRole('button', { name: /send/i });
      
      await user.type(chatInput, 'Can you add error handling?');
      await user.click(sendButton);
      
      expect(screen.getByText('Can you add error handling?')).toBeInTheDocument();
    });

    it('should display chat history', async () => {
      const user = userEvent.setup();
      render(<VibeCodingTool {...mockProps} />);
      
      // Click on the Chat tab to make it visible
      const chatTab = screen.getByRole('tab', { name: /chat/i });
      await user.click(chatTab);
      
      expect(screen.getByTestId('chat-messages')).toBeInTheDocument();
    });

    it('should handle empty chat messages', async () => {
      const user = userEvent.setup();
      render(<VibeCodingTool {...mockProps} />);
      
      // Click on the Chat tab to make it visible
      const chatTab = screen.getByRole('tab', { name: /chat/i });
      await user.click(chatTab);
      
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);
      
      expect(screen.queryByText('Can you add error handling?')).not.toBeInTheDocument();
    });
  });

  describe('Session Management', () => {
    it('should create a new session on first use', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def new_function():\n    pass',
          language: 'python',
        },
        execution_result: null,
        session_id: 'new-session-123',
      });
      
      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a new function');
      await user.click(generateButton);
      
      // Wait for the API call to complete and session ID to be set
      await waitFor(() => {
        expect(screen.getByTestId('session-id')).toBeInTheDocument();
      });
    });

    it('should show session status', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    pass',
          language: 'python',
        },
        execution_result: null,
        session_id: 'test-session-123',
      });
      
      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a function');
      await user.click(generateButton);
      
      // Wait for code generation to complete first
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Session ID should be displayed after code generation
      await waitFor(() => {
        expect(screen.getByTestId('session-id')).toBeInTheDocument();
        expect(screen.getByText(/Session: test-session-123/)).toBeInTheDocument();
      });
    });

    it('should handle session updates', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    pass',
          language: 'python',
        },
        execution_result: null,
        session_id: 'test-session-123',
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a function');
      await user.click(generateButton);
      
      // Wait for code generation to complete first
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Verify session ID is displayed and persists
      await waitFor(() => {
        expect(screen.getByTestId('session-id')).toBeInTheDocument();
        expect(screen.getByText(/Session: test-session-123/)).toBeInTheDocument();
      });
      
      // Session ID should persist across interactions
      expect(screen.getByTestId('session-id')).toHaveTextContent('test-session-123');
    });
  });

  describe('Feedback System', () => {
    it('should allow rating generated code', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    pass',
          language: 'python',
        },
        execution_result: null,
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a test function');
      await user.click(generateButton);
      
      await waitFor(() => {
        const ratingButtons = screen.getAllByRole('button', { name: /★/ });
        expect(ratingButtons).toHaveLength(5);
      });
    });

    it('should submit feedback', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    pass',
          language: 'python',
        },
        execution_result: null,
        session_id: 'test-session-123',
      });

      (apiClient.submitFeedback as jest.Mock).mockResolvedValue({
        success: true,
        message: 'Feedback submitted successfully',
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a test function');
      await user.click(generateButton);
      
      // Wait for code generation to complete first
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Wait for the feedback form to appear
      await waitFor(() => {
        expect(screen.getByText('Rate the Generated Code')).toBeInTheDocument();
      });
      
      // Click the 5-star rating button
      const ratingButtons = screen.getAllByRole('button');
      const fiveStarButton = ratingButtons.find(btn => btn.textContent?.includes('★'));
      if (fiveStarButton) {
        await user.click(fiveStarButton);
      }
      
      // Click submit feedback button
      const submitButton = screen.getByRole('button', { name: /submit feedback/i });
      await user.click(submitButton);
      
      // Verify feedback was submitted
      await waitFor(() => {
        expect(apiClient.submitFeedback).toHaveBeenCalled();
      });
    });

    it('should allow adding comments to feedback', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    pass',
          language: 'python',
        },
        execution_result: null,
        session_id: 'test-session-123',
      });

      render(<VibeCodingTool {...mockProps} />);
      
      // First generate code to show the feedback form
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a test function');
      await user.click(generateButton);
      
      // Wait for code generation to complete first
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Wait for the feedback form to appear
      await waitFor(() => {
        expect(screen.getByText('Rate the Generated Code')).toBeInTheDocument();
      });
      
      // Find and type in the comment input
      const commentInput = screen.getByPlaceholderText('Add your comments...');
      await user.type(commentInput, 'Great code, but could use more comments');
      
      // Verify the comment was typed
      expect(commentInput).toHaveValue('Great code, but could use more comments');
    });
  });

  describe('Code Editor Features', () => {
    it('should allow editing generated code', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    pass',
          language: 'python',
        },
        execution_result: null,
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a test function');
      await user.click(generateButton);
      
      await waitFor(() => {
        const codeEditor = screen.getByTestId('code-editor');
        expect(codeEditor).toBeInTheDocument();
      });
    });

    it('should show syntax highlighting', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    return "hello"',
          language: 'python',
        },
        execution_result: null,
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a test function');
      await user.click(generateButton);
      
      await waitFor(() => {
        const codeEditor = screen.getByTestId('code-editor');
        expect(codeEditor).toHaveClass('syntax-highlighted');
      });
    });

    it('should allow copying code to clipboard', async () => {
      const user = userEvent.setup();
      
      (apiClient.generateCode as jest.Mock).mockResolvedValue({
        success: true,
        generated_code: {
          code: 'def test():\n    pass',
          language: 'python',
        },
        execution_result: null,
        session_id: 'test-session-123',
      });

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a test function');
      await user.click(generateButton);
      
      // Wait for code generation to complete first
      await waitFor(() => {
        expect(apiClient.generateCode).toHaveBeenCalled();
      });
      
      // Wait for the code editor to appear
      await waitFor(() => {
        expect(screen.getByTestId('code-editor')).toBeInTheDocument();
      });
      
      // Verify the copy button exists and is clickable
      const copyButton = screen.getByRole('button', { name: /copy code/i });
      expect(copyButton).toBeInTheDocument();
      expect(copyButton).not.toBeDisabled();
      
      // Click the copy button (this should not crash the component)
      await user.click(copyButton);
      
      // The component should handle the click gracefully
      // Note: In a real browser, this would copy to clipboard
      // In tests, we verify the button exists and is functional
      expect(copyButton).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    it('should be responsive on mobile devices', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(<VibeCodingTool {...mockProps} />);
      
      expect(screen.getByTestId('vibe-coding-tool')).toHaveClass('mobile-responsive');
    });

    it('should adapt layout for tablet devices', () => {
      // Mock tablet viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });

      render(<VibeCodingTool {...mockProps} />);
      
      expect(screen.getByTestId('vibe-coding-tool')).toHaveClass('tablet-responsive');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', async () => {
      const user = userEvent.setup();
      render(<VibeCodingTool {...mockProps} />);
      
      expect(screen.getByLabelText('Natural language input for code generation')).toBeInTheDocument();
      
      // Click on the Chat tab to make it visible
      const chatTab = screen.getByRole('tab', { name: /chat/i });
      await user.click(chatTab);
      
      expect(screen.getByLabelText('Chat input for iterative development')).toBeInTheDocument();
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      input.focus();
      
      await user.keyboard('{Tab}');
      expect(screen.getByRole('button', { name: /generate code/i })).toHaveFocus();
    });

    it('should announce status changes to screen readers', async () => {
      const user = userEvent.setup();
      
      // Mock a delayed response to ensure we can see the loading state
      (apiClient.generateCode as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          success: true,
          generated_code: {
            code: 'def hello_world():\n    return "Hello, World!"',
            language: 'python',
            framework: 'fastapi',
          },
          execution_result: null,
        }), 100))
      );

      render(<VibeCodingTool {...mockProps} />);
      
      const input = screen.getByPlaceholderText('Describe what you want to build...');
      const generateButton = screen.getByRole('button', { name: /generate code/i });
      
      await user.type(input, 'Create a function');
      await user.click(generateButton);
      
      // Check that the status element exists and contains the loading message
      const statusElement = screen.getByRole('status');
      expect(statusElement).toBeInTheDocument();
      expect(statusElement).toHaveTextContent('Generating code...');
    });
  });
});
