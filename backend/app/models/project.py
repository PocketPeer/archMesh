"""
Project model for ArchMesh PoC.

This module defines the Project model which represents a software architecture
project with its domain, status, and relationships to requirements and architectures.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProjectDomain(PyEnum):
    """Project domain enumeration."""
    
    CLOUD_NATIVE = "cloud-native"
    DATA_PLATFORM = "data-platform"
    ENTERPRISE = "enterprise"


class ProjectStatus(PyEnum):
    """Project status enumeration."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    """
    Project model representing a software architecture project.
    
    A project contains requirements, architectures, and workflow sessions
    for analyzing and designing software architectures.
    """
    
    __tablename__ = "projects"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique project identifier"
    )
    
    # Basic information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Project name"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Project description"
    )
    
    # Domain and status
    domain: Mapped[ProjectDomain] = mapped_column(
        Enum(ProjectDomain),
        nullable=False,
        comment="Project domain (cloud-native, data-platform, enterprise)"
    )
    
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus),
        nullable=False,
        default=ProjectStatus.PENDING,
        comment="Current project status"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Project creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp"
    )
    
    # Relationships
    requirements: Mapped[List["Requirement"]] = relationship(
        "Requirement",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    architectures: Mapped[List["Architecture"]] = relationship(
        "Architecture",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    workflow_sessions: Mapped[List["WorkflowSession"]] = relationship(
        "WorkflowSession",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_projects_domain", "domain"),
        Index("idx_projects_status", "status"),
        Index("idx_projects_created_at", "created_at"),
        Index("idx_projects_name", "name"),
    )
    
    def __repr__(self) -> str:
        """String representation of the project."""
        return f"<Project(id={self.id}, name='{self.name}', domain={self.domain.value}, status={self.status.value})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Project: {self.name} ({self.domain.value})"
    
    @property
    def is_active(self) -> bool:
        """Check if project is currently active."""
        return self.status in [ProjectStatus.PENDING, ProjectStatus.PROCESSING]
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == ProjectStatus.COMPLETED
    
    @property
    def has_failed(self) -> bool:
        """Check if project has failed."""
        return self.status == ProjectStatus.FAILED
