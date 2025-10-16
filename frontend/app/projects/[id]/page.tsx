'use client';

import { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Project, WorkflowSession, WorkflowStatus } from '@/types';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { 
  ArrowLeftIcon, 
  UploadIcon, 
  PlayIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  AlertCircleIcon,
  BuildingIcon,
  FileTextIcon,
  SettingsIcon,
  CalendarIcon,
  UserIcon,
  ActivityIcon,
  BarChart3Icon,
  CloudIcon,
  DatabaseIcon,
  BriefcaseIcon,
  ArrowRightIcon,
  EyeIcon,
  RefreshCwIcon
} from 'lucide-react';

export default function ProjectDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const projectId = params.id as string;
  const workflowId = searchParams.get('workflow');
  
  const [project, setProject] = useState<Project | null>(null);
  const [workflows, setWorkflows] = useState<WorkflowSession[]>([]);
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowStatus | null>(null);
  const [workflowResults, setWorkflowResults] = useState<{
    requirements: any;
    architecture: any;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      loadProject();
      loadWorkflows();
    }
  }, [projectId]);

  useEffect(() => {
    if (workflowId) {
      loadCurrentWorkflow();
      // Set up polling for real-time updates
      const interval = setInterval(() => {
        if (currentWorkflow?.current_stage !== 'completed' && currentWorkflow?.current_stage !== 'failed') {
          loadCurrentWorkflow();
        }
      }, 5000); // Poll every 5 seconds
      
      return () => clearInterval(interval);
    }
  }, [workflowId, currentWorkflow?.current_stage]);

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

  const loadCurrentWorkflow = async () => {
    if (!workflowId) return;
    
    try {
      const workflowStatus = await apiClient.getWorkflowStatus(workflowId);
      setCurrentWorkflow(workflowStatus);
      
      // Update workflows list to reflect current status
      setWorkflows(prev => prev.map(w => 
        w.id === workflowId 
          ? { ...w, current_stage: workflowStatus.current_stage, status: workflowStatus.current_stage }
          : w
      ));

      // Load workflow results if completed
      if (workflowStatus.current_stage === 'completed') {
        await loadWorkflowResults(workflowId);
      }
    } catch (error) {
      console.error('Failed to load current workflow:', error);
    }
  };

  const loadWorkflowResults = async (sessionId: string) => {
    try {
      const [requirements, architecture] = await Promise.all([
        apiClient.getRequirements(sessionId).catch(() => null),
        apiClient.getArchitecture(sessionId).catch(() => null)
      ]);
      
      setWorkflowResults({
        requirements,
        architecture
      });
    } catch (error) {
      console.error('Failed to load workflow results:', error);
    }
  };

  const getStatusBadge = (status: Project['status']) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      processing: 'bg-blue-100 text-blue-800 border-blue-200',
      completed: 'bg-green-100 text-green-800 border-green-200',
      failed: 'bg-red-100 text-red-800 border-red-200'
    };

    const icons = {
      pending: <ClockIcon className="h-3 w-3 mr-1" />,
      processing: <PlayIcon className="h-3 w-3 mr-1" />,
      completed: <CheckCircleIcon className="h-3 w-3 mr-1" />,
      failed: <AlertCircleIcon className="h-3 w-3 mr-1" />
    };

    return (
      <Badge className={`${colors[status]} border`}>
        {icons[status]}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getDomainBadge = (domain: Project['domain']) => {
    const colors = {
      'cloud-native': 'bg-blue-100 text-blue-800 border-blue-200',
      'data-platform': 'bg-purple-100 text-purple-800 border-purple-200',
      'enterprise': 'bg-green-100 text-green-800 border-green-200'
    };

    const icons = {
      'cloud-native': <CloudIcon className="h-3 w-3 mr-1" />,
      'data-platform': <DatabaseIcon className="h-3 w-3 mr-1" />,
      'enterprise': <BriefcaseIcon className="h-3 w-3 mr-1" />
    };

    return (
      <Badge className={`${colors[domain]} border`}>
        {icons[domain]}
        {domain.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </Badge>
    );
  };

  const getWorkflowStatusBadge = (stage: string) => {
    const colors = {
      'starting': 'bg-gray-100 text-gray-800 border-gray-200',
      'document_analysis': 'bg-blue-100 text-blue-800 border-blue-200',
      'requirements_review': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'architecture_design': 'bg-purple-100 text-purple-800 border-purple-200',
      'architecture_review': 'bg-orange-100 text-orange-800 border-orange-200',
      'completed': 'bg-green-100 text-green-800 border-green-200',
      'failed': 'bg-red-100 text-red-800 border-red-200'
    };

    return (
      <Badge className={`${colors[stage as keyof typeof colors] || 'bg-gray-100 text-gray-800 border-gray-200'} border`}>
        {stage.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </Badge>
    );
  };

  const getDomainIcon = (domain: Project['domain']) => {
    switch (domain) {
      case 'cloud-native': return '☁️';
      case 'data-platform': return '📊';
      case 'enterprise': return '🏢';
      default: return '🔧';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress < 30) return 'bg-red-500';
    if (progress < 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="container mx-auto px-4 py-8">
          <div className="space-y-6">
            <div className="animate-pulse">
              <div className="h-8 bg-slate-200 rounded w-1/3 mb-4"></div>
              <div className="h-4 bg-slate-200 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircleIcon className="h-16 w-16 text-slate-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-slate-900 mb-4">Project Not Found</h1>
          <p className="text-slate-600 mb-6">The project you're looking for doesn't exist.</p>
          <Link href="/projects">
            <Button>
              <ArrowLeftIcon className="mr-2 h-4 w-4" />
              Back to Projects
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Header */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="flex items-center space-x-4">
              <Link href="/projects">
                <Button variant="outline" size="sm">
                  <ArrowLeftIcon className="mr-2 h-4 w-4" />
                  Back
                </Button>
              </Link>
              <div>
                <div className="flex items-center space-x-4 mb-2">
                  <span className="text-4xl">{getDomainIcon(project.domain)}</span>
                  <h1 className="text-4xl font-bold text-slate-900">{project.name}</h1>
                </div>
                <div className="flex items-center space-x-3 mb-2">
                  {getStatusBadge(project.status)}
                  {getDomainBadge(project.domain)}
                </div>
                <p className="text-lg text-slate-600">
                  {project.description || 'No description provided'}
                </p>
              </div>
            </div>
            <div className="flex space-x-3">
              <Link href={`/projects/${project.id}/upload`}>
                <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <UploadIcon className="mr-2 h-5 w-5" />
                  Start Workflow
                </Button>
              </Link>
            </div>
          </div>

          {/* Current Workflow Status */}
          {currentWorkflow && (
            <Card className="border-0 shadow-lg bg-gradient-to-r from-blue-50 to-purple-50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <ActivityIcon className="h-5 w-5 text-blue-600" />
                  <span>Current Workflow Status</span>
                  {currentWorkflow.current_stage !== 'completed' && currentWorkflow.current_stage !== 'failed' && (
                    <RefreshCwIcon className="h-4 w-4 text-blue-600 animate-spin" />
                  )}
                </CardTitle>
                <CardDescription>
                  Real-time updates for workflow session {workflowId}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Badge 
                        className={`${
                          currentWorkflow.current_stage === 'completed' 
                            ? 'bg-green-100 text-green-800 border-green-200'
                            : currentWorkflow.current_stage === 'failed'
                            ? 'bg-red-100 text-red-800 border-red-200'
                            : currentWorkflow.current_stage === 'requirements_review' || currentWorkflow.current_stage === 'architecture_review'
                            ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                            : 'bg-blue-100 text-blue-800 border-blue-200'
                        }`}
                      >
                        {currentWorkflow.current_stage === 'completed' && <CheckCircleIcon className="h-3 w-3 mr-1" />}
                        {currentWorkflow.current_stage === 'failed' && <AlertCircleIcon className="h-3 w-3 mr-1" />}
                        {(currentWorkflow.current_stage === 'requirements_review' || currentWorkflow.current_stage === 'architecture_review') && <ClockIcon className="h-3 w-3 mr-1" />}
                        {!['completed', 'failed', 'requirements_review', 'architecture_review'].includes(currentWorkflow.current_stage) && <PlayIcon className="h-3 w-3 mr-1" />}
                        {currentWorkflow.current_stage.replace('_', ' ').toUpperCase()}
                      </Badge>
                      <span className="text-sm text-slate-600">
                        Progress: {Math.round((currentWorkflow.stage_progress || 0) * 100)}%
                      </span>
                    </div>
                    <Link href={`/projects/${projectId}/workflows/${workflowId}`}>
                      <Button variant="outline" size="sm">
                        <EyeIcon className="mr-2 h-4 w-4" />
                        View Details
                      </Button>
                    </Link>
                  </div>
                  
                  {currentWorkflow.current_stage === 'requirements_review' && (
                    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <ClockIcon className="h-4 w-4 text-yellow-600" />
                        <span className="font-medium text-yellow-800">Requirements Review Required</span>
                      </div>
                      <p className="text-sm text-yellow-700">
                        Please review and approve the extracted requirements before the architecture design begins.
                      </p>
                    </div>
                  )}
                  
                  {currentWorkflow.current_stage === 'architecture_review' && (
                    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        <ClockIcon className="h-4 w-4 text-yellow-600" />
                        <span className="font-medium text-yellow-800">Architecture Review Required</span>
                      </div>
                      <p className="text-sm text-yellow-700">
                        Please review and approve the generated architecture design.
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Workflow Results */}
          {workflowResults && (workflowResults.requirements || workflowResults.architecture) && (
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                  <span>Workflow Results</span>
                </CardTitle>
                <CardDescription>
                  Generated requirements and architecture for this project
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="requirements" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="requirements" className="flex items-center space-x-2">
                      <FileTextIcon className="h-4 w-4" />
                      <span>Requirements</span>
                    </TabsTrigger>
                    <TabsTrigger value="architecture" className="flex items-center space-x-2">
                      <BuildingIcon className="h-4 w-4" />
                      <span>Architecture</span>
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="requirements" className="mt-6">
                    {workflowResults.requirements ? (
                      <div className="space-y-4">
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <h4 className="font-semibold text-slate-900 mb-2">Business Goals</h4>
                          <ul className="list-disc list-inside space-y-1 text-sm text-slate-700">
                            {workflowResults.requirements.structured_requirements?.business_goals?.map((goal: string, index: number) => (
                              <li key={index}>{goal}</li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <h4 className="font-semibold text-slate-900 mb-2">Functional Requirements</h4>
                          <ul className="list-disc list-inside space-y-1 text-sm text-slate-700">
                            {workflowResults.requirements.structured_requirements?.functional_requirements?.map((req: string, index: number) => (
                              <li key={index}>{req}</li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <h4 className="font-semibold text-slate-900 mb-2">Non-Functional Requirements</h4>
                          <div className="space-y-3">
                            {workflowResults.requirements.structured_requirements?.non_functional_requirements && 
                              Object.entries(workflowResults.requirements.structured_requirements.non_functional_requirements).map(([category, requirements]) => (
                                <div key={category}>
                                  <h5 className="font-medium text-slate-800 capitalize">{category}</h5>
                                  <ul className="list-disc list-inside space-y-1 text-sm text-slate-700 ml-4">
                                    {(requirements as string[]).map((req: string, index: number) => (
                                      <li key={index}>{req}</li>
                                    ))}
                                  </ul>
                                </div>
                              ))
                            }
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-slate-500">
                        <FileTextIcon className="h-12 w-12 mx-auto mb-4 text-slate-300" />
                        <p>Requirements not available</p>
                      </div>
                    )}
                  </TabsContent>
                  
                  <TabsContent value="architecture" className="mt-6">
                    {workflowResults.architecture ? (
                      <div className="space-y-4">
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <h4 className="font-semibold text-slate-900 mb-2">Architecture Overview</h4>
                          <p className="text-sm text-slate-700">
                            {workflowResults.architecture.overview || 'No overview available'}
                          </p>
                        </div>
                        
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <h4 className="font-semibold text-slate-900 mb-2">Key Components</h4>
                          <ul className="list-disc list-inside space-y-1 text-sm text-slate-700">
                            {workflowResults.architecture.components?.map((component: any, index: number) => (
                              <li key={index}>
                                <strong>{component.name}:</strong> {component.description}
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div className="p-4 bg-slate-50 rounded-lg">
                          <h4 className="font-semibold text-slate-900 mb-2">Technology Stack</h4>
                          <div className="flex flex-wrap gap-2">
                            {workflowResults.architecture.technology_stack?.map((tech: string, index: number) => (
                              <Badge key={index} variant="secondary">{tech}</Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-slate-500">
                        <BuildingIcon className="h-12 w-12 mx-auto mb-4 text-slate-300" />
                        <p>Architecture not available</p>
                      </div>
                    )}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}

          {/* Project Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Total Workflows</p>
                    <p className="text-2xl font-bold text-slate-900">{workflows.length}</p>
                  </div>
                  <ActivityIcon className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Active Workflows</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {workflows.filter(w => w.is_active).length}
                    </p>
                  </div>
                  <PlayIcon className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Completed</p>
                    <p className="text-2xl font-bold text-green-600">
                      {workflows.filter(w => w.current_stage === 'completed').length}
                    </p>
                  </div>
                  <CheckCircleIcon className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-md">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-600">Created</p>
                    <p className="text-2xl font-bold text-slate-900">
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <CalendarIcon className="h-8 w-8 text-slate-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <Tabs defaultValue="workflows" className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="workflows" className="flex items-center">
                <ActivityIcon className="mr-2 h-4 w-4" />
                Workflows
              </TabsTrigger>
              <TabsTrigger value="requirements" className="flex items-center">
                <FileTextIcon className="mr-2 h-4 w-4" />
                Requirements
              </TabsTrigger>
              <TabsTrigger value="architecture" className="flex items-center">
                <BuildingIcon className="mr-2 h-4 w-4" />
                Architecture
              </TabsTrigger>
            </TabsList>

            <TabsContent value="workflows" className="space-y-6">
              <Card className="border-0 shadow-md">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <ActivityIcon className="mr-2 h-5 w-5" />
                    Workflow Sessions
                  </CardTitle>
                  <CardDescription>
                    Track the progress of your architecture generation workflows
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {workflows.length === 0 ? (
                    <div className="text-center py-16">
                      <div className="h-20 w-20 mx-auto rounded-full bg-slate-100 flex items-center justify-center mb-6">
                        <UploadIcon className="h-10 w-10 text-slate-400" />
                      </div>
                      <h3 className="text-xl font-semibold text-slate-900 mb-2">No workflows yet</h3>
                      <p className="text-slate-600 mb-6 max-w-md mx-auto">
                        Start a new workflow by uploading a requirements document to begin the architecture design process
                      </p>
                      <Link href={`/projects/${project.id}/upload`}>
                        <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                          <UploadIcon className="mr-2 h-5 w-5" />
                          Start Your First Workflow
                        </Button>
                      </Link>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {workflows.map((workflow) => (
                        <Card key={workflow.session_id} className="border-0 shadow-md hover:shadow-lg transition-shadow">
                          <CardContent className="p-6">
                            <div className="flex items-start justify-between mb-4">
                              <div className="flex items-center space-x-4">
                                <div className="h-12 w-12 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                                  <ActivityIcon className="h-6 w-6 text-white" />
                                </div>
                                <div>
                                  <h3 className="text-lg font-semibold text-slate-900">Workflow Session</h3>
                                  <p className="text-sm text-slate-500 font-mono">{workflow.session_id}</p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                {getWorkflowStatusBadge(workflow.current_stage)}
                                <Badge variant={workflow.is_active ? "default" : "secondary"}>
                                  {workflow.is_active ? "Active" : "Inactive"}
                                </Badge>
                              </div>
                            </div>

                            {/* Progress Bar */}
                            <div className="mb-4">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium text-slate-700">Progress</span>
                                <span className="text-sm text-slate-600">
                                  {Math.round(workflow.state_data.stage_progress * 100)}%
                                </span>
                              </div>
                              <div className="w-full bg-slate-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(workflow.state_data.stage_progress * 100)}`}
                                  style={{ width: `${workflow.state_data.stage_progress * 100}%` }}
                                ></div>
                              </div>
                            </div>

                            <div className="grid gap-4 md:grid-cols-3 mb-4">
                              <div className="flex items-center space-x-2">
                                <CalendarIcon className="h-4 w-4 text-slate-400" />
                                <div>
                                  <p className="text-xs text-slate-500">Started</p>
                                  <p className="text-sm text-slate-900">
                                    {new Date(workflow.started_at).toLocaleDateString()}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <ClockIcon className="h-4 w-4 text-slate-400" />
                                <div>
                                  <p className="text-xs text-slate-500">Last Activity</p>
                                  <p className="text-sm text-slate-900">
                                    {new Date(workflow.last_activity_at).toLocaleDateString()}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <BarChart3Icon className="h-4 w-4 text-slate-400" />
                                <div>
                                  <p className="text-xs text-slate-500">Completed Stages</p>
                                  <p className="text-sm text-slate-900">
                                    {workflow.state_data.completed_stages.length}
                                  </p>
                                </div>
                              </div>
                            </div>

                            {workflow.state_data.errors.length > 0 && (
                              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                                <div className="flex items-center mb-2">
                                  <AlertCircleIcon className="h-4 w-4 text-red-600 mr-2" />
                                  <h4 className="text-sm font-medium text-red-800">Errors</h4>
                                </div>
                                <ul className="text-sm text-red-700 space-y-1">
                                  {workflow.state_data.errors.map((error, index) => (
                                    <li key={index}>• {error}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            <div className="flex space-x-3">
                              <Link href={`/projects/${project.id}/workflows/${workflow.session_id}`}>
                                <Button variant="outline" size="sm">
                                  <EyeIcon className="mr-2 h-4 w-4" />
                                  View Details
                                </Button>
                              </Link>
                              {workflow.is_active && (
                                <Button variant="outline" size="sm">
                                  <RefreshCwIcon className="mr-2 h-4 w-4" />
                                  Continue
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

            <TabsContent value="requirements" className="space-y-6">
              <Card className="border-0 shadow-md">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <FileTextIcon className="mr-2 h-5 w-5" />
                    Requirements
                  </CardTitle>
                  <CardDescription>
                    View extracted and structured requirements from your documents
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-16">
                    <FileTextIcon className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">No requirements yet</h3>
                    <p className="text-slate-600 mb-6">
                      Requirements will appear here once a workflow has been completed.
                    </p>
                    <Link href={`/projects/${project.id}/upload`}>
                      <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                        <UploadIcon className="mr-2 h-4 w-4" />
                        Start Workflow
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="architecture" className="space-y-6">
              <Card className="border-0 shadow-md">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BuildingIcon className="mr-2 h-5 w-5" />
                    Architecture
                  </CardTitle>
                  <CardDescription>
                    View generated system architectures and C4 diagrams
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-16">
                    <BuildingIcon className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">No architecture yet</h3>
                    <p className="text-slate-600 mb-6">
                      Architecture designs will appear here once a workflow has been completed.
                    </p>
                    <Link href={`/projects/${project.id}/upload`}>
                      <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                        <UploadIcon className="mr-2 h-4 w-4" />
                        Start Workflow
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Project Details */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <SettingsIcon className="mr-2 h-5 w-5" />
                Project Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <div>
                    <span className="text-sm font-medium text-slate-600">Project ID</span>
                    <p className="text-slate-900 font-mono text-sm bg-slate-100 px-2 py-1 rounded">
                      {project.id}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-slate-600">Created</span>
                    <p className="text-slate-900">
                      {new Date(project.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <span className="text-sm font-medium text-slate-600">Last Updated</span>
                    <p className="text-slate-900">
                      {new Date(project.updated_at).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-slate-600">Status</span>
                    <div className="mt-1">{getStatusBadge(project.status)}</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}