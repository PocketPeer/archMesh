"""
Workflow management API endpoints.

This module provides endpoints for workflow session management including
starting workflows, monitoring status, and handling human feedback.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import json

from app.core.database import get_db
from app.core.file_storage import file_storage
from app.workflows import ArchitectureWorkflow
from app.schemas.workflow import (
    WorkflowStartRequest,
    WorkflowStatusResponse,
    WorkflowUpdateRequest,
    WorkflowListResponse,
    WorkflowStats,
    AgentExecutionRequest,
    HumanFeedback,
    WorkflowStageEnum,
    AgentTypeEnum,
    AgentExecutionStatusEnum,
    LLMProviderEnum,
    FeedbackTypeEnum,
)
from app.models.workflow_session import WorkflowSession
from app.models.agent_execution import AgentExecution, AgentExecutionStatus
from app.models.project import Project

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/start", response_model=WorkflowStatusResponse, status_code=status.HTTP_201_CREATED)
async def start_workflow(
    workflow_request: WorkflowStartRequest,
    db: AsyncSession = Depends(get_db)
) -> WorkflowStatusResponse:
    """
    Start a new workflow session for a project.
    
    Args:
        workflow_request: Workflow start configuration
        db: Database session
        
    Returns:
        Created workflow session data
        
    Raises:
        HTTPException: 404 if project not found, 400 if validation fails, 500 if database error
    """
    try:
        # Verify project exists
        project_result = await db.execute(
            select(Project).where(Project.id == workflow_request.project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {workflow_request.project_id} not found"
            )
        
        # Check if there's already an active workflow for this project
        active_workflow_result = await db.execute(
            select(WorkflowSession).where(
                and_(
                    WorkflowSession.project_id == workflow_request.project_id,
                    WorkflowSession.is_active == True
                )
            )
        )
        active_workflow = active_workflow_result.scalar_one_or_none()
        
        if active_workflow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project {workflow_request.project_id} already has an active workflow session"
            )
        
        # Create new workflow session
        db_workflow = WorkflowSession(
            project_id=workflow_request.project_id,
            current_stage=workflow_request.initial_stage.value,
            state_data={
                "stage_progress": 0.0,
                "completed_stages": [],
                "stage_results": {},
                "pending_tasks": [],
                "errors": [],
                "metadata": {
                    "started_by": "api_user",  # TODO: Get from auth context
                    "configuration": workflow_request.configuration or {},
                    "context": workflow_request.context or {}
                }
            },
            is_active=True,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        # Add to database
        db.add(db_workflow)
        await db.commit()
        await db.refresh(db_workflow)
        
        # Convert to response schema
        return WorkflowStatusResponse(
            session_id=db_workflow.id,
            project_id=db_workflow.project_id,
            current_stage=WorkflowStageEnum(db_workflow.current_stage),
            state_data={
                "current_stage": WorkflowStageEnum(db_workflow.current_stage),
                "stage_progress": db_workflow.state_data.get("stage_progress", 0.0),
                "completed_stages": [
                    WorkflowStageEnum(stage) for stage in db_workflow.state_data.get("completed_stages", [])
                ],
                "stage_results": db_workflow.state_data.get("stage_results", {}),
                "pending_tasks": db_workflow.state_data.get("pending_tasks", []),
                "errors": db_workflow.state_data.get("errors", []),
                "metadata": db_workflow.state_data.get("metadata", {})
            },
            is_active=db_workflow.is_active,
            started_at=db_workflow.started_at,
            last_activity_at=db_workflow.last_activity,
            completed_at=db_workflow.completed_at,
            agent_executions=[],  # No executions yet
            human_feedback=[],    # No feedback yet
            estimated_completion=None  # TODO: Calculate based on workflow complexity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )


@router.get("/{session_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> WorkflowStatusResponse:
    """
    Get workflow session status and progress.
    
    Args:
        session_id: Workflow session UUID
        db: Database session
        
    Returns:
        Workflow status and progress data
        
    Raises:
        HTTPException: 404 if workflow not found, 500 if database error
    """
    try:
        # Get workflow session with related data
        result = await db.execute(
            select(WorkflowSession)
            .options(selectinload(WorkflowSession.agent_executions))
            .where(WorkflowSession.id == session_id)
        )
        db_workflow = result.scalar_one_or_none()
        
        if not db_workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow session with ID {session_id} not found"
            )
        
        # Get agent executions
        agent_executions = []
        for execution in db_workflow.agent_executions:
            agent_executions.append({
                "agent_type": AgentTypeEnum(execution.agent_type),
                "agent_version": execution.agent_version,
                "input_data": execution.input_data,
                "output_data": execution.output_data,
                "llm_provider": LLMProviderEnum(execution.llm_provider) if execution.llm_provider else None,
                "llm_model": execution.llm_model,
                "prompt_tokens": execution.prompt_tokens,
                "completion_tokens": execution.completion_tokens,
                "cost_usd": execution.cost_usd,
                "duration_seconds": execution.duration_seconds,
                "status": AgentExecutionStatusEnum(execution.status.value),
                "error_message": execution.error_message,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at
            })
        
        # Convert to response schema
        return WorkflowStatusResponse(
            session_id=db_workflow.id,
            project_id=db_workflow.project_id,
            current_stage=WorkflowStageEnum(db_workflow.current_stage),
            state_data={
                "current_stage": WorkflowStageEnum(db_workflow.current_stage),
                "stage_progress": db_workflow.state_data.get("stage_progress", 0.0),
                "completed_stages": [
                    WorkflowStageEnum(stage) for stage in db_workflow.state_data.get("completed_stages", [])
                ],
                "stage_results": db_workflow.state_data.get("stage_results", {}),
                "pending_tasks": db_workflow.state_data.get("pending_tasks", []),
                "errors": db_workflow.state_data.get("errors", []),
                "metadata": db_workflow.state_data.get("metadata", {})
            },
            is_active=db_workflow.is_active,
            started_at=db_workflow.started_at,
            last_activity_at=db_workflow.last_activity,
            completed_at=db_workflow.completed_at,
            agent_executions=agent_executions,
            human_feedback=[],  # TODO: Implement human feedback retrieval
            estimated_completion=None  # TODO: Calculate based on progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )


@router.put("/{session_id}", response_model=WorkflowStatusResponse)
async def update_workflow(
    session_id: UUID,
    workflow_update: WorkflowUpdateRequest,
    db: AsyncSession = Depends(get_db)
) -> WorkflowStatusResponse:
    """
    Update workflow session configuration or state.
    
    Args:
        session_id: Workflow session UUID
        workflow_update: Workflow update data
        db: Database session
        
    Returns:
        Updated workflow status
        
    Raises:
        HTTPException: 404 if workflow not found, 400 if validation fails, 500 if database error
    """
    try:
        # Get existing workflow
        result = await db.execute(
            select(WorkflowSession).where(WorkflowSession.id == session_id)
        )
        db_workflow = result.scalar_one_or_none()
        
        if not db_workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow session with ID {session_id} not found"
            )
        
        # Update fields if provided
        update_data = workflow_update.model_dump(exclude_unset=True)
        
        if "configuration" in update_data and update_data["configuration"] is not None:
            current_metadata = db_workflow.state_data.get("metadata", {})
            current_metadata["configuration"] = update_data["configuration"]
            db_workflow.state_data["metadata"] = current_metadata
        
        if "context" in update_data and update_data["context"] is not None:
            current_metadata = db_workflow.state_data.get("metadata", {})
            current_metadata["context"] = update_data["context"]
            db_workflow.state_data["metadata"] = current_metadata
        
        if "force_stage" in update_data and update_data["force_stage"] is not None:
            db_workflow.current_stage = update_data["force_stage"].value
            # Reset stage progress when forcing a stage
            db_workflow.state_data["stage_progress"] = 0.0
        
        if "pause" in update_data and update_data["pause"] is not None:
            db_workflow.is_active = not update_data["pause"]
            if update_data["pause"]:
                db_workflow.last_activity = datetime.utcnow()
        
        # Update last activity
        db_workflow.last_activity = datetime.utcnow()
        
        # Commit changes
        await db.commit()
        await db.refresh(db_workflow)
        
        # Return updated status (reuse the get_workflow_status logic)
        return await get_workflow_status(session_id, db)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow: {str(e)}"
        )


@router.post("/{session_id}/review", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_human_review(
    session_id: UUID,
    feedback: HumanFeedback,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Submit human feedback/review for a workflow session.
    
    Args:
        session_id: Workflow session UUID
        feedback: Human feedback data
        db: Database session
        
    Returns:
        Confirmation of feedback submission
        
    Raises:
        HTTPException: 404 if workflow not found, 500 if database error
    """
    try:
        # Verify workflow exists
        result = await db.execute(
            select(WorkflowSession).where(WorkflowSession.id == session_id)
        )
        db_workflow = result.scalar_one_or_none()
        
        if not db_workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow session with ID {session_id} not found"
            )
        
        # Add feedback to workflow state
        if "human_feedback" not in db_workflow.state_data:
            db_workflow.state_data["human_feedback"] = []
        
        feedback_data = {
            "id": feedback.id,
            "feedback_type": feedback.feedback_type.value,
            "stage": feedback.stage.value,
            "content": feedback.content,
            "provided_by": feedback.provided_by,
            "provided_at": feedback.provided_at.isoformat(),
            "related_items": feedback.related_items,
            "action_required": feedback.action_required,
            "resolved": feedback.resolved,
            "resolved_at": feedback.resolved_at.isoformat() if feedback.resolved_at else None
        }
        
        db_workflow.state_data["human_feedback"].append(feedback_data)
        
        # Update last activity
        db_workflow.last_activity = datetime.utcnow()
        
        # Commit changes
        await db.commit()
        
        return {
            "message": "Human feedback submitted successfully",
            "feedback_id": feedback.id,
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit human feedback: {str(e)}"
        )


