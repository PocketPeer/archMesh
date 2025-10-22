'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { Project, WorkflowSession, WorkflowStatus, TeamMember, Notification } from '@/types';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/src/contexts/AuthContext';
import { toast } from 'sonner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeftIcon, 
  SettingsIcon, 
  DownloadIcon, 
  UploadIcon,
  BuildingIcon,
  FileTextIcon,
  UsersIcon,
  BellIcon,
  ActivityIcon,
  CheckCircleIcon,
  ClockIcon,
  AlertCircleIcon,
  RefreshCwIcon,
  EyeIcon,
  ShareIcon,
  PlusIcon
} from 'lucide-react';
import Link from 'next/link';

export default function ProjectDetailPageRefactored() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const projectId = params.id as string;
  const workflowId = searchParams.get('workflow');
  
  // State management
  const [project, setProject] = useState<Project | null>(null);
  const [workflows, setWorkflows] = useState<WorkflowSession[]>([]);
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowStatus | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [workflowResults, setWorkflowResults] = useState<{
    requirements: any;
    architecture: any;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Load project data
  const loadProject = useCallback(async () => {
    if (!projectId) return;
    
    try {
      const projectData = await apiClient.getProject(projectId);
      setProject(projectData);
    } catch (error: any) {
      console.error('Failed to load project:', error);
      if (error.message?.includes('Unauthorized') || error.message?.includes('Not authenticated')) {
        router.push('/login');
        return;
      }
      toast.error('Failed to load project');
    }
  }, [projectId, router]);

  // Load workflows
  const loadWorkflows = useCallback(async () => {
    if (!projectId) return;
    
    try {
      const workflowsData = await apiClient.listWorkflows(0, 10, projectId);
      setWorkflows(workflowsData.workflows || []);
    } catch (error) {
      console.error('Failed to load workflows:', error);
    }
  }, [projectId]);

  // Load current workflow
  const loadCurrentWorkflow = useCallback(async () => {
    if (!workflowId) return;
    
    try {
      const workflowData = await apiClient.getWorkflow(workflowId);
      const workflowStatus: WorkflowStatus = {
        session_id: workflowData.session_id,
        project_id: workflowData.project_id,
        current_stage: workflowData.current_stage,
        errors: workflowData.state_data?.errors || []
      };
      setCurrentWorkflow(workflowStatus);
    } catch (error) {
      console.error('Failed to load current workflow:', error);
    }
  }, [workflowId]);

  // Load workflow results
  const loadWorkflowResults = useCallback(async (workflowId: string) => {
    try {
      // Try to get real results first
      try {
        const requirements = await apiClient.getRequirements(projectId);
        const architecture = await apiClient.getArchitecture(projectId);
        setWorkflowResults({ requirements, architecture });
      } catch {
        // Fallback to mock data if API doesn't exist yet
        const mockResults = {
          requirements: {
            functional_requirements: [
              "User authentication and authorization",
              "Data processing and analysis", 
              "Real-time notifications"
            ],
            non_functional_requirements: [
              "System must handle 1000+ concurrent users",
              "Response time should be under 200ms",
              "99.9% uptime requirement"
            ]
          },
          architecture: {
            components: [
              { name: "API Gateway", description: "Entry point for all requests", technology: "Kong" },
              { name: "Authentication Service", description: "Handles user auth", technology: "Auth0" },
              { name: "Database", description: "Primary data storage", technology: "PostgreSQL" }
            ],
            technology_stack: {
              backend: { language: "Python", framework: "FastAPI" },
              frontend: { language: "TypeScript", framework: "Next.js" },
              database: { primary: "PostgreSQL", cache: "Redis" }
            }
          }
        };
        setWorkflowResults(mockResults);
      }
    } catch (error) {
      console.error('Failed to load workflow results:', error);
    }
  }, [projectId]);

  // Load notifications
  const loadNotifications = useCallback(async () => {
    try {
      // Mock notifications for now - replace with real API call
      setNotifications([
        {
          id: '1',
          title: 'Workflow Completed',
          message: 'Requirements analysis workflow has been completed successfully',
          type: 'success',
          read: false,
          timestamp: new Date().toISOString()
        },
        {
          id: '2',
          title: 'Team Member Added',
          message: 'John Doe has been added to the project team',
          type: 'info',
          read: false,
          timestamp: new Date(Date.now() - 3600000).toISOString()
        }
      ]);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  }, []);

  // Load team members
  const loadTeamMembers = useCallback(async () => {
    try {
      // Mock team members for now - replace with real API call
      setTeamMembers([
        {
          id: '1',
          name: 'Current User',
          email: 'user@example.com',
          role: 'owner',
          avatar: null
        },
        {
          id: '2',
          name: 'John Doe',
          email: 'john@example.com',
          role: 'collaborator',
          avatar: null
        }
      ]);
    } catch (error) {
      console.error('Failed to load team members:', error);
    }
  }, []);

  // Initialize data loading
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    
    if (projectId) {
      const loadAllData = async () => {
        setLoading(true);
        try {
          await Promise.all([
            loadProject(),
            loadWorkflows(),
            loadNotifications(),
            loadTeamMembers()
          ]);
        } finally {
          setLoading(false);
        }
      };
      loadAllData();
    }
  }, [projectId, isAuthenticated, router, loadProject, loadWorkflows, loadNotifications, loadTeamMembers]);

  // Load current workflow when workflowId changes
  useEffect(() => {
    if (workflowId) {
      loadCurrentWorkflow();
      loadWorkflowResults(workflowId);
    }
  }, [workflowId, loadCurrentWorkflow, loadWorkflowResults]);

  // Event handlers
  const handleStartWorkflow = () => {
    router.push(`/projects/${projectId}/upload`);
  };

  const handleSettings = () => {
    toast.info('Settings functionality coming soon');
  };

  const handleExport = async () => {
    try {
      // Implement comprehensive export functionality
      const exportData = {
        project: project,
        workflows: workflows,
        results: workflowResults,
        timestamp: new Date().toISOString()
      };
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project?.name || 'project'}-export.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success('Project exported successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Export failed. Please try again.');
    }
  };

  const handleWorkflowAction = (action: string, workflowId: string) => {
    switch (action) {
      case 'retry':
        router.push(`/projects/${projectId}/upload?retry=${workflowId}`);
        break;
      case 'view':
        router.push(`/projects/${projectId}?workflow=${workflowId}`);
        break;
      default:
        console.log('Workflow action:', action, workflowId);
    }
  };

  const handleRefine = (type: string) => {
    toast.info(`Refining ${type}...`);
  };

  const handleShareResults = (type: string) => {
    toast.info(`Sharing ${type}...`);
  };

  const handleTeamAction = (action: string, memberId?: string) => {
    switch (action) {
      case 'invite':
        toast.info('Invite member functionality coming soon');
        break;
      case 'settings':
        toast.info('Member settings functionality coming soon');
        break;
      default:
        console.log('Team action:', action, memberId);
    }
  };

  const handleNotificationAction = (action: string, notificationId: string) => {
    switch (action) {
      case 'mark-all-read':
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
        break;
      case 'dismiss':
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
        break;
      default:
        console.log('Notification action:', action, notificationId);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading project...</p>
        </div>
      </div>
    );
  }

  // Project not found
  if (!project) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-900 mb-4">Project Not Found</h1>
          <p className="text-slate-600 mb-6">The project you're looking for doesn't exist or you don't have access to it.</p>
          <Button onClick={() => router.push('/projects')}>
            Back to Projects
          </Button>
        </div>
      </div>
    );
  }

  // Calculate statistics
  const completedWorkflows = workflows.filter(w => w.current_stage === 'completed').length;
  const activeWorkflows = workflows.filter(w => w.current_stage !== 'completed' && w.current_stage !== 'failed').length;
  const failedWorkflows = workflows.filter(w => w.current_stage === 'failed').length;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'processing': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'failed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon className="h-4 w-4" />;
      case 'processing': return <ClockIcon className="h-4 w-4" />;
      case 'failed': return <AlertCircleIcon className="h-4 w-4" />;
      default: return <ActivityIcon className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-6">
          <Link href="/projects" className="flex items-center space-x-2 text-slate-600 hover:text-slate-900">
            <ArrowLeftIcon className="h-4 w-4" />
            <span>Back to Projects</span>
          </Link>
          <div className="flex items-center space-x-2">
            <Link href={`/projects/${project.id}/architecture`}>
              <Button variant="outline" size="sm">
                <BuildingIcon className="h-4 w-4 mr-2" />
                Architecture
              </Button>
            </Link>
            <Link href={`/projects/${project.id}/diagrams`}>
              <Button variant="outline" size="sm">
                <BuildingIcon className="h-4 w-4 mr-2" />
                Diagrams
              </Button>
            </Link>
            <Button variant="outline" size="sm" onClick={handleSettings}>
              <SettingsIcon className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Button variant="outline" size="sm" onClick={handleExport}>
              <DownloadIcon className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Project Header */}
        <Card className="border-0 shadow-lg mb-8">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Project Information */}
              <div className="space-y-4">
                <div>
                  <h1 className="text-2xl font-bold text-slate-900 mb-2">{project.name}</h1>
                  <p className="text-slate-600">{project.description}</p>
                </div>
                <div className="flex items-center space-x-4">
                  <Badge className={getStatusColor(project.status)}>
                    {getStatusIcon(project.status)}
                    <span className="ml-1">{project.status.toUpperCase()}</span>
                  </Badge>
                  <Badge variant="outline" className="capitalize">
                    {project.domain}
                  </Badge>
                  <Badge variant="outline" className="capitalize">
                    {project.mode}
                  </Badge>
                </div>
              </div>

              {/* Workflow Statistics */}
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-slate-800">Workflow Statistics</h2>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                    <CheckCircleIcon className="h-6 w-6 text-green-500 mx-auto mb-2" />
                    <p className="text-xl font-bold">{completedWorkflows}</p>
                    <p className="text-sm text-slate-500">Completed</p>
                  </div>
                  <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                    <ClockIcon className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                    <p className="text-xl font-bold">{activeWorkflows}</p>
                    <p className="text-sm text-slate-500">Active</p>
                  </div>
                  <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                    <AlertCircleIcon className="h-6 w-6 text-red-500 mx-auto mb-2" />
                    <p className="text-xl font-bold">{failedWorkflows}</p>
                    <p className="text-sm text-slate-500">Failed</p>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col justify-center items-end space-y-4">
                <Button className="w-full lg:w-auto" onClick={handleStartWorkflow}>
                  <UploadIcon className="h-4 w-4 mr-2" />
                  Start New Workflow
                </Button>
                <Button variant="secondary" className="w-full lg:w-auto">
                  View All Workflows
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="workflows">Workflows</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
            <TabsTrigger value="collaboration">Collaboration</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Current Workflow Status */}
              {currentWorkflow && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ActivityIcon className="h-5 w-5" />
                      Current Workflow
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Status</span>
                        <Badge className={getStatusColor(currentWorkflow.current_stage)}>
                          {getStatusIcon(currentWorkflow.current_stage)}
                          <span className="ml-1">{currentWorkflow.current_stage}</span>
                        </Badge>
                      </div>
                      {currentWorkflow.errors.length > 0 && (
                        <div className="text-sm text-red-600">
                          <strong>Errors:</strong>
                          <ul className="list-disc list-inside mt-1">
                            {currentWorkflow.errors.map((error, index) => (
                              <li key={index}>{error}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Quick Actions */}
              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full justify-start" onClick={handleStartWorkflow}>
                    <UploadIcon className="h-4 w-4 mr-2" />
                    Start New Workflow
                  </Button>
                  <Button variant="outline" className="w-full justify-start" onClick={handleExport}>
                    <DownloadIcon className="h-4 w-4 mr-2" />
                    Export Project
                  </Button>
                  <Link href={`/projects/${project.id}/architecture`} className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <BuildingIcon className="h-4 w-4 mr-2" />
                      View Architecture
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Workflows Tab */}
          <TabsContent value="workflows" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Workflow History</CardTitle>
              </CardHeader>
              <CardContent>
                {workflows.length === 0 ? (
                  <div className="text-center py-8">
                    <ActivityIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">No workflows yet</p>
                    <Button onClick={handleStartWorkflow}>
                      <PlusIcon className="h-4 w-4 mr-2" />
                      Start First Workflow
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {workflows.map((workflow) => (
                      <div key={workflow.session_id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <Badge className={getStatusColor(workflow.current_stage)}>
                            {getStatusIcon(workflow.current_stage)}
                            <span className="ml-1">{workflow.current_stage}</span>
                          </Badge>
                          <div>
                            <p className="font-medium">Workflow {workflow.session_id.slice(0, 8)}</p>
                            <p className="text-sm text-gray-600">
                              Started: {new Date(workflow.started_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleWorkflowAction('view', workflow.session_id)}
                          >
                            <EyeIcon className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          {workflow.current_stage === 'failed' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleWorkflowAction('retry', workflow.session_id)}
                            >
                              <RefreshCwIcon className="h-4 w-4 mr-1" />
                              Retry
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="space-y-6">
            {workflowResults ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Requirements */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileTextIcon className="h-5 w-5" />
                      Requirements
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">Functional Requirements</h4>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          {workflowResults.requirements?.functional_requirements?.map((req: string, index: number) => (
                            <li key={index}>{req}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Non-Functional Requirements</h4>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          {workflowResults.requirements?.non_functional_requirements?.map((req: string, index: number) => (
                            <li key={index}>{req}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Architecture */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BuildingIcon className="h-5 w-5" />
                      Architecture
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">Components</h4>
                        <div className="space-y-2">
                          {workflowResults.architecture?.components?.map((component: any, index: number) => (
                            <div key={index} className="p-3 bg-gray-50 rounded-lg">
                              <p className="font-medium text-sm">{component.name}</p>
                              <p className="text-xs text-gray-600">{component.description}</p>
                              <p className="text-xs text-blue-600">{component.technology}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <FileTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No results available yet</p>
                  <p className="text-sm text-gray-500">Start a workflow to generate requirements and architecture</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Collaboration Tab */}
          <TabsContent value="collaboration" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Team Members */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UsersIcon className="h-5 w-5" />
                    Team Members
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {teamMembers.map((member) => (
                      <div key={member.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">{member.name}</p>
                          <p className="text-sm text-gray-600">{member.email}</p>
                        </div>
                        <Badge variant="outline" className="capitalize">
                          {member.role}
                        </Badge>
                      </div>
                    ))}
                    <Button variant="outline" className="w-full" onClick={() => handleTeamAction('invite')}>
                      <PlusIcon className="h-4 w-4 mr-2" />
                      Invite Member
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Notifications */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BellIcon className="h-5 w-5" />
                    Notifications
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {notifications.map((notification) => (
                      <div key={notification.id} className={`p-3 border rounded-lg ${!notification.read ? 'bg-blue-50' : ''}`}>
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium text-sm">{notification.title}</p>
                            <p className="text-xs text-gray-600">{notification.message}</p>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {notification.type}
                          </Badge>
                        </div>
                      </div>
                    ))}
                    <Button variant="outline" className="w-full" onClick={() => handleNotificationAction('mark-all-read', '')}>
                      Mark All as Read
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
