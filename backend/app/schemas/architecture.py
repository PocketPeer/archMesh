"""
Architecture-related Pydantic schemas for API request/response validation.

This module contains schemas for architectural design, components,
C4 diagrams, and technology stack management.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum


class ArchitectureStatusEnum(str, Enum):
    """Architecture status enumeration."""
    
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ArchitectureStyleEnum(str, Enum):
    """Architecture style enumeration."""
    
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event-driven"
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    CLEAN_ARCHITECTURE = "clean-architecture"


class ComponentTypeEnum(str, Enum):
    """Component type enumeration."""
    
    API_GATEWAY = "api-gateway"
    WEB_SERVICE = "web-service"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message-queue"
    FILE_STORAGE = "file-storage"
    AUTHENTICATION = "authentication"
    MONITORING = "monitoring"
    LOAD_BALANCER = "load-balancer"
    CDN = "cdn"


class TechnologyCategoryEnum(str, Enum):
    """Technology category enumeration."""
    
    FRAMEWORK = "framework"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_BROKER = "message-broker"
    CONTAINER = "container"
    ORCHESTRATION = "orchestration"
    MONITORING = "monitoring"
    SECURITY = "security"
    CI_CD = "ci-cd"
    CLOUD_PROVIDER = "cloud-provider"


class C4LevelEnum(str, Enum):
    """C4 model level enumeration."""
    
    CONTEXT = "context"
    CONTAINER = "container"
    COMPONENT = "component"
    CODE = "code"


class ComponentSpec(BaseModel):
    """
    Schema for architecture component specification.
    
    Represents a detailed component in the architecture.
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Component identifier",
        examples=["user-service", "payment-gateway", "user-db"]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Component name",
        examples=["User Management Service", "Payment Gateway", "User Database"]
    )
    type: ComponentTypeEnum = Field(
        ...,
        description="Component type",
        examples=[ComponentTypeEnum.WEB_SERVICE]
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Component description",
        examples=["Handles user registration, authentication, and profile management"]
    )
    responsibilities: List[str] = Field(
        ...,
        min_length=1,
        description="Component responsibilities",
        examples=[["User registration", "Authentication", "Profile management"]]
    )
    interfaces: List[Dict[str, Any]] = Field(
        ...,
        description="Component interfaces (APIs, events, etc.)",
        examples=[[{"name": "User API", "type": "REST", "endpoints": ["/users", "/auth"]}]]
    )
    dependencies: List[str] = Field(
        ...,
        description="Component dependencies",
        examples=[["user-db", "notification-service"]]
    )
    technology_stack: List[str] = Field(
        ...,
        description="Technologies used by this component",
        examples=[["Node.js", "Express", "PostgreSQL"]]
    )
    scalability: Dict[str, Any] = Field(
        ...,
        description="Scalability characteristics",
        examples=[{"horizontal": True, "max_instances": 10, "auto_scaling": True}]
    )
    security: Dict[str, Any] = Field(
        ...,
        description="Security considerations",
        examples=[{"authentication": "JWT", "authorization": "RBAC", "encryption": "TLS"}]
    )
    
    model_config = ConfigDict(from_attributes=True)


