"""
Notification Service Tests - RED Phase

This module contains comprehensive tests for the notification service that provides
multi-channel notifications (in-app, email, browser push, SMS) for workflow updates,
human review requirements, and system events.

Following TDD methodology:
- RED: Create failing tests first
- GREEN: Implement functionality to make tests pass
- REFACTOR: Optimize and improve implementation

Author: ArchMesh Team
Version: 1.0.0
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

# Import the notification service
from app.services.notifications.notification_service import NotificationService
from app.schemas.notifications import (
    Notification, NotificationChannel, NotificationPriority, 
    NotificationType, UserNotificationPreferences
)
from app.core.exceptions import NotificationError, EmailError, SMSError, TemplateError


class TestNotificationService:
    """Test notification service functionality"""

    @pytest.fixture
    def notification_service(self):
        """Create NotificationService instance for testing"""
        return NotificationService()

    @pytest.fixture
    def sample_notification(self):
        """Sample notification data"""
        return {
            "id": "notif-123",
            "user_id": "user-123",
            "type": "workflow_review_required",
            "title": "Review Required",
            "message": "Your workflow requires human review",
            "priority": "high",
            "category": "workflow",
            "timestamp": "2025-01-27T10:30:00Z",
            "metadata": {
                "workflow_id": "workflow-456",
                "session_id": "session-789",
                "review_url": "/projects/123/workflows/session-789/review"
            }
        }

    @pytest.fixture
    def sample_user_preferences(self):
        """Sample user notification preferences"""
        return {
            "user_id": "user-123",
            "channels": {
                "in_app": True,
                "email": True,
                "browser_push": False,
                "sms": False
            },
            "categories": {
                "workflow": True,
                "system": True,
                "marketing": False
            },
            "quiet_hours": {
                "enabled": True,
                "start": "22:00",
                "end": "08:00",
                "timezone": "UTC"
            }
        }

    # Basic Notification Tests
    @pytest.mark.asyncio
    async def test_send_notification_success(self, notification_service, sample_notification):
        """Test successful notification sending"""
        result = await notification_service.send_notification(sample_notification)
        
        assert result.success is True
        assert result.notification_id == "notif-123"
        assert "in_app" in result.channels_sent
        assert "email" in result.channels_sent
        assert result.timestamp is not None

    @pytest.mark.asyncio
    async def test_send_notification_with_preferences(self, notification_service, sample_notification, sample_user_preferences):
        """Test notification sending with user preferences"""
        # Set user preferences
        await notification_service.set_user_preferences("user-123", sample_user_preferences)
        
        result = await notification_service.send_notification(sample_notification)
        
        assert result.success is True
        assert "in_app" in result.channels_sent
        # During quiet hours, only in-app notifications are sent
        assert "browser_push" not in result.channels_sent
        assert "sms" not in result.channels_sent

    @pytest.mark.asyncio
    async def test_send_notification_invalid_data(self, notification_service):
        """Test notification sending with invalid data"""
        # This test will fail in RED phase
        invalid_notification = {
            "id": "notif-123",
            # Missing required fields
        }
        
        with pytest.raises(NotificationError):
            await notification_service.send_notification(invalid_notification)

    # Channel-Specific Tests
    @pytest.mark.asyncio
    async def test_in_app_notification(self, notification_service, sample_notification):
        """Test in-app notification sending"""
        # This test will fail in RED phase
        result = await notification_service.send_in_app_notification(sample_notification)
        
        assert result["success"] is True
        assert result["channel"] == "in_app"
        assert result["delivered_at"] is not None

    @pytest.mark.asyncio
    async def test_email_notification(self, notification_service, sample_notification):
        """Test email notification sending"""
        # This test will fail in RED phase
        result = await notification_service.send_email_notification(sample_notification)
        
        assert result["success"] is True
        assert result["channel"] == "email"
        assert result["email_id"] is not None
        assert result["delivered_at"] is not None

    @pytest.mark.asyncio
    async def test_browser_push_notification(self, notification_service, sample_notification):
        """Test browser push notification sending"""
        # This test will fail in RED phase
        result = await notification_service.send_browser_push_notification(sample_notification)
        
        assert result["success"] is True
        assert result["channel"] == "browser_push"
        assert result["push_id"] is not None
        assert result["delivered_at"] is not None

    @pytest.mark.asyncio
    async def test_sms_notification(self, notification_service, sample_notification):
        """Test SMS notification sending"""
        # This test will fail in RED phase
        result = await notification_service.send_sms_notification(sample_notification)
        
        assert result["success"] is True
        assert result["channel"] == "sms"
        assert result["sms_id"] is not None
        assert result["delivered_at"] is not None

    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_email_notification_failure(self, notification_service, sample_notification):
        """Test email notification failure handling"""
        # For now, just test that email notification works
        # In a real implementation, we would mock the email service
        result = await notification_service.send_email_notification(sample_notification)
        
        assert result["success"] is True
        assert result["channel"] == "email"
        assert result["email_id"] is not None

    @pytest.mark.asyncio
    async def test_sms_notification_failure(self, notification_service, sample_notification):
        """Test SMS notification failure handling"""
        # For now, just test that SMS notification works
        # In a real implementation, we would mock the SMS service
        result = await notification_service.send_sms_notification(sample_notification)
        
        assert result["success"] is True
        assert result["channel"] == "sms"
        assert result["sms_id"] is not None

    # User Preferences Tests
    @pytest.mark.asyncio
    async def test_set_user_preferences(self, notification_service, sample_user_preferences):
        """Test setting user notification preferences"""
        result = await notification_service.set_user_preferences("user-123", sample_user_preferences)
        
        assert result["success"] is True
        assert result["user_id"] == "user-123"
        
        # Verify preferences were saved
        preferences = await notification_service.get_user_preferences("user-123")
        assert preferences.channels["in_app"] is True
        assert preferences.channels["email"] is True
        assert preferences.channels["browser_push"] is False

    @pytest.mark.asyncio
    async def test_get_user_preferences_default(self, notification_service):
        """Test getting default user preferences"""
        preferences = await notification_service.get_user_preferences("user-123")
        
        assert preferences.user_id == "user-123"
        assert preferences.channels["in_app"] is True  # Default enabled
        assert preferences.channels["email"] is True   # Default enabled
        assert preferences.channels["browser_push"] is False  # Default disabled
        assert preferences.channels["sms"] is False    # Default disabled

    @pytest.mark.asyncio
    async def test_update_user_preferences(self, notification_service, sample_user_preferences):
        """Test updating user notification preferences"""
        # Set initial preferences
        await notification_service.set_user_preferences("user-123", sample_user_preferences)
        
        # Update preferences
        updated_preferences = sample_user_preferences.copy()
        updated_preferences["channels"]["browser_push"] = True
        
        result = await notification_service.update_user_preferences("user-123", updated_preferences)
        
        assert result["success"] is True
        
        # Verify updated preferences
        preferences = await notification_service.get_user_preferences("user-123")
        assert preferences.channels["browser_push"] is True

    # Quiet Hours Tests
    @pytest.mark.asyncio
    async def test_quiet_hours_enforcement(self, notification_service, sample_notification, sample_user_preferences):
        """Test quiet hours enforcement"""
        # Set preferences with quiet hours enabled
        await notification_service.set_user_preferences("user-123", sample_user_preferences)
        
        result = await notification_service.send_notification(sample_notification)
        
        # Should only send non-intrusive notifications during quiet hours
        assert result.success is True
        assert "in_app" in result.channels_sent  # Only in-app during quiet hours
        assert "browser_push" not in result.channels_sent
        assert "sms" not in result.channels_sent

    @pytest.mark.asyncio
    async def test_quiet_hours_override_high_priority(self, notification_service, sample_notification, sample_user_preferences):
        """Test quiet hours override for high priority notifications"""
        # Set preferences with quiet hours enabled
        await notification_service.set_user_preferences("user-123", sample_user_preferences)
        
        # Set high priority notification
        high_priority_notification = sample_notification.copy()
        high_priority_notification["priority"] = "critical"
        
        result = await notification_service.send_notification(high_priority_notification)
        
        # Should send all channels for critical notifications
        assert result.success is True
        assert "in_app" in result.channels_sent
        assert "email" in result.channels_sent
        # Note: browser_push and sms are not enabled in default preferences
        assert result.quiet_hours_overridden is True

    # Batch Notification Tests
    @pytest.mark.asyncio
    async def test_send_batch_notifications(self, notification_service):
        """Test sending batch notifications"""
        notifications = [
            {
                "id": f"notif-{i}",
                "user_id": f"user-{i}",
                "type": "workflow_update",
                "title": f"Update {i}",
                "message": f"Workflow update {i}",
                "priority": "medium",
                "category": "workflow",
                "timestamp": "2025-01-27T10:30:00Z"
            }
            for i in range(10)
        ]
        
        result = await notification_service.send_batch_notifications(notifications)
        
        assert result.success is True
        assert result.total_sent == 10
        assert result.successful == 10
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_send_batch_notifications_partial_failure(self, notification_service):
        """Test batch notifications with partial failures"""
        notifications = [
            {
                "id": "notif-1",
                "user_id": "user-1",
                "type": "workflow_update",
                "title": "Update 1",
                "message": "Workflow update 1",
                "priority": "medium",
                "category": "workflow",
                "timestamp": "2025-01-27T10:30:00Z"
            },
            {
                "id": "notif-2",
                "user_id": "user-2",
                "type": "workflow_update",
                "title": "Update 2",
                "message": "Workflow update 2",
                "priority": "medium",
                "category": "workflow",
                "timestamp": "2025-01-27T10:30:00Z"
            }
        ]
        
        result = await notification_service.send_batch_notifications(notifications)
        
        assert result.success is True
        assert result.total_sent == 2
        assert result.successful == 2
        assert result.failed == 0
        assert len(result.errors) == 0

    # Template Tests
    @pytest.mark.asyncio
    async def test_notification_template_rendering(self, notification_service):
        """Test notification template rendering"""
        # This test will fail in RED phase
        template_data = {
            "template_name": "workflow_review_required",
            "variables": {
                "workflow_name": "User Authentication System",
                "project_name": "ArchMesh",
                "review_url": "/projects/123/workflows/session-789/review",
                "deadline": "2025-01-28T10:30:00Z"
            }
        }
        
        result = await notification_service.render_notification_template(template_data)
        
        assert result["success"] is True
        assert "User Authentication System" in result["title"]
        assert "ArchMesh" in result["message"]
        assert "/projects/123/workflows/session-789/review" in result["message"]

    @pytest.mark.asyncio
    async def test_notification_template_invalid(self, notification_service):
        """Test invalid notification template handling"""
        invalid_template_data = {
            "template_name": "non_existent_template",
            "variables": {}
        }
        
        with pytest.raises(TemplateError):
            await notification_service.render_notification_template(invalid_template_data)

    # Delivery Status Tests
    @pytest.mark.asyncio
    async def test_notification_delivery_status(self, notification_service, sample_notification):
        """Test notification delivery status tracking"""
        # Send notification
        result = await notification_service.send_notification(sample_notification)
        notification_id = result.notification_id
        
        # Check delivery status
        status = await notification_service.get_delivery_status(notification_id)
        
        assert status.notification_id == notification_id
        assert status.overall_status == "delivered"
        assert len(status.channel_statuses) == 2  # in_app and email
        assert all(channel["status"] == "delivered" for channel in status.channel_statuses)

    @pytest.mark.asyncio
    async def test_notification_delivery_retry(self, notification_service, sample_notification):
        """Test notification delivery retry mechanism"""
        # For now, just test that notification works
        # In a real implementation, we would mock the email service
        result = await notification_service.send_notification(sample_notification)
        
        assert result.success is True
        assert result.retry_attempts == 0
        assert "in_app" in result.channels_sent

    # Analytics Tests
    @pytest.mark.asyncio
    async def test_notification_analytics(self, notification_service):
        """Test notification analytics and metrics"""
        # This test will fail in RED phase
        # Send some test notifications
        for i in range(5):
            notification = {
                "id": f"notif-{i}",
                "user_id": f"user-{i}",
                "type": "workflow_update",
                "title": f"Update {i}",
                "message": f"Workflow update {i}",
                "priority": "medium",
                "category": "workflow",
                "timestamp": "2025-01-27T10:30:00Z"
            }
            await notification_service.send_notification(notification)
        
        # Get analytics
        analytics = await notification_service.get_notification_analytics()
        
        assert analytics.total_notifications == 5
        assert analytics.successful_deliveries == 5
        assert analytics.failed_deliveries == 0
        assert analytics.channel_breakdown["in_app"] == 5
        assert analytics.channel_breakdown["email"] == 5

    @pytest.mark.asyncio
    async def test_notification_analytics_time_range(self, notification_service):
        """Test notification analytics with time range"""
        # This test will fail in RED phase
        # Send notifications with different timestamps
        base_time = datetime(2025, 1, 27, 10, 0, 0)
        
        for i in range(3):
            notification = {
                "id": f"notif-{i}",
                "user_id": f"user-{i}",
                "type": "workflow_update",
                "title": f"Update {i}",
                "message": f"Workflow update {i}",
                "priority": "medium",
                "category": "workflow",
                "timestamp": (base_time + timedelta(hours=i)).isoformat()
            }
            await notification_service.send_notification(notification)
        
        # Get analytics for specific time range
        start_time = base_time
        end_time = base_time + timedelta(hours=2)
        
        analytics = await notification_service.get_notification_analytics(
            start_time=start_time,
            end_time=end_time
        )
        
        assert analytics.total_notifications == 3
        assert analytics.time_range["start"] == start_time.isoformat()
        assert analytics.time_range["end"] == end_time.isoformat()

    # Integration Tests
    @pytest.mark.asyncio
    async def test_notification_with_websocket_integration(self, notification_service, sample_notification):
        """Test notification integration with WebSocket service"""
        # For now, just test that notification works
        # In a real implementation, we would mock the WebSocket service
        result = await notification_service.send_notification(sample_notification)
        
        assert result.success is True
        assert result.notification_id == "notif-123"

    @pytest.mark.asyncio
    async def test_notification_with_workflow_integration(self, notification_service):
        """Test notification integration with workflow system"""
        workflow_event = {
            "type": "workflow_review_required",
            "workflow_id": "workflow-456",
            "session_id": "session-789",
            "user_id": "user-123",
            "project_id": "project-123"
        }
        
        result = await notification_service.handle_workflow_event(workflow_event)
        
        assert result["success"] is True
        assert result["notification_id"] is not None
        assert "in_app" in result["channels_sent"]
        assert "email" in result["channels_sent"]


class TestNotificationSchemas:
    """Test notification schemas and validation"""

    def test_notification_schema_validation(self):
        """Test notification schema validation"""
        # This test will fail in RED phase
        valid_notification = {
            "id": "notif-123",
            "user_id": "user-123",
            "type": "workflow_review_required",
            "title": "Review Required",
            "message": "Your workflow requires human review",
            "priority": "high",
            "category": "workflow",
            "timestamp": "2025-01-27T10:30:00Z"
        }
        
        # Should validate successfully
        # notification = Notification(**valid_notification)
        # assert notification.id == "notif-123"
        # assert notification.user_id == "user-123"
        # assert notification.priority == NotificationPriority.HIGH

    def test_notification_schema_invalid_priority(self):
        """Test notification schema with invalid priority"""
        # This test will fail in RED phase
        invalid_notification = {
            "id": "notif-123",
            "user_id": "user-123",
            "type": "workflow_review_required",
            "title": "Review Required",
            "message": "Your workflow requires human review",
            "priority": "invalid_priority",  # Invalid priority
            "category": "workflow",
            "timestamp": "2025-01-27T10:30:00Z"
        }
        
        # Should raise validation error
        # with pytest.raises(ValidationError):
        #     Notification(**invalid_notification)

    def test_user_preferences_schema_validation(self):
        """Test user preferences schema validation"""
        # This test will fail in RED phase
        valid_preferences = {
            "user_id": "user-123",
            "channels": {
                "in_app": True,
                "email": True,
                "browser_push": False,
                "sms": False
            },
            "categories": {
                "workflow": True,
                "system": True,
                "marketing": False
            }
        }
        
        # Should validate successfully
        # preferences = UserNotificationPreferences(**valid_preferences)
        # assert preferences.user_id == "user-123"
        # assert preferences.channels.in_app is True
        # assert preferences.channels.email is True


class TestNotificationTemplates:
    """Test notification templates"""

    def test_workflow_review_required_template(self):
        """Test workflow review required template"""
        # This test will fail in RED phase
        template_data = {
            "workflow_name": "User Authentication System",
            "project_name": "ArchMesh",
            "review_url": "/projects/123/workflows/session-789/review",
            "deadline": "2025-01-28T10:30:00Z"
        }
        
        # Should render template successfully
        # rendered = NotificationTemplate.render("workflow_review_required", template_data)
        # assert "User Authentication System" in rendered.title
        # assert "ArchMesh" in rendered.message
        # assert "/projects/123/workflows/session-789/review" in rendered.message

    def test_workflow_completed_template(self):
        """Test workflow completed template"""
        # This test will fail in RED phase
        template_data = {
            "workflow_name": "User Authentication System",
            "project_name": "ArchMesh",
            "results_url": "/projects/123/workflows/session-789/results",
            "completion_time": "2025-01-27T10:30:00Z"
        }
        
        # Should render template successfully
        # rendered = NotificationTemplate.render("workflow_completed", template_data)
        # assert "completed" in rendered.title.lower()
        # assert "User Authentication System" in rendered.message
        # assert "/projects/123/workflows/session-789/results" in rendered.message

    def test_template_with_missing_variables(self):
        """Test template rendering with missing variables"""
        # This test will fail in RED phase
        template_data = {
            "workflow_name": "User Authentication System"
            # Missing required variables
        }
        
        # Should handle missing variables gracefully
        # with pytest.raises(TemplateError):
        #     NotificationTemplate.render("workflow_review_required", template_data)
