"""
Workflow Diagram Integration API Endpoints

This module provides API endpoints for integrating diagram generation
into the workflow system, allowing automatic diagram generation during
workflow execution.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.workflow_diagram_integration import WorkflowDiagramIntegration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow-diagrams", tags=["workflow-diagrams"])

class WorkflowDiagramRequest(BaseModel):
    """Request model for workflow diagram generation"""
    project_id: str = Field(..., description="Project ID")
    workflow_stage: str = Field(..., description="Current workflow stage")
    workflow_data: Dict[str, Any] = Field(..., description="Workflow execution data")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class WorkflowDiagramResponse(BaseModel):
    """Response model for workflow diagram generation"""
    diagrams: Dict[str, Any] = Field(..., description="Generated diagrams")
    generation_results: Dict[str, Any] = Field(..., description="Generation results")
    total_diagrams: int = Field(..., description="Total number of diagrams generated")
    successful_generations: int = Field(..., description="Number of successful generations")

class ProjectDiagramsRequest(BaseModel):
    """Request model for getting project diagrams"""
    project_id: str = Field(..., description="Project ID")

class ProjectDiagramsResponse(BaseModel):
    """Response model for project diagrams"""
    project_id: str = Field(..., description="Project ID")
    diagrams: Dict[str, Any] = Field(..., description="Project diagrams organized by type")
    total_diagrams: int = Field(..., description="Total number of diagrams")
    diagram_types: List[str] = Field(..., description="Available diagram types")

class RegenerateDiagramsRequest(BaseModel):
    """Request model for regenerating diagrams"""
    project_id: str = Field(..., description="Project ID")
    diagram_types: List[str] = Field(..., description="Diagram types to regenerate")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class RegenerateDiagramsResponse(BaseModel):
    """Response model for diagram regeneration"""
    project_id: str = Field(..., description="Project ID")
    regeneration_results: Dict[str, Any] = Field(..., description="Regeneration results")
    total_requested: int = Field(..., description="Total number of diagrams requested")
    successful_regenerations: int = Field(..., description="Number of successful regenerations")

@router.post("/generate", response_model=WorkflowDiagramResponse)
async def generate_workflow_diagrams(
    request: WorkflowDiagramRequest,
    current_user: User = Depends(get_current_user),
    diagram_service: WorkflowDiagramIntegration = Depends()
) -> WorkflowDiagramResponse:
    """
    Generate diagrams for a specific workflow stage.
    
    This endpoint automatically generates appropriate diagrams based on the
    current workflow stage and available data.
    """
    try:
        logger.info(f"Generating workflow diagrams for project {request.project_id}, stage {request.workflow_stage}")
        
        result = await diagram_service.generate_workflow_diagrams(
            project_id=request.project_id,
            workflow_stage=request.workflow_stage,
            workflow_data=request.workflow_data,
            context=request.context
        )
        
        return WorkflowDiagramResponse(
            diagrams=result.get("diagrams", {}),
            generation_results=result.get("generation_results", {}),
            total_diagrams=result.get("total_diagrams", 0),
            successful_generations=result.get("successful_generations", 0)
        )
        
    except Exception as e:
        logger.error(f"Failed to generate workflow diagrams: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate workflow diagrams: {str(e)}"
        )

@router.get("/project/{project_id}", response_model=ProjectDiagramsResponse)
async def get_project_diagrams(
    project_id: str,
    current_user: User = Depends(get_current_user),
    diagram_service: WorkflowDiagramIntegration = Depends()
) -> ProjectDiagramsResponse:
    """
    Get all diagrams for a project.
    
    This endpoint retrieves all diagrams associated with a project,
    organized by diagram type.
    """
    try:
        logger.info(f"Retrieving diagrams for project {project_id}")
        
        result = await diagram_service.get_project_diagrams(project_id)
        
        return ProjectDiagramsResponse(
            project_id=result.get("project_id", project_id),
            diagrams=result.get("diagrams", {}),
            total_diagrams=result.get("total_diagrams", 0),
            diagram_types=result.get("diagram_types", [])
        )
        
    except Exception as e:
        logger.error(f"Failed to get project diagrams: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get project diagrams: {str(e)}"
        )

@router.post("/regenerate", response_model=RegenerateDiagramsResponse)
async def regenerate_diagrams(
    request: RegenerateDiagramsRequest,
    current_user: User = Depends(get_current_user),
    diagram_service: WorkflowDiagramIntegration = Depends()
) -> RegenerateDiagramsResponse:
    """
    Regenerate specific diagram types for a project.
    
    This endpoint allows regenerating specific diagram types with updated
    context and data.
    """
    try:
        logger.info(f"Regenerating diagrams for project {request.project_id}, types: {request.diagram_types}")
        
        result = await diagram_service.regenerate_diagrams(
            project_id=request.project_id,
            diagram_types=request.diagram_types,
            context=request.context
        )
        
        return RegenerateDiagramsResponse(
            project_id=result.get("project_id", request.project_id),
            regeneration_results=result.get("regeneration_results", {}),
            total_requested=result.get("total_requested", 0),
            successful_regenerations=result.get("successful_regenerations", 0)
        )
        
    except Exception as e:
        logger.error(f"Failed to regenerate diagrams: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate diagrams: {str(e)}"
        )

@router.post("/workflow/{workflow_id}/generate")
async def generate_workflow_diagrams_async(
    workflow_id: str,
    request: WorkflowDiagramRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    diagram_service: WorkflowDiagramIntegration = Depends()
) -> Dict[str, Any]:
    """
    Generate diagrams asynchronously for a workflow.
    
    This endpoint starts diagram generation in the background and returns
    immediately with a task ID for tracking progress.
    """
    try:
        logger.info(f"Starting async diagram generation for workflow {workflow_id}")
        
        # Add diagram generation to background tasks
        background_tasks.add_task(
            diagram_service.generate_workflow_diagrams,
            project_id=request.project_id,
            workflow_stage=request.workflow_stage,
            workflow_data=request.workflow_data,
            context=request.context
        )
        
        return {
            "workflow_id": workflow_id,
            "project_id": request.project_id,
            "status": "started",
            "message": "Diagram generation started in background"
        }
        
    except Exception as e:
        logger.error(f"Failed to start async diagram generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start diagram generation: {str(e)}"
        )

@router.get("/workflow/{workflow_id}/status")
async def get_workflow_diagram_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the status of diagram generation for a workflow.
    
    This endpoint provides status information about diagram generation
    tasks for a specific workflow.
    """
    try:
        # TODO: Implement workflow diagram status tracking
        # This would require a task queue system like Celery or similar
        
        return {
            "workflow_id": workflow_id,
            "status": "not_implemented",
            "message": "Workflow diagram status tracking not yet implemented"
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow diagram status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get diagram status: {str(e)}"
        )
