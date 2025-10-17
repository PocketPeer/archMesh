"""
Pydantic schemas for Brownfield Analysis API.

This module defines the request and response models for brownfield analysis
endpoints, including repository analysis, knowledge base queries, and
architecture visualization.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator


class RepositoryAnalysisRequest(BaseModel):
    """
    Request model for repository analysis.
    
    Used to initiate analysis of a GitHub repository to extract
    architecture information and technology stack details.
    """
    project_id: str = Field(
        ...,
        description="Unique identifier for the project",
        min_length=1,
        max_length=100
    )
    repository_url: HttpUrl = Field(
        ...,
        description="GitHub repository URL to analyze"
    )
    branch: Optional[str] = Field(
        default="main",
        description="Git branch to analyze (defaults to 'main')",
        min_length=1,
        max_length=100
    )
    clone_depth: Optional[int] = Field(
        default=1,
        description="Clone depth for shallow clone (defaults to 1)",
        ge=1,
        le=100
    )
    analyze_private: Optional[bool] = Field(
        default=False,
        description="Whether to analyze private repositories"
    )
    include_commits: Optional[bool] = Field(
        default=False,
        description="Whether to analyze recent commits"
    )
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub token for private repository access",
        min_length=1
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional workflow session ID for logging",
        min_length=1,
        max_length=100
    )

    @validator('repository_url')
    def validate_github_url(cls, v):
        """Validate that the URL is a GitHub repository."""
        url_str = str(v)
        if 'github.com' not in url_str:
            raise ValueError('Repository URL must be a GitHub repository')
        return v

    @validator('project_id')
    def validate_project_id(cls, v):
        """Validate project ID format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Project ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "my-ecommerce-project",
                "repository_url": "https://github.com/user/ecommerce-platform",
                "branch": "main",
                "clone_depth": 1,
                "analyze_private": False,
                "include_commits": False,
                "session_id": "analysis_001"
            }
        }


class RepositoryAnalysisResponse(BaseModel):
    """
    Response model for repository analysis.
    
    Contains the complete analysis results including architecture,
    technology stack, services, and recommendations.
    """
    project_id: str = Field(
        ...,
        description="Project identifier"
    )
    repository_url: str = Field(
        ...,
        description="Analyzed repository URL"
    )
    status: str = Field(
        ...,
        description="Analysis status (completed, failed, in_progress)"
    )
    analysis: Dict[str, Any] = Field(
        ...,
        description="Complete repository analysis results"
    )
    indexed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when analysis was indexed in knowledge base"
    )
    processing_time_seconds: Optional[float] = Field(
        default=None,
        description="Time taken to complete the analysis"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional processing metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "my-ecommerce-project",
                "repository_url": "https://github.com/user/ecommerce-platform",
                "status": "completed",
                "analysis": {
                    "architecture": {
                        "architecture_style": "microservices",
                        "services": [
                            {
                                "name": "user-service",
                                "type": "service",
                                "technology": "Node.js + Express",
                                "responsibility": "User management"
                            }
                        ]
                    },
                    "tech_stack": {
                        "languages": {"JavaScript": 150, "TypeScript": 75},
                        "frameworks": ["Express.js", "React"]
                    }
                },
                "indexed_at": "2024-01-01T00:00:00Z",
                "processing_time_seconds": 45.2
            }
        }


