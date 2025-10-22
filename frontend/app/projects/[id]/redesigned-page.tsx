'use client';

import { useState, useEffect } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { Project, WorkflowSession, WorkflowStatus, TeamMember, Notification } from '@/types';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/src/contexts/AuthContext';
import { toast } from 'sonner';
import ProjectHeader from '@/components/ProjectHeader';
import WorkflowDashboard from '@/components/WorkflowDashboard';
import ResultsSection from '@/components/ResultsSection';
import CollaborationSection from '@/components/CollaborationSection';

export default function RedesignedProjectDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const projectId = params.id as string;
  const workflowId = searchParams.get('workflow');
  
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

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    
    if (projectId) {
      loadProject();
      loadWorkflows();
      loadNotifications();
      loadTeamMembers();
    }
  }, [projectId, isAuthenticated, router]);

  useEffect(() => {
    if (workflowId) {
      loadCurrentWorkflow();
      // Set up polling for real-time updates
      const interval = setInterval(() => {
        if (currentWorkflow?.current_stage !== 'completed' && currentWorkflow?.current_stage !== 'failed') {
          loadCurrentWorkflow();
        }
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [workflowId, currentWorkflow?.current_stage]);

  // Set up polling for workflow list updates
  useEffect(() => {
    const interval = setInterval(() => {
      loadWorkflows();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

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
      const workflowsData = await apiClient.listWorkflows(projectId);
      setWorkflows(workflowsData.items || []);
      
      // Load results from the most recent completed workflow
      const completedWorkflows = workflowsData.items?.filter(w => w.current_stage === 'completed');
      if (completedWorkflows && completedWorkflows.length > 0) {
        const latestWorkflow = completedWorkflows[0];
        await loadWorkflowResults(latestWorkflow.session_id);
      }
    } catch (error) {
      console.error('Failed to load workflows:', error);
    }
  };

  const loadCurrentWorkflow = async () => {
    if (!workflowId) return;
    
    try {
      const workflowData = await apiClient.getWorkflow(workflowId);
      setCurrentWorkflow(workflowData);
    } catch (error) {
      console.error('Failed to load current workflow:', error);
    }
  };

  const loadWorkflowResults = async (workflowId: string) => {
    try {
      const results = await apiClient.getWorkflowResults(workflowId);
      setWorkflowResults(results);
    } catch (error) {
      console.error('Failed to load workflow results:', error);
    }
  };

  const loadNotifications = async () => {
    try {
      // Mock notifications for now
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
  };

  const loadTeamMembers = async () => {
    try {
      // Mock team members for now
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
  };

  const handleStartWorkflow = () => {
    router.push(`/projects/${projectId}/upload`);
  };

  const handleSettings = () => {
    // Implement settings functionality
    toast.info('Settings functionality coming soon');
  };

  const handleExport = () => {
    // Implement export functionality
    toast.info('Export functionality coming soon');
  };

  const handleWorkflowAction = (action: string, workflowId: string) => {
    switch (action) {
      case 'retry':
        router.push(`/projects/${projectId}/upload?retry=${workflowId}`);
        break;
      default:
        console.log('Workflow action:', action, workflowId);
    }
  };

  const handleRefine = (type: string) => {
    toast.info(`Refining ${type}...`);
  };

  const handleExportResults = (type: string) => {
    toast.info(`Exporting ${type}...`);
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

  if (!project) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-slate-900 mb-4">Project Not Found</h1>
          <p className="text-slate-600 mb-6">The project you're looking for doesn't exist or you don't have access to it.</p>
          <button 
            onClick={() => router.push('/projects')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Back to Projects
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Project Header */}
          <ProjectHeader
            project={project}
            workflows={workflows}
            onStartWorkflow={handleStartWorkflow}
            onSettings={handleSettings}
            onExport={handleExport}
          />

          {/* Workflow Dashboard */}
          <WorkflowDashboard
            currentWorkflow={currentWorkflow}
            workflows={workflows}
            onWorkflowAction={handleWorkflowAction}
          />

          {/* Results & Outputs */}
          <ResultsSection
            workflowResults={workflowResults}
            projectId={projectId}
            onRefine={handleRefine}
            onExport={handleExportResults}
            onShare={handleShareResults}
          />

          {/* Collaboration & Tools */}
          <CollaborationSection
            teamMembers={teamMembers}
            notifications={notifications}
            onTeamAction={handleTeamAction}
            onNotificationAction={handleNotificationAction}
          />
        </div>
      </div>
    </div>
  );
}
