import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AIChatProvider, useAIChat } from '@/src/contexts/AIChatContext';
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

// Test component that uses the AI chat context
const TestComponent = () => {
  const {
    currentSession,
    sessions,
    availableModels,
    currentModel,
    isConnected,
    isLoading,
    error,
    createSession,
    loadSessions,
    loadSession,
    sendMessage,
    switchModel,
    deleteSession,
    clearError,
    connectWebSocket,
    disconnectWebSocket,
  } = useAIChat();

  const handleCreateSession = async () => {
    try {
      await createSession('Test Session');
    } catch (err) {
      console.error('Create session error:', err);
    }
  };

  const handleSendMessage = async () => {
    try {
      await sendMessage('Hello AI', 'deepseek-r1', { test: 'context' });
    } catch (err) {
      console.error('Send message error:', err);
    }
  };

  const handleSwitchModel = async () => {
    try {
      await switchModel('claude-opus');
    } catch (err) {
      console.error('Switch model error:', err);
    }
  };

  const handleDeleteSession = async () => {
    try {
      if (currentSession) {
        await deleteSession(currentSession.id);
      }
    } catch (err) {
      console.error('Delete session error:', err);
    }
  };

  return (
    <div>
      <div data-testid="current-session">
        {currentSession ? currentSession.title : 'No session'}
      </div>
      <div data-testid="sessions-count">{sessions.length}</div>
      <div data-testid="models-count">{availableModels.length}</div>
      <div data-testid="current-model">{currentModel}</div>
      <div data-testid="is-connected">{isConnected ? 'connected' : 'disconnected'}</div>
      <div data-testid="is-loading">{isLoading ? 'loading' : 'not loading'}</div>
      {error && <div data-testid="error">{error}</div>}
      
      <button onClick={handleCreateSession}>Create Session</button>
      <button onClick={handleSendMessage}>Send Message</button>
      <button onClick={handleSwitchModel}>Switch Model</button>
      <button onClick={handleDeleteSession}>Delete Session</button>
      <button onClick={clearError}>Clear Error</button>
      <button onClick={() => connectWebSocket('test-session')}>Connect WS</button>
      <button onClick={disconnectWebSocket}>Disconnect WS</button>
    </div>
  );
};

describe('AIChatContext', () => {
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

  it('should provide initial state', () => {
    render(
      <AIChatProvider>
        <TestComponent />
      </AIChatProvider>
    );

    expect(screen.getByTestId('current-session')).toHaveTextContent('No session');
    expect(screen.getByTestId('sessions-count')).toHaveTextContent('0');
    expect(screen.getByTestId('current-model')).toHaveTextContent('deepseek-r1');
    expect(screen.getByTestId('is-connected')).toHaveTextContent('disconnected');
    expect(screen.getByTestId('is-loading')).toHaveTextContent('not loading');
  });

  it('should load available models on mount', async () => {
    render(
      <AIChatProvider>
        <TestComponent />
      </AIChatProvider>
    );

    await waitFor(() => {
      expect(apiClient.getAIChatModels).toHaveBeenCalled();
      expect(screen.getByTestId('models-count')).toHaveTextContent('2');
    });
  });

  it('should create a new session', async () => {
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

    render(
      <AIChatProvider>
        <TestComponent />
      </AIChatProvider>
    );

    await user.click(screen.getByText('Create Session'));

    await waitFor(() => {
      expect(apiClient.createAIChatSession).toHaveBeenCalledWith('Test Session');
      expect(screen.getByTestId('current-session')).toHaveTextContent('Test Session');
      expect(screen.getByTestId('sessions-count')).toHaveTextContent('1');
    });
  });

  it('should send a message', async () => {
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
      <AIChatProvider>
        <TestComponent />
      </AIChatProvider>
    );

    // First create a session
    await user.click(screen.getByText('Create Session'));
    
    await waitFor(() => {
      expect(screen.getByTestId('current-session')).toHaveTextContent('Test Session');
    });

    // Then send a message
    await user.click(screen.getByText('Send Message'));

    await waitFor(() => {
      expect(apiClient.sendAIChatMessage).toHaveBeenCalledWith(
        'session-123',
        'Hello AI',
        'deepseek-r1',
        { test: 'context' }
      );
    });
  });

  it('should switch model', async () => {
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
      <AIChatProvider>
        <TestComponent />
      </AIChatProvider>
    );

    // First create a session
    await user.click(screen.getByText('Create Session'));
    
    await waitFor(() => {
      expect(screen.getByTestId('current-session')).toHaveTextContent('Test Session');
    });

    // Then switch model
    await user.click(screen.getByText('Switch Model'));

    await waitFor(() => {
      expect(apiClient.switchAIChatModel).toHaveBeenCalledWith('session-123', 'claude-opus');
      expect(screen.getByTestId('current-model')).toHaveTextContent('claude-opus');
    });
  });

  it('should delete a session', async () => {
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
    (apiClient.deleteAIChatSession as jest.Mock).mockResolvedValue({ success: true });

    render(
      <AIChatProvider>
        <TestComponent />
      </AIChatProvider>
    );

    // First create a session
    await user.click(screen.getByText('Create Session'));
    
    await waitFor(() => {
      expect(screen.getByTestId('current-session')).toHaveTextContent('Test Session');
    });

    // Then delete the session
    await user.click(screen.getByText('Delete Session'));

    await waitFor(() => {
      expect(apiClient.deleteAIChatSession).toHaveBeenCalledWith('session-123');
      expect(screen.getByTestId('current-session')).toHaveTextContent('No session');
      expect(screen.getByTestId('sessions-count')).toHaveTextContent('0');
    });
  });

  it('should handle errors gracefully', async () => {
    const user = userEvent.setup();
    
    (apiClient.createAIChatSession as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(
      <AIChatProvider>
        <TestComponent />
      </AIChatProvider>
    );

    await user.click(screen.getByText('Create Session'));

    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Network error');
    });

    // Test error clearing
    await user.click(screen.getByText('Clear Error'));

    await waitFor(() => {
      expect(screen.queryByTestId('error')).not.toBeInTheDocument();
    });
  });

  it('should connect and disconnect WebSocket', async () => {
    const user = userEvent.setup();

    render(
      <AIChatProvider>
        <TestComponent />
      </AIChatProvider>
    );

    // Connect WebSocket
    await user.click(screen.getByText('Connect WS'));

    expect(global.WebSocket).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/ai-chat/ws/test-session')
    );

    // Disconnect WebSocket
    await user.click(screen.getByText('Disconnect WS'));

    expect(mockWebSocket.close).toHaveBeenCalled();
  });

  it('should throw error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAIChat must be used within an AIChatProvider');

    consoleSpy.mockRestore();
  });
});

