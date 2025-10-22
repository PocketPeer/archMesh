"""
Admin Service - Main service for admin functionality
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from .model_manager import ModelManager
from .user_manager import UserManager
from .analytics_collector import AnalyticsCollector
from .models import ModelConfig, UserConfig, SystemHealth, UsageStats


class AdminService:
    """
    Main admin service that coordinates all admin functionality.
    
    Responsibilities:
    - Model management
    - User management
    - Analytics and monitoring
    - System administration
    """
    
    def __init__(self):
        self.model_manager = ModelManager()
        self.user_manager = UserManager()
        self.analytics_collector = AnalyticsCollector()
        logger.info("Admin service initialized")
    
    # Model Management Methods
    def get_available_models(self) -> List[ModelConfig]:
        """Get all available models"""
        return self.model_manager.get_available_models()
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelConfig]:
        """Get model by ID"""
        return self.model_manager.get_model_by_id(model_id)
    
    def select_optimal_model(self, task_type: str, budget_limit: Optional[float] = None) -> Optional[ModelConfig]:
        """Select optimal model for task"""
        return self.model_manager.select_optimal_model(task_type, budget_limit)
    
    def update_model_status(self, model_id: str, status: str) -> bool:
        """Update model status"""
        from .models import ModelStatus
        try:
            model_status = ModelStatus(status)
            return self.model_manager.update_model_status(model_id, model_status)
        except ValueError:
            logger.error(f"Invalid model status: {status}")
            return False
    
    def add_custom_model(self, model_data: Dict[str, Any]) -> bool:
        """Add custom model"""
        try:
            model_config = ModelConfig(**model_data)
            return self.model_manager.add_custom_model(model_config)
        except Exception as e:
            logger.error(f"Failed to add custom model: {e}")
            return False
    
    def update_model_timeout(self, model_id: str, timeout_seconds: int) -> bool:
        """Update model timeout"""
        return self.model_manager.update_model_timeout(model_id, timeout_seconds)
    
    # User Management Methods
    def get_all_users(self) -> List[UserConfig]:
        """Get all users"""
        return self.user_manager.get_all_users()
    
    def get_user_by_id(self, user_id: str) -> Optional[UserConfig]:
        """Get user by ID"""
        return self.user_manager.get_user_by_id(user_id)
    
    def create_user(self, email: str, name: str, role: str = "user", 
                   usage_limit: Optional[int] = None, cost_limit: Optional[float] = None) -> Optional[UserConfig]:
        """Create new user"""
        from .models import UserRole
        try:
            user_role = UserRole(role)
            return self.user_manager.create_user(email, name, user_role, usage_limit, cost_limit)
        except ValueError:
            logger.error(f"Invalid user role: {role}")
            return None
    
    def update_user(self, user_id: str, **updates) -> bool:
        """Update user"""
        return self.user_manager.update_user(user_id, **updates)
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        return self.user_manager.delete_user(user_id)
    
    def check_user_permission(self, user_id: str, permission: str) -> bool:
        """Check user permission"""
        return self.user_manager.check_permission(user_id, permission)
    
    def check_usage_limits(self, user_id: str, request_cost: float = 0.0) -> Dict[str, Any]:
        """Check user usage limits"""
        return self.user_manager.check_usage_limits(user_id, request_cost)
    
    # Analytics Methods
    def track_request(self, user_id: str, model_id: str, prompt_tokens: int, 
                     completion_tokens: int, cost: float, response_time: float):
        """Track a request"""
        self.analytics_collector.track_request(
            user_id, model_id, prompt_tokens, completion_tokens, cost, response_time
        )
    
    def track_error(self, user_id: str, model_id: str, error_type: str, error_message: str):
        """Track an error"""
        self.analytics_collector.track_error(user_id, model_id, error_type, error_message)
    
    def get_user_usage(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user usage statistics"""
        return self.analytics_collector.get_user_usage(user_id, days)
    
    def get_system_health(self) -> SystemHealth:
        """Get system health"""
        return self.analytics_collector.get_system_health()
    
    def get_usage_stats(self, days: int = 30) -> UsageStats:
        """Get usage statistics"""
        return self.analytics_collector.get_usage_stats(days)
    
    def get_cost_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get cost analysis"""
        return self.analytics_collector.get_cost_analysis(days)
    
    def get_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.analytics_collector.get_performance_metrics(days)
    
    # Dashboard Methods
    def get_admin_dashboard(self) -> Dict[str, Any]:
        """Get admin dashboard data"""
        return {
            "system_health": self.get_system_health().dict(),
            "usage_stats": self.get_usage_stats(7).dict(),  # Last 7 days
            "cost_analysis": self.get_cost_analysis(7),
            "performance_metrics": self.get_performance_metrics(7),
            "model_statistics": self.model_manager.get_model_statistics(),
            "user_statistics": self.user_manager.get_user_statistics(),
            "top_models": self._get_top_models(),
            "recent_activity": self._get_recent_activity()
        }
    
    def _get_top_models(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing models"""
        usage_stats = self.get_usage_stats(7)
        model_requests = usage_stats.requests_by_model
        
        # Sort by request count
        sorted_models = sorted(model_requests.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "model_id": model_id,
                "request_count": count,
                "percentage": (count / usage_stats.total_requests * 100) if usage_stats.total_requests > 0 else 0
            }
            for model_id, count in sorted_models[:limit]
        ]
    
    def _get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        # This would typically come from a log or activity feed
        # For now, we'll return a placeholder
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "type": "system",
                "message": "Admin service initialized",
                "user_id": "system"
            }
        ]
    
    # System Administration
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        health = self.get_system_health()
        models = self.get_available_models()
        users = self.user_manager.get_active_users()
        
        return {
            "status": health.status,
            "uptime_hours": health.uptime / 3600,
            "active_models": len(models),
            "active_users": len(users),
            "total_requests": health.total_requests,
            "error_rate": health.error_rate,
            "last_updated": health.last_updated.isoformat()
        }
    
    def get_model_recommendations(self, task_type: str, budget: Optional[float] = None) -> Dict[str, Any]:
        """Get model recommendations for a task"""
        optimal_model = self.select_optimal_model(task_type, budget)
        
        if not optimal_model:
            return {"error": "No suitable models found"}
        
        # Get alternative models
        all_models = self.get_available_models()
        alternatives = [
            model for model in all_models 
            if model.id != optimal_model.id and model.status.value == "active"
        ]
        
        return {
            "recommended_model": {
                "id": optimal_model.id,
                "name": optimal_model.name,
                "provider": optimal_model.provider.value,
                "cost_per_1k_tokens": optimal_model.cost_per_1k_tokens,
                "reason": f"Optimal for {task_type} tasks"
            },
            "alternatives": [
                {
                    "id": model.id,
                    "name": model.name,
                    "provider": model.provider.value,
                    "cost_per_1k_tokens": model.cost_per_1k_tokens
                }
                for model in alternatives[:3]  # Top 3 alternatives
            ]
        }
    
    def generate_usage_report(self, user_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Generate usage report"""
        if user_id:
            # User-specific report
            user_usage = self.get_user_usage(user_id, days)
            user_info = self.get_user_by_id(user_id)
            
            return {
                "report_type": "user",
                "user_id": user_id,
                "user_name": user_info.name if user_info else "Unknown",
                "period_days": days,
                "usage": user_usage,
                "generated_at": datetime.now().isoformat()
            }
        else:
            # System-wide report
            usage_stats = self.get_usage_stats(days)
            cost_analysis = self.get_cost_analysis(days)
            performance_metrics = self.get_performance_metrics(days)
            
            return {
                "report_type": "system",
                "period_days": days,
                "usage_stats": usage_stats.dict(),
                "cost_analysis": cost_analysis,
                "performance_metrics": performance_metrics,
                "generated_at": datetime.now().isoformat()
            }
