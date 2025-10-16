'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Project, WorkflowSession } from '@/types';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [workflows, setWorkflows] = useState<WorkflowSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      loadProject();
      loadWorkflows();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      const projectData = await apiClient.getProject(projectId);
      setProject(projectData);
    } catch (error) {
      console.error('Failed to load project:', error);
      toast.error('Failed to load project');
    }
  };

  const loadWorkflows = async () => {
    try {
      const response = await apiClient.listWorkflows(0, 100, projectId);
      setWorkflows(response.items || []);
    } catch (error) {
      console.error('Failed to load workflows:', error);
      toast.error('Failed to load workflows');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: Project['status']) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };

    return (
      <Badge className={colors[status]}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getDomainBadge = (domain: Project['domain']) => {
    const colors = {
      'cloud-native': 'bg-blue-100 text-blue-800',
      'data-platform': 'bg-purple-100 text-purple-800',
      'enterprise': 'bg-green-100 text-green-800'
    };

    return (
      <Badge className={colors[domain]}>
        {domain.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </Badge>
    );
  };

  const getWorkflowStatusBadge = (stage: string) => {
    const colors = {
      'starting': 'bg-gray-100 text-gray-800',
      'document_analysis': 'bg-blue-100 text-blue-800',
      'requirements_review': 'bg-yellow-100 text-yellow-800',
      'architecture_design': 'bg-purple-100 text-purple-800',
      'architecture_review': 'bg-orange-100 text-orange-800',
      'completed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800'
    };

    return (
      <Badge className={colors[stage as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {stage.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-slate-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-slate-900 mb-4">Project Not Found</h1>
        <p className="text-slate-600 mb-6">The project you're looking for doesn't exist.</p>
        <Link href="/projects">
          <Button>Back to Projects</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-4 mb-2">
            <h1 className="text-3xl font-bold text-slate-900">{project.name}</h1>
            {getStatusBadge(project.status)}
            {getDomainBadge(project.domain)}
          </div>
          <p className="text-slate-600">
            {project.description || 'No description provided'}
          </p>
        </div>
        <div className="flex space-x-2">
          <Link href={`/projects/${project.id}/upload`}>
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              Start Workflow
            </Button>
          </Link>
        </div>
      </div>

      {/* Project Details */}
      <Card>
        <CardHeader>
          <CardTitle>Project Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <span className="text-sm font-medium text-slate-600">Created:</span>
              <p className="text-slate-900">{new Date(project.created_at).toLocaleString()}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-slate-600">Last Updated:</span>
              <p className="text-slate-900">{new Date(project.updated_at).toLocaleString()}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-slate-600">Project ID:</span>
              <p className="text-slate-900 font-mono text-sm">{project.id}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-slate-600">Status:</span>
              <div className="mt-1">{getStatusBadge(project.status)}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Workflows */}
      <Tabs defaultValue="workflows" className="space-y-4">
        <TabsList>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="requirements">Requirements</TabsTrigger>
          <TabsTrigger value="architecture">Architecture</TabsTrigger>
        </TabsList>

        <TabsContent value="workflows" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Sessions</CardTitle>
              <CardDescription>
                Track the progress of your architecture generation workflows
              </CardDescription>
            </CardHeader>
            <CardContent>
              {workflows.length === 0 ? (
                <div className="text-center py-8">
                  <div className="h-16 w-16 mx-auto rounded-full bg-slate-100 flex items-center justify-center mb-4">
                    <svg className="h-8 w-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">No workflows yet</h3>
                  <p className="text-slate-600 mb-4">Start a new workflow to begin the architecture design process</p>
                  <Link href={`/projects/${project.id}/upload`}>
                    <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                      Start Workflow
                    </Button>
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {workflows.map((workflow) => (
                    <Card key={workflow.session_id} className="border-l-4 border-l-blue-500">
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h3 className="font-semibold text-slate-900">Workflow Session</h3>
                            <p className="text-sm text-slate-600 font-mono">{workflow.session_id}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {getWorkflowStatusBadge(workflow.current_stage)}
                            <Badge variant={workflow.is_active ? "default" : "secondary"}>
                              {workflow.is_active ? "Active" : "Inactive"}
                            </Badge>
                          </div>
                        </div>
                        <div className="grid gap-4 md:grid-cols-3 text-sm">
                          <div>
                            <span className="text-slate-600">Started:</span>
                            <p className="text-slate-900">{new Date(workflow.started_at).toLocaleString()}</p>
                          </div>
                          <div>
                            <span className="text-slate-600">Last Activity:</span>
                            <p className="text-slate-900">{new Date(workflow.last_activity_at).toLocaleString()}</p>
                          </div>
                          <div>
                            <span className="text-slate-600">Progress:</span>
                            <p className="text-slate-900">{Math.round(workflow.state_data.stage_progress * 100)}%</p>
                          </div>
                        </div>
                        {workflow.state_data.errors.length > 0 && (
                          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                            <h4 className="text-sm font-medium text-red-800 mb-2">Errors:</h4>
                            <ul className="text-sm text-red-700 space-y-1">
                              {workflow.state_data.errors.map((error, index) => (
                                <li key={index}>• {error}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        <div className="mt-4 flex space-x-2">
                          <Link href={`/projects/${project.id}/workflows/${workflow.session_id}`}>
                            <Button variant="outline" size="sm">
                              View Details
                            </Button>
                          </Link>
                          {workflow.is_active && (
                            <Button variant="outline" size="sm">
                              Continue Workflow
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="requirements" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Requirements</CardTitle>
              <CardDescription>
                View extracted and structured requirements from your documents
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-slate-600">
                Requirements will appear here once a workflow has been completed.
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="architecture" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Architecture</CardTitle>
              <CardDescription>
                View generated system architectures and C4 diagrams
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-slate-600">
                Architecture designs will appear here once a workflow has been completed.
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
