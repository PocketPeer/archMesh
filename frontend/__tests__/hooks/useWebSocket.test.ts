/**
 * Tests for useWebSocket hook
 */

import { renderHook, act } from '@testing-library/react';
import { useWebSocket } from '@/src/hooks/useWebSocket';

// Mock WebSocket implementation
const mockWebSocketInstance = {
  readyState: 0, // CONNECTING
  onopen: null as ((event: Event) => void) | null,
  onclose: null as ((event: CloseEvent) => void) | null,
  onmessage: null as ((event: MessageEvent) => void) | null,
  onerror: null as ((event: Event) => void) | null,
  close: jest.fn(),
  send: jest.fn(),
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
};

// Mock WebSocket constructor
const MockWebSocket = jest.fn().mockImplementation((url: string) => {
  mockWebSocketInstance.readyState = 0; // CONNECTING
  // Simulate connection opening
  setTimeout(() => {
    mockWebSocketInstance.readyState = 1; // OPEN
    if (mockWebSocketInstance.onopen) {
      mockWebSocketInstance.onopen(new Event('open'));
    }
  }, 0);
  return mockWebSocketInstance;
});

// Add static properties
MockWebSocket.CONNECTING = 0;
MockWebSocket.OPEN = 1;
MockWebSocket.CLOSING = 2;
MockWebSocket.CLOSED = 3;

// Mock global WebSocket
global.WebSocket = MockWebSocket as any;

describe('useWebSocket', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockWebSocketInstance.readyState = 0; // CONNECTING
    mockWebSocketInstance.onopen = null;
    mockWebSocketInstance.onclose = null;
    mockWebSocketInstance.onmessage = null;
    mockWebSocketInstance.onerror = null;
  });

  it('should initialize with default values', () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }));

    expect(result.current.isConnected).toBe(false);
    expect(result.current.isConnecting).toBe(false);
    expect(result.current.error).toBe(null);
    expect(result.current.lastMessage).toBe(null);
    expect(result.current.workflowUpdates).toEqual([]);
    expect(result.current.notifications).toEqual([]);
  });

  it('should connect when autoConnect is true', () => {
    renderHook(() => useWebSocket({ autoConnect: true }));

    expect(MockWebSocket).toHaveBeenCalledWith(
      process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
    );
  });

  it('should handle connection open', async () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }));

    act(() => {
      result.current.connect();
    });

    // Wait for the connection to open
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    expect(result.current.isConnected).toBe(true);
    expect(result.current.isConnecting).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('should handle messages', async () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }));

    act(() => {
      result.current.connect();
    });

    // Wait for connection to open
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    // Simulate receiving a workflow update
    const workflowMessage = {
      type: 'workflow_update',
      data: {
        sessionId: 'test-session',
        stage: 'requirements_parsing',
        progress: 50,
        status: 'running',
        message: 'Parsing requirements...'
      },
      timestamp: Date.now()
    };

    act(() => {
      if (mockWebSocketInstance.onmessage) {
        mockWebSocketInstance.onmessage({
          data: JSON.stringify(workflowMessage)
        } as MessageEvent);
      }
    });

    expect(result.current.lastMessage).toEqual(workflowMessage);
    expect(result.current.workflowUpdates).toHaveLength(1);
    expect(result.current.workflowUpdates[0].sessionId).toBe('test-session');
  });

  it('should handle notifications', async () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }));

    act(() => {
      result.current.connect();
    });

    // Wait for connection to open
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    const notificationMessage = {
      type: 'notification',
      data: {
        id: 'test-notification',
        type: 'info',
        title: 'Test Notification',
        message: 'This is a test notification',
        timestamp: Date.now(),
        read: false
      },
      timestamp: Date.now()
    };

    act(() => {
      if (mockWebSocketInstance.onmessage) {
        mockWebSocketInstance.onmessage({
          data: JSON.stringify(notificationMessage)
        } as MessageEvent);
      }
    });

    expect(result.current.notifications).toHaveLength(1);
    expect(result.current.notifications[0].id).toBe('test-notification');
  });

  it('should send messages', async () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }));

    act(() => {
      result.current.connect();
    });

    // Wait for connection to open
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    const testMessage = { type: 'test', data: 'test data' };

    act(() => {
      result.current.sendMessage(testMessage);
    });

    expect(mockWebSocketInstance.send).toHaveBeenCalledWith(JSON.stringify(testMessage));
  });

  it('should mark notifications as read', () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }));

    // Add a notification
    act(() => {
      result.current.notifications.push({
        id: 'test-notification',
        type: 'info',
        title: 'Test',
        message: 'Test message',
        timestamp: Date.now(),
        read: false
      });
    });

    act(() => {
      result.current.markNotificationAsRead('test-notification');
    });

    expect(result.current.notifications[0].read).toBe(true);
  });

  it('should clear notifications', () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }));

    // Add notifications
    act(() => {
      result.current.notifications.push(
        {
          id: 'notification-1',
          type: 'info',
          title: 'Test 1',
          message: 'Test message 1',
          timestamp: Date.now(),
          read: false
        },
        {
          id: 'notification-2',
          type: 'info',
          title: 'Test 2',
          message: 'Test message 2',
          timestamp: Date.now(),
          read: false
        }
      );
    });

    act(() => {
      result.current.clearNotifications();
    });

    expect(result.current.notifications).toHaveLength(0);
  });

  it('should disconnect', async () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }));

    act(() => {
      result.current.connect();
    });

    // Wait for connection to open
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 10));
    });

    act(() => {
      result.current.disconnect();
    });

    expect(mockWebSocketInstance.close).toHaveBeenCalledWith(1000, 'Manual disconnect');
  });
});
