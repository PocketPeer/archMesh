'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Project } from '@/types';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { 
  PlusIcon, 
  ArrowRightIcon, 
  FileTextIcon, 
  BuildingIcon, 
  UsersIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
  ZapIcon,
  ShieldIcon,
  GlobeIcon
} from 'lucide-react';

export default function HomePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await apiClient.listProjects(0, 6); // Get first 6 projects
      setProjects(response.items || []);
    } catch (error) {
      console.error('Failed to load projects:', error);
      toast.error('Failed to load projects');
      setProjects([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      'pending': 'bg-gray-100 text-gray-800',
      'processing': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800'
    };

    return (
      <Badge className={colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'cloud-native': return '☁️';
      case 'data-platform': return '📊';
      case 'enterprise': return '🏢';
      default: return '🔧';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10"></div>
        <div className="relative container mx-auto px-4 py-20">
          <div className="text-center max-w-4xl mx-auto">
            <div className="flex items-center justify-center mb-6">
              <SparklesIcon className="h-12 w-12 text-blue-600 mr-3" />
              <h1 className="text-5xl font-bold text-slate-900">
                ArchMesh PoC
              </h1>
            </div>
            <p className="text-xl text-slate-600 mb-8 leading-relaxed">
              Transform your requirements documents into comprehensive system architectures with AI-powered analysis and human-guided review
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/projects">
                <Button size="lg" className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3">
                  <PlusIcon className="mr-2 h-5 w-5" />
                  Create New Project
                </Button>
              </Link>
              <Link href="/projects">
                <Button size="lg" variant="outline" className="px-8 py-3">
                  View All Projects
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-16">
        {/* Recent Projects Section */}
        <div className="mb-20">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">Recent Projects</h2>
              <p className="text-slate-600">Continue working on your latest architecture projects</p>
            </div>
            <Link href="/projects">
              <Button variant="outline">
                View All
                <ArrowRightIcon className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>

          {loading ? (
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
          ) : projects && projects.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {projects.map((project) => (
                <Link key={project.id} href={`/projects/${project.id}`}>
                  <Card className="hover:shadow-xl transition-all duration-300 cursor-pointer border-0 shadow-md hover:scale-105">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center">
                          <span className="text-2xl mr-3">{getDomainIcon(project.domain)}</span>
                          <div>
                            <CardTitle className="text-lg text-slate-900">{project.name}</CardTitle>
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
                        {project.description || 'No description available'}
                      </p>
                      <div className="flex items-center justify-between text-xs text-slate-500">
                        <div className="flex items-center">
                          <ClockIcon className="h-3 w-3 mr-1" />
                          {new Date(project.created_at).toLocaleDateString()}
                        </div>
                        <div className="flex items-center">
                          <CheckCircleIcon className="h-3 w-3 mr-1" />
                          {project.status}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          ) : (
            <Card className="border-2 border-dashed border-slate-300">
              <CardContent className="text-center py-12">
                <FileTextIcon className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">No projects yet</h3>
                <p className="text-slate-600 mb-6">Get started by creating your first architecture project</p>
                <Link href="/projects">
                  <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                    <PlusIcon className="mr-2 h-4 w-4" />
                    Create Your First Project
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Features Section */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">How ArchMesh Works</h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Our AI-powered platform transforms your requirements into comprehensive system architectures through a structured, human-guided process
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                  <FileTextIcon className="h-8 w-8 text-blue-600" />
                </div>
                <CardTitle className="text-xl">1. Document Upload</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-600 leading-relaxed">
                  Upload your requirements documents in various formats. Our AI analyzes and extracts structured requirements automatically.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                  <BuildingIcon className="h-8 w-8 text-purple-600" />
                </div>
                <CardTitle className="text-xl">2. Architecture Design</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-600 leading-relaxed">
                  Generate comprehensive system architectures with C4 diagrams, technology stacks, and component specifications.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-lg hover:shadow-xl transition-shadow">
              <CardHeader>
                <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <UsersIcon className="h-8 w-8 text-green-600" />
                </div>
                <CardTitle className="text-xl">3. Human Review</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-600 leading-relaxed">
                  Review and refine AI-generated designs with human oversight, ensuring quality and alignment with your vision.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Key Features Grid */}
        <div className="mb-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Key Features</h2>
            <p className="text-xl text-slate-600">Everything you need for professional architecture design</p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card className="text-center border-0 shadow-md hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                  <ZapIcon className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle className="text-lg">AI-Powered Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">
                  Advanced AI agents extract structured requirements and identify gaps automatically
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-md hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
                  <GlobeIcon className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle className="text-lg">C4 Diagrams</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">
                  Interactive C4 architecture diagrams with Mermaid integration
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-md hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-3">
                  <ShieldIcon className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle className="text-lg">Human Oversight</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">
                  Built-in review gates ensure quality and alignment with business goals
                </p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 shadow-md hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="mx-auto w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-3">
                  <BuildingIcon className="h-6 w-6 text-orange-600" />
                </div>
                <CardTitle className="text-lg">Multi-Domain</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600">
                  Support for cloud-native, data platforms, and enterprise systems
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-xl mb-8 opacity-90">
            Transform your requirements into professional system architectures today
          </p>
          <Link href="/projects">
            <Button size="lg" variant="secondary" className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
              <PlusIcon className="mr-2 h-5 w-5" />
              Create Your First Project
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}