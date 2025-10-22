'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ActivityIcon, 
  CheckCircleIcon, 
  AlertCircleIcon, 
  ClockIcon, 
  EyeIcon, 
  RefreshCwIcon 
} from 'lucide-react';
import { WorkflowSession } from '@/types';

interface WorkflowSessionsProps {
  workflows: WorkflowSession[];
  currentWorkflowId?: string;
  projectId: string;
}

export default function WorkflowSessions({ workflows, currentWorkflowId, projectId }: WorkflowSessionsProps) {
  const router = useRouter();

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <ActivityIcon className="h-5 w-5 text-slate-600" />
          <span>Workflow Sessions</span>
          <Badge variant="secondary" className="ml-2">
            {workflows.length} runs
          </Badge>
        </CardTitle>
        <CardDescription>
          All workflow executions and their current status
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {workflows.map((workflow) => {
            const isCurrentWorkflow = currentWorkflowId === workflow.session_id;
            const isActive = workflow.current_stage !== 'completed' && workflow.current_stage !== 'failed';
            
            return (
              <div
                key={workflow.session_id}
                className={`p-4 border rounded-lg transition-colors ${
                  isCurrentWorkflow 
                    ? 'border-blue-300 bg-blue-50' 
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {workflow.current_stage === 'completed' ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-600" />
                      ) : workflow.current_stage === 'failed' ? (
                        <AlertCircleIcon className="h-5 w-5 text-red-600" />
                      ) : (
                        <ClockIcon className="h-5 w-5 text-blue-600" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <p className="font-medium text-slate-900">
                          Workflow {workflow.session_id.substring(0, 8)}...
                        </p>
                        {isCurrentWorkflow && (
                          <Badge variant="outline" className="text-blue-600 border-blue-300">
                            Current
                          </Badge>
                        )}
                        {isActive && (
                          <RefreshCwIcon className="h-4 w-4 text-blue-600 animate-spin" />
                        )}
                      </div>
                      <p className="text-sm text-slate-600">
                        {workflow.started_at ? new Date(workflow.started_at).toLocaleString() : 'Unknown start time'}
                      </p>
                      {workflow.current_stage === 'completed' && workflow.completed_at && (
                        <p className="text-xs text-slate-500">
                          Duration: {Math.round((new Date(workflow.completed_at).getTime() - new Date(workflow.started_at).getTime()) / 60000)} minutes
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge 
                      className={
                        workflow.current_stage === 'completed' 
                          ? 'bg-green-100 text-green-800 border-green-200'
                          : workflow.current_stage === 'failed'
                          ? 'bg-red-100 text-red-800 border-red-200'
                          : 'bg-blue-100 text-blue-800 border-blue-200'
                      }
                    >
                      {workflow.current_stage === 'completed' ? 'COMPLETED' : 
                       workflow.current_stage === 'failed' ? 'FAILED' : 
                       workflow.current_stage.toUpperCase().replace('_', ' ')}
                    </Badge>
                    <Link href={`/projects/${projectId}/workflows/${workflow.session_id}`}>
                      <Button variant="outline" size="sm">
                        <EyeIcon className="h-4 w-4 mr-1" />
                        View Details
                      </Button>
                    </Link>
                    {workflow.current_stage === 'failed' && (
                      <Button variant="outline" size="sm" onClick={() => {
                        router.push(`/projects/${projectId}/upload?retry=${workflow.session_id}`);
                      }}>
                        <RefreshCwIcon className="h-4 w-4 mr-1" />
                        Retry
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
