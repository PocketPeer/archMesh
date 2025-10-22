"""
Admin Module Data Models
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ModelProvider(str, Enum):
    """LLM Model Providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


class ModelStatus(str, Enum):
    """Model Status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class UserRole(str, Enum):
    """User Roles"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class MetricType(str, Enum):
    """Analytics Metric Types"""
    USAGE = "usage"
    COST = "cost"
    PERFORMANCE = "performance"
    ERROR = "error"


class ModelConfig(BaseModel):
    """LLM Model Configuration"""
    id: str
    name: str
    provider: ModelProvider
    model_name: str
    status: ModelStatus = ModelStatus.ACTIVE
    cost_per_1k_tokens: Dict[str, float] = Field(default_factory=dict)
    max_tokens: int = 4000
    temperature: float = 0.3
    timeout_seconds: int = 30
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserConfig(BaseModel):
    """User Configuration"""
    id: str
    email: str
    name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    api_key: Optional[str] = None
    usage_limit: Optional[int] = None
    cost_limit: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AnalyticsMetric(BaseModel):
    """Analytics Metric"""
    id: str
    user_id: str
    metric_type: MetricType
    value: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemHealth(BaseModel):
    """System Health Status"""
    status: str
    uptime: float
    memory_usage: float
    cpu_usage: float
    active_models: int
    total_requests: int
    error_rate: float
    last_updated: datetime = Field(default_factory=datetime.now)


class UsageStats(BaseModel):
    """Usage Statistics"""
    total_requests: int
    total_tokens: int
    total_cost: float
    requests_by_model: Dict[str, int] = Field(default_factory=dict)
    cost_by_model: Dict[str, float] = Field(default_factory=dict)
    requests_by_user: Dict[str, int] = Field(default_factory=dict)
    period_start: datetime
    period_end: datetime
