'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { DocumentUploader } from '@/components/DocumentUploader';
import { Project, WorkflowStartResponse } from '@/types';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

export default function UploadPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [projectContext, setProjectContext] = useState('');
  const [domain, setDomain] = useState<'cloud-native' | 'data-platform' | 'enterprise'>('cloud-native');
  const [llmProvider, setLlmProvider] = useState<'deepseek' | 'openai' | 'anthropic'>('deepseek');
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);

  // Load project details
  useEffect(() => {
    const loadProject = async () => {
      try {
        const projectData = await apiClient.getProject(projectId);
        setProject(projectData);
        setDomain(projectData.domain);
      } catch (error) {
        console.error('Failed to load project:', error);
        toast.error('Failed to load project');
        router.push('/projects');
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      loadProject();
    }
  }, [projectId, router]);

  const handleFileUpload = (file: File) => {
    setUploadedFile(file);
    toast.success(`File ${file.name} uploaded successfully!`);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!uploadedFile) {
      toast.error('Please upload a file first');
      return;
    }

    try {
      setUploading(true);
      const response: WorkflowStartResponse = await apiClient.startArchitectureWorkflow(
        uploadedFile,
        projectId,
        domain,
        projectContext || undefined,
        llmProvider
      );

      toast.success('Workflow started successfully!');
      // Redirect to project detail page with workflow status
      router.push(`/projects/${projectId}?workflow=${response.session_id}`);
    } catch (error) {
      console.error('Failed to start workflow:', error);
      toast.error('Failed to start workflow. Please try again.');
    } finally {
      setUploading(false);
    }
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
            <h1 className="text-3xl font-bold text-slate-900">Start Workflow</h1>
            {getDomainBadge(project.domain)}
          </div>
          <p className="text-slate-600">
            Upload a requirements document to begin the architecture design process for <strong>{project.name}</strong>
          </p>
        </div>
        <Link href={`/projects/${project.id}`}>
          <Button variant="outline">Back to Project</Button>
        </Link>
      </div>

      {/* Upload Form */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Upload Requirements Document</CardTitle>
              <CardDescription>
                Upload your business requirements document to start the AI-powered architecture design process.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* File Upload */}
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">
                    Requirements Document
                  </label>
                  <DocumentUploader 
                    onUploadComplete={handleFileUpload}
                    projectId={projectId}
                  />
                </div>

                {/* LLM Provider Selection */}
                <div>
                  <Label className="text-sm font-medium text-slate-700 mb-2 block">
                    AI Provider
                  </Label>
                  <Select value={llmProvider} onValueChange={(value: 'deepseek' | 'openai' | 'anthropic') => setLlmProvider(value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="deepseek">
                        <div className="flex items-center space-x-2">
                          <span>🤖</span>
                          <div>
                            <div className="font-medium">DeepSeek (Local)</div>
                            <div className="text-xs text-slate-500">Free, private, offline processing</div>
                          </div>
                        </div>
                      </SelectItem>
                      <SelectItem value="openai">
                        <div className="flex items-center space-x-2">
                          <span>🧠</span>
                          <div>
                            <div className="font-medium">OpenAI GPT-4</div>
                            <div className="text-xs text-slate-500">Cloud-based, paid service</div>
                          </div>
                        </div>
                      </SelectItem>
                      <SelectItem value="anthropic">
                        <div className="flex items-center space-x-2">
                          <span>🔮</span>
                          <div>
                            <div className="font-medium">Anthropic Claude</div>
                            <div className="text-xs text-slate-500">Cloud-based, paid service</div>
                          </div>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-slate-500 mt-1">
                    {llmProvider === 'deepseek' 
                      ? 'Recommended for development and sensitive data. No API costs.'
                      : 'Cloud-based AI with API costs. Use for production or when local processing is not available.'
                    }
                  </p>
                </div>

                {/* Project Context */}
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-2 block">
                    Additional Context (Optional)
                  </label>
                  <Textarea
                    value={projectContext}
                    onChange={(e) => setProjectContext(e.target.value)}
                    placeholder="Provide any additional context about your project, constraints, or specific requirements..."
                    rows={4}
                  />
                </div>

                {/* Submit Button */}
                <div className="flex justify-end space-x-2">
                  <Link href={`/projects/${project.id}`}>
                    <Button type="button" variant="outline">
                      Cancel
                    </Button>
                  </Link>
                  <Button 
                    type="submit" 
                    disabled={!uploadedFile || uploading}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    {uploading ? 'Starting Workflow...' : 'Start Workflow'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Project Info */}
          <Card>
            <CardHeader>
              <CardTitle>Project Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <span className="text-sm font-medium text-slate-600">Name:</span>
                <p className="text-slate-900">{project.name}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-slate-600">Domain:</span>
                <div className="mt-1">{getDomainBadge(project.domain)}</div>
              </div>
              <div>
                <span className="text-sm font-medium text-slate-600">Description:</span>
                <p className="text-slate-900 text-sm">
                  {project.description || 'No description provided'}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Process Info */}
          <Card>
            <CardHeader>
              <CardTitle>What Happens Next?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-600">
                  1
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-900">Document Analysis</p>
                  <p className="text-xs text-slate-600">AI agents parse your requirements document</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="h-6 w-6 rounded-full bg-yellow-100 flex items-center justify-center text-xs font-bold text-yellow-600">
                  2
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-900">Requirements Review</p>
                  <p className="text-xs text-slate-600">Review and approve extracted requirements</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="h-6 w-6 rounded-full bg-purple-100 flex items-center justify-center text-xs font-bold text-purple-600">
                  3
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-900">Architecture Design</p>
                  <p className="text-xs text-slate-600">AI generates system architecture and C4 diagrams</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="h-6 w-6 rounded-full bg-green-100 flex items-center justify-center text-xs font-bold text-green-600">
                  4
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-900">Final Review</p>
                  <p className="text-xs text-slate-600">Review and approve the final architecture</p>
                </div>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
}
