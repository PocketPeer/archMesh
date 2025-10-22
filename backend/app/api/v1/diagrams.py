"""
Diagram Generation API Endpoints.

This module provides REST API endpoints for comprehensive diagram generation including:
- C4 synthesis (Context & Containers) with PlantUML generation
- Sequence diagrams for key use-cases
- NFR mapping & trade-off notes
- Knowledge graph integration
- Round-trip editing support
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.diagram_generation_service import (
    DiagramGenerationService,
    DiagramType,
    C4Level,
    DiagramConfig,
    NFRRequirement,
    get_diagram_generation_service
)
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagrams", tags=["diagrams"])


class C4DiagramRequest(BaseModel):
    """Request model for C4 diagram generation"""
    project_id: str = Field(..., description="Project ID")
    workflow_id: Optional[str] = Field(None, description="Workflow ID for context")
    diagram_type: DiagramType = Field(..., description="C4 diagram type")
    title: str = Field(..., description="Diagram title")
    description: str = Field(..., description="Diagram description")
    include_nfr: bool = Field(default=True, description="Include NFR requirements")
    include_technology_stack: bool = Field(default=True, description="Include technology stack")
    include_data_flows: bool = Field(default=True, description="Include data flows")
    include_security: bool = Field(default=True, description="Include security considerations")
    include_monitoring: bool = Field(default=True, description="Include monitoring")


class SequenceDiagramRequest(BaseModel):
    """Request model for sequence diagram generation"""
    project_id: str = Field(..., description="Project ID")
    workflow_id: Optional[str] = Field(None, description="Workflow ID for context")
    use_cases: List[str] = Field(..., description="List of use-case scenarios")
    title: str = Field(..., description="Diagram title")
    description: str = Field(..., description="Diagram description")


class NFRMappingRequest(BaseModel):
    """Request model for NFR mapping generation"""
    project_id: str = Field(..., description="Project ID")
    workflow_id: Optional[str] = Field(None, description="Workflow ID for context")
    nfr_requirements: List[Dict[str, Any]] = Field(..., description="NFR requirements")
    title: str = Field(..., description="Diagram title")
    description: str = Field(..., description="Diagram description")


class DiagramResponse(BaseModel):
    """Response model for diagram generation"""
    diagram_id: str
    diagram_type: str
    title: str
    description: str
    plantuml_code: str
    mermaid_code: str
    metadata: Dict[str, Any]
    created_at: str


class C4DiagramResponse(DiagramResponse):
    """Response model for C4 diagram generation"""
    components: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    nfr_requirements: List[Dict[str, Any]]


class SequenceDiagramResponse(DiagramResponse):
    """Response model for sequence diagram generation"""
    sequence_diagrams: List[Dict[str, Any]]


class NFRMappingResponse(DiagramResponse):
    """Response model for NFR mapping generation"""
    component_nfr_mapping: Dict[str, List[Dict[str, Any]]]
    trade_offs: List[Dict[str, Any]]


@router.post("/c4", response_model=C4DiagramResponse)
async def generate_c4_diagram(
    request: C4DiagramRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate C4 diagram with PlantUML and Mermaid output.
    
    This endpoint generates comprehensive C4 diagrams including:
    - Context diagrams (system boundaries)
    - Container diagrams (high-level architecture)
    - Component diagrams (detailed component view)
    - Code diagrams (implementation details)
    
    Features:
    - PlantUML and Mermaid output formats
    - NFR requirements integration
    - Technology stack visualization
    - Data flow mapping
    - Security and monitoring considerations
    """
    try:
        # Get diagram generation service
        diagram_service = get_diagram_generation_service()
        
        # Create diagram configuration
        config = DiagramConfig(
            diagram_type=request.diagram_type,
            title=request.title,
            description=request.description,
            include_nfr=request.include_nfr,
            include_technology_stack=request.include_technology_stack,
            include_data_flows=request.include_data_flows,
            include_security=request.include_security,
            include_monitoring=request.include_monitoring
        )
        
        # Get architecture data from project/workflow
        architecture_data = await _get_architecture_data(request.project_id, request.workflow_id, db)
        
        # Get knowledge context
        knowledge_context = await _get_knowledge_context(request.project_id, db)
        
        # Generate C4 diagram
        result = await diagram_service.generate_c4_diagram(
            architecture_data=architecture_data,
            config=config,
            knowledge_context=knowledge_context
        )
        
        # Create response
        diagram_id = f"c4_{request.project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return C4DiagramResponse(
            diagram_id=diagram_id,
            diagram_type=result["diagram_type"],
            title=result["title"],
            description=result["description"],
            plantuml_code=result["plantuml_code"],
            mermaid_code=result["mermaid_code"],
            components=result["components"],
            relationships=result["relationships"],
            nfr_requirements=result["nfr_requirements"],
            metadata=result["metadata"],
            created_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating C4 diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=f"C4 diagram generation failed: {str(e)}")


