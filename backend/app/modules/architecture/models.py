"""
Simple data models for Architecture Module
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ArchitectureStyle(str, Enum):
    """Architecture styles"""
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    SERVERLESS = "serverless"
    LAYERED = "layered"
    EVENT_DRIVEN = "event_driven"


class ComponentType(str, Enum):
    """Types of architecture components"""
    SERVICE = "service"
    DATABASE = "database"
    API_GATEWAY = "api_gateway"
    LOAD_BALANCER = "load_balancer"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    FRONTEND = "frontend"
    BACKEND = "backend"
    MONITORING = "monitoring"
    SECURITY = "security"


class TechnologyCategory(str, Enum):
    """Technology categories"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    INFRASTRUCTURE = "infrastructure"
    MONITORING = "monitoring"
    SECURITY = "security"


class Priority(str, Enum):
    """Priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ArchitectureComponent(BaseModel):
    """Simple architecture component"""
    id: str
    name: str
    type: ComponentType
    description: str
    technologies: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)


class TechnologyStack(BaseModel):
    """Technology stack for architecture"""
    frontend: List[str] = Field(default_factory=list)
    backend: List[str] = Field(default_factory=list)
    database: List[str] = Field(default_factory=list)
    infrastructure: List[str] = Field(default_factory=list)
    monitoring: List[str] = Field(default_factory=list)
    security: List[str] = Field(default_factory=list)


class Architecture(BaseModel):
    """Simple architecture structure"""
    id: str
    name: str
    style: ArchitectureStyle
    description: str
    components: List[ArchitectureComponent] = Field(default_factory=list)
    technology_stack: TechnologyStack = Field(default_factory=TechnologyStack)
    quality_score: float = Field(ge=0.0, le=1.0, default=0.5)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DiagramType(str, Enum):
    """Types of diagrams"""
    C4_CONTEXT = "c4_context"
    C4_CONTAINER = "c4_container"
    C4_COMPONENT = "c4_component"
    SEQUENCE = "sequence"
    DEPLOYMENT = "deployment"


class Diagram(BaseModel):
    """Simple diagram structure"""
    id: str
    type: DiagramType
    title: str
    description: str
    content: str  # PlantUML or Mermaid code
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Recommendation(BaseModel):
    """Simple recommendation"""
    id: str
    title: str
    description: str
    priority: Priority
    impact: str
    effort: str
    cost: str
    rationale: str


class ArchitectureResult(BaseModel):
    """Complete architecture result"""
    architecture: Architecture
    diagrams: List[Diagram] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
