'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeftIcon, 
  CalendarIcon, 
  ClockIcon, 
  BarChart3Icon,
  CheckCircleIcon,
  XCircleIcon,
  AlertCircleIcon,
  RefreshCwIcon,
  DownloadIcon,
  EyeIcon
} from 'lucide-react';
import Link from 'next/link';
import { apiClient } from '@/lib/api-client';
import { WorkflowSession } from '@/types';

export default function WorkflowDetailPage() {
  const params = useParams();
  const projectId = params.id as string;
  const workflowId = params.workflowId as string;
  
  const [workflow, setWorkflow] = useState<WorkflowSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [client] = useState(() => apiClient);

  useEffect(() => {
    loadWorkflow();
  }, [workflowId]);

  const loadWorkflow = async () => {
    try {
      setLoading(true);
      const response = await client.getWorkflow(workflowId);
      setWorkflow(response);
    } catch (err) {
      console.error('Failed to load workflow:', err);
      setError('Failed to load workflow details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'running': return 'bg-blue-100 text-blue-800';
      case 'starting': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 100) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress >= 25) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const downloadResults = () => {
    if (!workflow) return;
    
    const results = {
      session_id: workflow.session_id,
      project_id: workflow.project_id,
      workflow_type: (workflow as any).workflow_type || 'requirements',
      current_stage: workflow.current_stage,
      is_active: workflow.is_active,
      started_at: workflow.started_at,
      completed_at: workflow.completed_at,
      last_activity: workflow.last_activity_at,
      state_data: workflow.state_data
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `workflow-${workflow.session_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <RefreshCwIcon className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-2 text-lg">Loading workflow details...</span>
        </div>
      </div>
    );
  }

  if (error || !workflow) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <XCircleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Workflow Not Found</h1>
          <p className="text-gray-600 mb-6">{error || 'The requested workflow could not be found.'}</p>
          <Link href={`/projects/${projectId}`}>
            <Button>
              <ArrowLeftIcon className="mr-2 h-4 w-4" />
              Back to Project
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Link href={`/projects/${projectId}`}>
            <Button variant="outline" size="sm">
              <ArrowLeftIcon className="mr-2 h-4 w-4" />
              Back to Project
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Workflow Details</h1>
            <p className="text-gray-600">Session ID: {workflow.session_id}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={downloadResults}>
            <DownloadIcon className="mr-2 h-4 w-4" />
            Export Results
          </Button>
          <Button variant="outline" onClick={loadWorkflow}>
            <RefreshCwIcon className="mr-2 h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Status Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Workflow Status</span>
                <div className="flex space-x-2">
                  <Badge className={getStatusColor(workflow.current_stage)}>
                    {workflow.current_stage}
                  </Badge>
                  <Badge variant={workflow.is_active ? "default" : "secondary"}>
                    {workflow.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Progress</span>
                    <span className="text-sm text-gray-600">
                      {workflow.current_stage === 'completed' ? '100%' : 
                       workflow.current_stage === 'failed' ? '0%' :
                       Math.round((workflow.state_data?.stage_progress || 0) * 100)}%
                    </span>
                  </div>
                  <Progress 
                    value={workflow.current_stage === 'completed' ? 100 : 
                           workflow.current_stage === 'failed' ? 0 :
                           (workflow.state_data?.stage_progress || 0) * 100} 
                    className="h-2"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <CalendarIcon className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Started</p>
                      <p className="text-sm text-gray-900">
                        {formatDate(workflow.started_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <ClockIcon className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Last Activity</p>
                      <p className="text-sm text-gray-900">
                        {formatDate(workflow.last_activity_at)}
                      </p>
                    </div>
                  </div>
                </div>

                {workflow.completed_at && (
                  <div className="flex items-center space-x-2">
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                    <div>
                      <p className="text-xs text-gray-500">Completed</p>
                      <p className="text-sm text-gray-900">
                        {formatDate(workflow.completed_at)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Stage Results */}
          {workflow.state_data?.stage_results && Object.keys(workflow.state_data.stage_results).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Stage Results</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(workflow.state_data.stage_results).map(([stage, result]) => (
                    <div key={stage} className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2 capitalize">
                        {stage.replace('_', ' ')}
                      </h4>
                      <div className="text-sm text-gray-600">
                        <pre className="whitespace-pre-wrap bg-gray-50 p-3 rounded">
                          {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Errors */}
          {workflow.state_data?.errors && workflow.state_data.errors.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-red-600">
                  <AlertCircleIcon className="mr-2 h-5 w-5" />
                  Errors
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {workflow.state_data.errors.map((error, index) => (
                    <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-sm text-red-800">
                        {typeof error === 'string' ? error : (error as any)?.error || JSON.stringify(error)}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Workflow Info */}
          <Card>
            <CardHeader>
              <CardTitle>Workflow Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-xs text-gray-500">Type</p>
                <p className="text-sm font-medium text-gray-900 capitalize">
                  {(workflow as any).workflow_type?.replace('_', ' ') || 'requirements'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Session ID</p>
                <p className="text-sm font-mono text-gray-900 break-all">
                  {workflow.session_id}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Project ID</p>
                <p className="text-sm font-mono text-gray-900 break-all">
                  {workflow.project_id}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Completed Stages */}
          {workflow.state_data?.completed_stages && workflow.state_data.completed_stages.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3Icon className="mr-2 h-5 w-5" />
                  Completed Stages ({workflow.state_data.completed_stages.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {workflow.state_data.completed_stages.map((stage, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <CheckCircleIcon className="h-4 w-4 text-green-500" />
                      <span className="text-sm text-gray-900 capitalize">
                        {stage.replace('_', ' ')}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Pending Tasks */}
          {workflow.state_data?.pending_tasks && workflow.state_data.pending_tasks.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Pending Tasks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {workflow.state_data.pending_tasks.map((task, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                      <span className="text-sm text-gray-900">{task}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
