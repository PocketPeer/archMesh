"""
Architecture model for ArchMesh PoC.

This module defines the Architecture model which represents software architecture
designs with components, C4 diagrams, technology stacks, and alternatives.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ArchitectureStatus(PyEnum):
    """Architecture status enumeration."""
    
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Architecture(Base):
    """
    Architecture model representing software architecture designs.
    
    Architectures are generated based on requirements and include components,
    C4 diagrams, technology stacks, and alternative designs.
    """
    
    __tablename__ = "architectures"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique architecture identifier"
    )
    
    # Foreign keys
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to the parent project"
    )
    
    requirement_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("requirements.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reference to the source requirement (optional)"
    )
    
    # Architecture information
    architecture_style: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Architecture style (e.g., microservices, monolith, serverless)"
    )
    
    # Architecture components and design
    components: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of architecture components with their properties and relationships"
    )
    
    c4_diagrams: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="C4 model diagrams (Context, Container, Component, Code)"
    )
    
    technology_stack: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Technology stack including frameworks, databases, and tools"
    )
    
    alternatives: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Alternative architecture designs and trade-offs"
    )
    
    # Status and metadata
    status: Mapped[ArchitectureStatus] = mapped_column(
        Enum(ArchitectureStatus),
        nullable=False,
        default=ArchitectureStatus.PENDING,
        comment="Current architecture status"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Architecture creation timestamp"
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
        back_populates="architectures",
        lazy="select"
    )
    
    requirement: Mapped[Optional["Requirement"]] = relationship(
        "Requirement",
        back_populates="architectures",
        lazy="select"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_architectures_project_id", "project_id"),
        Index("idx_architectures_requirement_id", "requirement_id"),
        Index("idx_architectures_status", "status"),
        Index("idx_architectures_style", "architecture_style"),
        Index("idx_architectures_created_at", "created_at"),
        # GIN indexes for JSONB fields
        Index("idx_architectures_components_gin", "components", postgresql_using="gin"),
        Index("idx_architectures_c4_diagrams_gin", "c4_diagrams", postgresql_using="gin"),
        Index("idx_architectures_technology_stack_gin", "technology_stack", postgresql_using="gin"),
        Index("idx_architectures_alternatives_gin", "alternatives", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        """String representation of the architecture."""
        return f"<Architecture(id={self.id}, project_id={self.project_id}, style='{self.architecture_style}', status={self.status.value})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        style = self.architecture_style or "Unknown"
        return f"Architecture: {style} (Project: {self.project_id})"
    
    @property
    def is_approved(self) -> bool:
        """Check if architecture is approved."""
        return self.status == ArchitectureStatus.APPROVED
    
    @property
    def is_rejected(self) -> bool:
        """Check if architecture is rejected."""
        return self.status == ArchitectureStatus.REJECTED
    
    @property
    def component_count(self) -> int:
        """Get the number of components."""
        if self.components is None:
            return 0
        return len(self.components)
    
    @property
    def alternative_count(self) -> int:
        """Get the number of alternatives."""
        if self.alternatives is None:
            return 0
        return len(self.alternatives)
    
    @property
    def has_c4_diagrams(self) -> bool:
        """Check if C4 diagrams are available."""
        return self.c4_diagrams is not None and len(self.c4_diagrams) > 0
    
    @property
    def has_technology_stack(self) -> bool:
        """Check if technology stack is defined."""
        return self.technology_stack is not None and len(self.technology_stack) > 0
    
    def get_components_by_type(self, component_type: str) -> List[Dict[str, Any]]:
        """Get components filtered by type."""
        if self.components is None:
            return []
        
        return [
            component for component in self.components
            if component.get("type") == component_type
        ]
    
    def get_technologies_by_category(self, category: str) -> List[str]:
        """Get technologies by category from the technology stack."""
        if self.technology_stack is None:
            return []
        
        return self.technology_stack.get(category, [])
