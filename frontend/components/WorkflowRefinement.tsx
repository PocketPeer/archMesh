'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Brain, 
  Target, 
  Zap,
  HelpCircle,
  TrendingUp,
  Clock,
  Settings
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface RefinementConfig {
  strategy: string;
  primary_llm: string;
  validation_llm: string;
  refinement_llm: string;
  max_iterations: number;
  quality_threshold: number;
  enable_cross_validation: boolean;
  enable_question_generation: boolean;
}

interface QualityScore {
  completeness: number;
  consistency: number;
  accuracy: number;
  relevance: number;
  overall: number;
  confidence: number;
}

interface RefinementResult {
  refinement_id: string;
  workflow_id: string;
  status: string;
  quality_improvement: number;
  iterations_performed: number;
  llm_used: string;
  refinement_notes: string[];
  questions_generated: Array<{
    question: string;
    category: string;
    priority: string;
    context: string;
  }>;
  timestamp: string;
}

interface WorkflowRefinementProps {
  workflowId: string;
  projectId: string;
  onRefinementComplete?: (result: RefinementResult) => void;
}

export default function WorkflowRefinement({ 
  workflowId, 
  projectId, 
  onRefinementComplete 
}: WorkflowRefinementProps) {
  const [config, setConfig] = useState<RefinementConfig>({
    strategy: 'iterative_improvement',
    primary_llm: 'deepseek',
    validation_llm: 'claude',
    refinement_llm: 'gpt-4',
    max_iterations: 3,
    quality_threshold: 0.8,
    enable_cross_validation: true,
    enable_question_generation: true
  });

  const [isRefining, setIsRefining] = useState(false);
  const [currentQuality, setCurrentQuality] = useState<QualityScore | null>(null);
  const [refinementResult, setRefinementResult] = useState<RefinementResult | null>(null);
  const [availableStrategies, setAvailableStrategies] = useState<any[]>([]);
  const [availableLLMs, setAvailableLLMs] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRefinementOptions();
    assessCurrentQuality();
  }, [workflowId]);

  const loadRefinementOptions = async () => {
    try {
      const [strategiesResponse, llmsResponse] = await Promise.all([
        apiClient.makeAuthenticatedRequest('/api/v1/refinement/strategies'),
        apiClient.makeAuthenticatedRequest('/api/v1/refinement/llm-providers')
      ]);

      const strategies = await strategiesResponse.json();
      const llms = await llmsResponse.json();

      setAvailableStrategies(strategies.strategies || []);
      setAvailableLLMs(llms.providers || []);
    } catch (error) {
      console.error('Failed to load refinement options:', error);
    }
  };

  const assessCurrentQuality = async () => {
    try {
      const response = await apiClient.makeAuthenticatedRequest('/api/v1/refinement/assess-quality', {
        method: 'POST',
        body: JSON.stringify({
          workflow_id: workflowId,
          llm_provider: config.validation_llm
        })
      });

      if (response.ok) {
        const quality = await response.json();
        setCurrentQuality({
          completeness: quality.completeness,
          consistency: quality.consistency,
          accuracy: quality.accuracy,
          relevance: quality.relevance,
          overall: quality.overall,
          confidence: quality.confidence
        });
      }
    } catch (error) {
      console.error('Failed to assess quality:', error);
    }
  };

  const startRefinement = async () => {
    setIsRefining(true);
    setError(null);

    try {
      const response = await apiClient.makeAuthenticatedRequest('/api/v1/refinement/refine', {
        method: 'POST',
        body: JSON.stringify({
          workflow_id: workflowId,
          ...config
        })
      });

      if (response.ok) {
        const result = await response.json();
        setRefinementResult(result);
        onRefinementComplete?.(result);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Refinement failed');
      }
    } catch (error) {
      setError('Network error during refinement');
    } finally {
      setIsRefining(false);
    }
  };

  const generateQuestions = async () => {
    try {
      const response = await apiClient.makeAuthenticatedRequest('/api/v1/refinement/generate-questions', {
        method: 'POST',
        body: JSON.stringify({
          workflow_id: workflowId
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Handle questions display
        console.log('Generated questions:', data.questions);
      }
    } catch (error) {
      console.error('Failed to generate questions:', error);
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getQualityLabel = (score: number) => {
    if (score >= 0.9) return 'Excellent';
    if (score >= 0.8) return 'Good';
    if (score >= 0.6) return 'Fair';
    return 'Poor';
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Workflow Refinement
          </CardTitle>
          <CardDescription>
            Improve workflow output quality using multi-LLM orchestration and iterative refinement
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="config" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="config">Configuration</TabsTrigger>
              <TabsTrigger value="quality">Quality Assessment</TabsTrigger>
              <TabsTrigger value="questions">Questions</TabsTrigger>
              <TabsTrigger value="results">Results</TabsTrigger>
            </TabsList>

            <TabsContent value="config" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="strategy">Refinement Strategy</Label>
                  <Select
                    value={config.strategy}
                    onValueChange={(value) => setConfig({ ...config, strategy: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select strategy" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableStrategies.map((strategy) => (
                        <SelectItem key={strategy.value} value={strategy.value}>
                          {strategy.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="primary_llm">Primary LLM</Label>
                  <Select
                    value={config.primary_llm}
                    onValueChange={(value) => setConfig({ ...config, primary_llm: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select primary LLM" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableLLMs.map((llm) => (
                        <SelectItem key={llm.id} value={llm.id}>
                          {llm.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="validation_llm">Validation LLM</Label>
                  <Select
                    value={config.validation_llm}
                    onValueChange={(value) => setConfig({ ...config, validation_llm: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select validation LLM" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableLLMs.map((llm) => (
                        <SelectItem key={llm.id} value={llm.id}>
                          {llm.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="refinement_llm">Refinement LLM</Label>
                  <Select
                    value={config.refinement_llm}
                    onValueChange={(value) => setConfig({ ...config, refinement_llm: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select refinement LLM" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableLLMs.map((llm) => (
                        <SelectItem key={llm.id} value={llm.id}>
                          {llm.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Max Iterations: {config.max_iterations}</Label>
                  <Slider
                    value={[config.max_iterations]}
                    onValueChange={([value]) => setConfig({ ...config, max_iterations: value })}
                    min={1}
                    max={10}
                    step={1}
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Quality Threshold: {Math.round(config.quality_threshold * 100)}%</Label>
                  <Slider
                    value={[config.quality_threshold]}
                    onValueChange={([value]) => setConfig({ ...config, quality_threshold: value })}
                    min={0.1}
                    max={1.0}
                    step={0.1}
                    className="w-full"
                  />
                </div>

                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="cross_validation"
                      checked={config.enable_cross_validation}
                      onCheckedChange={(checked) => 
                        setConfig({ ...config, enable_cross_validation: checked })
                      }
                    />
                    <Label htmlFor="cross_validation">Enable Cross-Validation</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch
                      id="question_generation"
                      checked={config.enable_question_generation}
                      onCheckedChange={(checked) => 
                        setConfig({ ...config, enable_question_generation: checked })
                      }
                    />
                    <Label htmlFor="question_generation">Enable Question Generation</Label>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <Button 
                  onClick={startRefinement} 
                  disabled={isRefining}
                  className="flex items-center gap-2"
                >
                  {isRefining ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Zap className="h-4 w-4" />
                  )}
                  {isRefining ? 'Refining...' : 'Start Refinement'}
                </Button>

                <Button 
                  variant="outline" 
                  onClick={assessCurrentQuality}
                  className="flex items-center gap-2"
                >
                  <Target className="h-4 w-4" />
                  Assess Quality
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="quality" className="space-y-4">
              {currentQuality ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className={`text-2xl font-bold ${getQualityColor(currentQuality.completeness)}`}>
                        {Math.round(currentQuality.completeness * 100)}%
                      </div>
                      <div className="text-sm text-gray-600">Completeness</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className={`text-2xl font-bold ${getQualityColor(currentQuality.consistency)}`}>
                        {Math.round(currentQuality.consistency * 100)}%
                      </div>
                      <div className="text-sm text-gray-600">Consistency</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className={`text-2xl font-bold ${getQualityColor(currentQuality.accuracy)}`}>
                        {Math.round(currentQuality.accuracy * 100)}%
                      </div>
                      <div className="text-sm text-gray-600">Accuracy</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className={`text-2xl font-bold ${getQualityColor(currentQuality.relevance)}`}>
                        {Math.round(currentQuality.relevance * 100)}%
                      </div>
                      <div className="text-sm text-gray-600">Relevance</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className={`text-2xl font-bold ${getQualityColor(currentQuality.overall)}`}>
                        {Math.round(currentQuality.overall * 100)}%
                      </div>
                      <div className="text-sm text-gray-600">Overall</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className={`text-2xl font-bold ${getQualityColor(currentQuality.confidence)}`}>
                        {Math.round(currentQuality.confidence * 100)}%
                      </div>
                      <div className="text-sm text-gray-600">Confidence</div>
                    </div>
                  </div>

                  <div className="text-center">
                    <Badge 
                      variant={currentQuality.overall >= 0.8 ? 'default' : 'secondary'}
                      className="text-lg px-4 py-2"
                    >
                      {getQualityLabel(currentQuality.overall)}
                    </Badge>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Target className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No quality assessment available</p>
                  <Button 
                    variant="outline" 
                    onClick={assessCurrentQuality}
                    className="mt-4"
                  >
                    Assess Quality
                  </Button>
                </div>
              )}
            </TabsContent>

            <TabsContent value="questions" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">Improvement Questions</h3>
                <Button 
                  variant="outline" 
                  onClick={generateQuestions}
                  className="flex items-center gap-2"
                >
                  <HelpCircle className="h-4 w-4" />
                  Generate Questions
                </Button>
              </div>

              {refinementResult?.questions_generated && refinementResult.questions_generated.length > 0 ? (
                <div className="space-y-3">
                  {refinementResult.questions_generated.map((question, index) => (
                    <Card key={index}>
                      <CardContent className="pt-4">
                        <div className="flex justify-between items-start mb-2">
                          <p className="font-medium">{question.question}</p>
                          <Badge variant="outline">{question.priority}</Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{question.context}</p>
                        <Badge variant="secondary">{question.category}</Badge>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <HelpCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No questions generated yet</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="results" className="space-y-4">
              {refinementResult ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <TrendingUp className="h-4 w-4" />
                          <span className="font-medium">Quality Improvement</span>
                        </div>
                        <div className="text-2xl font-bold text-green-600">
                          +{Math.round(refinementResult.quality_improvement * 100)}%
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <RefreshCw className="h-4 w-4" />
                          <span className="font-medium">Iterations</span>
                        </div>
                        <div className="text-2xl font-bold">
                          {refinementResult.iterations_performed}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Brain className="h-4 w-4" />
                          <span className="font-medium">LLM Used</span>
                        </div>
                        <div className="text-lg font-semibold">
                          {refinementResult.llm_used}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {refinementResult.refinement_notes.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Refinement Notes</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {refinementResult.refinement_notes.map((note, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span className="text-sm">{note}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Settings className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No refinement results available</p>
                  <p className="text-sm">Start a refinement process to see results here</p>
                </div>
              )}
            </TabsContent>
          </Tabs>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 text-red-800">
                <AlertCircle className="h-4 w-4" />
                <span className="font-medium">Error</span>
              </div>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
