"""
Monitoring and health check endpoints for ArchMesh production.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
import time
from datetime import datetime, timedelta

from app.core.monitoring import monitor, get_health_status
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/health")
async def health_check():
    """
    Health check endpoint for load balancers and monitoring systems.
    """
    return get_health_status()

@router.get("/metrics")
async def get_metrics():
    """
    Get current performance metrics.
    """
    return {
        "metrics": monitor.get_metrics_summary(),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics/detailed")
async def get_detailed_metrics(current_user: User = Depends(get_current_user)):
    """
    Get detailed performance metrics (requires authentication).
    """
    return {
        "metrics": monitor.metrics,
        "summary": monitor.get_metrics_summary(),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status")
async def system_status():
    """
    Get overall system status.
    """
    try:
        # Check database connection
        from app.core.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Check Redis connection
        from app.core.redis_client import redis_client
        redis_client.ping()
        
        return {
            "status": "healthy",
            "components": {
                "database": "healthy",
                "redis": "healthy",
                "api": "healthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
