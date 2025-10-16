"""
Requirement-related Pydantic schemas for API request/response validation.

This module contains schemas for requirement extraction, processing,
and management with nested models for structured data.
"""

from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum


class RequirementStatusEnum(str, Enum):
    """Requirement status enumeration."""
    
    PENDING = "pending"
    PROCESSED = "processed"
    APPROVED = "approved"
    REJECTED = "rejected"


class DocumentTypeEnum(str, Enum):
    """Document type enumeration."""
    
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "markdown"
    HTML = "html"
    PPTX = "pptx"


class PriorityEnum(str, Enum):
    """Requirement priority enumeration."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DocumentInfo(BaseModel):
    """
    Schema for document information.
    
    Represents metadata about a document used in requirement extraction.
    """
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Document name",
        examples=["requirements_specification.pdf"]
    )
    path: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Document file path",
        examples=["/uploads/project_123/requirements_specification.pdf"]
    )
    size_bytes: int = Field(
        ...,
        ge=0,
        description="Document size in bytes",
        examples=[1024000]
    )
    type: DocumentTypeEnum = Field(
        ...,
        description="Document type",
        examples=[DocumentTypeEnum.PDF]
    )
    uploaded_at: datetime = Field(
        ...,
        description="Document upload timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class FunctionalRequirement(BaseModel):
    """
    Schema for functional requirements.
    
    Represents a specific functional requirement with details.
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Requirement identifier",
        examples=["FR-001", "REQ-USER-AUTH-001"]
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Requirement title",
        examples=["User Authentication"]
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Detailed requirement description",
        examples=["The system shall provide secure user authentication using OAuth 2.0"]
    )
    priority: PriorityEnum = Field(
        ...,
        description="Requirement priority",
        examples=[PriorityEnum.HIGH]
    )
    acceptance_criteria: List[str] = Field(
        ...,
        min_length=1,
        description="Acceptance criteria for the requirement",
        examples=[["User can login with valid credentials", "System rejects invalid credentials"]]
    )
    source_document: Optional[str] = Field(
        None,
        description="Source document reference",
        examples=["requirements_specification.pdf, page 15"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class NonFunctionalRequirement(BaseModel):
    """
    Schema for non-functional requirements.
    
    Represents performance, security, and other quality requirements.
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Requirement identifier",
        examples=["NFR-001", "PERF-RESPONSE-TIME-001"]
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="NFR category",
        examples=["Performance", "Security", "Usability", "Reliability"]
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Requirement title",
        examples=["Response Time"]
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Detailed requirement description",
        examples=["The system shall respond to user requests within 2 seconds"]
    )
    priority: PriorityEnum = Field(
        ...,
        description="Requirement priority",
        examples=[PriorityEnum.HIGH]
    )
    metrics: Dict[str, Any] = Field(
        ...,
        description="Quantifiable metrics for the requirement",
        examples=[{"max_response_time": "2s", "throughput": "1000 req/s"}]
    )
    
    model_config = ConfigDict(from_attributes=True)


class StructuredRequirements(BaseModel):
    """
    Schema for structured requirements.
    
    Contains both functional and non-functional requirements.
    """
    
    functional_requirements: List[FunctionalRequirement] = Field(
        ...,
        description="List of functional requirements",
        examples=[]
    )
    non_functional_requirements: List[NonFunctionalRequirement] = Field(
        ...,
        description="List of non-functional requirements",
        examples=[]
    )
    summary: Dict[str, Any] = Field(
        ...,
        description="Summary statistics of requirements",
        examples=[{"total_functional": 15, "total_non_functional": 8, "high_priority": 5}]
    )
    
    model_config = ConfigDict(from_attributes=True)


class ClarificationQuestion(BaseModel):
    """
    Schema for clarification questions.
    
    Represents questions generated during requirement analysis.
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Question identifier",
        examples=["Q-001", "CLARIFY-USER-ROLES-001"]
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The clarification question",
        examples=["What are the different user roles in the system?"]
    )
    context: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Context for the question",
        examples=["Based on the requirements document, multiple user types are mentioned but roles are not clearly defined"]
    )
    priority: PriorityEnum = Field(
        ...,
        description="Question priority",
        examples=[PriorityEnum.MEDIUM]
    )
    related_requirements: List[str] = Field(
        ...,
        description="Related requirement IDs",
        examples=[["FR-001", "FR-002"]]
    )
    suggested_answer: Optional[str] = Field(
        None,
        max_length=2000,
        description="Suggested answer or clarification",
        examples=["Admin, User, Guest roles with different permission levels"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class RequirementCreate(BaseModel):
    """
    Schema for creating requirements from documents.
    
    Used when uploading documents for requirement extraction.
    """
    
    project_id: UUID = Field(
        ...,
        description="Project ID to associate requirements with",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    documents: List[DocumentInfo] = Field(
        ...,
        min_length=1,
        description="List of documents to process",
        examples=[]
    )
    extraction_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration for requirement extraction",
        examples=[{"confidence_threshold": 0.8, "extract_priorities": True}]
    )
    
    model_config = ConfigDict(from_attributes=True)


class RequirementUpdate(BaseModel):
    """
    Schema for updating requirements.
    
    Allows partial updates to requirement data.
    """
    
    structured_requirements: Optional[StructuredRequirements] = Field(
        None,
        description="Updated structured requirements"
    )
    clarification_questions: Optional[List[ClarificationQuestion]] = Field(
        None,
        description="Updated clarification questions"
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Updated confidence score",
        examples=[0.85]
    )
    status: Optional[RequirementStatusEnum] = Field(
        None,
        description="Updated requirement status"
    )
    
    model_config = ConfigDict(from_attributes=True)


class RequirementResponse(BaseModel):
    """
    Schema for requirement response data.
    
    Contains all requirement information including extracted data.
    """
    
    id: UUID = Field(
        ...,
        description="Unique requirement identifier",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    project_id: UUID = Field(
        ...,
        description="Associated project ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    raw_documents: List[DocumentInfo] = Field(
        ...,
        description="Original documents used for extraction",
        examples=[]
    )
    structured_requirements: Optional[StructuredRequirements] = Field(
        None,
        description="Extracted and structured requirements"
    )
    clarification_questions: List[ClarificationQuestion] = Field(
        ...,
        description="Generated clarification questions",
        examples=[]
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score of extraction",
        examples=[0.85]
    )
    status: RequirementStatusEnum = Field(
        ...,
        description="Current requirement status",
        examples=[RequirementStatusEnum.PENDING]
    )
    created_at: datetime = Field(
        ...,
        description="Requirement creation timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class RequirementListResponse(BaseModel):
    """
    Schema for paginated requirement list response.
    """
    
    requirements: List[RequirementResponse] = Field(
        ...,
        description="List of requirements"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of requirements",
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


class RequirementStats(BaseModel):
    """
    Schema for requirement statistics.
    """
    
    total_requirements: int = Field(
        ...,
        ge=0,
        description="Total number of requirements",
        examples=[150]
    )
    requirements_by_status: Dict[str, int] = Field(
        ...,
        description="Number of requirements by status",
        examples=[{"pending": 30, "processed": 80, "approved": 35, "rejected": 5}]
    )
    average_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Average confidence score",
        examples=[0.78]
    )
    total_clarification_questions: int = Field(
        ...,
        ge=0,
        description="Total number of clarification questions",
        examples=[45]
    )
    
    model_config = ConfigDict(from_attributes=True)
