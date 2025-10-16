"""
Workflow-related Pydantic schemas for API request/response validation.

This module contains schemas for workflow session management,
agent execution tracking, and human feedback handling.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum


class WorkflowStageEnum(str, Enum):
    """Workflow stage enumeration."""
    
    DOCUMENT_ANALYSIS = "document_analysis"
    REQUIREMENT_EXTRACTION = "requirement_extraction"
    REQUIREMENT_REVIEW = "requirement_review"
    ARCHITECTURE_DESIGN = "architecture_design"
    ARCHITECTURE_REVIEW = "architecture_review"
    TECHNOLOGY_SELECTION = "technology_selection"
    FINAL_REVIEW = "final_review"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentTypeEnum(str, Enum):
    """Agent type enumeration."""
    
    DOCUMENT_ANALYZER = "document_analyzer"
    REQUIREMENT_EXTRACTOR = "requirement_extractor"
    REQUIREMENT_REVIEWER = "requirement_reviewer"
    ARCHITECTURE_DESIGNER = "architecture_designer"
    ARCHITECTURE_REVIEWER = "architecture_reviewer"
    TECHNOLOGY_ADVISOR = "technology_advisor"
    QUALITY_ASSURANCE = "quality_assurance"


class AgentExecutionStatusEnum(str, Enum):
    """Agent execution status enumeration."""
    
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class LLMProviderEnum(str, Enum):
    """LLM provider enumeration."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    AWS = "aws"


class FeedbackTypeEnum(str, Enum):
    """Feedback type enumeration."""
    
    APPROVAL = "approval"
    REJECTION = "rejection"
    MODIFICATION = "modification"
    CLARIFICATION = "clarification"
    SUGGESTION = "suggestion"


class WorkflowStartRequest(BaseModel):
    """
    Schema for starting a new workflow session.
    
    Used to initiate a workflow for a project.
    """
    
    project_id: UUID = Field(
        ...,
        description="Project ID to start workflow for",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    initial_stage: WorkflowStageEnum = Field(
        WorkflowStageEnum.DOCUMENT_ANALYSIS,
        description="Initial workflow stage",
        examples=[WorkflowStageEnum.DOCUMENT_ANALYSIS]
    )
    configuration: Optional[Dict[str, Any]] = Field(
        None,
        description="Workflow configuration options",
        examples=[{"auto_approve": False, "max_iterations": 3, "timeout_minutes": 60}]
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for the workflow",
        examples=[{"priority": "high", "domain_expertise": "e-commerce"}]
    )
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowStateData(BaseModel):
    """
    Schema for workflow state data.
    
    Represents the current state of a workflow session.
    """
    
    current_stage: WorkflowStageEnum = Field(
        ...,
        description="Current workflow stage",
        examples=[WorkflowStageEnum.REQUIREMENT_EXTRACTION]
    )
    stage_progress: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Progress within current stage (0.0 to 1.0)",
        examples=[0.75]
    )
    completed_stages: List[WorkflowStageEnum] = Field(
        ...,
        description="List of completed stages",
        examples=[[WorkflowStageEnum.DOCUMENT_ANALYSIS]]
    )
    stage_results: Dict[str, Any] = Field(
        ...,
        description="Results from completed stages",
        examples=[{"document_analysis": {"documents_processed": 5, "confidence": 0.85}}]
    )
    pending_tasks: List[str] = Field(
        ...,
        description="List of pending tasks",
        examples=[["extract_functional_requirements", "generate_clarification_questions"]]
    )
    errors: List[Dict[str, Any]] = Field(
        ...,
        description="List of errors encountered",
        examples=[[{"stage": "document_analysis", "error": "Failed to parse PDF", "timestamp": "2024-01-15T10:30:00Z"}]]
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Additional workflow metadata",
        examples=[{"started_by": "user123", "estimated_completion": "2024-01-15T12:00:00Z"}]
    )
    
    model_config = ConfigDict(from_attributes=True)


