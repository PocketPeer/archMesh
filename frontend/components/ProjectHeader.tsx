'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeftIcon, 
  UploadIcon, 
  SettingsIcon, 
  DownloadIcon,
  CalendarIcon,
  UserIcon,
  ActivityIcon,
  CheckCircleIcon,
  ClockIcon,
  AlertCircleIcon,
  BuildingIcon
} from 'lucide-react';
import { Project, WorkflowSession } from '@/types';

interface ProjectHeaderProps {
  project: Project;
  workflows: WorkflowSession[];
  onStartWorkflow: () => void;
  onSettings: () => void;
  onExport: () => void;
}

export default function ProjectHeader({ 
  project, 
  workflows, 
  onStartWorkflow, 
  onSettings, 
  onExport 
}: ProjectHeaderProps) {
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
    <div className="space-y-6">
      {/* Navigation */}
      <div className="flex items-center justify-between">
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
          <Button variant="outline" size="sm" onClick={onSettings}>
            <SettingsIcon className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Button variant="outline" size="sm" onClick={onExport}>
            <DownloadIcon className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Project Header */}
      <Card className="border-0 shadow-lg">
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

              <div className="flex items-center space-x-6 text-sm text-slate-600">
                <div className="flex items-center space-x-1">
                  <CalendarIcon className="h-4 w-4" />
                  <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <UserIcon className="h-4 w-4" />
                  <span>Owner</span>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900">Project Statistics</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-slate-50 rounded-lg">
                  <div className="text-2xl font-bold text-slate-900">{workflows.length}</div>
                  <div className="text-sm text-slate-600">Total Workflows</div>
                </div>
                <div className="text-center p-3 bg-slate-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{completedWorkflows}</div>
                  <div className="text-sm text-slate-600">Completed</div>
                </div>
                <div className="text-center p-3 bg-slate-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{activeWorkflows}</div>
                  <div className="text-sm text-slate-600">Active</div>
                </div>
                <div className="text-center p-3 bg-slate-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{failedWorkflows}</div>
                  <div className="text-sm text-slate-600">Failed</div>
                </div>
              </div>
            </div>

            {/* Primary Actions */}
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900">Quick Actions</h3>
              <div className="space-y-3">
                <Button 
                  onClick={onStartWorkflow}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <UploadIcon className="h-4 w-4 mr-2" />
                  Start New Workflow
                </Button>
                
                {project.repository_url && (
                  <Button variant="outline" className="w-full">
                    <ActivityIcon className="h-4 w-4 mr-2" />
                    View Repository
                  </Button>
                )}
                
                <Button variant="outline" className="w-full">
                  <SettingsIcon className="h-4 w-4 mr-2" />
                  Project Settings
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
