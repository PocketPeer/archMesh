'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { RequirementsViewer } from '@/components/RequirementsViewer';
import { ArchitectureViewer } from '@/components/ArchitectureViewer';
import { Project, WorkflowSession, Requirements, Architecture, HumanFeedback } from '@/types';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';

export default function WorkflowDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const sessionId = params.sessionId as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [workflow, setWorkflow] = useState<WorkflowSession | null>(null);
  const [requirements, setRequirements] = useState<Requirements | null>(null);
  const [architecture, setArchitecture] = useState<Architecture | null>(null);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState<HumanFeedback>({
    decision: 'approved',
    comments: '',
    constraints: [],
    preferences: []
  });
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  useEffect(() => {
    if (projectId && sessionId) {
      loadData();
    }
  }, [projectId, sessionId]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load project and workflow in parallel
      const [projectData, workflowData] = await Promise.all([
        apiClient.getProject(projectId),
        apiClient.getWorkflowStatus(sessionId)
      ]);
      
      setProject(projectData);
      setWorkflow(workflowData);

      // Try to load requirements and architecture if available
      try {
        const requirementsData = await apiClient.getWorkflowRequirements(sessionId);
        setRequirements(requirementsData);
      } catch (error) {
        // Requirements not available yet
      }

      try {
        const architectureData = await apiClient.getWorkflowArchitecture(sessionId);
        setArchitecture(architectureData);
      } catch (error) {
        // Architecture not available yet
      }
    } catch (error) {
      console.error('Failed to load workflow data:', error);
      toast.error('Failed to load workflow data');
      router.push(`/projects/${projectId}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async () => {
    try {
      setSubmittingFeedback(true);
      const updatedWorkflow = await apiClient.submitWorkflowReview(sessionId, feedback);
      setWorkflow(updatedWorkflow);
      toast.success('Feedback submitted successfully');
      
      // Reload data to get updated status
      await loadData();
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast.error('Failed to submit feedback');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const getStatusBadge = (stage: string) => {
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

  const getProgressPercentage = () => {
    if (!workflow) return 0;
    return Math.round(workflow.state_data.stage_progress * 100);
  };

  const isWaitingForReview = () => {
    if (!workflow) return false;
    return workflow.current_stage.includes('review') && workflow.is_active;
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

  if (!project || !workflow) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-slate-900 mb-4">Workflow Not Found</h1>
        <p className="text-slate-600 mb-6">The workflow you're looking for doesn't exist.</p>
        <Link href={`/projects/${projectId}`}>
          <Button>Back to Project</Button>
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
            <h1 className="text-3xl font-bold text-slate-900">Workflow Session</h1>
            {getStatusBadge(workflow.current_stage)}
            <Badge variant={workflow.is_active ? "default" : "secondary"}>
              {workflow.is_active ? "Active" : "Inactive"}
            </Badge>
          </div>
          <p className="text-slate-600">
            Session ID: <span className="font-mono text-sm">{sessionId}</span>
          </p>
        </div>
        <div className="flex space-x-2">
          <Link href={`/projects/${projectId}`}>
            <Button variant="outline">Back to Project</Button>
          </Link>
          {isWaitingForReview() && (
            <Dialog>
              <DialogTrigger asChild>
                <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  Submit Review
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Submit Review</DialogTitle>
                  <DialogDescription>
                    Provide your feedback for the {workflow.current_stage.replace('_', ' ')} stage.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                      Decision
                    </label>
                    <select
                      value={feedback.decision}
                      onChange={(e) => setFeedback(prev => ({ ...prev, decision: e.target.value as HumanFeedback['decision'] }))}
                      className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="approved">Approve</option>
                      <option value="rejected">Reject</option>
                      <option value="needs_info">Needs More Information</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                      Comments
                    </label>
                    <Textarea
                      value={feedback.comments}
                      onChange={(e) => setFeedback(prev => ({ ...prev, comments: e.target.value }))}
                      placeholder="Provide detailed feedback..."
                      rows={4}
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button 
                      variant="outline" 
                      onClick={() => setFeedback({ decision: 'approved', comments: '', constraints: [], preferences: [] })}
                    >
                      Cancel
                    </Button>
                    <Button 
                      onClick={handleSubmitFeedback}
                      disabled={submittingFeedback}
                    >
                      {submittingFeedback ? 'Submitting...' : 'Submit Feedback'}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      {/* Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">Overall Progress</span>
              <span className="text-sm text-slate-600">{getProgressPercentage()}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getProgressPercentage()}%` }}
              ></div>
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
                <span className="text-slate-600">Completed Stages:</span>
                <p className="text-slate-900">{workflow.state_data.completed_stages.length}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Errors */}
      {workflow.state_data.errors.length > 0 && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-800">Errors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {workflow.state_data.errors.map((error, index) => (
                <div key={index} className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="requirements">Requirements</TabsTrigger>
          <TabsTrigger value="architecture">Architecture</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Overview</CardTitle>
              <CardDescription>
                Current status and stage information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <span className="text-sm font-medium text-slate-600">Current Stage:</span>
                  <p className="text-slate-900">{workflow.current_stage.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-slate-600">Status:</span>
                  <p className="text-slate-900">{workflow.is_active ? 'Active' : 'Inactive'}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-slate-600">Completed Stages:</span>
                  <div className="mt-1">
                    {workflow.state_data.completed_stages.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {workflow.state_data.completed_stages.map((stage, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {stage.replace('_', ' ')}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <span className="text-slate-500 text-sm">None yet</span>
                    )}
                  </div>
                </div>
                <div>
                  <span className="text-sm font-medium text-slate-600">Pending Tasks:</span>
                  <div className="mt-1">
                    {workflow.state_data.pending_tasks.length > 0 ? (
                      <ul className="text-sm text-slate-600 space-y-1">
                        {workflow.state_data.pending_tasks.map((task, index) => (
                          <li key={index}>• {task}</li>
                        ))}
                      </ul>
                    ) : (
                      <span className="text-slate-500 text-sm">None</span>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="requirements" className="space-y-4">
          {requirements ? (
            <RequirementsViewer 
              requirements={requirements}
              onApprove={async () => {
                // Handle requirements approval
                const feedback: HumanFeedback = {
                  decision: 'approved',
                  comments: 'Requirements look good, proceeding to architecture design'
                };
                await apiClient.submitWorkflowReview(sessionId, feedback);
                await loadData(); // Reload to get updated status
              }}
              onReject={async () => {
                // Handle requirements rejection
                const feedback: HumanFeedback = {
                  decision: 'rejected',
                  comments: 'Requirements need revision before proceeding'
                };
                await apiClient.submitWorkflowReview(sessionId, feedback);
                await loadData(); // Reload to get updated status
              }}
            />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Requirements</CardTitle>
                <CardDescription>
                  Extracted and structured requirements from your document
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-slate-600">
                  {workflow.current_stage === 'requirements_review' ? (
                    <div>
                      <p>Requirements are being processed...</p>
                      <p className="text-sm mt-2">This may take a few minutes.</p>
                    </div>
                  ) : (
                    <p>Requirements will appear here once the document analysis is complete.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="architecture" className="space-y-4">
          {architecture ? (
            <ArchitectureViewer 
              architecture={architecture}
              onApprove={async () => {
                // Handle architecture approval
                const feedback: HumanFeedback = {
                  decision: 'approved',
                  comments: 'Architecture design looks good, proceeding to completion'
                };
                await apiClient.submitWorkflowReview(sessionId, feedback);
                await loadData(); // Reload to get updated status
              }}
              onReject={async () => {
                // Handle architecture rejection
                const feedback: HumanFeedback = {
                  decision: 'rejected',
                  comments: 'Architecture needs revision before proceeding'
                };
                await apiClient.submitWorkflowReview(sessionId, feedback);
                await loadData(); // Reload to get updated status
              }}
            />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Architecture</CardTitle>
                <CardDescription>
                  Generated system architecture and design recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-slate-600">
                  {workflow.current_stage === 'architecture_design' || workflow.current_stage === 'architecture_review' ? (
                    <div>
                      <p>Architecture is being generated...</p>
                      <p className="text-sm mt-2">This may take a few minutes.</p>
                    </div>
                  ) : (
                    <p>Architecture will appear here once the design phase is complete.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
