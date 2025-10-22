"use client";

import React, { useState, useCallback, useEffect } from 'react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Progress } from '../../components/ui/progress';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { apiClient } from '../../lib/api-client';
import { useWebSocket } from '../hooks/useWebSocket';
import { toast } from 'sonner';

interface VibeCodingToolProps {
  projectId: string;
  onCodeGenerated?: (code: string) => void;
  onSessionUpdate?: (sessionId: string, status: string) => void;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface GeneratedCode {
  code: string;
  language: string;
  framework?: string;
  quality_score?: number;
}

interface ExecutionResult {
  success: boolean;
  stdout: string;
  stderr: string;
  execution_time: number;
  memory_usage_mb?: number;
  cpu_usage_percent?: number;
}

interface SessionStatus {
  session_id: string;
  status: string;
  progress: number;
  current_stage: string;
}

export const VibeCodingTool: React.FC<VibeCodingToolProps> = ({
  projectId,
  onCodeGenerated,
  onSessionUpdate,
}) => {
  const [naturalLanguageInput, setNaturalLanguageInput] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<SessionStatus | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [feedback, setFeedback] = useState({ rating: 0, comments: '' });
  const [error, setError] = useState<string | null>(null);

  const { isConnected, sendMessage, lastMessage } = useWebSocket();

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage as unknown as string);
        if (data.type === 'session_update') {
          setSessionStatus(data.session_status);
          if (onSessionUpdate) {
            onSessionUpdate(data.session_status.session_id, data.session_status.status);
          }
        } else if (data.type === 'code_generated') {
          setGeneratedCode(data.generated_code);
          setExecutionResult(data.execution_result);
          setIsGenerating(false);
          setIsExecuting(false);
          if (onCodeGenerated) {
            onCodeGenerated(data.generated_code.code);
          }
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    }
  }, [lastMessage, onCodeGenerated, onSessionUpdate]);

  const handleNaturalLanguageGeneration = useCallback(async () => {
    if (!naturalLanguageInput.trim()) {
      setError('Please enter a description');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await apiClient.generateCode({
        user_input: naturalLanguageInput,
        project_id: projectId,
        session_id: sessionId || undefined,
        context_sources: ['requirements', 'architecture'],
      });

      if (response.success) {
        setGeneratedCode(response.generated_code || null);
        setExecutionResult(response.execution_result || null);
        setSessionId(response.session_id);
        
        // Add to chat messages
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: naturalLanguageInput,
          timestamp: new Date(),
        };
        setChatMessages(prev => [...prev, userMessage]);

        if (onCodeGenerated && response.generated_code) {
          onCodeGenerated(response.generated_code.code);
        }

        toast.success('Code generated successfully!');
      } else {
        setError('Code generation failed');
        toast.error('Code generation failed');
      }
    } catch (err) {
      setError('Code generation failed');
      toast.error('Code generation failed');
    } finally {
      setIsGenerating(false);
    }
  }, [naturalLanguageInput, projectId, sessionId, onCodeGenerated]);

  const handleChatMessage = useCallback(async () => {
    if (!chatInput.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: chatInput,
      timestamp: new Date(),
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');

    try {
      const response = await apiClient.generateCode({
        user_input: chatInput,
        project_id: projectId,
        session_id: sessionId || undefined,
        context_sources: ['requirements', 'architecture'],
      });

      if (response.success) {
        setGeneratedCode(response.generated_code || null);
        setExecutionResult(response.execution_result || null);
        
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: 'Code updated based on your request.',
          timestamp: new Date(),
        };
        setChatMessages(prev => [...prev, assistantMessage]);
      }
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request.',
        timestamp: new Date(),
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }
  }, [chatInput, projectId, sessionId]);

  const handleFeedbackSubmit = useCallback(async () => {
    if (!sessionId || feedback.rating === 0) return;

    try {
      await apiClient.submitFeedback({
        session_id: sessionId,
        rating: feedback.rating,
        comments: feedback.comments,
        suggested_changes: [],
      });

      toast.success('Feedback submitted successfully');
      setFeedback({ rating: 0, comments: '' });
    } catch (err) {
      toast.error('Failed to submit feedback');
    }
  }, [sessionId, feedback]);

  const copyToClipboard = useCallback(async () => {
    if (generatedCode?.code) {
      await navigator.clipboard.writeText(generatedCode.code);
      toast.success('Code copied to clipboard!');
    }
  }, [generatedCode]);

  const renderStarRating = () => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Button
            key={star}
            variant="ghost"
            size="sm"
            onClick={() => setFeedback(prev => ({ ...prev, rating: star }))}
            className={`p-1 ${feedback.rating >= star ? 'text-yellow-500' : 'text-gray-300'}`}
          >
            ★
          </Button>
        ))}
      </div>
    );
  };

  return (
    <div 
      data-testid="vibe-coding-tool"
      className="h-full flex flex-col space-y-4 mobile-responsive tablet-responsive"
    >
      <Card>
        <CardHeader>
          <CardTitle>Vibe Coding Tool</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Natural Language Input */}
          <div className="space-y-2">
            <label 
              htmlFor="natural-language-input"
              className="text-sm font-medium"
            >
              Describe what you want to build
            </label>
            <div className="flex gap-2">
              <Input
                id="natural-language-input"
                placeholder="Describe what you want to build..."
                value={naturalLanguageInput}
                onChange={(e) => setNaturalLanguageInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleNaturalLanguageGeneration()}
                aria-label="Natural language input for code generation"
              />
              <Button 
                onClick={handleNaturalLanguageGeneration}
                disabled={isGenerating}
              >
                {isGenerating ? 'Generating...' : 'Generate Code'}
              </Button>
            </div>
            {error && (
              <p className="text-red-500 text-sm">{error}</p>
            )}
          </div>

          {/* Progress Indicator */}
          {isGenerating && (
            <div data-testid="progress-indicator" className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Generating code...</span>
                <span>{sessionStatus?.progress || 0}%</span>
              </div>
              <Progress value={sessionStatus?.progress || 0} />
            </div>
          )}

          {/* Session Info */}
          {sessionId && (
            <div className="flex gap-4 text-sm text-gray-600">
              <span data-testid="session-id">Session: {sessionId}</span>
              {sessionStatus && (
                <span data-testid="session-status">
                  Status: {sessionStatus.status} | Progress: {sessionStatus.progress}%
                </span>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="code" className="flex-1">
        <TabsList>
          <TabsTrigger value="code">Generated Code</TabsTrigger>
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="results">Execution Results</TabsTrigger>
        </TabsList>

        <TabsContent value="code" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Generated Code</CardTitle>
            </CardHeader>
            <CardContent>
              {generatedCode ? (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div className="flex gap-2">
                      <Badge variant="secondary">{generatedCode.language}</Badge>
                      {generatedCode.framework && (
                        <Badge variant="outline">{generatedCode.framework}</Badge>
                      )}
                      {generatedCode.quality_score && (
                        <Badge variant="default">
                          Quality Score: {Math.round(generatedCode.quality_score * 100)}%
                        </Badge>
                      )}
                    </div>
                    <Button onClick={copyToClipboard} size="sm">
                      Copy Code
                    </Button>
                  </div>
                  <div 
                    data-testid="code-editor"
                    className={`bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-auto max-h-96 syntax-highlighted`}
                  >
                    <pre>{generatedCode.code}</pre>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  No code generated yet. Enter a description above to get started.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Chat Interface</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div 
                data-testid="chat-messages"
                className="h-64 overflow-y-auto border rounded-lg p-4 space-y-2"
              >
                {chatMessages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs p-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-800'
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <Input
                  data-testid="chat-input"
                  placeholder="Ask for changes or improvements..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleChatMessage()}
                  aria-label="Chat input for iterative development"
                />
                <Button onClick={handleChatMessage}>Send</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Execution Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div data-testid="execution-results">
                {executionResult ? (
                  <div className="space-y-4">
                    <div className="flex gap-4 text-sm">
                      <Badge variant={executionResult.success ? 'default' : 'destructive'}>
                        {executionResult.success ? 'Success' : 'Failed'}
                      </Badge>
                      <span>Execution Time: {executionResult.execution_time}s</span>
                      {executionResult.memory_usage_mb && (
                        <span>Memory Usage: {executionResult.memory_usage_mb} MB</span>
                      )}
                      {executionResult.cpu_usage_percent && (
                        <span>CPU Usage: {executionResult.cpu_usage_percent}%</span>
                      )}
                    </div>
                    
                    {executionResult.stdout && (
                      <div>
                        <h4 className="font-medium mb-2">Output:</h4>
                        <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
                          {executionResult.stdout}
                        </pre>
                      </div>
                    )}
                    
                    {executionResult.stderr && (
                      <div>
                        <h4 className="font-medium mb-2 text-red-600">Errors:</h4>
                        <pre className="bg-red-50 p-2 rounded text-sm overflow-auto text-red-800">
                          {executionResult.stderr}
                        </pre>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">
                    No execution results yet. Generate code to see results here.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Feedback Section */}
      {generatedCode && (
        <Card>
          <CardHeader>
            <CardTitle>Rate the Generated Code</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium">Rating:</span>
              {renderStarRating()}
            </div>
            <div className="space-y-2">
              <label htmlFor="feedback-comments" className="text-sm font-medium">
                Comments (optional)
              </label>
              <Textarea
                id="feedback-comments"
                placeholder="Add your comments..."
                value={feedback.comments}
                onChange={(e) => setFeedback(prev => ({ ...prev, comments: e.target.value }))}
                rows={3}
              />
            </div>
            <Button 
              onClick={handleFeedbackSubmit}
              disabled={feedback.rating === 0}
            >
              Submit Feedback
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Status Announcements for Screen Readers */}
      <div role="status" aria-live="polite" className="sr-only">
        {isGenerating && 'Generating code...'}
        {isExecuting && 'Executing code...'}
        {error && `Error: ${error}`}
      </div>
    </div>
  );
};
