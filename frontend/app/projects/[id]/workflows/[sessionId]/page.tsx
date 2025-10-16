'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { RequirementsViewer } from '@/components/RequirementsViewer';
import { ArchitectureViewer } from '@/components/ArchitectureViewer';
import { Project, WorkflowStatus, Requirements, Architecture, HumanFeedback } from '@/types';
import { apiClient } from '@/lib/api-client';
import { toast } from 'sonner';
import { 
  ArrowLeftIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  AlertCircleIcon,
  BuildingIcon,
  FileTextIcon,
  RefreshCwIcon,
  PlayIcon,
  PauseIcon,
  EyeIcon,
  EditIcon,
  MessageSquareIcon,
  ThumbsUpIcon,
  ThumbsDownIcon,
  InfoIcon,
  ActivityIcon,
  CalendarIcon,
  UserIcon
} from 'lucide-react';

export default function WorkflowStatusPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const sessionId = params.sessionId as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus | null>(null);
  const [requirements, setRequirements] = useState<Requirements | null>(null);
  const [architecture, setArchitecture] = useState<Architecture | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  
  // Human feedback state
  const [feedback, setFeedback] = useState<HumanFeedback>({
    decision: 'approved',
    comments: '',
    constraints: [],
    preferences: []
  });
  const [newConstraint, setNewConstraint] = useState('');
  const [newPreference, setNewPreference] = useState('');

  useEffect(() => {
    if (projectId && sessionId) {
      loadData();
      // Set up polling for active workflows
      const interval = setInterval(() => {
        if (workflowStatus?.current_stage !== 'completed' && workflowStatus?.current_stage !== 'failed') {
          refreshWorkflowStatus();
        }
      }, 5000); // Poll every 5 seconds

      return () => clearInterval(interval);
    }
  }, [projectId, sessionId]);

  const loadData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadProject(),
        loadWorkflowStatus(),
        loadRequirements(),
        loadArchitecture()
      ]);
    } catch (error) {
      console.error('Failed to load data:', error);
      toast.error('Failed to load workflow data');
    } finally {
      setLoading(false);
    }
  };

  const loadProject = async () => {
    try {
      const projectData = await apiClient.getProject(projectId);
      setProject(projectData);
    } catch (error) {
      console.error('Failed to load project:', error);
    }
  };

  const loadWorkflowStatus = async () => {
    try {
      const status = await apiClient.getWorkflowStatus(sessionId);
      setWorkflowStatus(status);
    } catch (error) {
      console.error('Failed to load workflow status:', error);
    }
  };

  const loadRequirements = async () => {
    try {
      const req = await apiClient.getRequirements(sessionId);
      setRequirements(req);
    } catch (error) {
      // Requirements might not be available yet
      console.log('Requirements not available yet');
    }
  };

  const loadArchitecture = async () => {
    try {
      const arch = await apiClient.getArchitecture(sessionId);
      setArchitecture(arch);
    } catch (error) {
      // Architecture might not be available yet
      console.log('Architecture not available yet');
    }
  };

  const refreshWorkflowStatus = async () => {
    try {
      setRefreshing(true);
      await loadWorkflowStatus();
      
      // Reload requirements and architecture if they're now available
      if (workflowStatus?.current_stage === 'requirements_review' && !requirements) {
        await loadRequirements();
      }
      if (workflowStatus?.current_stage === 'architecture_review' && !architecture) {
        await loadArchitecture();
      }
    } catch (error) {
      console.error('Failed to refresh workflow status:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleSubmitFeedback = async () => {
    if (!feedback.decision) {
      toast.error('Please select a decision');
      return;
    }

    try {
      setSubmittingFeedback(true);
      const updatedStatus = await apiClient.submitReview(sessionId, feedback);
      setWorkflowStatus(updatedStatus);
      
      toast.success('Feedback submitted successfully!');
      
      // Clear feedback form
      setFeedback({
        decision: 'approved',
        comments: '',
        constraints: [],
        preferences: []
      });
      setNewConstraint('');
      setNewPreference('');
      
      // Refresh data
      await refreshWorkflowStatus();
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast.error('Failed to submit feedback. Please try again.');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const addConstraint = () => {
    if (newConstraint.trim()) {
      setFeedback(prev => ({
        ...prev,
        constraints: [...prev.constraints, newConstraint.trim()]
      }));
      setNewConstraint('');
    }
  };

  const removeConstraint = (index: number) => {
    setFeedback(prev => ({
      ...prev,
      constraints: prev.constraints.filter((_, i) => i !== index)
    }));
  };

  const addPreference = () => {
    if (newPreference.trim()) {
      setFeedback(prev => ({
        ...prev,
        preferences: [...prev.preferences, newPreference.trim()]
      }));
      setNewPreference('');
    }
  };

  const removePreference = (index: number) => {
    setFeedback(prev => ({
      ...prev,
      preferences: prev.preferences.filter((_, i) => i !== index)
    }));
  };

  const getStageProgress = () => {
    if (!workflowStatus) return 0;
    
    const stages = ['starting', 'document_analysis', 'requirements_review', 'architecture_design', 'architecture_review', 'completed'];
    const currentIndex = stages.indexOf(workflowStatus.current_stage);
    return ((currentIndex + 1) / stages.length) * 100;
  };

  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'starting': return <PlayIcon className="h-4 w-4" />;
      case 'document_analysis': return <FileTextIcon className="h-4 w-4" />;
      case 'requirements_review': return <MessageSquareIcon className="h-4 w-4" />;
      case 'architecture_design': return <BuildingIcon className="h-4 w-4" />;
      case 'architecture_review': return <EyeIcon className="h-4 w-4" />;
      case 'completed': return <CheckCircleIcon className="h-4 w-4" />;
      case 'failed': return <AlertCircleIcon className="h-4 w-4" />;
      default: return <ActivityIcon className="h-4 w-4" />;
    }
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'starting': return 'text-blue-600';
      case 'document_analysis': return 'text-blue-600';
      case 'requirements_review': return 'text-yellow-600';
      case 'architecture_design': return 'text-purple-600';
      case 'architecture_review': return 'text-orange-600';
      case 'completed': return 'text-green-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const isWaitingForReview = () => {
    return workflowStatus?.current_stage === 'requirements_review' || 
           workflowStatus?.current_stage === 'architecture_review';
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

  if (!project || !workflowStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircleIcon className="h-16 w-16 text-slate-400 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-slate-900 mb-4">Workflow Not Found</h1>
          <p className="text-slate-600 mb-6">The workflow session you're looking for doesn't exist.</p>
          <Link href={`/projects/${projectId}`}>
            <Button>
              <ArrowLeftIcon className="mr-2 h-4 w-4" />
              Back to Project
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
              <Link href={`/projects/${projectId}`}>
                <Button variant="outline" size="sm">
                  <ArrowLeftIcon className="mr-2 h-4 w-4" />
                  Back to Project
                </Button>
              </Link>
              <div>
                <h1 className="text-4xl font-bold text-slate-900">Workflow Status</h1>
                <p className="text-lg text-slate-600">
                  {project.name} • Session {sessionId.slice(0, 8)}...
                </p>
              </div>
            </div>
            <div className="flex space-x-3">
              <Button 
                variant="outline" 
                onClick={refreshWorkflowStatus}
                disabled={refreshing}
              >
                <RefreshCwIcon className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          {/* Progress Overview */}
          <Card className="border-0 shadow-md">
            <CardHeader>
              <CardTitle className="flex items-center">
                <ActivityIcon className="mr-2 h-5 w-5" />
                Workflow Progress
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Progress Bar */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700">Overall Progress</span>
                    <span className="text-sm text-slate-600">{Math.round(getStageProgress())}%</span>
                  </div>
                  <Progress value={getStageProgress()} className="h-3" />
                </div>

                {/* Current Stage */}
                <div className="flex items-center space-x-4">
                  <div className={`flex items-center space-x-2 ${getStageColor(workflowStatus.current_stage)}`}>
                    {getStageIcon(workflowStatus.current_stage)}
                    <span className="font-medium">
                      {workflowStatus.current_stage.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </div>
                  {isWaitingForReview() && (
                    <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                      <MessageSquareIcon className="mr-1 h-3 w-3" />
                      Awaiting Review
                    </Badge>
                  )}
                </div>

                {/* Errors */}
                {workflowStatus.errors && workflowStatus.errors.length > 0 && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center mb-2">
                      <AlertCircleIcon className="h-4 w-4 text-red-600 mr-2" />
                      <h4 className="text-sm font-medium text-red-800">Errors</h4>
                    </div>
                    <ul className="text-sm text-red-700 space-y-1">
                      {workflowStatus.errors.map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Main Content */}
          <Tabs defaultValue="status" className="space-y-6">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="status" className="flex items-center">
                <ActivityIcon className="mr-2 h-4 w-4" />
                Status
              </TabsTrigger>
              <TabsTrigger value="requirements" className="flex items-center" disabled={!requirements}>
                <FileTextIcon className="mr-2 h-4 w-4" />
                Requirements
              </TabsTrigger>
              <TabsTrigger value="architecture" className="flex items-center" disabled={!architecture}>
                <BuildingIcon className="mr-2 h-4 w-4" />
                Architecture
              </TabsTrigger>
              <TabsTrigger value="feedback" className="flex items-center" disabled={!isWaitingForReview()}>
                <MessageSquareIcon className="mr-2 h-4 w-4" />
                Review
              </TabsTrigger>
            </TabsList>

            <TabsContent value="status" className="space-y-6">
              <Card className="border-0 shadow-md">
                <CardHeader>
                  <CardTitle>Workflow Details</CardTitle>
                  <CardDescription>
                    Current status and progress of the architecture generation workflow
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <span className="text-sm font-medium text-slate-600">Session ID</span>
                      <p className="text-slate-900 font-mono text-sm bg-slate-100 px-2 py-1 rounded">
                        {sessionId}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-slate-600">Current Stage</span>
                      <div className="flex items-center space-x-2 mt-1">
                        {getStageIcon(workflowStatus.current_stage)}
                        <span className="text-slate-900">
                          {workflowStatus.current_stage.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {isWaitingForReview() && (
                    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-center mb-2">
                        <MessageSquareIcon className="h-4 w-4 text-yellow-600 mr-2" />
                        <h4 className="text-sm font-medium text-yellow-800">Human Review Required</h4>
                      </div>
                      <p className="text-sm text-yellow-700">
                        The workflow is waiting for your review and feedback. Please go to the Review tab to provide your input.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="requirements" className="space-y-6">
              {requirements ? (
                <RequirementsViewer
                  requirements={requirements}
                  onApprove={() => {
                    setFeedback(prev => ({ ...prev, decision: 'approved' }));
                    handleSubmitFeedback();
                  }}
                  onReject={() => {
                    setFeedback(prev => ({ ...prev, decision: 'rejected' }));
                    handleSubmitFeedback();
                  }}
                />
              ) : (
                <Card className="border-0 shadow-md">
                  <CardContent className="text-center py-16">
                    <FileTextIcon className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">Requirements Not Available</h3>
                    <p className="text-slate-600">
                      Requirements will be available once the document analysis is complete.
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="architecture" className="space-y-6">
              {architecture ? (
                <ArchitectureViewer
                  architecture={architecture}
                  onApprove={() => {
                    setFeedback(prev => ({ ...prev, decision: 'approved' }));
                    handleSubmitFeedback();
                  }}
                  onReject={() => {
                    setFeedback(prev => ({ ...prev, decision: 'rejected' }));
                    handleSubmitFeedback();
                  }}
                />
              ) : (
                <Card className="border-0 shadow-md">
                  <CardContent className="text-center py-16">
                    <BuildingIcon className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">Architecture Not Available</h3>
                    <p className="text-slate-600">
                      Architecture will be available once the design phase is complete.
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="feedback" className="space-y-6">
              <Card className="border-0 shadow-md">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <MessageSquareIcon className="mr-2 h-5 w-5" />
                    Human Review & Feedback
                  </CardTitle>
                  <CardDescription>
                    Provide your feedback to continue the workflow
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Decision */}
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-3 block">
                      Decision
                    </label>
                    <div className="flex space-x-4">
                      <Button
                        variant={feedback.decision === 'approved' ? 'default' : 'outline'}
                        onClick={() => setFeedback(prev => ({ ...prev, decision: 'approved' }))}
                        className="flex items-center"
                      >
                        <ThumbsUpIcon className="mr-2 h-4 w-4" />
                        Approve
                      </Button>
                      <Button
                        variant={feedback.decision === 'rejected' ? 'destructive' : 'outline'}
                        onClick={() => setFeedback(prev => ({ ...prev, decision: 'rejected' }))}
                        className="flex items-center"
                      >
                        <ThumbsDownIcon className="mr-2 h-4 w-4" />
                        Reject
                      </Button>
                      <Button
                        variant={feedback.decision === 'needs_info' ? 'default' : 'outline'}
                        onClick={() => setFeedback(prev => ({ ...prev, decision: 'needs_info' }))}
                        className="flex items-center"
                      >
                        <InfoIcon className="mr-2 h-4 w-4" />
                        Needs More Info
                      </Button>
                    </div>
                  </div>

                  {/* Comments */}
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                      Comments
                    </label>
                    <Textarea
                      value={feedback.comments}
                      onChange={(e) => setFeedback(prev => ({ ...prev, comments: e.target.value }))}
                      placeholder="Provide detailed feedback about the current stage..."
                      rows={4}
                    />
                  </div>

                  {/* Constraints */}
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                      Additional Constraints
                    </label>
                    <div className="space-y-2">
                      <div className="flex space-x-2">
                        <Input
                          value={newConstraint}
                          onChange={(e) => setNewConstraint(e.target.value)}
                          placeholder="Add a constraint..."
                          onKeyPress={(e) => e.key === 'Enter' && addConstraint()}
                        />
                        <Button onClick={addConstraint} size="sm">
                          Add
                        </Button>
                      </div>
                      {feedback.constraints.length > 0 && (
                        <div className="space-y-1">
                          {feedback.constraints.map((constraint, index) => (
                            <div key={index} className="flex items-center justify-between bg-slate-50 px-3 py-2 rounded">
                              <span className="text-sm">{constraint}</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeConstraint(index)}
                                className="h-6 w-6 p-0 text-slate-400 hover:text-red-600"
                              >
                                ×
                              </Button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Preferences */}
                  <div>
                    <label className="text-sm font-medium text-slate-700 mb-2 block">
                      Preferences
                    </label>
                    <div className="space-y-2">
                      <div className="flex space-x-2">
                        <Input
                          value={newPreference}
                          onChange={(e) => setNewPreference(e.target.value)}
                          placeholder="Add a preference..."
                          onKeyPress={(e) => e.key === 'Enter' && addPreference()}
                        />
                        <Button onClick={addPreference} size="sm">
                          Add
                        </Button>
                      </div>
                      {feedback.preferences.length > 0 && (
                        <div className="space-y-1">
                          {feedback.preferences.map((preference, index) => (
                            <div key={index} className="flex items-center justify-between bg-slate-50 px-3 py-2 rounded">
                              <span className="text-sm">{preference}</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removePreference(index)}
                                className="h-6 w-6 p-0 text-slate-400 hover:text-red-600"
                              >
                                ×
                              </Button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="flex justify-end">
                    <Button
                      onClick={handleSubmitFeedback}
                      disabled={submittingFeedback || !feedback.decision}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                    >
                      {submittingFeedback ? 'Submitting...' : 'Submit Feedback'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}