@router.post("/sequence", response_model=SequenceDiagramResponse)
async def generate_sequence_diagram(
    request: SequenceDiagramRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate sequence diagrams for key use-cases.
    
    This endpoint generates sequence diagrams from workflow execution data
    and use-case scenarios, showing the interaction between actors and
    system components.
    
    Features:
    - Multiple use-case scenarios
    - Actor identification from workflow data
    - Interaction mapping
    - PlantUML and Mermaid output formats
    """
    try:
        # Get diagram generation service
        diagram_service = get_diagram_generation_service()
        
        # Create diagram configuration
        config = DiagramConfig(
            diagram_type=DiagramType.SEQUENCE,
            title=request.title,
            description=request.description
        )
        
        # Get workflow data
        workflow_data = await _get_workflow_data(request.project_id, request.workflow_id, db)
        
        # Generate sequence diagrams
        result = await diagram_service.generate_sequence_diagram(
            workflow_data=workflow_data,
            use_cases=request.use_cases,
            config=config
        )
        
        # Create response
        diagram_id = f"seq_{request.project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return SequenceDiagramResponse(
            diagram_id=diagram_id,
            diagram_type=result["diagram_type"],
            title=result["title"],
            description=result["description"],
            plantuml_code=result.get("plantuml_code", ""),
            mermaid_code=result.get("mermaid_code", ""),
            sequence_diagrams=result["sequence_diagrams"],
            metadata=result["metadata"],
            created_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating sequence diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sequence diagram generation failed: {str(e)}")


@router.post("/nfr-mapping", response_model=NFRMappingResponse)
async def generate_nfr_mapping(
    request: NFRMappingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate NFR mapping and trade-off analysis diagrams.
    
    This endpoint generates diagrams showing how non-functional requirements
    map to system components and identifies potential trade-offs.
    
    Features:
    - NFR to component mapping
    - Trade-off analysis
    - Latency budgets and SLOs
    - Throughput requirements
    - Security considerations
    """
    try:
        # Get diagram generation service
        diagram_service = get_diagram_generation_service()
        
        # Create diagram configuration
        config = DiagramConfig(
            diagram_type=DiagramType.NFR_MAPPING,
            title=request.title,
            description=request.description
        )
        
        # Get architecture data
        architecture_data = await _get_architecture_data(request.project_id, request.workflow_id, db)
        
        # Convert NFR requirements
        nfr_requirements = []
        for nfr_data in request.nfr_requirements:
            nfr_requirements.append(NFRRequirement(
                id=nfr_data.get("id", ""),
                name=nfr_data.get("name", ""),
                description=nfr_data.get("description", ""),
                metric=nfr_data.get("metric", ""),
                target_value=nfr_data.get("target_value", ""),
                unit=nfr_data.get("unit", ""),
                priority=nfr_data.get("priority", "medium"),
                affected_components=nfr_data.get("affected_components", [])
            ))
        
        # Generate NFR mapping
        result = await diagram_service.generate_nfr_mapping(
            architecture_data=architecture_data,
            nfr_requirements=nfr_requirements,
            config=config
        )
        
        # Create response
        diagram_id = f"nfr_{request.project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return NFRMappingResponse(
            diagram_id=diagram_id,
            diagram_type=result["diagram_type"],
            title=result["title"],
            description=result["description"],
            plantuml_code=result["plantuml_code"],
            mermaid_code=result["mermaid_code"],
            component_nfr_mapping=result["component_nfr_mapping"],
            trade_offs=result["trade_offs"],
            metadata=result["metadata"],
            created_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating NFR mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"NFR mapping generation failed: {str(e)}")


