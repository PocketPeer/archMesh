"""
Notification schemas for ArchMesh

This module provides Pydantic schemas for notifications,
including multi-channel support, user preferences, and templates.
"""

from .notification_schemas import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationType,
    UserNotificationPreferences,
    NotificationTemplate,
    NotificationDeliveryStatus,
    NotificationResult,
    BatchNotificationResult,
    NotificationAnalytics
)

__all__ = [
    "Notification",
    "NotificationChannel", 
    "NotificationPriority",
    "NotificationType",
    "UserNotificationPreferences",
    "NotificationTemplate",
    "NotificationDeliveryStatus",
    "NotificationResult",
    "BatchNotificationResult",
    "NotificationAnalytics"
]
