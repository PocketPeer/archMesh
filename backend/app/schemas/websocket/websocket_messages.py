"""
WebSocket message schemas for ArchMesh

This module defines Pydantic schemas for all WebSocket messages
including workflow updates, notifications, and system events.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class MessageType(str, Enum):
    """WebSocket message types"""
    WORKFLOW_UPDATE = "workflow_update"
    NOTIFICATION = "notification"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    LARGE_DATA = "large_data"
    LARGE_DATA_RECEIVED = "large_data_received"


class WorkflowStatus(str, Enum):
    """Workflow status values"""
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationCategory(str, Enum):
    """Notification categories"""
    WORKFLOW = "workflow"
    SYSTEM = "system"
    MARKETING = "marketing"
    SECURITY = "security"


class BaseWebSocketMessage(BaseModel):
    """Base WebSocket message schema"""
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    type: MessageType = Field(..., description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class WorkflowUpdate(BaseWebSocketMessage):
    """Workflow update message schema"""
    type: MessageType = Field(default=MessageType.WORKFLOW_UPDATE, description="Message type")
    session_id: str = Field(..., description="Workflow session ID")
    workflow_id: Optional[str] = Field(None, description="Workflow ID")
    stage: str = Field(..., description="Current workflow stage")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress percentage (0.0-1.0)")
    status: WorkflowStatus = Field(..., description="Workflow status")
    message: str = Field(..., description="Status message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class NotificationMessage(BaseWebSocketMessage):
    """Notification message schema"""
    type: MessageType = Field(default=MessageType.NOTIFICATION, description="Message type")
    id: str = Field(..., description="Notification ID")
    user_id: str = Field(..., description="Target user ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    priority: NotificationPriority = Field(..., description="Notification priority")
    category: NotificationCategory = Field(..., description="Notification category")
    action: Optional[Dict[str, str]] = Field(None, description="Action button configuration")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class PingMessage(BaseWebSocketMessage):
    """Ping message schema"""
    type: MessageType = Field(default=MessageType.PING, description="Message type")


class PongMessage(BaseWebSocketMessage):
    """Pong message schema"""
    type: MessageType = Field(default=MessageType.PONG, description="Message type")


class ErrorMessage(BaseWebSocketMessage):
    """Error message schema"""
    type: MessageType = Field(default=MessageType.ERROR, description="Message type")
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class LargeDataMessage(BaseWebSocketMessage):
    """Large data message schema"""
    type: MessageType = Field(default=MessageType.LARGE_DATA, description="Message type")
    data: str = Field(..., description="Large data payload")


class LargeDataReceivedMessage(BaseWebSocketMessage):
    """Large data received confirmation schema"""
    type: MessageType = Field(default=MessageType.LARGE_DATA_RECEIVED, description="Message type")
    size: int = Field(..., description="Data size in bytes")


# Union type for all WebSocket messages
WebSocketMessage = Union[
    WorkflowUpdate,
    NotificationMessage,
    PingMessage,
    PongMessage,
    ErrorMessage,
    LargeDataMessage,
    LargeDataReceivedMessage
]
