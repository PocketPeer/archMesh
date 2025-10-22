"""
Workflow Refinement API Endpoints

This module provides API endpoints for workflow refinement functionality,
including multi-LLM orchestration, quality assessment, and iterative improvement.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.refinement import (
    WorkflowRefinementService,
    RefinementConfig,
    RefinementStrategy,
    get_refinement_service
)
from app.models.user import User
from app.models.workflow_session import WorkflowSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/refinement", tags=["refinement"])


class RefinementRequest(BaseModel):
    """Request model for workflow refinement"""
    workflow_id: str = Field(..., description="ID of the workflow to refine")
    strategy: RefinementStrategy = Field(..., description="Refinement strategy to use")
    primary_llm: str = Field(default="deepseek", description="Primary LLM for refinement")
    validation_llm: str = Field(default="claude", description="LLM for validation")
    refinement_llm: str = Field(default="gpt-4", description="LLM for refinement")
    max_iterations: int = Field(default=3, ge=1, le=10, description="Maximum refinement iterations")
    quality_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Quality threshold to achieve")
    enable_cross_validation: bool = Field(default=True, description="Enable cross-validation")
    enable_question_generation: bool = Field(default=True, description="Enable question generation")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional user context")


class RefinementResponse(BaseModel):
    """Response model for workflow refinement"""
    refinement_id: str
    workflow_id: str
    status: str
    quality_improvement: float
    iterations_performed: int
    llm_used: str
    refinement_notes: List[str]
    questions_generated: List[Dict[str, Any]]
    timestamp: str


class QualityAssessmentRequest(BaseModel):
    """Request model for quality assessment"""
    workflow_id: str = Field(..., description="ID of the workflow to assess")
    llm_provider: str = Field(default="claude", description="LLM provider for assessment")


class QualityAssessmentResponse(BaseModel):
    """Response model for quality assessment"""
    workflow_id: str
    completeness: float
    consistency: float
    accuracy: float
    relevance: float
    overall: float
    confidence: float
    notes: str


class QuestionGenerationRequest(BaseModel):
    """Request model for question generation"""
    workflow_id: str = Field(..., description="ID of the workflow")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional user context")


class QuestionGenerationResponse(BaseModel):
    """Response model for question generation"""
    workflow_id: str
    questions: List[Dict[str, Any]]
    total_questions: int


@router.post("/refine", response_model=RefinementResponse)
async def refine_workflow(
    request: RefinementRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refine a workflow output using multi-LLM orchestration
    
    This endpoint initiates the refinement process for a workflow output,
    using different LLMs for validation, critique, and improvement.
    """
    try:
        # Verify workflow exists and user has access
        result = await db.execute(
            select(WorkflowSession).where(
                WorkflowSession.session_id == request.workflow_id
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Create refinement configuration
        config = RefinementConfig(
            strategy=request.strategy,
            primary_llm=request.primary_llm,
            validation_llm=request.validation_llm,
            refinement_llm=request.refinement_llm,
            max_iterations=request.max_iterations,
            quality_threshold=request.quality_threshold,
            enable_cross_validation=request.enable_cross_validation,
            enable_question_generation=request.enable_question_generation
        )
        
        # Get refinement service
        refinement_service = get_refinement_service()
        
        # Perform refinement
        result = await refinement_service.refine_workflow_output(
            workflow_id=request.workflow_id,
            config=config,
            user_context=request.user_context
        )
        
        # Store refinement result (you might want to create a RefinementResult model)
        refinement_id = f"ref_{request.workflow_id}_{result.timestamp.isoformat()}"
        
        return RefinementResponse(
            refinement_id=refinement_id,
            workflow_id=request.workflow_id,
            status="completed",
            quality_improvement=result.quality_improvement,
            iterations_performed=result.iterations_performed,
            llm_used=result.llm_used,
            refinement_notes=result.refinement_notes,
            questions_generated=result.questions_generated,
            timestamp=result.timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error refining workflow {request.workflow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


@router.post("/assess-quality", response_model=QualityAssessmentResponse)
async def assess_workflow_quality(
    request: QualityAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Assess the quality of a workflow output
    
    This endpoint evaluates the quality of a workflow output across multiple
    dimensions: completeness, consistency, accuracy, and relevance.
    """
    try:
        # Verify workflow exists
        result = await db.execute(
            select(WorkflowSession).where(
                WorkflowSession.session_id == request.workflow_id
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get refinement service
        refinement_service = get_refinement_service()
        
        # Get workflow output
        output = await refinement_service._get_workflow_output(request.workflow_id)
        if not output:
            raise HTTPException(status_code=404, detail="Workflow output not found")
        
        # Assess quality
        quality_score = await refinement_service._validate_output(
            output, request.llm_provider, request.workflow_id
        )
        
        return QualityAssessmentResponse(
            workflow_id=request.workflow_id,
            completeness=quality_score.completeness,
            consistency=quality_score.consistency,
            accuracy=quality_score.accuracy,
            relevance=quality_score.relevance,
            overall=quality_score.overall,
            confidence=quality_score.confidence,
            notes=f"Quality assessment completed using {request.llm_provider}"
        )
        
    except Exception as e:
        logger.error(f"Error assessing quality for workflow {request.workflow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quality assessment failed: {str(e)}")


@router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_improvement_questions(
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate questions to improve workflow output quality
    
    This endpoint generates targeted questions that would help improve
    the quality and completeness of a workflow output.
    """
    try:
        # Verify workflow exists
        result = await db.execute(
            select(WorkflowSession).where(
                WorkflowSession.session_id == request.workflow_id
            )
        )
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get refinement service
        refinement_service = get_refinement_service()
        
        # Get workflow output
        output = await refinement_service._get_workflow_output(request.workflow_id)
        if not output:
            raise HTTPException(status_code=404, detail="Workflow output not found")
        
        # Generate questions
        questions = await refinement_service._generate_questions(
            output, request.workflow_id, request.user_context
        )
        
        return QuestionGenerationResponse(
            workflow_id=request.workflow_id,
            questions=questions,
            total_questions=len(questions)
        )
        
    except Exception as e:
        logger.error(f"Error generating questions for workflow {request.workflow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")


@router.get("/strategies")
async def get_refinement_strategies():
    """
    Get available refinement strategies
    
    Returns the list of available refinement strategies that can be used
    for workflow output improvement.
    """
    return {
        "strategies": [
            {
                "value": strategy.value,
                "name": strategy.name.replace("_", " ").title(),
                "description": _get_strategy_description(strategy)
            }
            for strategy in RefinementStrategy
        ]
    }


@router.get("/llm-providers")
async def get_available_llm_providers():
    """
    Get available LLM providers for refinement
    
    Returns the list of available LLM providers that can be used
    for different refinement tasks.
    """
    return {
        "providers": [
            {
                "id": "deepseek",
                "name": "DeepSeek",
                "description": "Good for reasoning and analysis tasks",
                "best_for": ["validation", "analysis"]
            },
            {
                "id": "claude",
                "name": "Claude",
                "description": "Excellent for critique and question generation",
                "best_for": ["validation", "question_generation", "critique"]
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "Strong for synthesis and refinement",
                "best_for": ["refinement", "synthesis", "improvement"]
            },
            {
                "id": "ollama",
                "name": "Ollama (Local)",
                "description": "Local model for privacy and cost efficiency",
                "best_for": ["all_tasks", "privacy", "cost_effective"]
            }
        ]
    }


def _get_strategy_description(strategy: RefinementStrategy) -> str:
    """Get description for refinement strategy"""
    descriptions = {
        RefinementStrategy.VALIDATION_ONLY: "Only validate output quality without refinement",
        RefinementStrategy.CROSS_VALIDATION: "Use multiple LLMs to validate and cross-check outputs",
        RefinementStrategy.ITERATIVE_IMPROVEMENT: "Iteratively improve output through multiple refinement cycles",
        RefinementStrategy.MULTI_LLM_SYNTHESIS: "Synthesize outputs from multiple LLMs for best results"
    }
    return descriptions.get(strategy, "Unknown strategy")