class C4Diagram(BaseModel):
    """
    Schema for C4 model diagram.
    
    Represents a diagram at a specific C4 level.
    """
    
    level: C4LevelEnum = Field(
        ...,
        description="C4 model level",
        examples=[C4LevelEnum.CONTAINER]
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Diagram title",
        examples=["E-commerce Platform - Container View"]
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Diagram description",
        examples=["Shows the high-level containers and their interactions"]
    )
    elements: List[Dict[str, Any]] = Field(
        ...,
        description="Diagram elements (containers, components, etc.)",
        examples=[[{"id": "web-app", "name": "Web Application", "type": "container"}]]
    )
    relationships: List[Dict[str, Any]] = Field(
        ...,
        description="Relationships between elements",
        examples=[[{"from": "web-app", "to": "user-service", "description": "API calls"}]]
    )
    diagram_data: Optional[str] = Field(
        None,
        description="Mermaid or PlantUML diagram code",
        examples=["graph TD\n    A[Web App] --> B[User Service]"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class TechnologySpec(BaseModel):
    """
    Schema for technology specification.
    
    Represents a technology in the architecture stack.
    """
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Technology name",
        examples=["React", "Node.js", "PostgreSQL", "Docker"]
    )
    category: TechnologyCategoryEnum = Field(
        ...,
        description="Technology category",
        examples=[TechnologyCategoryEnum.FRAMEWORK]
    )
    version: Optional[str] = Field(
        None,
        description="Technology version",
        examples=["18.2.0", "16.14.0", "13.4"]
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Technology description",
        examples=["A JavaScript library for building user interfaces"]
    )
    purpose: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Purpose in the architecture",
        examples=["Frontend UI framework", "Backend runtime", "Primary database"]
    )
    alternatives: List[str] = Field(
        ...,
        description="Alternative technologies considered",
        examples=[["Vue.js", "Angular"], ["Python", "Java"], ["MySQL", "MongoDB"]]
    )
    rationale: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Rationale for choosing this technology",
        examples=["Chosen for its component-based architecture and large ecosystem"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class TechnologyStack(BaseModel):
    """
    Schema for technology stack.
    
    Contains all technologies organized by category.
    """
    
    frontend: List[TechnologySpec] = Field(
        ...,
        description="Frontend technologies",
        examples=[]
    )
    backend: List[TechnologySpec] = Field(
        ...,
        description="Backend technologies",
        examples=[]
    )
    database: List[TechnologySpec] = Field(
        ...,
        description="Database technologies",
        examples=[]
    )
    infrastructure: List[TechnologySpec] = Field(
        ...,
        description="Infrastructure technologies",
        examples=[]
    )
    monitoring: List[TechnologySpec] = Field(
        ...,
        description="Monitoring and observability technologies",
        examples=[]
    )
    security: List[TechnologySpec] = Field(
        ...,
        description="Security technologies",
        examples=[]
    )
    summary: Dict[str, Any] = Field(
        ...,
        description="Technology stack summary",
        examples=[{"total_technologies": 15, "categories": 6, "open_source": 12}]
    )
    
    model_config = ConfigDict(from_attributes=True)


class ArchitectureAlternative(BaseModel):
    """
    Schema for architecture alternative.
    
    Represents an alternative architectural approach.
    """
    
    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Alternative identifier",
        examples=["alt-001", "microservices-vs-monolith"]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Alternative name",
        examples=["Microservices Architecture", "Monolithic Architecture"]
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Alternative description",
        examples=["A distributed architecture with independent services"]
    )
    pros: List[str] = Field(
        ...,
        description="Advantages of this alternative",
        examples=[["Scalability", "Technology diversity", "Team independence"]]
    )
    cons: List[str] = Field(
        ...,
        description="Disadvantages of this alternative",
        examples=[["Complexity", "Network latency", "Distributed transactions"]]
    )
    trade_offs: Dict[str, Any] = Field(
        ...,
        description="Key trade-offs",
        examples=[{"complexity": "high", "scalability": "excellent", "maintenance": "medium"}]
    )
    recommendation: Optional[str] = Field(
        None,
        max_length=1000,
        description="Recommendation and rationale",
        examples=["Recommended for large teams and complex domains"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class ArchitectureCreate(BaseModel):
    """
    Schema for creating architecture.
    
    Used when generating architecture from requirements.
    """
    
    project_id: UUID = Field(
        ...,
        description="Project ID to associate architecture with",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    requirement_id: Optional[UUID] = Field(
        None,
        description="Source requirement ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    architecture_style: ArchitectureStyleEnum = Field(
        ...,
        description="Preferred architecture style",
        examples=[ArchitectureStyleEnum.MICROSERVICES]
    )
    constraints: Optional[Dict[str, Any]] = Field(
        None,
        description="Architecture constraints",
        examples=[{"budget": "low", "team_size": "small", "timeline": "aggressive"}]
    )
    preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="Architecture preferences",
        examples=[{"cloud_provider": "aws", "programming_language": "python"}]
    )
    
    model_config = ConfigDict(from_attributes=True)


class ArchitectureUpdate(BaseModel):
    """
    Schema for updating architecture.
    
    Allows partial updates to architecture data.
    """
    
    architecture_style: Optional[ArchitectureStyleEnum] = Field(
        None,
        description="Updated architecture style"
    )
    components: Optional[List[ComponentSpec]] = Field(
        None,
        description="Updated component specifications"
    )
    c4_diagrams: Optional[List[C4Diagram]] = Field(
        None,
        description="Updated C4 diagrams"
    )
    technology_stack: Optional[TechnologyStack] = Field(
        None,
        description="Updated technology stack"
    )
    alternatives: Optional[List[ArchitectureAlternative]] = Field(
        None,
        description="Updated architecture alternatives"
    )
    status: Optional[ArchitectureStatusEnum] = Field(
        None,
        description="Updated architecture status"
    )
    
    model_config = ConfigDict(from_attributes=True)


class ArchitectureResponse(BaseModel):
    """
    Schema for architecture response data.
    
    Contains all architecture information including components and diagrams.
    """
    
    id: UUID = Field(
        ...,
        description="Unique architecture identifier",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    project_id: UUID = Field(
        ...,
        description="Associated project ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    requirement_id: Optional[UUID] = Field(
        None,
        description="Source requirement ID",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    architecture_style: ArchitectureStyleEnum = Field(
        ...,
        description="Architecture style",
        examples=[ArchitectureStyleEnum.MICROSERVICES]
    )
    components: List[ComponentSpec] = Field(
        ...,
        description="Architecture components",
        examples=[]
    )
    c4_diagrams: List[C4Diagram] = Field(
        ...,
        description="C4 model diagrams",
        examples=[]
    )
    technology_stack: TechnologyStack = Field(
        ...,
        description="Technology stack",
        examples=[]
    )
    alternatives: List[ArchitectureAlternative] = Field(
        ...,
        description="Architecture alternatives",
        examples=[]
    )
    status: ArchitectureStatusEnum = Field(
        ...,
        description="Current architecture status",
        examples=[ArchitectureStatusEnum.PENDING]
    )
    created_at: datetime = Field(
        ...,
        description="Architecture creation timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )
    
    model_config = ConfigDict(from_attributes=True)


class ArchitectureListResponse(BaseModel):
    """
    Schema for paginated architecture list response.
    """
    
    architectures: List[ArchitectureResponse] = Field(
        ...,
        description="List of architectures"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of architectures",
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


class ArchitectureStats(BaseModel):
    """
    Schema for architecture statistics.
    """
    
    total_architectures: int = Field(
        ...,
        ge=0,
        description="Total number of architectures",
        examples=[75]
    )
    architectures_by_style: Dict[str, int] = Field(
        ...,
        description="Number of architectures by style",
        examples=[{"microservices": 40, "monolith": 20, "serverless": 15}]
    )
    architectures_by_status: Dict[str, int] = Field(
        ...,
        description="Number of architectures by status",
        examples=[{"pending": 10, "approved": 60, "rejected": 5}]
    )
    average_components: float = Field(
        ...,
        ge=0,
        description="Average number of components per architecture",
        examples=[8.5]
    )
    
    model_config = ConfigDict(from_attributes=True)