class KnowledgeSearchRequest(BaseModel):
    """
    Request model for knowledge base search.
    
    Used to search for similar architectures and patterns
    in the knowledge base using semantic search.
    """
    query: str = Field(
        ...,
        description="Natural language query for searching similar architectures",
        min_length=1,
        max_length=1000
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Optional filter by specific project",
        min_length=1,
        max_length=100
    )
    top_k: Optional[int] = Field(
        default=5,
        description="Number of results to return",
        ge=1,
        le=50
    )
    filter_types: Optional[List[str]] = Field(
        default=None,
        description="Filter by chunk types (e.g., ['service', 'architecture_overview'])",
        max_items=10
    )
    min_score: Optional[float] = Field(
        default=0.0,
        description="Minimum similarity score for results",
        ge=0.0,
        le=1.0
    )

    @validator('filter_types')
    def validate_filter_types(cls, v):
        """Validate filter types."""
        if v:
            allowed_types = [
                'architecture_overview', 'service', 'tech_stack', 
                'api_contract', 'recommendations'
            ]
            for filter_type in v:
                if filter_type not in allowed_types:
                    raise ValueError(f'Invalid filter type: {filter_type}. Allowed: {allowed_types}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "query": "microservices with user authentication and payment processing",
                "project_id": "my-ecommerce-project",
                "top_k": 5,
                "filter_types": ["service", "architecture_overview"],
                "min_score": 0.7
            }
        }


class KnowledgeSearchResponse(BaseModel):
    """
    Response model for knowledge base search.
    
    Contains search results with similarity scores and metadata.
    """
    query: str = Field(
        ...,
        description="Original search query"
    )
    results: List[Dict[str, Any]] = Field(
        ...,
        description="Search results with similarity scores and metadata"
    )
    total_results: int = Field(
        ...,
        description="Total number of results found"
    )
    search_time_ms: Optional[float] = Field(
        default=None,
        description="Time taken to perform the search in milliseconds"
    )
    filters_applied: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filters that were applied to the search"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "microservices with user authentication",
                "results": [
                    {
                        "score": 0.95,
                        "content": "Service Name: user-service...",
                        "type": "service",
                        "project_id": "project_001",
                        "repository_url": "https://github.com/user/repo"
                    }
                ],
                "total_results": 5,
                "search_time_ms": 150.5
            }
        }


class ArchitectureGraphNode(BaseModel):
    """
    Model for architecture graph nodes.
    
    Represents a service or component in the architecture graph.
    """
    id: str = Field(
        ...,
        description="Unique node identifier"
    )
    label: str = Field(
        ...,
        description="Node display label"
    )
    type: str = Field(
        ...,
        description="Node type (service, database, gateway, etc.)"
    )
    technology: Optional[str] = Field(
        default=None,
        description="Technology stack used by this node"
    )
    properties: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional node properties"
    )


class ArchitectureGraphEdge(BaseModel):
    """
    Model for architecture graph edges.
    
    Represents relationships between services/components.
    """
    source: str = Field(
        ...,
        description="Source node ID"
    )
    target: str = Field(
        ...,
        description="Target node ID"
    )
    relationship_type: str = Field(
        ...,
        description="Type of relationship (depends_on, communicates_with, etc.)"
    )
    properties: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional edge properties"
    )


class ArchitectureGraphResponse(BaseModel):
    """
    Response model for architecture graph visualization.
    
    Contains nodes and edges for rendering the architecture graph.
    """
    project_id: str = Field(
        ...,
        description="Project identifier"
    )
    nodes: List[ArchitectureGraphNode] = Field(
        ...,
        description="Graph nodes (services, components)"
    )
    edges: List[ArchitectureGraphEdge] = Field(
        ...,
        description="Graph edges (relationships, dependencies)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Graph metadata and statistics"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "my-ecommerce-project",
                "nodes": [
                    {
                        "id": "user-service",
                        "label": "User Service",
                        "type": "service",
                        "technology": "Node.js + Express"
                    }
                ],
                "edges": [
                    {
                        "source": "user-service",
                        "target": "user-database",
                        "relationship_type": "depends_on"
                    }
                ]
            }
        }


