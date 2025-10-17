/**
 * ProjectCard component for displaying project information.
 */

import React from 'react';
import { Project } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ProjectCardProps {
  project: Project;
  onView?: (project: Project) => void;
  onEdit?: (project: Project) => void;
  onDelete?: (project: Project) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onView,
  onEdit,
  onDelete
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'cloud-native':
        return '☁️';
      case 'microservices':
        return '🔧';
      case 'monolith':
        return '🏗️';
      case 'serverless':
        return '⚡';
      default:
        return '📋';
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{getDomainIcon(project.domain)}</span>
            <CardTitle className="text-lg">{project.name}</CardTitle>
          </div>
          <Badge className={getStatusColor(project.status)}>
            {project.status}
          </Badge>
        </div>
        <CardDescription>{project.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>Domain:</span>
            <Badge variant="outline">{project.domain}</Badge>
          </div>
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>Created:</span>
            <span>{new Date(project.created_at).toLocaleDateString()}</span>
          </div>
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>Updated:</span>
            <span>{new Date(project.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="flex space-x-2 mt-4">
          {onView && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onView(project)}
              className="flex-1"
            >
              View
            </Button>
          )}
          {onEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onEdit(project)}
              className="flex-1"
            >
              Edit
            </Button>
          )}
          {onDelete && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => onDelete(project)}
              className="flex-1"
            >
              Delete
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
