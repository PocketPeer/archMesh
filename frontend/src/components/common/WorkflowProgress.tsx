"use client";

/**
 * Workflow Progress Component
 * 
 * Displays real-time progress updates for workflow execution.
 * Shows current stage, progress percentage, and status messages.
 */

import React, { useState, useEffect } from 'react';
import { CheckCircle, Clock, AlertCircle, Pause, Play, RefreshCw } from 'lucide-react';
import { useWebSocket, WorkflowUpdate } from '../../hooks/useWebSocket';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface WorkflowProgressProps {
  sessionId?: string;
  className?: string;
}

const WorkflowProgress: React.FC<WorkflowProgressProps> = ({ 
  sessionId, 
  className = '' 
}) => {
  const { workflowUpdates, isConnected } = useWebSocket();
  const [isPolling, setIsPolling] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Filter updates for specific session or show all if no sessionId provided
  const relevantUpdates = sessionId 
    ? workflowUpdates.filter(update => update.sessionId === sessionId)
    : workflowUpdates;

  const latestUpdate = relevantUpdates[0];

  // Enhanced polling for real-time updates
  useEffect(() => {
    if (sessionId && latestUpdate && !['completed', 'failed'].includes(latestUpdate.status)) {
      setIsPolling(true);
      const interval = setInterval(() => {
        setLastUpdate(new Date());
        // Trigger a refresh of workflow data
        window.dispatchEvent(new CustomEvent('workflow-refresh', { detail: { sessionId } }));
      }, 5000); // Poll every 5 seconds

      return () => {
        clearInterval(interval);
        setIsPolling(false);
      };
    }
  }, [sessionId, latestUpdate?.status]);

  // Update last update time when new updates arrive
  useEffect(() => {
    if (latestUpdate) {
      setLastUpdate(new Date());
    }
  }, [latestUpdate]);

  if (!latestUpdate) {
    return (
      <Card className={`p-4 ${className}`}>
        <div className="flex items-center gap-3">
          <Clock className="h-5 w-5 text-gray-400" />
          <div className="flex-1">
            <h3 className="font-medium text-sm">Workflow Status</h3>
            <p className="text-sm text-gray-500">
              {isConnected ? 'Waiting for workflow to start...' : 'Connecting...'}
            </p>
          </div>
          {isPolling && (
            <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
          )}
        </div>
      </Card>
    );
  }

  const getStatusIcon = (status: WorkflowUpdate['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'paused':
        return <Pause className="h-5 w-5 text-yellow-500" />;
      case 'running':
      default:
        return <Play className="h-5 w-5 text-blue-500" />;
    }
  };

  const getStatusBadge = (status: WorkflowUpdate['status']) => {
    const variants = {
      completed: 'default',
      failed: 'destructive',
      paused: 'secondary',
      running: 'default'
    } as const;

    const colors = {
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      paused: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800'
    };

    return (
      <Badge 
        variant={variants[status]}
        className={`text-xs ${colors[status]}`}
      >
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatStage = (stage: string) => {
    return stage
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Card className={`p-4 ${className}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getStatusIcon(latestUpdate.status)}
            <div>
              <h3 className="font-medium text-sm">Workflow Progress</h3>
              <p className="text-sm text-gray-500">
                {formatStage(latestUpdate.stage)}
              </p>
            </div>
          </div>
          {getStatusBadge(latestUpdate.status)}
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Progress</span>
            <span className="font-medium">{latestUpdate.progress}%</span>
          </div>
          <Progress 
            value={latestUpdate.progress} 
            className="h-2"
          />
        </div>

        {/* Status Message */}
        {latestUpdate.message && (
          <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
            {latestUpdate.message}
          </div>
        )}

        {/* Connection Status */}
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>

        {/* Additional Data */}
        {latestUpdate.data && (
          <div className="text-xs text-gray-500">
            <details className="cursor-pointer">
              <summary className="hover:text-gray-700">Show Details</summary>
              <pre className="mt-2 p-2 bg-gray-50 rounded text-xs overflow-auto">
                {JSON.stringify(latestUpdate.data, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </Card>
  );
};

export default WorkflowProgress;
