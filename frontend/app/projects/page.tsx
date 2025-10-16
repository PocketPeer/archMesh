'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Project, ProjectCreate } from '@/types';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { 
  PlusIcon, 
  SearchIcon, 
  FilterIcon, 
  BuildingIcon, 
  ClockIcon, 
  CheckCircleIcon,
  AlertCircleIcon,
  PlayIcon,
  CloudIcon,
  DatabaseIcon,
  BriefcaseIcon,
  ArrowRightIcon
} from 'lucide-react';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [domainFilter, setDomainFilter] = useState<string>('all');
  const [newProject, setNewProject] = useState<ProjectCreate>({
    name: '',
    description: '',
    domain: 'cloud-native'
  });

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    filterProjects();
  }, [projects, searchTerm, statusFilter, domainFilter]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await apiClient.listProjects();
      setProjects(response.items || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
      toast.error('Failed to load projects');
      setProjects([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const filterProjects = () => {
    let filtered = projects;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(project =>
        project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(project => project.status === statusFilter);
    }

    // Domain filter
    if (domainFilter !== 'all') {
      filtered = filtered.filter(project => project.domain === domainFilter);
    }

    setFilteredProjects(filtered);
  };

  const handleCreateProject = async () => {
    try {
      if (!newProject.name.trim()) {
        toast.error('Project name is required');
        return;
      }

      const project = await apiClient.createProject(newProject);
      setProjects(prev => [project, ...prev]);
      setNewProject({ name: '', description: '', domain: 'cloud-native' });
      setIsCreateDialogOpen(false);
      toast.success('Project created successfully');
    } catch (error) {
      console.error('Failed to create project:', error);
      toast.error('Failed to create project');
    }
  };

  const getStatusBadge = (status: Project['status']) => {
    const variants = {
      pending: 'secondary',
      processing: 'default',
      completed: 'default',
      failed: 'destructive'
    } as const;

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
      <Badge className={`${colors[status]} border`} variant={variants[status]}>
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

  const getDomainIcon = (domain: Project['domain']) => {
    switch (domain) {
      case 'cloud-native': return '☁️';
      case 'data-platform': return '📊';
      case 'enterprise': return '🏢';
      default: return '🔧';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="container mx-auto px-4 py-8">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="h-8 bg-slate-200 rounded w-48 mb-2 animate-pulse"></div>
                <div className="h-4 bg-slate-200 rounded w-64 animate-pulse"></div>
              </div>
              <div className="h-10 bg-slate-200 rounded w-32 animate-pulse"></div>
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="h-5 bg-slate-200 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-slate-200 rounded w-1/2"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-3 bg-slate-200 rounded w-full mb-2"></div>
                    <div className="h-3 bg-slate-200 rounded w-2/3 mb-4"></div>
                    <div className="flex justify-between items-center">
                      <div className="h-6 bg-slate-200 rounded w-16"></div>
                      <div className="h-6 bg-slate-200 rounded w-20"></div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
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
            <div>
              <h1 className="text-4xl font-bold text-slate-900 mb-2">Projects</h1>
              <p className="text-xl text-slate-600">
                Manage your architecture projects and track their progress
              </p>
            </div>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <PlusIcon className="mr-2 h-5 w-5" />
                  Create Project
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Create New Project</DialogTitle>
                  <DialogDescription>
                    Create a new project to start the architecture design process.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-2 block">Project Name</label>
                    <Input
                      value={newProject.name}
                      onChange={(e) => setNewProject(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter project name"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-2 block">Description</label>
                    <Textarea
                      value={newProject.description}
                      onChange={(e) => setNewProject(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Enter project description (optional)"
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-2 block">Domain</label>
                    <select
                      value={newProject.domain}
                      onChange={(e) => setNewProject(prev => ({ ...prev, domain: e.target.value as Project['domain'] }))}
                      className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="cloud-native">☁️ Cloud-Native</option>
                      <option value="data-platform">📊 Data Platform</option>
                      <option value="enterprise">🏢 Enterprise</option>
                    </select>
                  </div>
                  <div className="flex justify-end space-x-2 pt-4">
                    <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleCreateProject} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                      Create Project
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Filters */}
          <Card className="border-0 shadow-md">
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                      placeholder="Search projects..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex items-center gap-2">
                    <FilterIcon className="h-4 w-4 text-slate-500" />
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                      className="px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    >
                      <option value="all">All Status</option>
                      <option value="pending">Pending</option>
                      <option value="processing">Processing</option>
                      <option value="completed">Completed</option>
                      <option value="failed">Failed</option>
                    </select>
                  </div>
                  <select
                    value={domainFilter}
                    onChange={(e) => setDomainFilter(e.target.value)}
                    className="px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  >
                    <option value="all">All Domains</option>
                    <option value="cloud-native">Cloud-Native</option>
                    <option value="data-platform">Data Platform</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Projects Grid */}
          {filteredProjects.length === 0 ? (
            <Card className="border-2 border-dashed border-slate-300">
              <CardContent className="text-center py-16">
                <BuildingIcon className="h-16 w-16 text-slate-400 mx-auto mb-6" />
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  {projects.length === 0 ? 'No projects yet' : 'No projects match your filters'}
                </h3>
                <p className="text-slate-600 mb-6">
                  {projects.length === 0 
                    ? 'Create your first project to get started with ArchMesh'
                    : 'Try adjusting your search or filter criteria'
                  }
                </p>
                {projects.length === 0 ? (
                  <Button 
                    onClick={() => setIsCreateDialogOpen(true)}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    <PlusIcon className="mr-2 h-4 w-4" />
                    Create Your First Project
                  </Button>
                ) : (
                  <Button 
                    onClick={() => {
                      setSearchTerm('');
                      setStatusFilter('all');
                      setDomainFilter('all');
                    }}
                    variant="outline"
                  >
                    Clear Filters
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredProjects.map((project) => (
                <Link key={project.id} href={`/projects/${project.id}`}>
                  <Card className="hover:shadow-xl transition-all duration-300 cursor-pointer border-0 shadow-md hover:scale-105 group">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center">
                          <span className="text-3xl mr-3">{getDomainIcon(project.domain)}</span>
                          <div>
                            <CardTitle className="text-lg text-slate-900 group-hover:text-blue-600 transition-colors">
                              {project.name}
                            </CardTitle>
                            <CardDescription className="text-sm text-slate-500">
                              {project.domain.replace('-', ' ').toUpperCase()}
                            </CardDescription>
                          </div>
                        </div>
                        {getStatusBadge(project.status)}
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <p className="text-slate-600 text-sm mb-4 line-clamp-2">
                        {project.description || 'No description provided'}
                      </p>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-500">Domain:</span>
                          {getDomainBadge(project.domain)}
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-500">Created:</span>
                          <span className="text-xs text-slate-900">
                            {new Date(project.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="pt-2">
                          <Button className="w-full" variant="outline" size="sm">
                            View Project
                            <ArrowRightIcon className="ml-2 h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}

          {/* Stats */}
          {projects.length > 0 && (
            <Card className="border-0 shadow-md">
              <CardContent className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                  <div>
                    <div className="text-2xl font-bold text-slate-900">{projects.length}</div>
                    <div className="text-sm text-slate-600">Total Projects</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      {projects.filter(p => p.status === 'processing').length}
                    </div>
                    <div className="text-sm text-slate-600">In Progress</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600">
                      {projects.filter(p => p.status === 'completed').length}
                    </div>
                    <div className="text-sm text-slate-600">Completed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-slate-900">
                      {projects.filter(p => p.status === 'pending').length}
                    </div>
                    <div className="text-sm text-slate-600">Pending</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}