"""
Database models package.

This package contains all SQLAlchemy models for the ArchMesh PoC application.
Models are imported here to ensure they are registered with the metadata.
"""

# Import all models here to ensure they are registered with Base.metadata
from .project import Project, ProjectDomain, ProjectStatus
from .requirement import Requirement, RequirementStatus
from .architecture import Architecture, ArchitectureStatus
from .workflow_session import WorkflowSession
from .agent_execution import AgentExecution, AgentExecutionStatus

__all__ = [
    # Project models
    "Project",
    "ProjectDomain", 
    "ProjectStatus",
    
    # Requirement models
    "Requirement",
    "RequirementStatus",
    
    # Architecture models
    "Architecture",
    "ArchitectureStatus",
    
    # Workflow models
    "WorkflowSession",
    
    # Agent execution models
    "AgentExecution",
    "AgentExecutionStatus",
]
