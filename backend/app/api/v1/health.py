"""
Health check endpoints.

This module provides health check endpoints to monitor the application
status, database connectivity, and Redis connectivity.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.core.logging_config import get_logger
from app.config import settings

router = APIRouter()
logger = get_logger(__name__)


@router.get(
    "/health",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check the health status of the application and its dependencies",
    tags=["health"],
)
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Checks the health of:
    - Application status
    - Database connectivity
    - Redis connectivity
    
    Args:
        db: Database session dependency
        
    Returns:
        Dict containing health status and details
        
    Example:
        ```bash
        curl -X GET "http://localhost:8000/api/v1/health"
        ```
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {
            "database": {"status": "unknown", "details": {}},
            "redis": {"status": "unknown", "details": {}},
        },
    }
    
    overall_healthy = True
    
    # Check database connectivity
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "details": {
                "connection": "active",
                "query_time": "< 1ms",
            },
        }
        logger.debug("Database health check passed")
        
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "details": {
                "error": str(e),
                "connection": "failed",
            },
        }
        overall_healthy = False
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis connectivity
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "details": {
                "connection": "active",
                "ping": "pong",
            },
        }
        logger.debug("Redis health check passed")
        
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "details": {
                "error": str(e),
                "connection": "failed",
            },
        }
        overall_healthy = False
        logger.error(f"Redis health check failed: {e}")
    
    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
    
    return health_status


@router.get(
    "/health/ready",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the application is ready to serve requests",
    tags=["health"],
)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Readiness check endpoint for Kubernetes/container orchestration.
    
    This endpoint is used by load balancers and orchestration systems
    to determine if the application is ready to receive traffic.
    
    Args:
        db: Database session dependency
        
    Returns:
        Dict containing readiness status
        
    Example:
        ```bash
        curl -X GET "http://localhost:8000/api/v1/health/ready"
        ```
    """
    try:
        # Quick database check
        await db.execute(text("SELECT 1"))
        
        # Quick Redis check
        redis_client = await get_redis()
        await redis_client.ping()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Application is ready to serve requests",
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Application is not ready: {str(e)}",
        }


@router.get(
    "/health/live",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Check if the application is alive and running",
    tags=["health"],
)
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint for Kubernetes/container orchestration.
    
    This endpoint is used by orchestration systems to determine if the
    application process is alive and should be restarted if not.
    
    Returns:
        Dict containing liveness status
        
    Example:
        ```bash
        curl -X GET "http://localhost:8000/api/v1/health/live"
        ```
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Application is alive and running",
        "uptime": "N/A",  # Could be enhanced with actual uptime tracking
    }


@router.get(
    "/health/version",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Version information",
    description="Get application version and build information",
    tags=["health"],
)
async def version_info() -> Dict[str, Any]:
    """
    Get application version and build information.
    
    Returns:
        Dict containing version information
        
    Example:
        ```bash
        curl -X GET "http://localhost:8000/api/v1/health/version"
        ```
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "build_time": datetime.utcnow().isoformat(),  # Could be enhanced with actual build time
        "python_version": "3.11+",  # Could be enhanced with actual Python version
    }
