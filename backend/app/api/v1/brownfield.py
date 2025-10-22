"""
Brownfield Analysis API endpoints.

This module provides REST API endpoints for brownfield analysis including:
- Repository analysis and architecture extraction
- Knowledge base queries and semantic search
- Architecture graph visualization
- Feature context generation for brownfield projects
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.agents.github_analyzer_agent import GitHubAnalyzerAgent
from app.services.local_knowledge_base_service import LocalKnowledgeBaseService
from app.schemas.brownfield import (
    ArchitectureGraphResponse,
    ErrorResponse,
    FeatureContextRequest,
    FeatureContextResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    ProjectStatusResponse,
    RepositoryAnalysisRequest,
    RepositoryAnalysisResponse,
)

router = APIRouter(prefix="/brownfield", tags=["brownfield"])


def get_knowledge_base_service() -> LocalKnowledgeBaseService:
    """
    Dependency to get Local Knowledge Base Service instance.
    
    Returns:
        LocalKnowledgeBaseService: Configured local knowledge base service
    """
    return LocalKnowledgeBaseService()


@router.post(
    "/analyze-repository",
    response_model=RepositoryAnalysisResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Analysis failed"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
    summary="Analyze GitHub Repository",
    description="""
    Analyze a GitHub repository to extract comprehensive architecture information.
    
    This endpoint:
    1. Clones the repository (with configurable depth)
    2. Analyzes file structure, technology stack, and architecture patterns
    3. Extracts services, dependencies, and API contracts
    4. Indexes results in the knowledge base for future queries
    5. Returns detailed analysis results
    
    **Features:**
    - Supports both public and private repositories (with GitHub token)
    - Configurable clone depth for faster analysis
    - Background indexing for large repositories
    - Comprehensive technology stack detection
    - Architecture pattern recognition
    - Service dependency analysis
    
    **Use Cases:**
    - Understanding existing codebases before making changes
    - Documenting legacy systems
    - Planning brownfield integrations
    - Architecture assessment and modernization planning
    """,
)
async def analyze_repository(
    request: RepositoryAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> RepositoryAnalysisResponse:
    """
    Analyze a GitHub repository to extract architecture information.
    
    Args:
        request: Repository analysis request with URL and options
        background_tasks: FastAPI background tasks for async processing
        db: Database session dependency
        
    Returns:
        RepositoryAnalysisResponse: Complete analysis results
        
    Raises:
        HTTPException: If analysis fails or repository is inaccessible
    """
    start_time = time.time()
    
    try:
        logger.info(
            f"Starting repository analysis",
            extra={
                "project_id": request.project_id,
                "repository_url": str(request.repository_url),
                "branch": request.branch,
                "endpoint": "analyze_repository"
            }
        )
        
        # Initialize GitHub Analyzer Agent
        analyzer = GitHubAnalyzerAgent(
            github_token=request.github_token
        )
        
        # Prepare analysis input
        analysis_input = {
            "repo_url": str(request.repository_url),
            "branch": request.branch or "main",
            "clone_depth": request.clone_depth or 1,
            "analyze_private": request.analyze_private or False,
            "include_commits": request.include_commits or False,
            "session_id": request.session_id
        }
        
        # Perform repository analysis
        analysis = await analyzer.execute(analysis_input)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Index results in knowledge base (background task)
        background_tasks.add_task(
            index_analysis_results,
            request.project_id,
            str(request.repository_url),
            analysis
        )
        
        # Prepare response
        response = RepositoryAnalysisResponse(
            project_id=request.project_id,
            repository_url=str(request.repository_url),
            status="completed",
            analysis=analysis,
            processing_time_seconds=processing_time,
            metadata={
                "branch": request.branch,
                "clone_depth": request.clone_depth,
                "services_count": len(analysis.get("architecture", {}).get("services", [])),
                "languages_count": len(analysis.get("tech_stack", {}).get("languages", {})),
                "frameworks_count": len(analysis.get("tech_stack", {}).get("frameworks", [])),
                "architecture_style": analysis.get("architecture", {}).get("architecture_style", "Unknown")
            }
        )
        
        logger.info(
            f"Repository analysis completed successfully",
            extra={
                "project_id": request.project_id,
                "processing_time": processing_time,
                "services_count": response.metadata.get("services_count", 0),
                "endpoint": "analyze_repository"
            }
        )
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Repository analysis failed: {str(e)}"
        
        logger.error(
            error_msg,
            extra={
                "project_id": request.project_id,
                "repository_url": str(request.repository_url),
                "processing_time": processing_time,
                "error": str(e),
                "endpoint": "analyze_repository"
            }
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.post(
    "/search-knowledge",
    response_model=KnowledgeSearchResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Search failed"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
    summary="Search Knowledge Base",
    description="""
    Search the knowledge base for relevant architecture patterns and solutions.
    
    This endpoint uses semantic search to find similar architectures, services,
    and patterns based on natural language queries.
    
    **Features:**
    - Natural language queries for intuitive searching
    - Semantic similarity matching using vector embeddings
    - Filtering by project, type, and similarity score
    - Rich metadata and context in results
    - Fast sub-second response times
    
    **Use Cases:**
    - Finding similar architectural patterns
    - Discovering reusable components and services
    - Learning from previous architectural decisions
    - Getting context for new feature development
    - Architecture pattern research and analysis
    """,
)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    kb_service: LocalKnowledgeBaseService = Depends(get_knowledge_base_service),
) -> KnowledgeSearchResponse:
    """
    Search knowledge base for relevant architecture patterns.
    
    Args:
        request: Knowledge search request with query and filters
        kb_service: Knowledge base service dependency
        
    Returns:
        KnowledgeSearchResponse: Search results with similarity scores
        
    Raises:
        HTTPException: If search fails or knowledge base is unavailable
    """
    start_time = time.time()
    
    try:
        logger.info(
            f"Starting knowledge base search",
            extra={
                "query": request.query[:100],  # Truncate for logging
                "project_id": request.project_id,
                "top_k": request.top_k,
                "endpoint": "search_knowledge"
            }
        )
        
        # Perform semantic search
        results = await kb_service.search_similar_architectures(
            query=request.query,
            project_id=request.project_id,
            top_k=request.top_k or 5,
            filter_types=request.filter_types
        )
        
        # Apply minimum score filter if specified
        if request.min_score and request.min_score > 0:
            results = [r for r in results if r.get("score", 0) >= request.min_score]
        
        # Calculate search time
        search_time_ms = (time.time() - start_time) * 1000
        
        # Prepare response
        response = KnowledgeSearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_ms=search_time_ms,
            filters_applied={
                "project_id": request.project_id,
                "filter_types": request.filter_types,
                "min_score": request.min_score,
                "top_k": request.top_k
            }
        )
        
        logger.info(
            f"Knowledge base search completed",
            extra={
                "query_length": len(request.query),
                "results_count": len(results),
                "search_time_ms": search_time_ms,
                "endpoint": "search_knowledge"
            }
        )
        
        return response
        
    except Exception as e:
        search_time_ms = (time.time() - start_time) * 1000
        error_msg = f"Knowledge base search failed: {str(e)}"
        
        logger.error(
            error_msg,
            extra={
                "query": request.query[:100],
                "search_time_ms": search_time_ms,
                "error": str(e),
                "endpoint": "search_knowledge"
            }
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.get(
    "/project/{project_id}/architecture-graph",
    response_model=ArchitectureGraphResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Failed to get architecture graph"},
        404: {"model": ErrorResponse, "description": "Project not found"},
    },
    summary="Get Architecture Graph",
    description="""
    Get architecture graph data for visualization.
    
    Returns nodes (services, components) and edges (relationships, dependencies)
    for rendering interactive architecture diagrams.
    
    **Features:**
    - Service and component nodes with metadata
    - Dependency and communication relationships
    - Technology stack information for each node
    - Graph statistics and metadata
    - Optimized for frontend visualization components
    
    **Use Cases:**
    - Interactive architecture visualization
    - Service dependency analysis
    - Architecture documentation
    - Impact analysis for changes
    - Onboarding new team members
    """,
)
async def get_architecture_graph(
    project_id: str,
    kb_service: LocalKnowledgeBaseService = Depends(get_knowledge_base_service),
) -> ArchitectureGraphResponse:
    """
    Get architecture graph for visualization.
    
    Args:
        project_id: Project identifier
        kb_service: Knowledge base service dependency
        
    Returns:
        ArchitectureGraphResponse: Graph nodes and edges for visualization
        
    Raises:
        HTTPException: If graph retrieval fails or project not found
    """
    try:
        logger.info(
            f"Getting architecture graph",
            extra={
                "project_id": project_id,
                "endpoint": "get_architecture_graph"
            }
        )
        
        # Get services and dependencies from Neo4j
        services = await kb_service.get_service_dependencies(project_id)
        
        # Format nodes and edges for visualization
        nodes = []
        edges = []
        node_ids = set()
        
        for service_record in services:
            if "s" in service_record and service_record["s"]:
                service = service_record["s"]
                service_id = service.get("name", "unknown")
                
                # Add service node
                if service_id not in node_ids:
                    nodes.append({
                        "id": service_id,
                        "label": service.get("name", "Unknown Service"),
                        "type": service.get("type", "service"),
                        "technology": service.get("technology", ""),
                        "properties": {
                            "responsibility": service.get("responsibility", ""),
                            "interfaces": service.get("interfaces", []),
                            "scalability": service.get("scalability", "")
                        }
                    })
                    node_ids.add(service_id)
                
                # Add dependency edges
                if "dep" in service_record and service_record["dep"]:
                    dep_service = service_record["dep"]
                    dep_id = dep_service.get("name", "unknown")
                    
                    # Add dependency node if not already present
                    if dep_id not in node_ids:
                        nodes.append({
                            "id": dep_id,
                            "label": dep_service.get("name", "Unknown Service"),
                            "type": dep_service.get("type", "service"),
                            "technology": dep_service.get("technology", ""),
                            "properties": {
                                "responsibility": dep_service.get("responsibility", ""),
                                "interfaces": dep_service.get("interfaces", []),
                                "scalability": dep_service.get("scalability", "")
                            }
                        })
                        node_ids.add(dep_id)
                    
                    # Add dependency edge
                    edges.append({
                        "source": service_id,
                        "target": dep_id,
                        "relationship_type": "depends_on",
                        "properties": {
                            "description": f"{service_id} depends on {dep_id}"
                        }
                    })
        
        # Get architecture patterns for metadata
        patterns = await kb_service.get_architecture_patterns(project_id)
        
        # Prepare response
        response = ArchitectureGraphResponse(
            project_id=project_id,
            nodes=nodes,
            edges=edges,
            metadata={
                "nodes_count": len(nodes),
                "edges_count": len(edges),
                "architecture_patterns": [p.get("a", {}) for p in patterns] if patterns else [],
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(
            f"Architecture graph retrieved successfully",
            extra={
                "project_id": project_id,
                "nodes_count": len(nodes),
                "edges_count": len(edges),
                "endpoint": "get_architecture_graph"
            }
        )
        
        return response
        
    except Exception as e:
        error_msg = f"Failed to get architecture graph: {str(e)}"
        
        logger.error(
            error_msg,
            extra={
                "project_id": project_id,
                "error": str(e),
                "endpoint": "get_architecture_graph"
            }
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.get(
    "/project/{project_id}/context",
    response_model=FeatureContextResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Failed to get context"},
        404: {"model": ErrorResponse, "description": "Project not found"},
    },
    summary="Get Feature Context",
    description="""
    Get relevant context for adding a new feature to an existing project.
    
    This endpoint provides RAG (Retrieval-Augmented Generation) capabilities
    to retrieve relevant architectural context for new feature development.
    
    **Features:**
    - Semantic search for similar features and patterns
    - Analysis of existing services and dependencies
    - Technology stack recommendations
    - Integration point suggestions
    - AI-generated architectural recommendations
    
    **Use Cases:**
    - Planning new feature development
    - Understanding integration requirements
    - Identifying reusable patterns and components
    - Making informed architectural decisions
    - Reducing development time and complexity
    """,
)
async def get_project_context(
    project_id: str,
    feature_description: str = Query(..., description="Description of the new feature"),
    context_types: Optional[List[str]] = Query(
        default=None,
        description="Types of context to retrieve (service, architecture_overview, etc.)"
    ),
    include_recommendations: bool = Query(
        default=True,
        description="Whether to include AI-generated recommendations"
    ),
    kb_service: LocalKnowledgeBaseService = Depends(get_knowledge_base_service),
) -> FeatureContextResponse:
    """
    Get context for adding a new feature to existing project.
    
    Args:
        project_id: Project identifier
        feature_description: Description of the new feature
        context_types: Types of context to retrieve
        include_recommendations: Whether to include AI recommendations
        kb_service: Knowledge base service dependency
        
    Returns:
        FeatureContextResponse: Relevant context for feature development
        
    Raises:
        HTTPException: If context generation fails or project not found
    """
    try:
        logger.info(
            f"Getting project context for new feature",
            extra={
                "project_id": project_id,
                "feature_description": feature_description[:100],
                "context_types": context_types,
                "endpoint": "get_project_context"
            }
        )
        
        # Get context for new feature
        context = await kb_service.get_context_for_new_feature(
            project_id=project_id,
            feature_description=feature_description,
            context_types=context_types
        )
        
        # Prepare response
        response = FeatureContextResponse(
            project_id=project_id,
            feature_description=feature_description,
            similar_patterns=context.get("similar_patterns", []),
            existing_services=context.get("existing_services", []),
            architecture_patterns=context.get("architecture_patterns", []),
            technology_context=context.get("technology_context", {}),
            recommendations=context.get("recommendations", {}) if include_recommendations else {},
            generated_at=datetime.fromisoformat(context.get("generated_at", datetime.utcnow().isoformat()))
        )
        
        logger.info(
            f"Project context generated successfully",
            extra={
                "project_id": project_id,
                "similar_patterns_count": len(response.similar_patterns),
                "existing_services_count": len(response.existing_services),
                "endpoint": "get_project_context"
            }
        )
        
        return response
        
    except Exception as e:
        error_msg = f"Failed to get project context: {str(e)}"
        
        logger.error(
            error_msg,
            extra={
                "project_id": project_id,
                "feature_description": feature_description[:100],
                "error": str(e),
                "endpoint": "get_project_context"
            }
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.get(
    "/project/{project_id}/status",
    response_model=ProjectStatusResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Failed to get project status"},
        404: {"model": ErrorResponse, "description": "Project not found"},
    },
    summary="Get Project Status",
    description="""
    Get the current status of a project's analysis and knowledge base indexing.
    
    Provides information about:
    - Analysis completion status
    - Knowledge base indexing status
    - Project statistics and metadata
    - Last analysis timestamp
    
    **Use Cases:**
    - Monitoring analysis progress
    - Checking project readiness for queries
    - Project management and tracking
    - System health monitoring
    """,
)
async def get_project_status(
    project_id: str,
    kb_service: LocalKnowledgeBaseService = Depends(get_knowledge_base_service),
) -> ProjectStatusResponse:
    """
    Get project analysis and indexing status.
    
    Args:
        project_id: Project identifier
        kb_service: Knowledge base service dependency
        
    Returns:
        ProjectStatusResponse: Project status information
        
    Raises:
        HTTPException: If status retrieval fails
    """
    try:
        logger.info(
            f"Getting project status",
            extra={
                "project_id": project_id,
                "endpoint": "get_project_status"
            }
        )
        
        # Get project services to determine if it exists
        services = await kb_service.get_service_dependencies(project_id)
        
        # Get architecture patterns
        patterns = await kb_service.get_architecture_patterns(project_id)
        
        # Determine status based on available data
        if services or patterns:
            analysis_status = "completed"
            indexed_in_knowledge_base = True
            services_count = len(services)
            architecture_style = None
            
            if patterns:
                arch_data = patterns[0].get("a", {})
                architecture_style = arch_data.get("style")
        else:
            analysis_status = "not_started"
            indexed_in_knowledge_base = False
            services_count = 0
            architecture_style = None
        
        # Prepare response
        response = ProjectStatusResponse(
            project_id=project_id,
            analysis_status=analysis_status,
            indexed_in_knowledge_base=indexed_in_knowledge_base,
            services_count=services_count,
            architecture_style=architecture_style,
            # Note: In a full implementation, these would come from database
            repository_url=None,
            last_analyzed=None,
            technologies_count=None
        )
        
        logger.info(
            f"Project status retrieved successfully",
            extra={
                "project_id": project_id,
                "analysis_status": analysis_status,
                "indexed": indexed_in_knowledge_base,
                "endpoint": "get_project_status"
            }
        )
        
        return response
        
    except Exception as e:
        error_msg = f"Failed to get project status: {str(e)}"
        
        logger.error(
            error_msg,
            extra={
                "project_id": project_id,
                "error": str(e),
                "endpoint": "get_project_status"
            }
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


# Background task helper functions

async def index_analysis_results(
    project_id: str,
    repository_url: str,
    analysis: Dict[str, Any]
) -> None:
    """
    Index analysis results in knowledge base (background task).
    
    Args:
        project_id: Project identifier
        repository_url: Repository URL
        analysis: Analysis results to index
    """
    try:
        logger.info(
            f"Starting background indexing of analysis results",
            extra={
                "project_id": project_id,
                "repository_url": repository_url,
                "background_task": "index_analysis_results"
            }
        )
        
        # Initialize knowledge base service
        kb_service = KnowledgeBaseService()
        
        # Index the analysis results
        result = await kb_service.index_repository_analysis(
            project_id=project_id,
            repository_url=repository_url,
            analysis=analysis
        )
        
        logger.info(
            f"Background indexing completed successfully",
            extra={
                "project_id": project_id,
                "vector_chunks": result.get("vector_chunks", 0),
                "graph_nodes": result.get("graph_nodes", 0),
                "background_task": "index_analysis_results"
            }
        )
        
    except Exception as e:
        logger.error(
            f"Background indexing failed: {str(e)}",
            extra={
                "project_id": project_id,
                "repository_url": repository_url,
                "error": str(e),
                "background_task": "index_analysis_results"
            }
        )
