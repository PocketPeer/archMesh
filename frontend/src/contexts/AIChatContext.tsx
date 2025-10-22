'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/src/contexts/AuthContext';

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
  model_used?: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
  current_model: string;
  context?: Record<string, any>;
}

export interface AIModel {
  name: string;
  provider: string;
  description: string;
  capabilities: string[];
  cost_per_token: number;
  max_tokens: number;
}

interface AIChatContextType {
  // State
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  availableModels: AIModel[];
  currentModel: string;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  createSession: (title?: string) => Promise<ChatSession>;
  loadSessions: () => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  sendMessage: (content: string, model?: string, context?: Record<string, any>) => Promise<void>;
  switchModel: (model: string) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  clearError: () => void;
  
  // WebSocket
  connectWebSocket: (sessionId: string) => void;
  disconnectWebSocket: () => void;
}

const AIChatContext = createContext<AIChatContextType | undefined>(undefined);

export const useAIChat = () => {
  const context = useContext(AIChatContext);
  if (!context) {
    throw new Error('useAIChat must be used within an AIChatProvider');
  }
  return context;
};

interface AIChatProviderProps {
  children: React.ReactNode;
}

export const AIChatProvider: React.FC<AIChatProviderProps> = ({ children }) => {
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [availableModels, setAvailableModels] = useState<AIModel[]>([]);
  const [currentModel, setCurrentModel] = useState<string>('deepseek-r1');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const lastCreatedSessionIdRef = React.useRef<string | null>(null);
  // Safely access auth; default to unauthenticated when provider is absent (e.g., in unit tests)
  let isAuthenticated = false as boolean;
  let accessToken: string | null = null;
  try {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const auth = useAuth();
    isAuthenticated = auth.isAuthenticated;
    accessToken = auth.accessToken;
  } catch (_e) {
    isAuthenticated = false;
    accessToken = null;
  }

  // Load available models and sessions on mount AND whenever auth becomes available
  useEffect(() => {
    // Avoid noisy errors before authentication
    if (!isAuthenticated) return;
    loadAvailableModels();
    loadSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, accessToken]);

          const loadAvailableModels = async () => {
    try {
              const response = await apiClient.getAIChatModels();
      setAvailableModels(response.models);
      setCurrentModel(response.current_model || 'deepseek-r1');
    } catch (err) {
              console.error('Failed to load available models:', err);
              setError('Failed to load available models');
    }
  };

          const createSession = async (title: string = 'New Chat Session'): Promise<ChatSession> => {
    try {
      setIsLoading(true);
              const session = await apiClient.createAIChatSession(title);
      setSessions(prev => [session, ...prev]);
      setCurrentSession(session);
      lastCreatedSessionIdRef.current = session.id;
      return session;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create session';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSessions = async () => {
    try {
      const response = await apiClient.getAIChatSessions();
      setSessions(response);
      // If no current session is selected, adopt the first available
      if (!currentSession && Array.isArray(response) && response.length > 0) {
        setCurrentSession(response[0]);
        lastCreatedSessionIdRef.current = response[0].id;
      }
    } catch (err) {
      // Only surface errors after auth; otherwise 401s during initial load would be noisy
      if (isAuthenticated) {
        console.error('Failed to load sessions:', err);
        setError('Failed to load chat sessions');
      }
    }
  };

  const loadSession = async (sessionId: string) => {
    try {
      setIsLoading(true);
      const session = await apiClient.getAIChatSession(sessionId);
      setCurrentSession(session);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

          const sendMessage = async (
    content: string, 
    model?: string, 
    context?: Record<string, any>
  ) => {
    const resolvedSessionId = currentSession?.id || lastCreatedSessionIdRef.current || sessions[0]?.id;
    if (!resolvedSessionId) throw new Error('No active session');

    try {
      setIsLoading(true);
      // Optimistically append the user message so history shows immediately
      const userMsg: ChatMessage = {
        id: `${Date.now()}-user`,
        content,
        role: 'user',
        timestamp: new Date().toISOString(),
      };
      setCurrentSession(prev => prev ? { ...prev, messages: [...prev.messages, userMsg], updated_at: new Date().toISOString() } : prev);
      setSessions(prev => prev.map(s => s.id === resolvedSessionId ? { ...s, messages: [...s.messages, userMsg], updated_at: new Date().toISOString() } : s));

              const response = await apiClient.sendAIChatMessage(
                resolvedSessionId,
                content,
                model || currentModel,
                context
              );

      if (response.success) {
        // Update current session with new message
        setCurrentSession(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            messages: [...prev.messages, {
              ...response.message,
              role: response.message.role as 'user' | 'assistant' | 'system'
            }],
            updated_at: new Date().toISOString()
          };
        });

        // Update sessions list
        setSessions(prev => 
          prev.map(session => 
            session.id === resolvedSessionId 
              ? { ...session, messages: [...session.messages, response.message as any], updated_at: new Date().toISOString() }
              : session
          )
        );
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const switchModel = async (model: string) => {
    try {
      const sessionId = currentSession?.id || lastCreatedSessionIdRef.current || sessions[0]?.id;
      if (!sessionId) throw new Error('No active session');
      await (apiClient as any).switchAIChatModel(sessionId, model);
      setCurrentModel(model);
      setCurrentSession(prev => prev ? { ...prev, current_model: model } : prev);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to switch model';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await apiClient.deleteAIChatSession(sessionId);
      setSessions(prev => prev.filter(session => session.id !== sessionId));
      
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        disconnectWebSocket();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete session';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const connectWebSocket = useCallback((sessionId: string) => {
    if (ws) {
      ws.close();
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/ai-chat/ws/${sessionId}`;
    
    const websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
      setIsConnected(true);
      setError(null);
    };
    
    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'ai_message') {
          const newMessage: ChatMessage = {
            id: data.id || Date.now().toString(),
            content: data.content,
            role: 'assistant',
            timestamp: data.timestamp,
            model_used: data.model_used,
            metadata: data.metadata
          };
          
          setCurrentSession(prev => {
            if (!prev) return null;
            return {
              ...prev,
              messages: [...prev.messages, newMessage],
              updated_at: new Date().toISOString()
            };
          });
        } else if (data.type === 'user_message') {
          const newMessage: ChatMessage = {
            id: data.id || `${Date.now()}-user-ws`,
            content: data.content,
            role: 'user',
            timestamp: data.timestamp || new Date().toISOString(),
          };
          setCurrentSession(prev => prev ? { ...prev, messages: [...prev.messages, newMessage], updated_at: new Date().toISOString() } : prev);
        } else if (data.type === 'error') {
          setError(data.content);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };
    
    websocket.onclose = () => {
      setIsConnected(false);
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket connection error');
      setIsConnected(false);
    };
    
    setWs(websocket);
  }, [ws]);

  const disconnectWebSocket = useCallback(() => {
    if (ws) {
      ws.close();
      setWs(null);
      setIsConnected(false);
    }
  }, [ws]);

  const clearError = () => {
    setError(null);
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [ws]);

  const value: AIChatContextType = {
    // State
    currentSession,
    sessions,
    availableModels,
    currentModel,
    isConnected,
    isLoading,
    error,
    
    // Actions
    createSession,
    loadSessions,
    loadSession,
    sendMessage,
    switchModel,
    deleteSession,
    clearError,
    
    // WebSocket
    connectWebSocket,
    disconnectWebSocket,
  };

  return (
    <AIChatContext.Provider value={value}>
      {children}
    </AIChatContext.Provider>
  );
};