@router.get("/types")
async def get_diagram_types():
    """
    Get available diagram types and their descriptions.
    
    Returns information about all supported diagram types including
    C4 levels, sequence diagrams, and NFR mapping capabilities.
    """
    return {
        "diagram_types": [
            {
                "type": "c4_context",
                "name": "C4 Context Diagram",
                "description": "System boundaries and external actors",
                "level": "context",
                "use_cases": ["System overview", "Stakeholder communication"]
            },
            {
                "type": "c4_container",
                "name": "C4 Container Diagram", 
                "description": "High-level architecture with containers",
                "level": "container",
                "use_cases": ["Architecture review", "Technology decisions"]
            },
            {
                "type": "c4_component",
                "name": "C4 Component Diagram",
                "description": "Detailed component interactions",
                "level": "component", 
                "use_cases": ["Implementation planning", "Code organization"]
            },
            {
                "type": "sequence",
                "name": "Sequence Diagram",
                "description": "Interaction flows for use-cases",
                "level": "interaction",
                "use_cases": ["Use-case analysis", "API design"]
            },
            {
                "type": "nfr_mapping",
                "name": "NFR Mapping",
                "description": "Non-functional requirements mapping",
                "level": "requirements",
                "use_cases": ["Performance planning", "Trade-off analysis"]
            }
        ],
        "output_formats": [
            {
                "format": "plantuml",
                "name": "PlantUML",
                "description": "Text-based diagram language with rich features",
                "features": ["C4 support", "Styling", "Export options"]
            },
            {
                "format": "mermaid",
                "name": "Mermaid",
                "description": "Markdown-based diagram language",
                "features": ["GitHub integration", "Web rendering", "Simple syntax"]
            }
        ]
    }


@router.get("/templates")
async def get_diagram_templates():
    """
    Get diagram templates and examples.
    
    Returns pre-configured templates for common diagram types
    to help users get started quickly.
    """
    return {
        "templates": [
            {
                "id": "ecommerce_c4_context",
                "name": "E-commerce C4 Context",
                "description": "Context diagram for e-commerce platform",
                "type": "c4_context",
                "template": {
                    "title": "E-commerce Platform - Context",
                    "description": "High-level view of e-commerce system",
                    "include_nfr": True,
                    "include_technology_stack": True
                }
            },
            {
                "id": "microservices_sequence",
                "name": "Microservices Sequence",
                "description": "Sequence diagram for microservices interaction",
                "type": "sequence",
                "template": {
                    "title": "Microservices Interaction",
                    "description": "Service communication patterns",
                    "use_cases": ["User Registration", "Order Processing", "Payment Flow"]
                }
            },
            {
                "id": "performance_nfr",
                "name": "Performance NFR Mapping",
                "description": "Performance requirements mapping",
                "type": "nfr_mapping",
                "template": {
                    "title": "Performance Requirements",
                    "description": "Performance and scalability mapping",
                    "nfr_requirements": [
                        {
                            "name": "Response Time",
                            "metric": "latency",
                            "target_value": "200",
                            "unit": "ms",
                            "priority": "high"
                        },
                        {
                            "name": "Throughput",
                            "metric": "requests_per_second",
                            "target_value": "1000",
                            "unit": "rps",
                            "priority": "high"
                        }
                    ]
                }
            }
        ]
    }


async def _get_architecture_data(project_id: str, workflow_id: Optional[str], db: AsyncSession) -> Dict[str, Any]:
    """Get architecture data from project or workflow."""
    # This would typically query the database for architecture data
    # For now, return mock data
    return {
        "architecture_overview": {
            "name": "Sample System",
            "description": "A sample system for demonstration",
            "responsibilities": ["User management", "Data processing"],
            "interfaces": ["REST API", "Web UI"]
        },
        "components": [
            {
                "id": "web-app",
                "name": "Web Application",
                "description": "Frontend web application",
                "type": "container",
                "technology": "React",
                "responsibilities": ["User interface", "User interaction"],
                "interfaces": ["REST API"],
                "data_flows": ["User requests", "API responses"]
            },
            {
                "id": "api-gateway",
                "name": "API Gateway",
                "description": "API gateway for routing requests",
                "type": "container",
                "technology": "Kong",
                "responsibilities": ["Request routing", "Authentication"],
                "interfaces": ["REST API", "Internal services"],
                "data_flows": ["HTTP requests", "Service calls"]
            }
        ],
        "relationships": [
            {
                "from": "web-app",
                "to": "api-gateway",
                "label": "API calls",
                "description": "Web app calls API gateway",
                "protocol": "HTTPS",
                "data_format": "JSON"
            }
        ],
        "non_functional_requirements": [
            {
                "id": "performance",
                "name": "Response Time",
                "description": "API response time requirement",
                "metric": "latency",
                "target_value": "200",
                "unit": "ms",
                "priority": "high",
                "affected_components": ["api-gateway", "web-app"]
            }
        ]
    }


async def _get_knowledge_context(project_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Get knowledge context from knowledge base."""
    # This would typically query the knowledge base
    # For now, return empty context
    return {}


async def _get_workflow_data(project_id: str, workflow_id: Optional[str], db: AsyncSession) -> Dict[str, Any]:
    """Get workflow execution data."""
    # This would typically query the database for workflow data
    # For now, return mock data
    return {
        "steps": [
            {
                "actor": "User",
                "description": "User initiates action",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "actor": "System",
                "description": "System processes request",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }
