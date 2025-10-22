'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { 
  Brain, 
  Zap, 
  TrendingUp, 
  Settings,
  RefreshCw,
  HelpCircle
} from 'lucide-react';
import WorkflowRefinement from './WorkflowRefinement';
import { apiClient } from '@/lib/api-client';

interface RefinementButtonProps {
  workflowId: string;
  projectId: string;
  currentQuality?: number;
  onRefinementComplete?: (result: any) => void;
  variant?: 'default' | 'outline' | 'secondary';
  size?: 'sm' | 'default' | 'lg';
}

export default function RefinementButton({
  workflowId,
  projectId,
  currentQuality,
  onRefinementComplete,
  variant = 'outline',
  size = 'default'
}: RefinementButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isRefining, setIsRefining] = useState(false);

  const getQualityColor = (quality?: number) => {
    if (!quality) return 'text-gray-500';
    if (quality >= 0.8) return 'text-green-600';
    if (quality >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getQualityLabel = (quality?: number) => {
    if (!quality) return 'Unknown';
    if (quality >= 0.9) return 'Excellent';
    if (quality >= 0.8) return 'Good';
    if (quality >= 0.6) return 'Fair';
    return 'Poor';
  };

  const handleRefinementComplete = (result: any) => {
    setIsRefining(false);
    onRefinementComplete?.(result);
    // Keep dialog open to show results
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button 
          variant={variant} 
          size={size}
          className="flex items-center gap-2"
          onClick={() => setIsOpen(true)}
        >
          <Brain className="h-4 w-4" />
          Refine Output
          {currentQuality && (
            <Badge 
              variant={currentQuality >= 0.8 ? 'default' : 'secondary'}
              className="ml-1"
            >
              {Math.round(currentQuality * 100)}%
            </Badge>
          )}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Workflow Refinement
          </DialogTitle>
          <DialogDescription>
            Improve workflow output quality using multi-LLM orchestration and iterative refinement.
            {currentQuality && (
              <span className="block mt-2">
                Current Quality: <span className={getQualityColor(currentQuality)}>
                  {getQualityLabel(currentQuality)} ({Math.round(currentQuality * 100)}%)
                </span>
              </span>
            )}
          </DialogDescription>
        </DialogHeader>
        
        <div className="mt-4">
          <WorkflowRefinement
            workflowId={workflowId}
            projectId={projectId}
            onRefinementComplete={handleRefinementComplete}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Quick refinement button for inline use
export function QuickRefinementButton({
  workflowId,
  projectId,
  onRefinementComplete,
  className = ""
}: {
  workflowId: string;
  projectId: string;
  onRefinementComplete?: (result: any) => void;
  className?: string;
}) {
  const [isRefining, setIsRefining] = useState(false);

  const handleQuickRefinement = async () => {
    setIsRefining(true);
    
    try {
      // Use default refinement settings for quick refinement
      const response = await apiClient.makeAuthenticatedRequest('/api/v1/refinement/refine', {
        method: 'POST',
        body: JSON.stringify({
          workflow_id: workflowId,
          strategy: 'iterative_improvement',
          primary_llm: 'deepseek',
          validation_llm: 'claude',
          refinement_llm: 'gpt-4',
          max_iterations: 2,
          quality_threshold: 0.8,
          enable_cross_validation: true,
          enable_question_generation: false
        })
      });

      if (response.ok) {
        const result = await response.json();
        onRefinementComplete?.(result);
      }
    } catch (error) {
      console.error('Quick refinement failed:', error);
    } finally {
      setIsRefining(false);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleQuickRefinement}
      disabled={isRefining}
      className={`flex items-center gap-2 ${className}`}
    >
      {isRefining ? (
        <RefreshCw className="h-3 w-3 animate-spin" />
      ) : (
        <Zap className="h-3 w-3" />
      )}
      {isRefining ? 'Refining...' : 'Quick Refine'}
    </Button>
  );
}

// Quality indicator component
export function QualityIndicator({ 
  quality, 
  showLabel = true, 
  size = 'default' 
}: { 
  quality?: number; 
  showLabel?: boolean;
  size?: 'sm' | 'default' | 'lg';
}) {
  if (!quality) return null;

  const getColor = (quality: number) => {
    if (quality >= 0.8) return 'bg-green-500';
    if (quality >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getLabel = (quality: number) => {
    if (quality >= 0.9) return 'Excellent';
    if (quality >= 0.8) return 'Good';
    if (quality >= 0.6) return 'Fair';
    return 'Poor';
  };

  const sizeClasses = {
    sm: 'h-2 w-2',
    default: 'h-3 w-3',
    lg: 'h-4 w-4'
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`rounded-full ${getColor(quality)} ${sizeClasses[size]}`} />
      {showLabel && (
        <span className="text-sm text-gray-600">
          {getLabel(quality)} ({Math.round(quality * 100)}%)
        </span>
      )}
    </div>
  );
}
