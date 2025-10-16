'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Requirements, ClarificationQuestion } from '@/types';
import { toast } from 'sonner';

interface RequirementsViewerProps {
  requirements: Requirements;
  onApprove: () => void;
  onReject: () => void;
}

export function RequirementsViewer({ requirements, onApprove, onReject }: RequirementsViewerProps) {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleApprove = async () => {
    setIsProcessing(true);
    try {
      await onApprove();
      toast.success('Requirements approved successfully!');
    } catch (error) {
      toast.error('Failed to approve requirements');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    setIsProcessing(true);
    try {
      await onReject();
      toast.success('Requirements rejected');
    } catch (error) {
      toast.error('Failed to reject requirements');
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadJSON = () => {
    const dataStr = JSON.stringify(requirements, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `requirements-${requirements.id}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    toast.success('Requirements exported as JSON');
  };

  const getPriorityColor = (priority: ClarificationQuestion['priority']) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getConfidenceText = (score: number) => {
    if (score >= 0.8) return 'High Confidence';
    if (score >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  };

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Requirements Analysis</CardTitle>
              <CardDescription>
                Review the extracted and structured requirements from your document
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                onClick={downloadJSON}
                className="flex items-center space-x-2"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Export JSON</span>
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-slate-700">Confidence Score:</span>
                <Badge variant="secondary" className={getConfidenceColor(requirements.confidence_score)}>
                  {Math.round(requirements.confidence_score * 100)}%
                </Badge>
                <span className="text-sm text-slate-600">
                  {getConfidenceText(requirements.confidence_score)}
                </span>
              </div>
              <div className="w-64">
                <Progress 
                  value={requirements.confidence_score * 100} 
                  className="h-2"
                />
              </div>
            </div>
            <div className="flex space-x-2">
              <Button
                variant="destructive"
                onClick={handleReject}
                disabled={isProcessing}
                className="flex items-center space-x-2"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span>Reject</span>
              </Button>
              <Button
                onClick={handleApprove}
                disabled={isProcessing}
                className="bg-green-600 hover:bg-green-700 flex items-center space-x-2"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Approve</span>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Business Goals */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span className="text-2xl">🎯</span>
            <span>Business Goals</span>
            <Badge variant="secondary">{requirements.structured_requirements.business_goals.length}</Badge>
          </CardTitle>
          <CardDescription>
            High-level business objectives and outcomes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {requirements.structured_requirements.business_goals.map((goal, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <p className="text-slate-800">{goal}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Functional Requirements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span className="text-2xl">⚙️</span>
            <span>Functional Requirements</span>
            <Badge variant="secondary">{requirements.structured_requirements.functional_requirements.length}</Badge>
          </CardTitle>
          <CardDescription>
            Specific functionality and features the system must provide
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {requirements.structured_requirements.functional_requirements.map((req, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <p className="text-slate-800">{req}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Non-Functional Requirements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span className="text-2xl">📊</span>
            <span>Non-Functional Requirements</span>
          </CardTitle>
          <CardDescription>
            Quality attributes and constraints that affect system behavior
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="performance" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="performance">Performance</TabsTrigger>
              <TabsTrigger value="security">Security</TabsTrigger>
              <TabsTrigger value="scalability">Scalability</TabsTrigger>
              <TabsTrigger value="reliability">Reliability</TabsTrigger>
              <TabsTrigger value="maintainability">Maintainability</TabsTrigger>
            </TabsList>
            
            {Object.entries(requirements.structured_requirements.non_functional_requirements).map(([category, reqs]) => (
              <TabsContent key={category} value={category} className="mt-4">
                <div className="space-y-3">
                  {reqs.length > 0 ? (
                    reqs.map((req, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                        <div className="flex-shrink-0 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </div>
                        <p className="text-slate-800">{req}</p>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-slate-500">
                      <p>No {category} requirements identified</p>
                    </div>
                  )}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Constraints */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span className="text-2xl">⚠️</span>
            <span>Constraints</span>
            <Badge variant="secondary">{requirements.structured_requirements.constraints.length}</Badge>
          </CardTitle>
          <CardDescription>
            Limitations and restrictions that must be considered
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {requirements.structured_requirements.constraints.map((constraint, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex-shrink-0 w-6 h-6 bg-orange-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <p className="text-slate-800">{constraint}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Stakeholders */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span className="text-2xl">👥</span>
            <span>Stakeholders</span>
            <Badge variant="secondary">{requirements.structured_requirements.stakeholders.length}</Badge>
          </CardTitle>
          <CardDescription>
            People and organizations with interest in the project
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {requirements.structured_requirements.stakeholders.map((stakeholder, index) => (
              <div key={index} className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 bg-slate-600 text-white rounded-full flex items-center justify-center font-bold">
                    {stakeholder.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900">{stakeholder.name}</h4>
                    <p className="text-sm text-slate-600">{stakeholder.role}</p>
                  </div>
                </div>
                <div>
                  <h5 className="text-sm font-medium text-slate-700 mb-2">Concerns:</h5>
                  <div className="flex flex-wrap gap-1">
                    {stakeholder.concerns.map((concern, concernIndex) => (
                      <Badge key={concernIndex} variant="outline" className="text-xs">
                        {concern}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Clarification Questions */}
      {requirements.clarification_questions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span className="text-2xl">❓</span>
              <span>Clarification Questions</span>
              <Badge variant="secondary">{requirements.clarification_questions.length}</Badge>
            </CardTitle>
            <CardDescription>
              Questions that need clarification to improve requirements completeness
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {requirements.clarification_questions
                .sort((a, b) => {
                  const priorityOrder = { high: 3, medium: 2, low: 1 };
                  return priorityOrder[b.priority] - priorityOrder[a.priority];
                })
                .map((question, index) => (
                <div key={index} className={`p-4 border rounded-lg ${getPriorityColor(question.priority)}`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-xs">
                        {question.category}
                      </Badge>
                      <Badge 
                        variant={question.priority === 'high' ? 'destructive' : 
                                question.priority === 'medium' ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {question.priority} priority
                      </Badge>
                    </div>
                  </div>
                  <p className="text-slate-800 font-medium">{question.question}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Identified Gaps */}
      {requirements.identified_gaps.length > 0 && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-red-800">
              <span className="text-2xl">🚨</span>
              <span>Identified Gaps</span>
              <Badge variant="destructive">{requirements.identified_gaps.length}</Badge>
            </CardTitle>
            <CardDescription>
              Missing or incomplete information that may impact the project
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {requirements.identified_gaps.map((gap, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 bg-red-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    !
                  </div>
                  <p className="text-red-800">{gap}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Requirements Summary</CardTitle>
          <CardDescription>
            Overview of extracted requirements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {requirements.structured_requirements.business_goals.length}
              </div>
              <div className="text-sm text-blue-800">Business Goals</div>
            </div>
            <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {requirements.structured_requirements.functional_requirements.length}
              </div>
              <div className="text-sm text-green-800">Functional Requirements</div>
            </div>
            <div className="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {Object.values(requirements.structured_requirements.non_functional_requirements)
                  .flat().length}
              </div>
              <div className="text-sm text-purple-800">Non-Functional Requirements</div>
            </div>
            <div className="text-center p-4 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {requirements.clarification_questions.length}
              </div>
              <div className="text-sm text-orange-800">Clarification Questions</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
