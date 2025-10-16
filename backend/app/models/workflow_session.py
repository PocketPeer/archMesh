"""
WorkflowSession model for ArchMesh PoC.

This module defines the WorkflowSession model which represents LangGraph workflow
sessions with state management and execution tracking.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class WorkflowSession(Base):
    """
    WorkflowSession model representing LangGraph workflow execution sessions.
    
    Workflow sessions track the state and progress of multi-step AI workflows
    for document analysis, requirement extraction, and architecture generation.
    """
    
    __tablename__ = "workflow_sessions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique workflow session identifier"
    )
    
    # Foreign key to project
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent project"
    )
    
    # Workflow information
    current_stage: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Current workflow stage (e.g., document_analysis, requirement_extraction, architecture_design)"
    )
    
    # State management
    state_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Current workflow state data including intermediate results and context"
    )
    
    # Session status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the workflow session is currently active"
    )
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Workflow session start timestamp"
    )
    
    last_activity: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last activity timestamp"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Workflow session completion timestamp"
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="workflow_sessions",
        lazy="select"
    )
    
    agent_executions: Mapped[list["AgentExecution"]] = relationship(
        "AgentExecution",
        back_populates="workflow_session",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_workflow_sessions_project_id", "project_id"),
        Index("idx_workflow_sessions_current_stage", "current_stage"),
        Index("idx_workflow_sessions_is_active", "is_active"),
        Index("idx_workflow_sessions_started_at", "started_at"),
        Index("idx_workflow_sessions_last_activity", "last_activity"),
        Index("idx_workflow_sessions_completed_at", "completed_at"),
        # GIN index for JSONB state data
        Index("idx_workflow_sessions_state_data_gin", "state_data", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        """String representation of the workflow session."""
        return f"<WorkflowSession(id={self.id}, project_id={self.project_id}, stage='{self.current_stage}', active={self.is_active})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        stage = self.current_stage or "Unknown"
        return f"Workflow Session: {stage} (Project: {self.project_id})"
    
    @property
    def is_completed(self) -> bool:
        """Check if workflow session is completed."""
        return self.completed_at is not None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get workflow session duration in seconds."""
        if self.completed_at is None:
            return None
        
        return (self.completed_at - self.started_at).total_seconds()
    
    @property
    def is_stale(self, timeout_minutes: int = 30) -> bool:
        """Check if workflow session is stale (no activity for timeout period)."""
        if self.last_activity is None:
            return True
        
        from datetime import timedelta
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.utcnow() - self.last_activity > timeout
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark the workflow session as completed."""
        self.is_active = False
        self.completed_at = datetime.utcnow()
        self.update_activity()
    
    def get_state_value(self, key: str, default: Any = None) -> Any:
        """Get a value from the state data."""
        if self.state_data is None:
            return default
        return self.state_data.get(key, default)
    
    def set_state_value(self, key: str, value: Any) -> None:
        """Set a value in the state data."""
        if self.state_data is None:
            self.state_data = {}
        self.state_data[key] = value
        self.update_activity()
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update multiple state values at once."""
        if self.state_data is None:
            self.state_data = {}
        self.state_data.update(updates)
        self.update_activity()
    
    def get_execution_count(self) -> int:
        """Get the number of agent executions in this session."""
        return len(self.agent_executions)
    
    def get_successful_executions(self) -> list["AgentExecution"]:
        """Get all successful agent executions."""
        return [execution for execution in self.agent_executions if execution.status == "success"]
    
    def get_failed_executions(self) -> list["AgentExecution"]:
        """Get all failed agent executions."""
        return [execution for execution in self.agent_executions if execution.status == "failure"]
