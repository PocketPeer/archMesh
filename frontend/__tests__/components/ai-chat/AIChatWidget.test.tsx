import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AIChatWidget } from '@/src/components/ai-chat/AIChatWidget';
import { AIChatProvider } from '@/src/contexts/AIChatContext';
import { apiClient } from '@/lib/api-client';

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    getAIChatModels: jest.fn(),
    createAIChatSession: jest.fn(),
    getAIChatSessions: jest.fn(),
    getAIChatSession: jest.fn(),
    sendAIChatMessage: jest.fn(),
    switchAIChatModel: jest.fn(),
    deleteAIChatSession: jest.fn(),
  },
}));

// Mock WebSocket
const mockWebSocket = {
  close: jest.fn(),
  send: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  readyState: 1, // OPEN
};

global.WebSocket = jest.fn(() => mockWebSocket) as any;

// Mock sonner toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AIChatProvider>
    {children}
  </AIChatProvider>
);

describe('AIChatWidget', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock implementations
    (apiClient.getAIChatModels as jest.Mock).mockResolvedValue({
      models: [
        {
          name: 'DeepSeek R1',
          provider: 'deepseek',
          description: 'Advanced reasoning model',
          capabilities: ['reasoning', 'analysis'],
          cost_per_token: 0.001,
          max_tokens: 8192,
        },
        {
          name: 'Claude Opus',
          provider: 'anthropic',
          description: 'Most capable model',
          capabilities: ['analysis', 'writing'],
          cost_per_token: 0.015,
          max_tokens: 200000,
        },
      ],
      current_model: 'deepseek-r1',
      default_model: 'deepseek-r1',
    });

    (apiClient.getAIChatSessions as jest.Mock).mockResolvedValue([]);
  });

  it('should render the chat widget', () => {
    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
    expect(screen.getByText('DeepSeek R1')).toBeInTheDocument();
  });

  it('should expand and collapse the chat interface', async () => {
    const user = userEvent.setup();

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Initially collapsed
    expect(screen.queryByPlaceholderText('Ask AI anything...')).not.toBeInTheDocument();

    // Expand
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    expect(screen.getByPlaceholderText('Ask AI anything...')).toBeInTheDocument();
    expect(screen.getByText('Start a conversation with AI')).toBeInTheDocument();

    // Collapse
    const collapseButton = screen.getByText('−');
    await user.click(collapseButton);

    expect(screen.queryByPlaceholderText('Ask AI anything...')).not.toBeInTheDocument();
  });

  it('should minimize and restore the widget', async () => {
    const user = userEvent.setup();

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Minimize
    const minimizeButton = screen.getByText('×');
    await user.click(minimizeButton);

    // Should show only the floating button
    expect(screen.getByRole('button', { name: /message circle/i })).toBeInTheDocument();
    expect(screen.queryByText('AI Assistant')).not.toBeInTheDocument();

    // Restore
    const restoreButton = screen.getByRole('button', { name: /message circle/i });
    await user.click(restoreButton);

    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
  });

  it('should send a message when Enter is pressed', async () => {
    const user = userEvent.setup();

    const mockSession = {
      id: 'session-123',
      user_id: 'user-123',
      title: 'New Chat Session',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [],
      current_model: 'deepseek-r1',
      context: {},
    };

    const mockResponse = {
      success: true,
      message: {
        id: 'msg-123',
        content: 'Hello! How can I help you?',
        role: 'assistant',
        timestamp: '2024-01-01T00:00:00Z',
        model_used: 'deepseek-r1',
        metadata: {},
      },
      session_id: 'session-123',
      model_used: 'deepseek-r1',
    };

    (apiClient.createAIChatSession as jest.Mock).mockResolvedValue(mockSession);
    (apiClient.sendAIChatMessage as jest.Mock).mockResolvedValue(mockResponse);

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Expand the chat
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    // Type a message
    const input = screen.getByPlaceholderText('Ask AI anything...');
    await user.type(input, 'Hello AI');

    // Press Enter
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(apiClient.createAIChatSession).toHaveBeenCalledWith('Quick Chat');
      expect(apiClient.sendAIChatMessage).toHaveBeenCalledWith(
        'session-123',
        'Hello AI',
        'deepseek-r1',
        {}
      );
    });
  });

  it('should send a message when send button is clicked', async () => {
    const user = userEvent.setup();

    const mockSession = {
      id: 'session-123',
      user_id: 'user-123',
      title: 'New Chat Session',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [],
      current_model: 'deepseek-r1',
      context: {},
    };

    const mockResponse = {
      success: true,
      message: {
        id: 'msg-123',
        content: 'Hello! How can I help you?',
        role: 'assistant',
        timestamp: '2024-01-01T00:00:00Z',
        model_used: 'deepseek-r1',
        metadata: {},
      },
      session_id: 'session-123',
      model_used: 'deepseek-r1',
    };

    (apiClient.createAIChatSession as jest.Mock).mockResolvedValue(mockSession);
    (apiClient.sendAIChatMessage as jest.Mock).mockResolvedValue(mockResponse);

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Expand the chat
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    // Type a message
    const input = screen.getByPlaceholderText('Ask AI anything...');
    await user.type(input, 'Hello AI');

    // Click send button
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(apiClient.sendAIChatMessage).toHaveBeenCalledWith(
        'session-123',
        'Hello AI',
        'deepseek-r1',
        {}
      );
    });
  });

  it('should switch models', async () => {
    const user = userEvent.setup();

    const mockSession = {
      id: 'session-123',
      user_id: 'user-123',
      title: 'Test Session',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [],
      current_model: 'deepseek-r1',
      context: {},
    };

    (apiClient.createAIChatSession as jest.Mock).mockResolvedValue(mockSession);
    (apiClient.switchAIChatModel as jest.Mock).mockResolvedValue({
      success: true,
      model: 'claude-opus',
    });

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Expand the chat first
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    // Click on model selector
    const modelButton = screen.getByText('DeepSeek R1');
    await user.click(modelButton);

    // Select Claude Opus using onSelect
    const claudeOption = screen.getByText('Claude Opus');
    await user.click(claudeOption);

    await waitFor(() => {
      expect(apiClient.switchAIChatModel).toHaveBeenCalledWith('session-123', 'claude-opus');
    });
  });

  it('should display messages correctly', async () => {
    const user = userEvent.setup();

    const mockSession = {
      id: 'session-123',
      user_id: 'user-123',
      title: 'Test Session',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [
        {
          id: 'msg-1',
          content: 'Hello AI',
          role: 'user',
          timestamp: '2024-01-01T00:00:00Z',
          model_used: null,
          metadata: {},
        },
        {
          id: 'msg-2',
          content: 'Hello! How can I help you?',
          role: 'assistant',
          timestamp: '2024-01-01T00:00:01Z',
          model_used: 'deepseek-r1',
          metadata: {},
        },
      ],
      current_model: 'deepseek-r1',
      context: {},
    };

    // Mock the session creation to return the session with messages
    (apiClient.createAIChatSession as jest.Mock).mockResolvedValue(mockSession);

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Expand the chat
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    // Wait for session to be created and messages to be displayed
    await waitFor(() => {
      expect(screen.getByText('Hello AI')).toBeInTheDocument();
      expect(screen.getByText('Hello! How can I help you?')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('should show loading state when sending message', async () => {
    const user = userEvent.setup();

    const mockSession = {
      id: 'session-123',
      user_id: 'user-123',
      title: 'New Chat Session',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [],
      current_model: 'deepseek-r1',
      context: {},
    };

    // Mock a delayed response
    (apiClient.createAIChatSession as jest.Mock).mockResolvedValue(mockSession);
    (apiClient.sendAIChatMessage as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        success: true,
        message: {
          id: 'msg-123',
          content: 'Response',
          role: 'assistant',
          timestamp: '2024-01-01T00:00:00Z',
          model_used: 'deepseek-r1',
          metadata: {},
        },
        session_id: 'session-123',
        model_used: 'deepseek-r1',
      }), 100))
    );

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Expand the chat
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    // Type a message
    const input = screen.getByPlaceholderText('Ask AI anything...');
    await user.type(input, 'Hello AI');

    // Click send button
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText('AI is thinking...')).toBeInTheDocument();
    });
    expect(sendButton).toBeDisabled();

    // Wait for response
    await waitFor(() => {
      expect(screen.queryByText('AI is thinking...')).not.toBeInTheDocument();
    }, { timeout: 200 });
  });

  it('should handle errors gracefully', async () => {
    const user = userEvent.setup();

    (apiClient.createAIChatSession as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Expand the chat
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    // Type a message
    const input = screen.getByPlaceholderText('Ask AI anything...');
    await user.type(input, 'Hello AI');

    // Click send button
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('should not send empty messages', async () => {
    const user = userEvent.setup();

    render(
      <TestWrapper>
        <AIChatWidget />
      </TestWrapper>
    );

    // Expand the chat
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    // Try to send empty message
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeDisabled();

    // Try pressing Enter with empty input
    const input = screen.getByPlaceholderText('Ask AI anything...');
    await user.keyboard('{Enter}');

    // With auto-create on expand, a session is created even for empty input
    expect(apiClient.createAIChatSession).toHaveBeenCalled();
    expect(apiClient.sendAIChatMessage).not.toHaveBeenCalled();
  });

  it('should accept custom context', async () => {
    const user = userEvent.setup();

    const customContext = { projectId: 'proj-123', page: 'architecture' };

    const mockSession = {
      id: 'session-123',
      user_id: 'user-123',
      title: 'New Chat Session',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      messages: [],
      current_model: 'deepseek-r1',
      context: {},
    };

    const mockResponse = {
      success: true,
      message: {
        id: 'msg-123',
        content: 'Response',
        role: 'assistant',
        timestamp: '2024-01-01T00:00:00Z',
        model_used: 'deepseek-r1',
        metadata: {},
      },
      session_id: 'session-123',
      model_used: 'deepseek-r1',
    };

    (apiClient.createAIChatSession as jest.Mock).mockResolvedValue(mockSession);
    (apiClient.sendAIChatMessage as jest.Mock).mockResolvedValue(mockResponse);

    render(
      <TestWrapper>
        <AIChatWidget context={customContext} />
      </TestWrapper>
    );

    // Expand the chat
    const expandButton = screen.getByText('+');
    await user.click(expandButton);

    // Wait for session to be created
    await waitFor(() => {
      expect(apiClient.createAIChatSession).toHaveBeenCalled();
    });

    // Type a message
    const input = screen.getByPlaceholderText('Ask AI anything...');
    await user.type(input, 'Hello AI');

    // Click send button
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);

    await waitFor(() => {
      expect(apiClient.sendAIChatMessage).toHaveBeenCalledWith(
        'session-123',
        'Hello AI',
        'deepseek-r1',
        customContext
      );
    });
  });
});

