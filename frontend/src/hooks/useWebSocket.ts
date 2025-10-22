"use client";

/**
 * WebSocket hook for real-time updates
 * 
 * This hook provides real-time communication with the backend for:
 * - Workflow progress updates
 * - Notification delivery
 * - Live status monitoring
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export interface WebSocketMessage {
  type: 'workflow_update' | 'notification' | 'error' | 'ping' | 'pong';
  data: any;
  timestamp: number;
}

export interface WorkflowUpdate {
  sessionId: string;
  stage: string;
  progress: number;
  status: 'running' | 'completed' | 'failed' | 'paused';
  message?: string;
  data?: any;
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
  action?: {
    label: string;
    url: string;
  };
}

interface UseWebSocketOptions {
  url?: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: any) => void;
  connect: () => void;
  disconnect: () => void;
  workflowUpdates: WorkflowUpdate[];
  notifications: Notification[];
  markNotificationAsRead: (id: string) => void;
  clearNotifications: () => void;
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketReturn => {
  const {
    url = typeof window !== 'undefined' ? (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws') : 'ws://localhost:8000/ws',
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [workflowUpdates, setWorkflowUpdates] = useState<WorkflowUpdate[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const baseDelayMs = 1000;
  const errorLoggedRef = useRef(false);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (process.env.NODE_ENV !== 'test') console.log('WebSocket connected');
        setIsConnected(true);
        setIsConnecting(false);
        setError(null);
        reconnectAttemptsRef.current = 0;

        // Start ping interval
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          if (typeof event.data !== 'string') {
            return; // ignore blobs/binary
          }
          const trimmed = event.data.trim();
          if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) {
            // Non-JSON frames like pings/echo logs; ignore safely
            return;
          }
          const message: WebSocketMessage = JSON.parse(trimmed);
          setLastMessage(message);

          switch (message.type) {
            case 'workflow_update':
              setWorkflowUpdates(prev => {
                const existing = prev.find(update => update.sessionId === message.data.sessionId);
                if (existing) {
                  return prev.map(update => 
                    update.sessionId === message.data.sessionId 
                      ? { ...update, ...message.data }
                      : update
                  );
                } else {
                  return [...prev, message.data];
                }
              });
              break;

            case 'notification':
              setNotifications(prev => [message.data, ...prev]);
              break;

            case 'pong':
              // Handle pong response
              break;

            case 'error':
              setError(message.data.message || 'WebSocket error');
              break;
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = (event) => {
        if (process.env.NODE_ENV !== 'test') console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setIsConnecting(false);

        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Attempt to reconnect if not a manual disconnect
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(baseDelayMs * 2 ** (reconnectAttemptsRef.current - 1), 15000);
          reconnectTimeoutRef.current = setTimeout(() => {
            if (process.env.NODE_ENV !== 'test') console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (event) => {
        if (!errorLoggedRef.current && process.env.NODE_ENV !== 'test') {
          const info = {
            url,
            readyState: ws.readyState,
            type: (event as any)?.type || 'error'
          };
          if (process.env.NEXT_PUBLIC_DEBUG_WS === 'true') {
            console.warn('WebSocket error', info);
          }
          errorLoggedRef.current = true;
        }
        setError('WebSocket connection error');
        setIsConnecting(false);
      };

    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
      setIsConnecting(false);
    }
  }, [url, reconnectInterval, maxReconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsConnecting(false);
    setError(null);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Cannot send message:', message);
    }
  }, []);

  const markNotificationAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, read: true }
          : notification
      )
    );
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    isConnecting,
    error,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    workflowUpdates,
    notifications,
    markNotificationAsRead,
    clearNotifications
  };
};
