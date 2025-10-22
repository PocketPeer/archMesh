'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ActivityIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  AlertCircleIcon, 
  EyeIcon, 
  RefreshCwIcon,
  BarChart3Icon,
  TrendingUpIcon,
  PlayIcon,
  PauseIcon
} from 'lucide-react';
import { WorkflowSession, WorkflowStatus } from '@/types';

interface WorkflowDashboardProps {
  currentWorkflow: WorkflowStatus | null;
  workflows: WorkflowSession[];
  onWorkflowAction: (action: string, workflowId: string) => void;
}

export default function WorkflowDashboard({ 
  currentWorkflow, 
  workflows, 
  onWorkflowAction 
}: WorkflowDashboardProps) {
  const [activeTab, setActiveTab] = useState('current');

  const getStatusIcon = (stage: string) => {
    switch (stage) {
      case 'completed': return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'failed': return <AlertCircleIcon className="h-5 w-5 text-red-600" />;
      default: return <ClockIcon className="h-5 w-5 text-blue-600" />;
    }
  };

  const getStatusColor = (stage: string) => {
    switch (stage) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const formatDuration = (startedAt: string, completedAt?: string) => {
    const start = new Date(startedAt);
    const end = completedAt ? new Date(completedAt) : new Date();
    const duration = Math.round((end.getTime() - start.getTime()) / 60000);
    return `${duration} min`;
  };

  const getWorkflowAnalytics = () => {
    const completed = workflows.filter(w => w.current_stage === 'completed').length;
    const failed = workflows.filter(w => w.current_stage === 'failed').length;
    const active = workflows.filter(w => w.current_stage !== 'completed' && w.current_stage !== 'failed').length;
    const total = workflows.length;
    
    return {
      completed,
      failed,
      active,
      total,
      successRate: total > 0 ? Math.round((completed / total) * 100) : 0
    };
  };

  const analytics = getWorkflowAnalytics();

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <ActivityIcon className="h-5 w-5 text-slate-600" />
          <span>Workflow Dashboard</span>
        </CardTitle>
        <CardDescription>
          Monitor and manage your workflow executions
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="current" className="flex items-center space-x-2">
              <PlayIcon className="h-4 w-4" />
              <span>Current</span>
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center space-x-2">
              <ClockIcon className="h-4 w-4" />
              <span>History</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <BarChart3Icon className="h-4 w-4" />
              <span>Analytics</span>
            </TabsTrigger>
          </TabsList>

          {/* Current Workflow */}
          <TabsContent value="current" className="mt-6">
            {currentWorkflow ? (
              <div className="space-y-4">
                <div className="p-4 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(currentWorkflow.current_stage)}
                      <div>
                        <h3 className="font-medium text-slate-900">Current Workflow</h3>
                        <p className="text-sm text-slate-600">
                          Stage: {currentWorkflow.current_stage.replace('_', ' ').toUpperCase()}
                        </p>
                      </div>
                    </div>
                    <Badge className={getStatusColor(currentWorkflow.current_stage)}>
                      {currentWorkflow.current_stage.toUpperCase().replace('_', ' ')}
                    </Badge>
                  </div>
                  
                  {currentWorkflow.errors && currentWorkflow.errors.length > 0 && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <h4 className="font-medium text-red-800 mb-2">Errors</h4>
                      <ul className="text-sm text-red-700 space-y-1">
                        {currentWorkflow.errors.map((error, index) => (
                          <li key={index}>• {error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <ActivityIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No Active Workflow</h3>
                <p className="text-slate-600 mb-4">Start a new workflow to begin analysis</p>
                <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <PlayIcon className="h-4 w-4 mr-2" />
                  Start Workflow
                </Button>
              </div>
            )}
          </TabsContent>

          {/* Workflow History */}
          <TabsContent value="history" className="mt-6">
            <div className="space-y-4">
              {workflows.length > 0 ? (
                workflows.map((workflow) => (
                  <div
                    key={workflow.session_id}
                    className="p-4 border border-slate-200 rounded-lg hover:border-slate-300 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(workflow.current_stage)}
                        <div>
                          <h4 className="font-medium text-slate-900">
                            Workflow {workflow.session_id.substring(0, 8)}...
                          </h4>
                          <p className="text-sm text-slate-600">
                            {new Date(workflow.started_at).toLocaleString()}
                          </p>
                          {workflow.completed_at && (
                            <p className="text-xs text-slate-500">
                              Duration: {formatDuration(workflow.started_at, workflow.completed_at)}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(workflow.current_stage)}>
                          {workflow.current_stage.toUpperCase().replace('_', ' ')}
                        </Badge>
                        <Link href={`/projects/workflows/${workflow.session_id}`}>
                          <Button variant="outline" size="sm">
                            <EyeIcon className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                        </Link>
                        {workflow.current_stage === 'failed' && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => onWorkflowAction('retry', workflow.session_id)}
                          >
                            <RefreshCwIcon className="h-4 w-4 mr-1" />
                            Retry
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <ClockIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">No Workflow History</h3>
                  <p className="text-slate-600">Workflow executions will appear here</p>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Analytics */}
          <TabsContent value="analytics" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-slate-900">Total Workflows</h4>
                  <ActivityIcon className="h-5 w-5 text-slate-600" />
                </div>
                <div className="text-2xl font-bold text-slate-900">{analytics.total}</div>
              </div>
              
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-slate-900">Completed</h4>
                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                </div>
                <div className="text-2xl font-bold text-green-600">{analytics.completed}</div>
              </div>
              
              <div className="p-4 bg-red-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-slate-900">Failed</h4>
                  <AlertCircleIcon className="h-5 w-5 text-red-600" />
                </div>
                <div className="text-2xl font-bold text-red-600">{analytics.failed}</div>
              </div>
              
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-slate-900">Success Rate</h4>
                  <TrendingUpIcon className="h-5 w-5 text-blue-600" />
                </div>
                <div className="text-2xl font-bold text-blue-600">{analytics.successRate}%</div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
