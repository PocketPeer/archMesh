"""
Project-related Pydantic schemas for API request/response validation.

This module contains all schemas related to project management including
creation, updates, and responses with proper validation and examples.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class DomainEnum(str, Enum):
    """Project domain enumeration."""
    
    CLOUD_NATIVE = "cloud-native"
    DATA_PLATFORM = "data-platform"
    ENTERPRISE = "enterprise"


class ProjectStatusEnum(str, Enum):
    """Project status enumeration."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectCreate(BaseModel):
    """
    Schema for creating a new project.
    
    Attributes:
        name: Project name (1-200 characters)
        description: Optional project description
        domain: Project domain (cloud-native, data-platform, enterprise)
    """
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Project name",
        examples=["E-commerce Platform", "Data Analytics Pipeline", "Microservices Architecture"]
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional project description",
        examples=["A scalable e-commerce platform with microservices architecture"]
    )
    domain: DomainEnum = Field(
        ...,
        description="Project domain",
        examples=[DomainEnum.CLOUD_NATIVE]
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.
    
    All fields are optional for partial updates.
    """
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated project name",
        examples=["Updated E-commerce Platform"]
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated project description"
    )
    domain: Optional[DomainEnum] = Field(
        None,
        description="Updated project domain"
    )
    status: Optional[ProjectStatusEnum] = Field(
        None,
        description="Updated project status"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )


class ProjectResponse(BaseModel):
    """
    Schema for project response data.
    
    Contains all project information including timestamps and status.
    """
    
    id: UUID = Field(
        ...,
        description="Unique project identifier",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ...,
        description="Project name",
        examples=["E-commerce Platform"]
    )
    description: Optional[str] = Field(
        None,
        description="Project description",
        examples=["A scalable e-commerce platform with microservices architecture"]
    )
    domain: DomainEnum = Field(
        ...,
        description="Project domain",
        examples=[DomainEnum.CLOUD_NATIVE]
    )
    status: ProjectStatusEnum = Field(
        ...,
        description="Current project status",
        examples=[ProjectStatusEnum.PENDING]
    )
    created_at: datetime = Field(
        ...,
        description="Project creation timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """
    Schema for paginated project list response.
    
    Attributes:
        projects: List of projects
        total: Total number of projects
        page: Current page number
        page_size: Number of items per page
        has_next: Whether there are more pages
    """
    
    projects: List[ProjectResponse] = Field(
        ...,
        description="List of projects"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of projects",
        examples=[25]
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


class ProjectStats(BaseModel):
    """
    Schema for project statistics.
    
    Provides aggregated statistics about projects.
    """
    
    total_projects: int = Field(
        ...,
        ge=0,
        description="Total number of projects",
        examples=[150]
    )
    projects_by_domain: dict[str, int] = Field(
        ...,
        description="Number of projects by domain",
        examples=[{"cloud-native": 75, "data-platform": 50, "enterprise": 25}]
    )
    projects_by_status: dict[str, int] = Field(
        ...,
        description="Number of projects by status",
        examples=[{"pending": 30, "processing": 20, "completed": 90, "failed": 10}]
    )
    active_workflows: int = Field(
        ...,
        ge=0,
        description="Number of active workflow sessions",
        examples=[15]
    )
    
    model_config = ConfigDict(from_attributes=True)
