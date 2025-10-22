"""
Notification schemas for ArchMesh

This module defines Pydantic schemas for notifications,
user preferences, templates, and delivery status.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, validator


class NotificationChannel(str, Enum):
    """Notification channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    BROWSER_PUSH = "browser_push"
    SMS = "sms"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    """Notification types"""
    WORKFLOW_REVIEW_REQUIRED = "workflow_review_required"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_UPDATE = "workflow_update"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SECURITY_ALERT = "security_alert"
    MARKETING = "marketing"


class NotificationCategory(str, Enum):
    """Notification categories"""
    WORKFLOW = "workflow"
    SYSTEM = "system"
    MARKETING = "marketing"
    SECURITY = "security"


class DeliveryStatus(str, Enum):
    """Delivery status values"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Notification(BaseModel):
    """Notification schema"""
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    id: str = Field(..., description="Unique notification ID")
    user_id: str = Field(..., description="Target user ID")
    type: NotificationType = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    priority: NotificationPriority = Field(..., description="Notification priority")
    category: NotificationCategory = Field(..., description="Notification category")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Notification timestamp")
    action: Optional[Dict[str, str]] = Field(None, description="Action button configuration")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class UserNotificationPreferences(BaseModel):
    """User notification preferences schema"""
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    user_id: str = Field(..., description="User ID")
    channels: Dict[NotificationChannel, bool] = Field(
        default_factory=lambda: {
            NotificationChannel.IN_APP: True,
            NotificationChannel.EMAIL: True,
            NotificationChannel.BROWSER_PUSH: False,
            NotificationChannel.SMS: False
        },
        description="Channel preferences"
    )
    categories: Dict[NotificationCategory, bool] = Field(
        default_factory=lambda: {
            NotificationCategory.WORKFLOW: True,
            NotificationCategory.SYSTEM: True,
            NotificationCategory.MARKETING: False,
            NotificationCategory.SECURITY: True
        },
        description="Category preferences"
    )
    quiet_hours: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "enabled": False,
            "start": "22:00",
            "end": "08:00",
            "timezone": "UTC"
        },
        description="Quiet hours configuration"
    )
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last updated timestamp")


class NotificationTemplate(BaseModel):
    """Notification template schema"""
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    name: str = Field(..., description="Template name")
    type: NotificationType = Field(..., description="Notification type")
    title_template: str = Field(..., description="Title template with variables")
    message_template: str = Field(..., description="Message template with variables")
    variables: List[str] = Field(default_factory=list, description="Required template variables")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Default priority")
    category: NotificationCategory = Field(..., description="Notification category")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last updated timestamp")


class NotificationDeliveryStatus(BaseModel):
    """Notification delivery status schema"""
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    notification_id: str = Field(..., description="Notification ID")
    overall_status: DeliveryStatus = Field(..., description="Overall delivery status")
    channel_statuses: List[Dict[str, Any]] = Field(default_factory=list, description="Per-channel delivery status")
    retry_attempts: int = Field(default=0, ge=0, description="Number of retry attempts")
    last_attempt: Optional[datetime] = Field(None, description="Last delivery attempt timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    delivered_at: Optional[datetime] = Field(None, description="Delivery completion timestamp")


class NotificationResult(BaseModel):
    """Notification sending result schema"""
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    success: bool = Field(..., description="Whether notification was sent successfully")
    notification_id: str = Field(..., description="Notification ID")
    channels_sent: List[NotificationChannel] = Field(default_factory=list, description="Channels that were used")
    channels_failed: List[NotificationChannel] = Field(default_factory=list, description="Channels that failed")
    retry_attempts: int = Field(default=0, ge=0, description="Number of retry attempts")
    quiet_hours_overridden: bool = Field(default=False, description="Whether quiet hours were overridden")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Result timestamp")
    errors: List[str] = Field(default_factory=list, description="Error messages")


class BatchNotificationResult(BaseModel):
    """Batch notification result schema"""
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    success: bool = Field(..., description="Whether batch operation was successful")
    total_sent: int = Field(..., ge=0, description="Total notifications sent")
    successful: int = Field(..., ge=0, description="Successfully sent notifications")
    failed: int = Field(..., ge=0, description="Failed notifications")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Result timestamp")


class NotificationAnalytics(BaseModel):
    """Notification analytics schema"""
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    total_notifications: int = Field(..., ge=0, description="Total notifications sent")
    successful_deliveries: int = Field(..., ge=0, description="Successful deliveries")
    failed_deliveries: int = Field(..., ge=0, description="Failed deliveries")
    channel_breakdown: Dict[NotificationChannel, int] = Field(default_factory=dict, description="Per-channel statistics")
    category_breakdown: Dict[NotificationCategory, int] = Field(default_factory=dict, description="Per-category statistics")
    priority_breakdown: Dict[NotificationPriority, int] = Field(default_factory=dict, description="Per-priority statistics")
    time_range: Optional[Dict[str, str]] = Field(None, description="Analytics time range")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analytics timestamp")
