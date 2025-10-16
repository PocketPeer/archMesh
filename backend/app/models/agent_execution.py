"""
AgentExecution model for ArchMesh PoC.

This module defines the AgentExecution model which tracks individual AI agent
executions with performance metrics, costs, and results.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Dict, Optional

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Integer, Float, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AgentExecutionStatus(PyEnum):
    """Agent execution status enumeration."""
    
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class AgentExecution(Base):
    """
    AgentExecution model representing individual AI agent executions.
    
    Agent executions track the performance, costs, and results of individual
    AI agent runs within workflow sessions.
    """
    
    __tablename__ = "agent_executions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique agent execution identifier"
    )
    
    # Foreign key to workflow session
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_sessions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent workflow session"
    )
    
    # Agent information
    agent_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Type of agent (e.g., document_analyzer, requirement_extractor, architecture_designer)"
    )
    
    agent_version: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Version of the agent"
    )
    
    # Input and output data
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Input data provided to the agent"
    )
    
    output_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Output data produced by the agent"
    )
    
    # LLM information
    llm_provider: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="LLM provider used (e.g., openai, anthropic)"
    )
    
    llm_model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="LLM model used (e.g., gpt-4, claude-3)"
    )
    
    # Token usage and costs
    prompt_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of prompt tokens used"
    )
    
    completion_tokens: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of completion tokens used"
    )
    
    cost_usd: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Cost of the execution in USD"
    )
    
    # Performance metrics
    duration_seconds: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Execution duration in seconds"
    )
    
    # Status and error information
    status: Mapped[AgentExecutionStatus] = mapped_column(
        Enum(AgentExecutionStatus),
        nullable=False,
        default=AgentExecutionStatus.SUCCESS,
        comment="Execution status"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if execution failed"
    )
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Execution start timestamp"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Execution completion timestamp"
    )
    
    # Relationships
    workflow_session: Mapped["WorkflowSession"] = relationship(
        "WorkflowSession",
        back_populates="agent_executions",
        lazy="select"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_agent_executions_session_id", "session_id"),
        Index("idx_agent_executions_agent_type", "agent_type"),
        Index("idx_agent_executions_status", "status"),
        Index("idx_agent_executions_llm_provider", "llm_provider"),
        Index("idx_agent_executions_llm_model", "llm_model"),
        Index("idx_agent_executions_started_at", "started_at"),
        Index("idx_agent_executions_completed_at", "completed_at"),
        Index("idx_agent_executions_cost_usd", "cost_usd"),
        Index("idx_agent_executions_duration_seconds", "duration_seconds"),
        # GIN indexes for JSONB fields
        Index("idx_agent_executions_input_data_gin", "input_data", postgresql_using="gin"),
        Index("idx_agent_executions_output_data_gin", "output_data", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        """String representation of the agent execution."""
        return f"<AgentExecution(id={self.id}, agent_type='{self.agent_type}', status={self.status.value})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Agent Execution: {self.agent_type} ({self.status.value})"
    
    @property
    def is_successful(self) -> bool:
        """Check if execution was successful."""
        return self.status == AgentExecutionStatus.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        """Check if execution failed."""
        return self.status == AgentExecutionStatus.FAILURE
    
    @property
    def is_timeout(self) -> bool:
        """Check if execution timed out."""
        return self.status == AgentExecutionStatus.TIMEOUT
    
    @property
    def total_tokens(self) -> Optional[int]:
        """Get total token usage."""
        if self.prompt_tokens is None or self.completion_tokens is None:
            return None
        return self.prompt_tokens + self.completion_tokens
    
    @property
    def cost_per_token(self) -> Optional[float]:
        """Get cost per token."""
        if self.cost_usd is None or self.total_tokens is None or self.total_tokens == 0:
            return None
        return self.cost_usd / self.total_tokens
    
    @property
    def tokens_per_second(self) -> Optional[float]:
        """Get tokens processed per second."""
        if self.total_tokens is None or self.duration_seconds is None or self.duration_seconds == 0:
            return None
        return self.total_tokens / self.duration_seconds
    
    def complete(self, status: AgentExecutionStatus, output_data: Optional[Dict[str, Any]] = None, error_message: Optional[str] = None) -> None:
        """Mark the execution as completed."""
        self.status = status
        self.completed_at = datetime.utcnow()
        
        if output_data is not None:
            self.output_data = output_data
        
        if error_message is not None:
            self.error_message = error_message
        
        # Calculate duration if not already set
        if self.duration_seconds is None:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def set_token_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Set token usage information."""
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
    
    def set_cost(self, cost_usd: float) -> None:
        """Set execution cost."""
        self.cost_usd = cost_usd
    
    def get_output_value(self, key: str, default: Any = None) -> Any:
        """Get a value from the output data."""
        if self.output_data is None:
            return default
        return self.output_data.get(key, default)
    
    def set_output_value(self, key: str, value: Any) -> None:
        """Set a value in the output data."""
        if self.output_data is None:
            self.output_data = {}
        self.output_data[key] = value
