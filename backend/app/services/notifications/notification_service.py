"""
Notification Service for ArchMesh

This module provides multi-channel notification functionality
including in-app, email, browser push, and SMS notifications
with user preferences, quiet hours, and comprehensive analytics.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from app.schemas.notifications import (
    Notification, NotificationChannel, NotificationPriority,
    NotificationType, UserNotificationPreferences, NotificationTemplate,
    NotificationDeliveryStatus, NotificationResult, BatchNotificationResult,
    NotificationAnalytics
)
from app.core.exceptions import NotificationError, EmailError, SMSError, TemplateError

logger = logging.getLogger(__name__)


@dataclass
class NotificationStats:
    """Notification statistics tracking"""
    total_sent: int = 0
    successful: int = 0
    failed: int = 0
    channel_stats: Dict[NotificationChannel, int] = field(default_factory=dict)
    category_stats: Dict[str, int] = field(default_factory=dict)
    priority_stats: Dict[NotificationPriority, int] = field(default_factory=dict)


class NotificationService:
    """
    Multi-channel notification service
    
    Provides comprehensive notification functionality with user preferences,
    quiet hours, templates, and analytics.
    """
    
    def __init__(self):
        """Initialize notification service"""
        self.user_preferences: Dict[str, UserNotificationPreferences] = {}
        self.delivery_status: Dict[str, NotificationDeliveryStatus] = {}
        self.templates: Dict[str, NotificationTemplate] = {}
        self.stats = NotificationStats()
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize notification templates"""
        # Workflow review required template
        self.templates["workflow_review_required"] = NotificationTemplate(
            name="workflow_review_required",
            type=NotificationType.WORKFLOW_REVIEW_REQUIRED,
            title_template="Review Required: {workflow_name}",
            message_template="Your workflow '{workflow_name}' in project '{project_name}' requires human review. Please review and approve before proceeding. Review URL: {review_url}",
            variables=["workflow_name", "project_name", "review_url", "deadline"],
            priority=NotificationPriority.HIGH,
            category="workflow"
        )
        
        # Workflow completed template
        self.templates["workflow_completed"] = NotificationTemplate(
            name="workflow_completed",
            type=NotificationType.WORKFLOW_COMPLETED,
            title_template="Workflow Completed: {workflow_name}",
            message_template="Your workflow '{workflow_name}' in project '{project_name}' has been completed successfully. View results: {results_url}",
            variables=["workflow_name", "project_name", "results_url", "completion_time"],
            priority=NotificationPriority.MEDIUM,
            category="workflow"
        )
    
    async def send_notification(self, notification_data: Dict[str, Any]) -> NotificationResult:
        """
        Send notification through appropriate channels
        
        Args:
            notification_data: Notification data
            
        Returns:
            NotificationResult: Sending result
            
        Raises:
            NotificationError: If notification data is invalid
        """
        try:
            # Validate notification data
            notification = Notification(**notification_data)
            
            # Get user preferences
            preferences = await self.get_user_preferences(notification.user_id)
            
            # Check quiet hours
            quiet_hours_override = await self._check_quiet_hours(notification, preferences)
            
            # Determine channels to use
            channels_to_use = self._determine_channels(notification, preferences, quiet_hours_override)
            
            # Send through each channel
            channels_sent = []
            channels_failed = []
            errors = []
            
            for channel in channels_to_use:
                try:
                    result = await self._send_to_channel(notification, channel)
                    if result["success"]:
                        channels_sent.append(channel)
                    else:
                        channels_failed.append(channel)
                        errors.append(f"{channel}: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    channels_failed.append(channel)
                    errors.append(f"{channel}: {str(e)}")
            
            # Update statistics
            self._update_stats(notification, channels_sent, channels_failed)
            
            # Create delivery status
            delivery_status = NotificationDeliveryStatus(
                notification_id=notification.id,
                overall_status="delivered" if channels_sent else "failed",
                channel_statuses=[
                    {"channel": channel, "status": "delivered"} for channel in channels_sent
                ] + [
                    {"channel": channel, "status": "failed"} for channel in channels_failed
                ],
                delivered_at=datetime.utcnow() if channels_sent else None,
                error_message="; ".join(errors) if errors else None
            )
            self.delivery_status[notification.id] = delivery_status
            
            return NotificationResult(
                success=len(channels_sent) > 0,
                notification_id=notification.id,
                channels_sent=channels_sent,
                channels_failed=channels_failed,
                quiet_hours_overridden=quiet_hours_override,
                errors=errors
            )
            
        except Exception as e:
            raise NotificationError(f"Failed to send notification: {e}")
    
    async def send_in_app_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send in-app notification"""
        notification = Notification(**notification_data)
        
        # Simulate in-app notification sending
        await asyncio.sleep(0.01)  # Simulate processing time
        
        return {
            "success": True,
            "channel": NotificationChannel.IN_APP,
            "delivered_at": datetime.utcnow().isoformat()
        }
    
    async def send_email_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notification"""
        notification = Notification(**notification_data)
        
        # Simulate email sending (in real implementation, this would use an email service)
        await asyncio.sleep(0.1)  # Simulate email processing time
        
        return {
            "success": True,
            "channel": NotificationChannel.EMAIL,
            "email_id": f"email-{notification.id}",
            "delivered_at": datetime.utcnow().isoformat()
        }
    
    async def send_browser_push_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send browser push notification"""
        notification = Notification(**notification_data)
        
        # Simulate browser push notification sending
        await asyncio.sleep(0.05)  # Simulate push processing time
        
        return {
            "success": True,
            "channel": NotificationChannel.BROWSER_PUSH,
            "push_id": f"push-{notification.id}",
            "delivered_at": datetime.utcnow().isoformat()
        }
    
    async def send_sms_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send SMS notification"""
        notification = Notification(**notification_data)
        
        # Simulate SMS sending
        await asyncio.sleep(0.2)  # Simulate SMS processing time
        
        return {
            "success": True,
            "channel": NotificationChannel.SMS,
            "sms_id": f"sms-{notification.id}",
            "delivered_at": datetime.utcnow().isoformat()
        }
    
    async def set_user_preferences(self, user_id: str, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set user notification preferences"""
        preferences = UserNotificationPreferences(**preferences_data)
        self.user_preferences[user_id] = preferences
        
        return {
            "success": True,
            "user_id": user_id
        }
    
    async def get_user_preferences(self, user_id: str) -> UserNotificationPreferences:
        """Get user notification preferences"""
        if user_id not in self.user_preferences:
            # Return default preferences
            return UserNotificationPreferences(user_id=user_id)
        
        return self.user_preferences[user_id]
    
    async def update_user_preferences(self, user_id: str, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user notification preferences"""
        if user_id not in self.user_preferences:
            raise NotificationError(f"User preferences not found: {user_id}")
        
        # Update existing preferences
        existing = self.user_preferences[user_id]
        updated_data = existing.dict()
        updated_data.update(preferences_data)
        
        preferences = UserNotificationPreferences(**updated_data)
        self.user_preferences[user_id] = preferences
        
        return {
            "success": True
        }
    
    async def send_batch_notifications(self, notifications: List[Dict[str, Any]]) -> BatchNotificationResult:
        """Send batch notifications"""
        total_sent = len(notifications)
        successful = 0
        failed = 0
        errors = []
        
        for notification_data in notifications:
            try:
                result = await self.send_notification(notification_data)
                if result.success:
                    successful += 1
                else:
                    failed += 1
                    errors.extend(result.errors)
            except Exception as e:
                failed += 1
                errors.append(f"Notification {notification_data.get('id', 'unknown')}: {str(e)}")
        
        return BatchNotificationResult(
            success=successful > 0,
            total_sent=total_sent,
            successful=successful,
            failed=failed,
            errors=errors
        )
    
    async def render_notification_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render notification template"""
        template_name = template_data.get("template_name")
        variables = template_data.get("variables", {})
        
        if template_name not in self.templates:
            raise TemplateError(f"Template not found: {template_name}")
        
        template = self.templates[template_name]
        
        # Check required variables
        missing_vars = [var for var in template.variables if var not in variables]
        if missing_vars:
            raise TemplateError(f"Missing required variables: {missing_vars}")
        
        # Render template
        try:
            title = template.title_template.format(**variables)
            message = template.message_template.format(**variables)
            
            return {
                "success": True,
                "title": title,
                "message": message,
                "priority": template.priority,
                "category": template.category
            }
        except KeyError as e:
            raise TemplateError(f"Template rendering failed: {e}")
    
    async def get_delivery_status(self, notification_id: str) -> NotificationDeliveryStatus:
        """Get notification delivery status"""
        if notification_id not in self.delivery_status:
            raise NotificationError(f"Delivery status not found: {notification_id}")
        
        return self.delivery_status[notification_id]
    
    async def get_notification_analytics(self, start_time: Optional[datetime] = None, 
                                       end_time: Optional[datetime] = None) -> NotificationAnalytics:
        """Get notification analytics"""
        # In a real implementation, this would query a database
        # For now, return mock analytics based on stats
        
        channel_breakdown = {}
        for channel in NotificationChannel:
            channel_breakdown[channel] = self.stats.channel_stats.get(channel, 0)
        
        category_breakdown = {}
        for category in ["workflow", "system", "marketing", "security"]:
            category_breakdown[category] = self.stats.category_stats.get(category, 0)
        
        priority_breakdown = {}
        for priority in NotificationPriority:
            priority_breakdown[priority] = self.stats.priority_stats.get(priority, 0)
        
        time_range = None
        if start_time and end_time:
            time_range = {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            }
        
        return NotificationAnalytics(
            total_notifications=self.stats.total_sent,
            successful_deliveries=self.stats.successful,
            failed_deliveries=self.stats.failed,
            channel_breakdown=channel_breakdown,
            category_breakdown=category_breakdown,
            priority_breakdown=priority_breakdown,
            time_range=time_range
        )
    
    async def handle_workflow_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow event and send appropriate notification"""
        event_type = event_data.get("type")
        
        if event_type == "workflow_review_required":
            # Create notification from workflow event
            notification_data = {
                "id": f"notif-{event_data.get('workflow_id', 'unknown')}",
                "user_id": event_data.get("user_id"),
                "type": NotificationType.WORKFLOW_REVIEW_REQUIRED,
                "title": "Review Required",
                "message": "Your workflow requires human review",
                "priority": NotificationPriority.HIGH,
                "category": "workflow",
                "metadata": event_data
            }
            
            result = await self.send_notification(notification_data)
            return {
                "success": result.success,
                "notification_id": result.notification_id,
                "channels_sent": result.channels_sent
            }
        
        return {"success": False, "error": f"Unknown event type: {event_type}"}
    
    def _determine_channels(self, notification: Notification, preferences: UserNotificationPreferences, 
                          quiet_hours_override: bool) -> List[NotificationChannel]:
        """Determine which channels to use for notification"""
        channels = []
        
        # Check user preferences
        if preferences.channels.get(NotificationChannel.IN_APP, True):
            channels.append(NotificationChannel.IN_APP)
        
        if preferences.channels.get(NotificationChannel.EMAIL, True):
            channels.append(NotificationChannel.EMAIL)
        
        if preferences.channels.get(NotificationChannel.BROWSER_PUSH, False):
            channels.append(NotificationChannel.BROWSER_PUSH)
        
        if preferences.channels.get(NotificationChannel.SMS, False):
            channels.append(NotificationChannel.SMS)
        
        # Apply quiet hours logic
        if not quiet_hours_override and preferences.quiet_hours.get("enabled", False):
            # During quiet hours, only send in-app notifications
            channels = [ch for ch in channels if ch == NotificationChannel.IN_APP]
        
        return channels
    
    async def _check_quiet_hours(self, notification: Notification, preferences: UserNotificationPreferences) -> bool:
        """Check if quiet hours should be overridden"""
        if not preferences.quiet_hours.get("enabled", False):
            return False
        
        # Override quiet hours for critical notifications
        if notification.priority == NotificationPriority.CRITICAL:
            return True
        
        return False
    
    async def _send_to_channel(self, notification: Notification, channel: NotificationChannel) -> Dict[str, Any]:
        """Send notification to specific channel"""
        notification_data = notification.dict()
        
        if channel == NotificationChannel.IN_APP:
            return await self.send_in_app_notification(notification_data)
        elif channel == NotificationChannel.EMAIL:
            return await self.send_email_notification(notification_data)
        elif channel == NotificationChannel.BROWSER_PUSH:
            return await self.send_browser_push_notification(notification_data)
        elif channel == NotificationChannel.SMS:
            return await self.send_sms_notification(notification_data)
        else:
            raise NotificationError(f"Unknown channel: {channel}")
    
    def _update_stats(self, notification: Notification, channels_sent: List[NotificationChannel], 
                     channels_failed: List[NotificationChannel]):
        """Update notification statistics"""
        self.stats.total_sent += 1
        
        if channels_sent:
            self.stats.successful += 1
        else:
            self.stats.failed += 1
        
        # Update channel stats
        for channel in channels_sent:
            self.stats.channel_stats[channel] = self.stats.channel_stats.get(channel, 0) + 1
        
        # Update category stats
        category = notification.category
        self.stats.category_stats[category] = self.stats.category_stats.get(category, 0) + 1
        
        # Update priority stats
        priority = notification.priority
        self.stats.priority_stats[priority] = self.stats.priority_stats.get(priority, 0) + 1