class FeatureContextRequest(BaseModel):
    """
    Request model for feature context generation.
    
    Used to get relevant context for adding new features to existing projects.
    """
    project_id: str = Field(
        ...,
        description="Project identifier",
        min_length=1,
        max_length=100
    )
    feature_description: str = Field(
        ...,
        description="Description of the new feature to be added",
        min_length=1,
        max_length=2000
    )
    context_types: Optional[List[str]] = Field(
        default=None,
        description="Types of context to retrieve",
        max_items=10
    )
    include_recommendations: Optional[bool] = Field(
        default=True,
        description="Whether to include AI-generated recommendations"
    )

    @validator('context_types')
    def validate_context_types(cls, v):
        """Validate context types."""
        if v:
            allowed_types = [
                'service', 'architecture_overview', 'tech_stack',
                'api_contract', 'recommendations'
            ]
            for context_type in v:
                if context_type not in allowed_types:
                    raise ValueError(f'Invalid context type: {context_type}. Allowed: {allowed_types}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "my-ecommerce-project",
                "feature_description": "Add payment processing functionality with Stripe integration",
                "context_types": ["service", "architecture_overview"],
                "include_recommendations": True
            }
        }


class FeatureContextResponse(BaseModel):
    """
    Response model for feature context generation.
    
    Contains relevant context for new feature development.
    """
    project_id: str = Field(
        ...,
        description="Project identifier"
    )
    feature_description: str = Field(
        ...,
        description="Original feature description"
    )
    similar_patterns: List[Dict[str, Any]] = Field(
        ...,
        description="Similar architectural patterns found"
    )
    existing_services: List[Dict[str, Any]] = Field(
        ...,
        description="Existing services in the project"
    )
    architecture_patterns: List[Dict[str, Any]] = Field(
        ...,
        description="Architecture patterns used in the project"
    )
    technology_context: Dict[str, Any] = Field(
        ...,
        description="Technology stack context"
    )
    recommendations: Dict[str, Any] = Field(
        ...,
        description="AI-generated recommendations for feature development"
    )
    generated_at: datetime = Field(
        ...,
        description="Timestamp when context was generated"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "my-ecommerce-project",
                "feature_description": "Add payment processing functionality",
                "similar_patterns": [
                    {
                        "score": 0.9,
                        "content": "Payment service with Stripe integration...",
                        "type": "service"
                    }
                ],
                "existing_services": [
                    {
                        "name": "user-service",
                        "type": "service",
                        "technology": "Node.js + Express"
                    }
                ],
                "recommendations": {
                    "reuse_patterns": ["Consider using existing payment patterns"],
                    "integration_points": ["Integrate with user-service for authentication"]
                },
                "generated_at": "2024-01-01T00:00:00Z"
            }
        }


class ProjectStatusResponse(BaseModel):
    """
    Response model for project status.
    
    Contains information about project analysis status and knowledge base indexing.
    """
    project_id: str = Field(
        ...,
        description="Project identifier"
    )
    repository_url: Optional[str] = Field(
        default=None,
        description="Repository URL if analyzed"
    )
    analysis_status: str = Field(
        ...,
        description="Analysis status (completed, in_progress, failed, not_started)"
    )
    indexed_in_knowledge_base: bool = Field(
        ...,
        description="Whether project is indexed in knowledge base"
    )
    last_analyzed: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last analysis"
    )
    services_count: Optional[int] = Field(
        default=None,
        description="Number of services identified"
    )
    technologies_count: Optional[int] = Field(
        default=None,
        description="Number of technologies identified"
    )
    architecture_style: Optional[str] = Field(
        default=None,
        description="Identified architecture style"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "my-ecommerce-project",
                "repository_url": "https://github.com/user/ecommerce-platform",
                "analysis_status": "completed",
                "indexed_in_knowledge_base": True,
                "last_analyzed": "2024-01-01T00:00:00Z",
                "services_count": 5,
                "technologies_count": 8,
                "architecture_style": "microservices"
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    
    Used for consistent error responses across all endpoints.
    """
    error: str = Field(
        ...,
        description="Error message"
    )
    detail: Optional[str] = Field(
        default=None,
        description="Detailed error information"
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Application-specific error code"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Repository analysis failed",
                "detail": "Failed to clone repository: Repository not found",
                "error_code": "REPO_CLONE_FAILED",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
