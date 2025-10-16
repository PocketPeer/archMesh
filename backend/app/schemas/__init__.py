"""
Pydantic schemas package.

This package contains all Pydantic models for request/response validation
and serialization in the ArchMesh PoC application.
"""

# Project schemas
from .project import (
    DomainEnum,
    ProjectStatusEnum,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStats,
)

# Requirement schemas
from .requirement import (
    RequirementStatusEnum,
    DocumentTypeEnum,
    PriorityEnum,
    DocumentInfo,
    FunctionalRequirement,
    NonFunctionalRequirement,
    StructuredRequirements,
    ClarificationQuestion,
    RequirementCreate,
    RequirementUpdate,
    RequirementResponse,
    RequirementListResponse,
    RequirementStats,
)

# Architecture schemas
from .architecture import (
    ArchitectureStatusEnum,
    ArchitectureStyleEnum,
    ComponentTypeEnum,
    TechnologyCategoryEnum,
    C4LevelEnum,
    ComponentSpec,
    C4Diagram,
    TechnologySpec,
    TechnologyStack,
    ArchitectureAlternative,
    ArchitectureCreate,
    ArchitectureUpdate,
    ArchitectureResponse,
    ArchitectureListResponse,
    ArchitectureStats,
)

# Workflow schemas
from .workflow import (
    WorkflowStageEnum,
    AgentTypeEnum,
    AgentExecutionStatusEnum,
    LLMProviderEnum,
    FeedbackTypeEnum,
    WorkflowStartRequest,
    WorkflowStateData,
    AgentExecutionData,
    HumanFeedback,
    WorkflowStatusResponse,
    WorkflowUpdateRequest,
    WorkflowListResponse,
    WorkflowStats,
    AgentExecutionRequest,
)

__all__ = [
    # Project schemas
    "DomainEnum",
    "ProjectStatusEnum",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    "ProjectStats",
    
    # Requirement schemas
    "RequirementStatusEnum",
    "DocumentTypeEnum",
    "PriorityEnum",
    "DocumentInfo",
    "FunctionalRequirement",
    "NonFunctionalRequirement",
    "StructuredRequirements",
    "ClarificationQuestion",
    "RequirementCreate",
    "RequirementUpdate",
    "RequirementResponse",
    "RequirementListResponse",
    "RequirementStats",
    
    # Architecture schemas
    "ArchitectureStatusEnum",
    "ArchitectureStyleEnum",
    "ComponentTypeEnum",
    "TechnologyCategoryEnum",
    "C4LevelEnum",
    "ComponentSpec",
    "C4Diagram",
    "TechnologySpec",
    "TechnologyStack",
    "ArchitectureAlternative",
    "ArchitectureCreate",
    "ArchitectureUpdate",
    "ArchitectureResponse",
    "ArchitectureListResponse",
    "ArchitectureStats",
    
    # Workflow schemas
    "WorkflowStageEnum",
    "AgentTypeEnum",
    "AgentExecutionStatusEnum",
    "LLMProviderEnum",
    "FeedbackTypeEnum",
    "WorkflowStartRequest",
    "WorkflowStateData",
    "AgentExecutionData",
    "HumanFeedback",
    "WorkflowStatusResponse",
    "WorkflowUpdateRequest",
    "WorkflowListResponse",
    "WorkflowStats",
    "AgentExecutionRequest",
]