class AgentExecutionData(BaseModel):
    """
    Schema for agent execution data.
    
    Represents input/output data for agent executions.
    """
    
    agent_type: AgentTypeEnum = Field(
        ...,
        description="Type of agent",
        examples=[AgentTypeEnum.REQUIREMENT_EXTRACTOR]
    )
    agent_version: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Agent version",
        examples=["1.2.0", "v2.1.3"]
    )
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data for the agent",
        examples=[{"documents": ["doc1.pdf", "doc2.docx"], "extraction_config": {"confidence_threshold": 0.8}}]
    )
    output_data: Dict[str, Any] = Field(
        ...,
        description="Output data from the agent",
        examples=[{"requirements": [], "confidence_score": 0.85, "processing_time": 45.2}]
    )
    llm_provider: Optional[LLMProviderEnum] = Field(
        None,
        description="LLM provider used",
        examples=[LLMProviderEnum.OPENAI]
    )
    llm_model: Optional[str] = Field(
        None,
        description="LLM model used",
        examples=["gpt-4", "claude-3-sonnet"]
    )
    prompt_tokens: Optional[int] = Field(
        None,
        ge=0,
        description="Number of prompt tokens used",
        examples=[1500]
    )
    completion_tokens: Optional[int] = Field(
        None,
        ge=0,
        description="Number of completion tokens used",
        examples=[800]
    )
    cost_usd: Optional[float] = Field(
        None,
        ge=0.0,
        description="Cost of execution in USD",
        examples=[0.05]
    )
    duration_seconds: Optional[float] = Field(
        None,
        ge=0.0,
        description="Execution duration in seconds",
        examples=[45.2]
    )
    status: AgentExecutionStatusEnum = Field(
        ...,
        description="Execution status",
        examples=[AgentExecutionStatusEnum.SUCCESS]
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if execution failed",
        examples=["Connection timeout after 30 seconds"]
    )
    started_at: datetime = Field(
        ...,
        description="Execution start timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Execution completion timestamp",
        examples=["2024-01-15T10:30:45Z"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class HumanFeedback(BaseModel):
    """
    Schema for human feedback.
    
    Represents feedback provided by humans during workflow execution.
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Feedback identifier",
        examples=["feedback-001", "req-review-001"]
    )
    feedback_type: FeedbackTypeEnum = Field(
        ...,
        description="Type of feedback",
        examples=[FeedbackTypeEnum.APPROVAL]
    )
    stage: WorkflowStageEnum = Field(
        ...,
        description="Workflow stage this feedback relates to",
        examples=[WorkflowStageEnum.REQUIREMENT_REVIEW]
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Feedback content",
        examples=["The requirements look good, but please add more details about the authentication flow"]
    )
    provided_by: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Person who provided the feedback",
        examples=["john.doe@company.com", "user123"]
    )
    provided_at: datetime = Field(
        ...,
        description="Feedback timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    related_items: List[str] = Field(
        ...,
        description="Related items (requirements, components, etc.)",
        examples=[["FR-001", "FR-002"]]
    )
    action_required: Optional[str] = Field(
        None,
        max_length=1000,
        description="Required action based on feedback",
        examples=["Update authentication requirements with OAuth 2.0 details"]
    )
    resolved: bool = Field(
        False,
        description="Whether the feedback has been resolved",
        examples=[False]
    )
    resolved_at: Optional[datetime] = Field(
        None,
        description="Resolution timestamp",
        examples=["2024-01-15T11:00:00Z"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowStatusResponse(BaseModel):
    """
    Schema for workflow status response.
    
    Provides current status and progress of a workflow session.
    """
    
    session_id: UUID = Field(
        ...,
        description="Workflow session ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    project_id: UUID = Field(
        ...,
        description="Associated project ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    current_stage: WorkflowStageEnum = Field(
        ...,
        description="Current workflow stage",
        examples=[WorkflowStageEnum.REQUIREMENT_EXTRACTION]
    )
    state_data: WorkflowStateData = Field(
        ...,
        description="Current workflow state"
    )
    is_active: bool = Field(
        ...,
        description="Whether the workflow is currently active",
        examples=[True]
    )
    started_at: datetime = Field(
        ...,
        description="Workflow start timestamp",
        examples=["2024-01-15T10:00:00Z"]
    )
    last_activity_at: Optional[datetime] = Field(
        None,
        description="Last activity timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Workflow completion timestamp",
        examples=["2024-01-15T12:00:00Z"]
    )
    agent_executions: List[AgentExecutionData] = Field(
        ...,
        description="List of agent executions",
        examples=[]
    )
    human_feedback: List[HumanFeedback] = Field(
        ...,
        description="List of human feedback",
        examples=[]
    )
    estimated_completion: Optional[datetime] = Field(
        None,
        description="Estimated completion time",
        examples=["2024-01-15T12:00:00Z"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowUpdateRequest(BaseModel):
    """
    Schema for updating workflow state.
    
    Used to update workflow configuration or state.
    """
    
    configuration: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated workflow configuration"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated workflow context"
    )
    force_stage: Optional[WorkflowStageEnum] = Field(
        None,
        description="Force workflow to specific stage"
    )
    pause: Optional[bool] = Field(
        None,
        description="Pause or resume workflow"
    )
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowListResponse(BaseModel):
    """
    Schema for paginated workflow list response.
    """
    
    workflows: List[WorkflowStatusResponse] = Field(
        ...,
        description="List of workflow sessions"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of workflow sessions",
        examples=[50]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
        examples=[10]
    )
    has_next: bool = Field(
        ...,
        description="Whether there are more pages available",
        examples=[True]
    )
    
    model_config = ConfigDict(from_attributes=True)


class WorkflowStats(BaseModel):
    """
    Schema for workflow statistics.
    """
    
    total_workflows: int = Field(
        ...,
        ge=0,
        description="Total number of workflow sessions",
        examples=[150]
    )
    active_workflows: int = Field(
        ...,
        ge=0,
        description="Number of active workflow sessions",
        examples=[15]
    )
    completed_workflows: int = Field(
        ...,
        ge=0,
        description="Number of completed workflow sessions",
        examples=[120]
    )
    failed_workflows: int = Field(
        ...,
        ge=0,
        description="Number of failed workflow sessions",
        examples=[15]
    )
    average_duration_minutes: float = Field(
        ...,
        ge=0.0,
        description="Average workflow duration in minutes",
        examples=[45.5]
    )
    workflows_by_stage: Dict[str, int] = Field(
        ...,
        description="Number of workflows by current stage",
        examples=[{"document_analysis": 5, "requirement_extraction": 8, "architecture_design": 2}]
    )
    total_agent_executions: int = Field(
        ...,
        ge=0,
        description="Total number of agent executions",
        examples=[500]
    )
    successful_executions: int = Field(
        ...,
        ge=0,
        description="Number of successful agent executions",
        examples=[450]
    )
    total_cost_usd: float = Field(
        ...,
        ge=0.0,
        description="Total cost of agent executions in USD",
        examples=[25.50]
    )
    
    model_config = ConfigDict(from_attributes=True)


class AgentExecutionRequest(BaseModel):
    """
    Schema for manual agent execution request.
    
    Used to manually trigger agent executions.
    """
    
    agent_type: AgentTypeEnum = Field(
        ...,
        description="Type of agent to execute",
        examples=[AgentTypeEnum.REQUIREMENT_EXTRACTOR]
    )
    input_data: Dict[str, Any] = Field(
        ...,
        description="Input data for the agent",
        examples=[{"documents": ["doc1.pdf"], "config": {"confidence_threshold": 0.8}}]
    )
    llm_provider: Optional[LLMProviderEnum] = Field(
        None,
        description="LLM provider to use",
        examples=[LLMProviderEnum.OPENAI]
    )
    llm_model: Optional[str] = Field(
        None,
        description="LLM model to use",
        examples=["gpt-4"]
    )
    timeout_seconds: Optional[int] = Field(
        None,
        ge=1,
        le=3600,
        description="Execution timeout in seconds",
        examples=[300]
    )
    
    model_config = ConfigDict(from_attributes=True)
