"""
Admin API endpoints for the modular ArchMesh system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger

from app.modules.admin.admin_service import AdminService
from app.modules.admin.models import ModelConfig, UserConfig, SystemHealth, UsageStats
from app.modules.admin.llm_logger import read_interactions

router = APIRouter()

# Initialize admin service
admin_service = AdminService()


# Request/Response Models
class ModelStatusUpdate(BaseModel):
    status: str


class UserCreateRequest(BaseModel):
    email: str
    name: str
    role: str = "user"
    usage_limit: Optional[int] = None
    cost_limit: Optional[float] = None


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    usage_limit: Optional[int] = None
    cost_limit: Optional[float] = None


class CustomModelRequest(BaseModel):
    id: str
    name: str
    provider: str
    model_name: str
    cost_per_1k_tokens: Dict[str, float]
    max_tokens: int = 4000
    temperature: float = 0.3
    timeout_seconds: int = 30


class ModelTimeoutUpdate(BaseModel):
    timeout_seconds: int


# Health and Status Endpoints
@router.get("/health")
async def get_admin_health():
    """Get admin module health status"""
    try:
        system_status = admin_service.get_system_status()
        return {
            "status": "healthy",
            "admin_module": "operational",
            "system_status": system_status
        }
    except Exception as e:
        logger.error(f"Admin health check failed: {e}")
        raise HTTPException(status_code=500, detail="Admin service unavailable")


@router.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    try:
        status = admin_service.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


@router.get("/system/health", response_model=SystemHealth)
async def get_system_health():
    """Get detailed system health"""
    try:
        health = admin_service.get_system_health()
        return health
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")


# Model Management Endpoints
@router.get("/models")
async def get_models():
    """Get all available models"""
    try:
        models = admin_service.get_available_models()
        return {
            "models": [model.dict() for model in models],
            "total": len(models)
        }
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models")


@router.get("/models/{model_id}")
async def get_model(model_id: str):
    """Get specific model by ID"""
    try:
        model = admin_service.get_model_by_id(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model {model_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model")


@router.put("/models/{model_id}/status")
async def update_model_status(model_id: str, status_update: ModelStatusUpdate):
    """Update model status"""
    try:
        success = admin_service.update_model_status(model_id, status_update.status)
        if not success:
            raise HTTPException(status_code=404, detail="Model not found or invalid status")
        return {"message": f"Model {model_id} status updated to {status_update.status}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update model status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update model status")


@router.put("/models/{model_id}/timeout")
async def update_model_timeout(model_id: str, timeout_update: ModelTimeoutUpdate):
    """Update model timeout"""
    try:
        success = admin_service.update_model_timeout(model_id, timeout_update.timeout_seconds)
        if not success:
            raise HTTPException(status_code=404, detail="Model not found")
        return {"message": f"Model {model_id} timeout updated to {timeout_update.timeout_seconds} seconds"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update model timeout: {e}")
        raise HTTPException(status_code=500, detail="Failed to update model timeout")


@router.post("/models/custom")
async def add_custom_model(model_request: CustomModelRequest):
    """Add custom model"""
    try:
        model_data = model_request.dict()
        success = admin_service.add_custom_model(model_data)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add custom model")
        return {"message": f"Custom model {model_request.name} added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add custom model: {e}")
        raise HTTPException(status_code=500, detail="Failed to add custom model")


@router.get("/models/recommendations/{task_type}")
async def get_model_recommendations(task_type: str, budget: Optional[float] = Query(None)):
    """Get model recommendations for a task"""
    try:
        recommendations = admin_service.get_model_recommendations(task_type, budget)
        return recommendations
    except Exception as e:
        logger.error(f"Failed to get model recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model recommendations")


# User Management Endpoints
@router.get("/users")
async def get_users():
    """Get all users"""
    try:
        users = admin_service.get_all_users()
        return {
            "users": [user.dict() for user in users],
            "total": len(users)
        }
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users")


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get specific user by ID"""
    try:
        user = admin_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")


@router.post("/users")
async def create_user(user_request: UserCreateRequest):
    """Create new user"""
    try:
        user = admin_service.create_user(
            email=user_request.email,
            name=user_request.name,
            role=user_request.role,
            usage_limit=user_request.usage_limit,
            cost_limit=user_request.cost_limit
        )
        if not user:
            raise HTTPException(status_code=400, detail="Failed to create user")
        return {"message": f"User {user.name} created successfully", "user": user.dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdateRequest):
    """Update user"""
    try:
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        success = admin_service.update_user(user_id, **update_data)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": f"User {user_id} updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    try:
        success = admin_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found or cannot be deleted")
        return {"message": f"User {user_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")


# Analytics Endpoints
@router.get("/analytics/usage")
async def get_usage_stats(days: int = Query(30, ge=1, le=365)):
    """Get usage statistics"""
    try:
        stats = admin_service.get_usage_stats(days)
        return stats.dict()
    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage stats")


@router.get("/analytics/costs")
async def get_cost_analysis(days: int = Query(30, ge=1, le=365)):
    """Get cost analysis"""
    try:
        analysis = admin_service.get_cost_analysis(days)
        return analysis
    except Exception as e:
        logger.error(f"Failed to get cost analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cost analysis")


@router.get("/analytics/performance")
async def get_performance_metrics(days: int = Query(30, ge=1, le=365)):
    """Get performance metrics"""
    try:
        metrics = admin_service.get_performance_metrics(days)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")


@router.get("/analytics/users/{user_id}")
async def get_user_usage(user_id: str, days: int = Query(30, ge=1, le=365)):
    """Get user usage statistics"""
    try:
        usage = admin_service.get_user_usage(user_id, days)
        return usage
    except Exception as e:
        logger.error(f"Failed to get user usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user usage")


# Dashboard Endpoints
@router.get("/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard data"""
    try:
        dashboard = admin_service.get_admin_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Failed to get admin dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get admin dashboard")


@router.get("/reports/usage")
async def generate_usage_report(user_id: Optional[str] = Query(None), days: int = Query(30, ge=1, le=365)):
    """Generate usage report"""
    try:
        report = admin_service.generate_usage_report(user_id, days)
        return report
    except Exception as e:
        logger.error(f"Failed to generate usage report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate usage report")


# LLM Interaction Logs
@router.get("/llm/interactions")
async def list_llm_interactions(stage: Optional[str] = Query(None), provider: Optional[str] = Query(None), model: Optional[str] = Query(None), limit: int = Query(200, ge=1, le=1000)):
    try:
        items = list(read_interactions(stage=stage, provider=provider, model=model, limit=limit))
        return {"data": items, "count": len(items)}
    except Exception as e:
        logger.error(f"Failed to read LLM interactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to read LLM interactions")
