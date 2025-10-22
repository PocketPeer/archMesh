"""
Project management API endpoints.

This module provides CRUD operations for projects including creation,
retrieval, updates, and listing with proper error handling and validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStats,
    DomainEnum,
    ProjectStatusEnum,
)
from app.models.project import Project, ProjectDomain, ProjectStatus
from app.models.requirement import Requirement
from app.models.architecture import Architecture
from app.models.workflow_session import WorkflowSession

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    Create a new project.
    
    Args:
        project: Project creation data
        db: Database session
        
    Returns:
        Created project data
        
    Raises:
        HTTPException: 400 if validation fails, 500 if database error
    """
    try:
        # Convert enum values to model enums
        domain_enum = ProjectDomain(project.domain)
        
        # Create new project instance
        db_project = Project(
            name=project.name,
            description=project.description,
            domain=domain_enum,
            status=ProjectStatus.PENDING,
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        
        # Convert back to response schema
        return ProjectResponse(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            domain=db_project.domain.value,  # Already a string, Pydantic will validate it
            status=db_project.status.value,  # Already a string, Pydantic will validate it
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid enum value: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    Get project by ID.
    
    Args:
        project_id: Project UUID
        db: Database session
        
    Returns:
        Project data
        
    Raises:
        HTTPException: 404 if project not found, 500 if database error
    """
    try:
        # Query project by ID and owner
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.owner_id == current_user.id
                )
            )
        )
        db_project = result.scalar_one_or_none()
        
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found or access denied"
            )
        
        # Convert to response schema
        return ProjectResponse(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            domain=db_project.domain,  # Already a string, Pydantic will validate it
            status=db_project.status,  # Already a string, Pydantic will validate it
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project: {str(e)}"
        )


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of projects to return"),
    domain: Optional[DomainEnum] = Query(None, description="Filter by domain"),
    status_filter: Optional[ProjectStatusEnum] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, min_length=1, max_length=200, description="Search in name and description"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectListResponse:
    """
    List projects with filtering and pagination.
    
    Args:
        skip: Number of projects to skip
        limit: Maximum number of projects to return
        domain: Filter by project domain
        status_filter: Filter by project status
        search: Search term for name and description
        db: Database session
        
    Returns:
        Paginated list of projects
        
    Raises:
        HTTPException: 500 if database error
    """
    try:
        # Build query with filters
        query = select(Project)
        count_query = select(func.count(Project.id))
        
        # Apply filters
        filters = []
        
        # Always filter by owner - users can only see their own projects
        filters.append(Project.owner_id == current_user.id)
        
        if domain:
            filters.append(Project.domain == ProjectDomain(domain))
        
        if status_filter:
            filters.append(Project.status == ProjectStatus(status_filter))
        
        if search:
            search_filter = or_(
                Project.name.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        db_projects = result.scalars().all()
        
        # Convert to response schemas
        projects = [
            ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                domain=DomainEnum(project.domain.value),
                status=ProjectStatusEnum(project.status.value),
                created_at=project.created_at,
                updated_at=project.updated_at
            )
            for project in db_projects
        ]
        
        # Calculate pagination info
        has_next = (skip + limit) < total
        
        return ProjectListResponse(
            projects=projects,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            has_next=has_next
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    Update an existing project.
    
    Args:
        project_id: Project UUID
        project_update: Project update data
        db: Database session
        
    Returns:
        Updated project data
        
    Raises:
        HTTPException: 404 if project not found, 400 if validation fails, 500 if database error
    """
    try:
        # Get existing project and verify ownership
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.owner_id == current_user.id
                )
            )
        )
        db_project = result.scalar_one_or_none()
        
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found or access denied"
            )
        
        # Update fields if provided
        update_data = project_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "domain" and value is not None:
                setattr(db_project, field, ProjectDomain(value))
            elif field == "status" and value is not None:
                setattr(db_project, field, ProjectStatus(value.value))
            elif value is not None:
                setattr(db_project, field, value)
        
        # Update timestamp
        db_project.updated_at = datetime.utcnow()
        
        # Commit changes
        await db.commit()
        await db.refresh(db_project)
        
        # Convert to response schema
        from enum import Enum as PyEnum
        return ProjectResponse(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            domain=DomainEnum(db_project.domain.value) if isinstance(db_project.domain, PyEnum) else DomainEnum(db_project.domain),
            status=ProjectStatusEnum(db_project.status.value) if isinstance(db_project.status, PyEnum) else ProjectStatusEnum(db_project.status),
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid enum value: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a project and all associated data.
    
    Args:
        project_id: Project UUID
        db: Database session
        
    Raises:
        HTTPException: 404 if project not found, 500 if database error
    """
    try:
        # Get existing project and verify ownership
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.owner_id == current_user.id
                )
            )
        )
        db_project = result.scalar_one_or_none()
        
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found or access denied"
            )
        
        # Delete project (cascade will handle related records)
        await db.delete(db_project)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


@router.get("/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectStats:
    """
    Get statistics for a specific project.
    
    Args:
        project_id: Project UUID
        db: Database session
        
    Returns:
        Project statistics
        
    Raises:
        HTTPException: 404 if project not found, 500 if database error
    """
    try:
        # Verify project exists and user has access
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.owner_id == current_user.id
                )
            )
        )
        db_project = result.scalar_one_or_none()
        
        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found or access denied"
            )
        
        # Get requirement count
        req_count = await db.execute(
            select(func.count(Requirement.id)).where(Requirement.project_id == project_id)
        )
        total_requirements = req_count.scalar()
        
        # Get architecture count
        arch_count = await db.execute(
            select(func.count(Architecture.id)).where(Architecture.project_id == project_id)
        )
        total_architectures = arch_count.scalar()
        
        # Get active workflow count
        active_workflows = await db.execute(
            select(func.count(WorkflowSession.id)).where(
                and_(
                    WorkflowSession.project_id == project_id,
                    WorkflowSession.is_active == True
                )
            )
        )
        active_workflow_count = active_workflows.scalar()
        
        return ProjectStats(
            total_projects=1,  # This is for a single project
            projects_by_domain={db_project.domain: 1},
            projects_by_status={db_project.status: 1},
            active_workflows=active_workflow_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project stats: {str(e)}"
        )


@router.get("/stats/overview", response_model=ProjectStats)
async def get_overview_stats(
    db: AsyncSession = Depends(get_db)
) -> ProjectStats:
    """
    Get overall project statistics.
    
    Args:
        db: Database session
        
    Returns:
        Overall project statistics
        
    Raises:
        HTTPException: 500 if database error
    """
    try:
        # Get total projects
        total_result = await db.execute(select(func.count(Project.id)))
        total_projects = total_result.scalar()
        
        # Get projects by domain
        domain_result = await db.execute(
            select(Project.domain, func.count(Project.id)).group_by(Project.domain)
        )
        projects_by_domain = {row[0]: row[1] for row in domain_result.fetchall()}
        
        # Get projects by status
        status_result = await db.execute(
            select(Project.status, func.count(Project.id)).group_by(Project.status)
        )
        projects_by_status = {row[0]: row[1] for row in status_result.fetchall()}
        
        # Get active workflows
        active_workflows_result = await db.execute(
            select(func.count(WorkflowSession.id)).where(WorkflowSession.is_active == True)
        )
        active_workflows = active_workflows_result.scalar()
        
        return ProjectStats(
            total_projects=total_projects,
            projects_by_domain=projects_by_domain,
            projects_by_status=projects_by_status,
            active_workflows=active_workflows
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get overview stats: {str(e)}"
        )
