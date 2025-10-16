"""
Requirement model for ArchMesh PoC.

This module defines the Requirement model which represents structured requirements
extracted from raw documents with confidence scores and clarification questions.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Float, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RequirementStatus(PyEnum):
    """Requirement status enumeration."""
    
    PENDING = "pending"
    PROCESSED = "processed"
    APPROVED = "approved"
    REJECTED = "rejected"


class Requirement(Base):
    """
    Requirement model representing structured requirements extracted from documents.
    
    Requirements are extracted from raw documents and processed to create
    structured, analyzable requirement specifications.
    """
    
    __tablename__ = "requirements"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique requirement identifier"
    )
    
    # Foreign key to project
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent project"
    )
    
    # Raw document information
    raw_documents: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of raw document information including file paths, types, and metadata"
    )
    
    # Structured requirements
    structured_requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Structured requirements in a standardized format"
    )
    
    # Clarification questions
    clarification_questions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of clarification questions generated during requirement analysis"
    )
    
    # Confidence and status
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Confidence score for requirement extraction (0.0 to 1.0)"
    )
    
    status: Mapped[RequirementStatus] = mapped_column(
        Enum(RequirementStatus),
        nullable=False,
        default=RequirementStatus.PENDING,
        comment="Current requirement processing status"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Requirement creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp"
    )
    
    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="requirements",
        lazy="select"
    )
    
    architectures: Mapped[List["Architecture"]] = relationship(
        "Architecture",
        back_populates="requirement",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_requirements_project_id", "project_id"),
        Index("idx_requirements_status", "status"),
        Index("idx_requirements_confidence_score", "confidence_score"),
        Index("idx_requirements_created_at", "created_at"),
        # GIN index for JSONB fields for efficient querying
        Index("idx_requirements_raw_documents_gin", "raw_documents", postgresql_using="gin"),
        Index("idx_requirements_structured_requirements_gin", "structured_requirements", postgresql_using="gin"),
        Index("idx_requirements_clarification_questions_gin", "clarification_questions", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        """String representation of the requirement."""
        return f"<Requirement(id={self.id}, project_id={self.project_id}, status={self.status.value})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Requirement: {self.id} (Project: {self.project_id})"
    
    @property
    def is_processed(self) -> bool:
        """Check if requirement has been processed."""
        return self.status in [RequirementStatus.PROCESSED, RequirementStatus.APPROVED, RequirementStatus.REJECTED]
    
    @property
    def is_approved(self) -> bool:
        """Check if requirement is approved."""
        return self.status == RequirementStatus.APPROVED
    
    @property
    def has_high_confidence(self) -> bool:
        """Check if requirement has high confidence score."""
        return self.confidence_score is not None and self.confidence_score >= 0.8
    
    @property
    def document_count(self) -> int:
        """Get the number of source documents."""
        if self.raw_documents is None:
            return 0
        return len(self.raw_documents)
    
    @property
    def question_count(self) -> int:
        """Get the number of clarification questions."""
        if self.clarification_questions is None:
            return 0
        return len(self.clarification_questions)