@router.post("/{session_id}/execute-agent", response_model=dict, status_code=status.HTTP_201_CREATED)
async def execute_agent(
    session_id: UUID,
    agent_request: AgentExecutionRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Manually trigger an agent execution within a workflow session.
    
    Args:
        session_id: Workflow session UUID
        agent_request: Agent execution request
        db: Database session
        
    Returns:
        Agent execution details
        
    Raises:
        HTTPException: 404 if workflow not found, 500 if database error
    """
    try:
        # Verify workflow exists
        result = await db.execute(
            select(WorkflowSession).where(WorkflowSession.id == session_id)
        )
        db_workflow = result.scalar_one_or_none()
        
        if not db_workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow session with ID {session_id} not found"
            )
        
        # Create agent execution record
        db_execution = AgentExecution(
            session_id=session_id,
            agent_type=agent_request.agent_type.value,
            agent_version="1.0.0",  # TODO: Get from agent registry
            input_data=agent_request.input_data,
            output_data={},  # Will be populated after execution
            llm_provider=agent_request.llm_provider.value if agent_request.llm_provider else None,
            llm_model=agent_request.llm_model,
            status=AgentExecutionStatus.PENDING,
            started_at=datetime.utcnow()
        )
        
        # Add to database
        db.add(db_execution)
        await db.commit()
        await db.refresh(db_execution)
        
        # TODO: Actually execute the agent (this would be async)
        # For now, just return the execution record
        
        return {
            "message": "Agent execution started",
            "execution_id": str(db_execution.id),
            "session_id": session_id,
            "agent_type": agent_request.agent_type.value,
            "status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute agent: {str(e)}"
        )


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(
    skip: int = Query(0, ge=0, description="Number of workflows to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of workflows to return"),
    project_id: Optional[UUID] = Query(None, description="Filter by project ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    stage: Optional[WorkflowStageEnum] = Query(None, description="Filter by current stage"),
    db: AsyncSession = Depends(get_db)
) -> WorkflowListResponse:
    """
    List workflow sessions with filtering and pagination.
    
    Args:
        skip: Number of workflows to skip
        limit: Maximum number of workflows to return
        project_id: Filter by project ID
        is_active: Filter by active status
        stage: Filter by current stage
        db: Database session
        
    Returns:
        Paginated list of workflow sessions
        
    Raises:
        HTTPException: 500 if database error
    """
    try:
        # Build query with filters
        query = select(WorkflowSession)
        count_query = select(func.count(WorkflowSession.id))
        
        # Apply filters
        filters = []
        
        if project_id:
            filters.append(WorkflowSession.project_id == project_id)
        
        if is_active is not None:
            filters.append(WorkflowSession.is_active == is_active)
        
        if stage:
            filters.append(WorkflowSession.current_stage == stage.value)
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(WorkflowSession.started_at.desc()).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        db_workflows = result.scalars().all()
        
        # Convert to response schemas (simplified for list view)
        workflows = []
        for workflow in db_workflows:
            workflows.append(WorkflowStatusResponse(
                session_id=workflow.id,
                project_id=workflow.project_id,
                current_stage=WorkflowStageEnum(workflow.current_stage),
                state_data={
                    "current_stage": WorkflowStageEnum(workflow.current_stage),
                    "stage_progress": workflow.state_data.get("stage_progress", 0.0),
                    "completed_stages": [
                        WorkflowStageEnum(stage) for stage in workflow.state_data.get("completed_stages", [])
                    ],
                    "stage_results": workflow.state_data.get("stage_results", {}),
                    "pending_tasks": workflow.state_data.get("pending_tasks", []),
                    "errors": workflow.state_data.get("errors", []),
                    "metadata": workflow.state_data.get("metadata", {})
                },
                is_active=workflow.is_active,
                started_at=workflow.started_at,
                last_activity_at=workflow.last_activity,
                completed_at=workflow.completed_at,
                agent_executions=[],  # Not loaded for list view
                human_feedback=[],    # Not loaded for list view
                estimated_completion=None
            ))
        
        # Calculate pagination info
        has_next = (skip + limit) < total
        
        return WorkflowListResponse(
            workflows=workflows,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            has_next=has_next
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.get("/stats/overview", response_model=WorkflowStats)
async def get_workflow_stats(
    db: AsyncSession = Depends(get_db)
) -> WorkflowStats:
    """
    Get overall workflow statistics.
    
    Args:
        db: Database session
        
    Returns:
        Overall workflow statistics
        
    Raises:
        HTTPException: 500 if database error
    """
    try:
        # Get total workflows
        total_result = await db.execute(select(func.count(WorkflowSession.id)))
        total_workflows = total_result.scalar()
        
        # Get active workflows
        active_result = await db.execute(
            select(func.count(WorkflowSession.id)).where(WorkflowSession.is_active == True)
        )
        active_workflows = active_result.scalar()
        
        # Get completed workflows
        completed_result = await db.execute(
            select(func.count(WorkflowSession.id)).where(WorkflowSession.completed_at.isnot(None))
        )
        completed_workflows = completed_result.scalar()
        
        # Get failed workflows (workflows with errors)
        failed_result = await db.execute(
            select(func.count(WorkflowSession.id)).where(
                WorkflowSession.state_data["errors"].astext != "[]"
            )
        )
        failed_workflows = failed_result.scalar()
        
        # Get average duration
        duration_result = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', WorkflowSession.completed_at - WorkflowSession.started_at) / 60
                )
            ).where(WorkflowSession.completed_at.isnot(None))
        )
        avg_duration = duration_result.scalar() or 0.0
        
        # Get workflows by stage
        stage_result = await db.execute(
            select(WorkflowSession.current_stage, func.count(WorkflowSession.id))
            .group_by(WorkflowSession.current_stage)
        )
        workflows_by_stage = {row[0]: row[1] for row in stage_result.fetchall()}
        
        # Get agent execution stats
        agent_total_result = await db.execute(select(func.count(AgentExecution.id)))
        total_agent_executions = agent_total_result.scalar()
        
        agent_success_result = await db.execute(
            select(func.count(AgentExecution.id)).where(AgentExecution.status == AgentExecutionStatus.SUCCESS)
        )
        successful_executions = agent_success_result.scalar()
        
        # Get total cost
        cost_result = await db.execute(
            select(func.sum(AgentExecution.cost_usd)).where(AgentExecution.cost_usd.isnot(None))
        )
        total_cost = cost_result.scalar() or 0.0
        
        return WorkflowStats(
            total_workflows=total_workflows,
            active_workflows=active_workflows,
            completed_workflows=completed_workflows,
            failed_workflows=failed_workflows,
            average_duration_minutes=avg_duration,
            workflows_by_stage=workflows_by_stage,
            total_agent_executions=total_agent_executions,
            successful_executions=successful_executions,
            total_cost_usd=total_cost
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow stats: {str(e)}"
        )


# New workflow management endpoints

@router.post("/start-architecture", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def start_architecture_workflow(
    file: UploadFile = File(..., description="Requirements document to process"),
    project_id: str = Form(..., description="Project ID"),
    domain: str = Form("cloud-native", description="Project domain"),
    project_context: Optional[str] = Form(None, description="Additional project context"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start a new architecture workflow with document upload.
    
    Args:
        file: Requirements document file
        project_id: Project ID
        domain: Project domain (cloud-native, data-platform, enterprise)
        project_context: Optional project context
        db: Database session
        
    Returns:
        Session ID and initial workflow status
        
    Raises:
        HTTPException: 400 if file validation fails, 404 if project not found, 500 if workflow fails
    """
    try:
        # Verify project exists
        project_result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Save uploaded file
        file_info = await file_storage.save_uploaded_file(file, None)
        
        # Initialize workflow
        workflow = ArchitectureWorkflow()
        
        # Start workflow
        session_id, initial_result = await workflow.start(
            project_id=project_id,
            document_path=file_info["file_path"],
            domain=domain,
            project_context=project_context,
            db=db
        )
        
        # Move file to processed directory
        file_storage.move_to_processed(file_info["file_id"])
        
        return {
            "session_id": session_id,
            "project_id": project_id,
            "file_info": {
                "file_id": file_info["file_id"],
                "original_filename": file_info["original_filename"],
                "file_size": file_info["file_size"]
            },
            "workflow_status": {
                "current_stage": initial_result.get("current_stage", "unknown"),
                "started_at": initial_result.get("started_at"),
                "is_active": True
            },
            "message": "Workflow started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )


@router.get("/{session_id}/status", response_model=Dict[str, Any])
async def get_workflow_status_new(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current workflow status and progress.
    
    Args:
        session_id: Workflow session ID
        db: Database session
        
    Returns:
        Current workflow state and progress
        
    Raises:
        HTTPException: 404 if session not found, 500 if status retrieval fails
    """
    try:
        # Initialize workflow
        workflow = ArchitectureWorkflow()
        
        # Get workflow status
        status = await workflow.get_status(session_id)
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow session {session_id} not found"
            )
        
        return {
            "session_id": session_id,
            "current_stage": status.get("current_stage", "unknown"),
            "project_id": status.get("project_id"),
            "domain": status.get("domain"),
            "is_active": status.get("current_stage") not in ["completed", "failed", "cancelled"],
            "started_at": status.get("started_at"),
            "last_updated": status.get("last_updated"),
            "requirements": status.get("requirements"),
            "architecture": status.get("architecture"),
            "errors": status.get("errors", []),
            "review_history": status.get("review_history", []),
            "waiting_for_review": status.get("current_stage") in ["requirements_review", "architecture_review"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )


@router.post("/{session_id}/review", response_model=Dict[str, Any])
async def submit_workflow_review(
    session_id: str,
    decision: str = Form(..., description="Review decision: approved, rejected, needs_info"),
    comments: Optional[str] = Form(None, description="Review comments"),
    constraints: Optional[str] = Form(None, description="JSON string of constraints"),
    preferences: Optional[str] = Form(None, description="JSON string of preferences"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Submit human feedback and continue workflow.
    
    Args:
        session_id: Workflow session ID
        decision: Review decision (approved, rejected, needs_info)
        comments: Optional review comments
        constraints: Optional JSON constraints
        preferences: Optional JSON preferences
        db: Database session
        
    Returns:
        Updated workflow status after processing feedback
        
    Raises:
        HTTPException: 400 if validation fails, 404 if session not found, 500 if processing fails
    """
    try:
        # Validate decision
        valid_decisions = ["approved", "rejected", "needs_info"]
        if decision not in valid_decisions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid decision '{decision}'. Must be one of: {', '.join(valid_decisions)}"
            )
        
        # Parse constraints and preferences
        parsed_constraints = {}
        parsed_preferences = []
        
        if constraints:
            try:
                parsed_constraints = json.loads(constraints)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON format for constraints"
                )
        
        if preferences:
            try:
                parsed_preferences = json.loads(preferences)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid JSON format for preferences"
                )
        
        # Prepare human feedback
        human_feedback = {
            "decision": decision,
            "comments": comments,
            "constraints": parsed_constraints,
            "preferences": parsed_preferences,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Initialize workflow
        workflow = ArchitectureWorkflow()
        
        # Continue workflow with feedback
        result = await workflow.continue_workflow(session_id, human_feedback)
        
        return {
            "session_id": session_id,
            "feedback_submitted": True,
            "decision": decision,
            "updated_status": {
                "current_stage": result.get("current_stage", "unknown"),
                "last_updated": result.get("last_updated"),
                "is_active": result.get("current_stage") not in ["completed", "failed", "cancelled"]
            },
            "message": f"Feedback submitted successfully. Workflow is now in stage: {result.get('current_stage', 'unknown')}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit review: {str(e)}"
        )


@router.get("/{session_id}/requirements", response_model=Dict[str, Any])
async def get_workflow_requirements(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get parsed requirements from workflow.
    
    Args:
        session_id: Workflow session ID
        db: Database session
        
    Returns:
        Parsed requirements data
        
    Raises:
        HTTPException: 404 if session not found or requirements not available, 500 if retrieval fails
    """
    try:
        # Initialize workflow
        workflow = ArchitectureWorkflow()
        
        # Get workflow status
        workflow_status = await workflow.get_status(session_id)
        
        if not workflow_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow session {session_id} not found"
            )
        
        requirements = workflow_status.get("requirements")
        if not requirements:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Requirements not available for session {session_id}. Workflow may not have reached requirements parsing stage."
            )
        
        return {
            "session_id": session_id,
            "requirements": requirements,
            "parsed_at": workflow_status.get("requirements_completed_at"),
            "confidence_score": requirements.get("confidence_score", 0.0),
            "summary": {
                "business_goals_count": len(requirements.get("structured_requirements", {}).get("business_goals", [])),
                "functional_requirements_count": len(requirements.get("structured_requirements", {}).get("functional_requirements", [])),
                "stakeholders_count": len(requirements.get("structured_requirements", {}).get("stakeholders", [])),
                "clarification_questions_count": len(requirements.get("clarification_questions", [])),
                "identified_gaps_count": len(requirements.get("identified_gaps", []))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get requirements: {str(e)}"
        )


@router.get("/{session_id}/architecture", response_model=Dict[str, Any])
async def get_workflow_architecture(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get generated architecture from workflow.
    
    Args:
        session_id: Workflow session ID
        db: Database session
        
    Returns:
        Generated architecture data
        
    Raises:
        HTTPException: 404 if session not found or architecture not available, 500 if retrieval fails
    """
    try:
        # Initialize workflow
        workflow = ArchitectureWorkflow()
        
        # Get workflow status
        status = await workflow.get_status(session_id)
        
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow session {session_id} not found"
            )
        
        architecture = status.get("architecture")
        if not architecture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Architecture not available for session {session_id}. Workflow may not have reached architecture design stage."
            )
        
        return {
            "session_id": session_id,
            "architecture": architecture,
            "generated_at": status.get("architecture_completed_at"),
            "quality_score": architecture.get("quality_score", 0.0),
            "summary": {
                "architecture_style": architecture.get("architecture_overview", {}).get("style", "unknown"),
                "components_count": len(architecture.get("components", [])),
                "alternatives_count": len(architecture.get("alternatives", [])),
                "implementation_phases_count": len(architecture.get("implementation_plan", {}).get("phases", [])),
                "risks_count": len(architecture.get("implementation_plan", {}).get("risks", []))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get architecture: {str(e)}"
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_workflow(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Cancel a running workflow.
    
    Args:
        session_id: Workflow session ID
        db: Database session
        
    Raises:
        HTTPException: 404 if session not found, 500 if cancellation fails
    """
    try:
        # Initialize workflow
        workflow = ArchitectureWorkflow()
        
        # Cancel workflow
        cancelled = await workflow.cancel_workflow(session_id)
        
        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to cancel workflow session {session_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}"
        )
