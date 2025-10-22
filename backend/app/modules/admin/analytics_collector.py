"""
Analytics Collector - Tracks usage, costs, and performance metrics
"""

import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

from .models import AnalyticsMetric, MetricType, SystemHealth, UsageStats


class AnalyticsCollector:
    """
    Collects and analyzes system metrics.
    
    Responsibilities:
    - Usage tracking
    - Cost monitoring
    - Performance metrics
    - Error tracking
    - System health monitoring
    """
    
    def __init__(self):
        self.metrics: List[AnalyticsMetric] = []
        self.start_time = time.time()
        self.request_counts = defaultdict(int)
        self.cost_totals = defaultdict(float)
        self.error_counts = defaultdict(int)
        self.response_times = []
    
    def track_request(self, user_id: str, model_id: str, prompt_tokens: int, 
                     completion_tokens: int, cost: float, response_time: float):
        """Track a successful request"""
        # Track usage metrics
        self.metrics.append(AnalyticsMetric(
            id=f"usage_{int(time.time())}_{user_id}",
            user_id=user_id,
            metric_type=MetricType.USAGE,
            value=1.0,
            metadata={
                "model_id": model_id,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "response_time": response_time
            }
        ))
        
        # Track cost metrics
        self.metrics.append(AnalyticsMetric(
            id=f"cost_{int(time.time())}_{user_id}",
            user_id=user_id,
            metric_type=MetricType.COST,
            value=cost,
            metadata={
                "model_id": model_id,
                "cost_per_1k_tokens": cost / ((prompt_tokens + completion_tokens) / 1000) if (prompt_tokens + completion_tokens) > 0 else 0
            }
        ))
        
        # Track performance metrics
        self.metrics.append(AnalyticsMetric(
            id=f"perf_{int(time.time())}_{user_id}",
            user_id=user_id,
            metric_type=MetricType.PERFORMANCE,
            value=response_time,
            metadata={
                "model_id": model_id,
                "tokens_per_second": (prompt_tokens + completion_tokens) / response_time if response_time > 0 else 0
            }
        ))
        
        # Update aggregated counters
        self.request_counts[user_id] += 1
        self.cost_totals[user_id] += cost
        self.response_times.append(response_time)
        
        logger.debug(f"Tracked request for user {user_id} using model {model_id}")
    
    def track_error(self, user_id: str, model_id: str, error_type: str, error_message: str):
        """Track an error"""
        self.metrics.append(AnalyticsMetric(
            id=f"error_{int(time.time())}_{user_id}",
            user_id=user_id,
            metric_type=MetricType.ERROR,
            value=1.0,
            metadata={
                "model_id": model_id,
                "error_type": error_type,
                "error_message": error_message
            }
        ))
        
        self.error_counts[user_id] += 1
        logger.warning(f"Tracked error for user {user_id}: {error_type}")
    
    def get_user_usage(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for a specific user"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        user_metrics = [
            m for m in self.metrics 
            if m.user_id == user_id and m.timestamp >= cutoff_date
        ]
        
        usage_metrics = [m for m in user_metrics if m.metric_type == MetricType.USAGE]
        cost_metrics = [m for m in user_metrics if m.metric_type == MetricType.COST]
        performance_metrics = [m for m in user_metrics if m.metric_type == MetricType.PERFORMANCE]
        error_metrics = [m for m in user_metrics if m.metric_type == MetricType.ERROR]
        
        total_requests = len(usage_metrics)
        total_cost = sum(m.value for m in cost_metrics)
        avg_response_time = sum(m.value for m in performance_metrics) / len(performance_metrics) if performance_metrics else 0
        total_errors = len(error_metrics)
        
        # Model breakdown
        model_usage = defaultdict(int)
        model_costs = defaultdict(float)
        
        for metric in usage_metrics:
            model_id = metric.metadata.get("model_id", "unknown")
            model_usage[model_id] += 1
        
        for metric in cost_metrics:
            model_id = metric.metadata.get("model_id", "unknown")
            model_costs[model_id] += metric.value
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_requests": total_requests,
            "total_cost": total_cost,
            "average_response_time": avg_response_time,
            "total_errors": total_errors,
            "error_rate": total_errors / total_requests if total_requests > 0 else 0,
            "model_usage": dict(model_usage),
            "model_costs": dict(model_costs),
            "requests_per_day": total_requests / days if days > 0 else 0,
            "cost_per_day": total_cost / days if days > 0 else 0
        }
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        uptime = time.time() - self.start_time
        
        # Calculate error rate
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        error_rate = total_errors / total_requests if total_requests > 0 else 0
        
        # Calculate average response time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        # Get active models (this would need integration with ModelManager)
        active_models = 5  # Placeholder
        
        return SystemHealth(
            status="healthy" if error_rate < 0.05 else "degraded",
            uptime=uptime,
            memory_usage=0.0,  # Would need system monitoring
            cpu_usage=0.0,    # Would need system monitoring
            active_models=active_models,
            total_requests=total_requests,
            error_rate=error_rate,
            last_updated=datetime.now()
        )
    
    def get_usage_stats(self, days: int = 30) -> UsageStats:
        """Get overall usage statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_metrics = [
            m for m in self.metrics 
            if m.timestamp >= cutoff_date
        ]
        
        usage_metrics = [m for m in recent_metrics if m.metric_type == MetricType.USAGE]
        cost_metrics = [m for m in recent_metrics if m.metric_type == MetricType.COST]
        
        total_requests = len(usage_metrics)
        total_cost = sum(m.value for m in cost_metrics)
        total_tokens = sum(m.metadata.get("total_tokens", 0) for m in usage_metrics)
        
        # Requests by model
        requests_by_model = defaultdict(int)
        for metric in usage_metrics:
            model_id = metric.metadata.get("model_id", "unknown")
            requests_by_model[model_id] += 1
        
        # Cost by model
        cost_by_model = defaultdict(float)
        for metric in cost_metrics:
            model_id = metric.metadata.get("model_id", "unknown")
            cost_by_model[model_id] += metric.value
        
        # Requests by user
        requests_by_user = defaultdict(int)
        for metric in usage_metrics:
            requests_by_user[metric.user_id] += 1
        
        return UsageStats(
            total_requests=total_requests,
            total_tokens=total_tokens,
            total_cost=total_cost,
            requests_by_model=dict(requests_by_model),
            cost_by_model=dict(cost_by_model),
            requests_by_user=dict(requests_by_user),
            period_start=cutoff_date,
            period_end=datetime.now()
        )
    
    def get_cost_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed cost analysis"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_metrics = [
            m for m in self.metrics 
            if m.timestamp >= cutoff_date and m.metric_type == MetricType.COST
        ]
        
        total_cost = sum(m.value for m in recent_metrics)
        
        # Cost by model
        cost_by_model = defaultdict(float)
        for metric in recent_metrics:
            model_id = metric.metadata.get("model_id", "unknown")
            cost_by_model[model_id] += metric.value
        
        # Cost by user
        cost_by_user = defaultdict(float)
        for metric in recent_metrics:
            cost_by_user[metric.user_id] += metric.value
        
        # Daily cost trend
        daily_costs = defaultdict(float)
        for metric in recent_metrics:
            date_key = metric.timestamp.date().isoformat()
            daily_costs[date_key] += metric.value
        
        return {
            "total_cost": total_cost,
            "average_daily_cost": total_cost / days if days > 0 else 0,
            "cost_by_model": dict(cost_by_model),
            "cost_by_user": dict(cost_by_user),
            "daily_costs": dict(daily_costs),
            "most_expensive_model": max(cost_by_model.items(), key=lambda x: x[1])[0] if cost_by_model else None,
            "highest_spending_user": max(cost_by_user.items(), key=lambda x: x[1])[0] if cost_by_user else None
        }
    
    def get_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_metrics = [
            m for m in self.metrics 
            if m.timestamp >= cutoff_date and m.metric_type == MetricType.PERFORMANCE
        ]
        
        if not recent_metrics:
            return {"error": "No performance data available"}
        
        response_times = [m.value for m in recent_metrics]
        tokens_per_second = [m.metadata.get("tokens_per_second", 0) for m in recent_metrics]
        
        return {
            "average_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "average_tokens_per_second": sum(tokens_per_second) / len(tokens_per_second) if tokens_per_second else 0,
            "total_requests": len(recent_metrics),
            "performance_by_model": self._get_performance_by_model(recent_metrics)
        }
    
    def _get_performance_by_model(self, metrics: List[AnalyticsMetric]) -> Dict[str, Dict[str, float]]:
        """Get performance metrics grouped by model"""
        model_performance = defaultdict(list)
        
        for metric in metrics:
            model_id = metric.metadata.get("model_id", "unknown")
            model_performance[model_id].append(metric.value)
        
        result = {}
        for model_id, response_times in model_performance.items():
            result[model_id] = {
                "average_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "request_count": len(response_times)
            }
        
        return result
    
    def export_metrics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Export metrics data for analysis"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_metrics = [
            m for m in self.metrics 
            if m.timestamp >= cutoff_date
        ]
        
        return [
            {
                "id": m.id,
                "user_id": m.user_id,
                "metric_type": m.metric_type.value,
                "value": m.value,
                "metadata": m.metadata,
                "timestamp": m.timestamp.isoformat()
            }
            for m in recent_metrics
        ]
