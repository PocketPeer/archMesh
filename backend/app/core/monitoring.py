"""
Performance monitoring and logging for ArchMesh production.
"""

import time
import logging
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor performance metrics and log them."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_time = time.time()
    
    def log_metric(self, name: str, value: float, unit: str = "ms", metadata: Optional[Dict] = None):
        """Log a performance metric."""
        metric = {
            "name": name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        logger.info(f"METRIC: {json.dumps(metric)}")
        
        # Store in memory for real-time monitoring
        self.metrics[name] = metric
    
    def log_llm_call(self, provider: str, model: str, response_time: float, 
                    tokens_used: Optional[int] = None, success: bool = True):
        """Log LLM call performance."""
        self.log_metric(
            name="llm_call",
            value=response_time,
            unit="ms",
            metadata={
                "provider": provider,
                "model": model,
                "tokens_used": tokens_used,
                "success": success
            }
        )
    
    def log_workflow_step(self, workflow_id: str, step_name: str, duration: float, 
                         status: str, metadata: Optional[Dict] = None):
        """Log workflow step performance."""
        self.log_metric(
            name="workflow_step",
            value=duration,
            unit="ms",
            metadata={
                "workflow_id": workflow_id,
                "step_name": step_name,
                "status": status,
                **(metadata or {})
            }
        )
    
    def log_api_request(self, endpoint: str, method: str, response_time: float, 
                       status_code: int, user_id: Optional[str] = None):
        """Log API request performance."""
        self.log_metric(
            name="api_request",
            value=response_time,
            unit="ms",
            metadata={
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "user_id": user_id
            }
        )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        return {
            "uptime": time.time() - self.start_time,
            "metrics_count": len(self.metrics),
            "recent_metrics": dict(list(self.metrics.items())[-10:])
        }

# Global monitor instance
monitor = PerformanceMonitor()

def track_performance(metric_name: str, unit: str = "ms"):
    """Decorator to track function performance."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                monitor.log_metric(metric_name, duration, unit)
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                monitor.log_metric(f"{metric_name}_error", duration, unit, 
                                {"error": str(e)})
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                monitor.log_metric(metric_name, duration, unit)
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                monitor.log_metric(f"{metric_name}_error", duration, unit, 
                                {"error": str(e)})
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def log_llm_performance(provider: str, model: str, response_time: float, 
                       tokens_used: Optional[int] = None, success: bool = True):
    """Log LLM performance metrics."""
    monitor.log_llm_call(provider, model, response_time, tokens_used, success)

def log_workflow_performance(workflow_id: str, step_name: str, duration: float, 
                           status: str, metadata: Optional[Dict] = None):
    """Log workflow performance metrics."""
    monitor.log_workflow_step(workflow_id, step_name, duration, status, metadata)

def log_api_performance(endpoint: str, method: str, response_time: float, 
                       status_code: int, user_id: Optional[str] = None):
    """Log API performance metrics."""
    monitor.log_api_request(endpoint, method, response_time, status_code, user_id)

# Health check endpoint data
def get_health_status() -> Dict[str, Any]:
    """Get system health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - monitor.start_time,
        "metrics": monitor.get_metrics_summary()
    }
