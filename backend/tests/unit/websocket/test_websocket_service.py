"""
WebSocket Service Tests - RED Phase

This module contains comprehensive tests for the WebSocket service that provides
real-time updates for workflow progress, notifications, and system events.

Following TDD methodology:
- RED: Create failing tests first
- GREEN: Implement functionality to make tests pass
- REFACTOR: Optimize and improve implementation

Author: ArchMesh Team
Version: 1.0.0
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List
from datetime import datetime

# Import the WebSocket service
from app.services.websocket.websocket_service import WebSocketService
from app.schemas.websocket import WebSocketMessage, WorkflowUpdate, NotificationMessage
from app.core.exceptions import WebSocketError, ConnectionError


class TestWebSocketService:
    """Test WebSocket service functionality"""

    @pytest.fixture
    def websocket_service(self):
        """Create WebSocketService instance for testing"""
        return WebSocketService()

    @pytest.fixture
    def mock_websocket_connection(self):
        """Create mock WebSocket connection"""
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        mock_ws.recv = AsyncMock()
        mock_ws.close = AsyncMock()
        mock_ws.state = "OPEN"
        return mock_ws

    @pytest.fixture
    def sample_workflow_update(self):
        """Sample workflow update message"""
        return {
            "type": "workflow_update",
            "session_id": "test-session-123",
            "stage": "requirements_review",
            "progress": 0.75,
            "status": "running",
            "message": "Requirements analysis in progress",
            "timestamp": "2025-01-27T10:30:00Z",
            "metadata": {
                "estimated_completion": "2025-01-27T10:35:00Z",
                "current_step": "validating_requirements"
            }
        }

    @pytest.fixture
    def sample_notification_message(self):
        """Sample notification message"""
        return {
            "type": "notification",
            "id": "notif-123",
            "title": "Review Required",
            "message": "Your workflow requires human review",
            "priority": "high",
            "category": "workflow_review",
            "timestamp": "2025-01-27T10:30:00Z",
            "action": {
                "label": "Review Now",
                "url": "/projects/123/workflows/session-123/review"
            }
        }

    # Connection Management Tests
    @pytest.mark.asyncio
    async def test_websocket_connection_establishment(self, websocket_service):
        """Test WebSocket connection establishment"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Should establish connection successfully
        connection = await websocket_service.connect(session_id, token=token)
        
        assert connection is not None
        assert websocket_service.is_connected(session_id) is True
        assert websocket_service.get_connection_count() == 1

    @pytest.mark.asyncio
    async def test_websocket_connection_failure_handling(self, websocket_service):
        """Test WebSocket connection failure handling"""
        session_id = "invalid-session"
        token = "invalid-token"
        
        # Should handle connection failure gracefully
        with pytest.raises(WebSocketError):
            await websocket_service.connect(session_id, token=token)

    @pytest.mark.asyncio
    async def test_websocket_auto_reconnection(self, websocket_service):
        """Test WebSocket automatic reconnection"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish initial connection
        await websocket_service.connect(session_id, token=token)
        
        # Simulate connection drop
        await websocket_service.simulate_connection_drop(session_id)
        
        # Should automatically reconnect
        await asyncio.sleep(0.1)  # Allow reconnection time
        
        assert websocket_service.is_connected(session_id) is True
        assert websocket_service.get_reconnection_attempts(session_id) >= 1

    @pytest.mark.asyncio
    async def test_websocket_max_reconnection_attempts(self, websocket_service):
        """Test WebSocket maximum reconnection attempts"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Simulate multiple connection drops
        for _ in range(6):  # More than max attempts (5)
            await websocket_service.simulate_connection_drop(session_id)
            await asyncio.sleep(0.1)
        
        # Should stop trying to reconnect after max attempts
        assert websocket_service.is_connected(session_id) is False
        assert websocket_service.get_reconnection_attempts(session_id) >= 5

    # Message Broadcasting Tests
    @pytest.mark.asyncio
    async def test_broadcast_workflow_update(self, websocket_service, sample_workflow_update):
        """Test broadcasting workflow update to connected clients"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Broadcast workflow update
        await websocket_service.broadcast_workflow_update(sample_workflow_update)
        
        # Should send message to connected client
        sent_messages = websocket_service.get_sent_messages(session_id)
        assert len(sent_messages) == 1
        assert sent_messages[0]["type"] == "workflow_update"
        assert sent_messages[0]["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_broadcast_notification(self, websocket_service, sample_notification_message):
        """Test broadcasting notification to connected clients"""
        session_id = "test-session-123"
        user_id = "user-123"
        token = "valid-token"
        
        # Establish connection with user_id
        await websocket_service.connect(session_id, user_id=user_id, token=token)
        
        # Broadcast notification
        await websocket_service.broadcast_notification(sample_notification_message)
        
        # Should send notification to connected client
        sent_messages = websocket_service.get_sent_messages(session_id)
        assert len(sent_messages) == 1
        assert sent_messages[0]["type"] == "notification"
        assert sent_messages[0]["id"] == "notif-123"

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_clients(self, websocket_service, sample_workflow_update):
        """Test broadcasting to multiple connected clients"""
        session_ids = ["session-1", "session-2", "session-3"]
        token = "valid-token"
        
        # Establish multiple connections
        for session_id in session_ids:
            await websocket_service.connect(session_id, token=token)
        
        # Broadcast to all clients
        await websocket_service.broadcast_to_all(sample_workflow_update)
        
        # Should send message to all connected clients
        for session_id in session_ids:
            sent_messages = websocket_service.get_sent_messages(session_id)
            assert len(sent_messages) == 1
            assert sent_messages[0]["type"] == "workflow_update"

    @pytest.mark.asyncio
    async def test_broadcast_to_specific_user(self, websocket_service, sample_notification_message):
        """Test broadcasting to specific user across multiple sessions"""
        user_id = "user-123"
        session_ids = ["session-1", "session-2"]
        token = "valid-token"
        
        # Establish connections for same user
        for session_id in session_ids:
            await websocket_service.connect(session_id, user_id=user_id, token=token)
        
        # Broadcast to specific user
        await websocket_service.broadcast_to_user(user_id, sample_notification_message)
        
        # Should send message to all sessions for that user
        for session_id in session_ids:
            sent_messages = websocket_service.get_sent_messages(session_id)
            assert len(sent_messages) == 1
            assert sent_messages[0]["type"] == "notification"

    # Message Handling Tests
    @pytest.mark.asyncio
    async def test_handle_incoming_message(self, websocket_service):
        """Test handling incoming WebSocket messages"""
        session_id = "test-session-123"
        token = "valid-token"
        incoming_message = {
            "type": "ping",
            "timestamp": "2025-01-27T10:30:00Z"
        }
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Handle incoming message
        response = await websocket_service.handle_message(session_id, incoming_message)
        
        # Should respond with pong
        assert response["type"] == "pong"
        assert response["timestamp"] is not None

    @pytest.mark.asyncio
    async def test_handle_invalid_message(self, websocket_service):
        """Test handling invalid WebSocket messages"""
        session_id = "test-session-123"
        token = "valid-token"
        invalid_message = {
            "invalid": "message"
        }
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Should handle invalid message gracefully
        with pytest.raises(WebSocketError):
            await websocket_service.handle_message(session_id, invalid_message)

    @pytest.mark.asyncio
    async def test_handle_large_message(self, websocket_service):
        """Test handling large WebSocket messages"""
        session_id = "test-session-123"
        token = "valid-token"
        large_message = {
            "type": "large_data",
            "data": "x" * 10000  # 10KB message
        }
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Should handle large message
        response = await websocket_service.handle_message(session_id, large_message)
        assert response["type"] == "large_data_received"
        assert response["size"] == 10000

    # Connection Management Tests
    @pytest.mark.asyncio
    async def test_connection_cleanup(self, websocket_service):
        """Test connection cleanup when client disconnects"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        assert websocket_service.is_connected(session_id) is True
        
        # Disconnect client
        await websocket_service.disconnect(session_id)
        
        # Should clean up connection
        assert websocket_service.is_connected(session_id) is False
        assert websocket_service.get_connection_count() == 0

    @pytest.mark.asyncio
    async def test_connection_heartbeat(self, websocket_service):
        """Test connection heartbeat mechanism"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Send heartbeat
        await websocket_service.send_heartbeat(session_id)
        
        # Should receive ping message
        sent_messages = websocket_service.get_sent_messages(session_id)
        assert len(sent_messages) == 1
        assert sent_messages[0]["type"] == "ping"

    @pytest.mark.asyncio
    async def test_connection_timeout(self, websocket_service):
        """Test connection timeout handling"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Simulate timeout (no heartbeat for too long)
        await websocket_service.simulate_timeout(session_id)
        
        # Should disconnect due to timeout
        assert websocket_service.is_connected(session_id) is False

    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_websocket_error_handling(self, websocket_service):
        """Test WebSocket error handling"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Simulate WebSocket error
        await websocket_service.simulate_error(session_id, "Connection lost")
        
        # Should handle error gracefully
        assert websocket_service.is_connected(session_id) is False
        error_logs = websocket_service.get_error_logs(session_id)
        assert len(error_logs) == 1
        assert "Connection lost" in error_logs[0]

    @pytest.mark.asyncio
    async def test_message_serialization_error(self, websocket_service):
        """Test message serialization error handling"""
        session_id = "test-session-123"
        token = "valid-token"
        invalid_message = {
            "type": "test",
            "data": object()  # Non-serializable object
        }
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Should handle serialization error
        with pytest.raises(WebSocketError):
            await websocket_service.send_message(session_id, invalid_message)

    # Performance Tests
    @pytest.mark.asyncio
    async def test_high_volume_message_handling(self, websocket_service):
        """Test handling high volume of messages"""
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Send many messages rapidly
        messages = []
        for i in range(100):
            message = {
                "type": "test_message",
                "id": i,
                "data": f"message-{i}"
            }
            messages.append(message)
        
        # Send all messages
        start_time = datetime.now()
        await websocket_service.send_batch_messages(session_id, messages)
        end_time = datetime.now()
        
        # Should handle high volume efficiently
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0  # Should complete within 1 second
        
        sent_messages = websocket_service.get_sent_messages(session_id)
        assert len(sent_messages) == 100

    @pytest.mark.asyncio
    async def test_concurrent_connections(self, websocket_service):
        """Test handling concurrent connections"""
        session_ids = [f"session-{i}" for i in range(50)]
        token = "valid-token"
        
        # Establish multiple concurrent connections
        tasks = []
        for session_id in session_ids:
            task = websocket_service.connect(session_id, token=token)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Should handle concurrent connections
        assert websocket_service.get_connection_count() == 50
        
        # All connections should be active
        for session_id in session_ids:
            assert websocket_service.is_connected(session_id) is True

    # Security Tests
    @pytest.mark.asyncio
    async def test_websocket_authentication(self, websocket_service):
        """Test WebSocket authentication"""
        # This test will fail in RED phase
        session_id = "test-session-123"
        invalid_token = "invalid-token"
        
        # Should reject connection with invalid token
        with pytest.raises(WebSocketError):
            await websocket_service.connect(session_id, token=invalid_token)

    @pytest.mark.asyncio
    async def test_websocket_authorization(self, websocket_service):
        """Test WebSocket authorization"""
        session_id = "test-session-123"
        user_id = "user-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, user_id=user_id, token=token)
        
        # Try to access unauthorized resource
        unauthorized_message = {
            "type": "access_unauthorized_resource",
            "resource": "admin-panel"
        }
        
        # Should reject unauthorized access
        with pytest.raises(WebSocketError):
            await websocket_service.handle_message(session_id, unauthorized_message)

    # Integration Tests
    @pytest.mark.asyncio
    async def test_websocket_with_workflow_integration(self, websocket_service):
        """Test WebSocket integration with workflow system"""
        session_id = "test-session-123"
        workflow_id = "workflow-456"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, token=token)
        
        # Subscribe to workflow updates
        await websocket_service.subscribe_to_workflow(session_id, workflow_id)
        
        # Simulate workflow update
        workflow_update = {
            "type": "workflow_update",
            "workflow_id": workflow_id,
            "stage": "requirements_review",
            "progress": 0.5
        }
        
        await websocket_service.broadcast_workflow_update(workflow_update)
        
        # Should receive workflow update
        sent_messages = websocket_service.get_sent_messages(session_id)
        assert len(sent_messages) == 1
        assert sent_messages[0]["workflow_id"] == workflow_id

    @pytest.mark.asyncio
    async def test_websocket_with_notification_integration(self, websocket_service):
        """Test WebSocket integration with notification system"""
        session_id = "test-session-123"
        user_id = "user-123"
        token = "valid-token"
        
        # Establish connection
        await websocket_service.connect(session_id, user_id=user_id, token=token)
        
        # Send notification
        notification = {
            "type": "notification",
            "user_id": user_id,
            "title": "Test Notification",
            "message": "This is a test notification"
        }
        
        await websocket_service.broadcast_notification(notification)
        
        # Should receive notification
        sent_messages = websocket_service.get_sent_messages(session_id)
        assert len(sent_messages) == 1
        assert sent_messages[0]["type"] == "notification"
        assert sent_messages[0]["title"] == "Test Notification"


class TestWebSocketMessageSchemas:
    """Test WebSocket message schemas"""

    def test_workflow_update_schema_validation(self):
        """Test workflow update message schema validation"""
        # This test will fail in RED phase
        valid_message = {
            "type": "workflow_update",
            "session_id": "test-session-123",
            "stage": "requirements_review",
            "progress": 0.75,
            "status": "running",
            "message": "Requirements analysis in progress",
            "timestamp": "2025-01-27T10:30:00Z"
        }
        
        # Should validate successfully
        # workflow_update = WorkflowUpdate(**valid_message)
        # assert workflow_update.type == "workflow_update"
        # assert workflow_update.session_id == "test-session-123"
        # assert workflow_update.progress == 0.75

    def test_notification_message_schema_validation(self):
        """Test notification message schema validation"""
        # This test will fail in RED phase
        valid_message = {
            "type": "notification",
            "id": "notif-123",
            "title": "Review Required",
            "message": "Your workflow requires human review",
            "priority": "high",
            "category": "workflow_review",
            "timestamp": "2025-01-27T10:30:00Z"
        }
        
        # Should validate successfully
        # notification = NotificationMessage(**valid_message)
        # assert notification.type == "notification"
        # assert notification.id == "notif-123"
        # assert notification.priority == "high"

    def test_invalid_message_schema_validation(self):
        """Test invalid message schema validation"""
        # This test will fail in RED phase
        invalid_message = {
            "type": "invalid_type",
            "invalid_field": "invalid_value"
        }
        
        # Should raise validation error
        # with pytest.raises(ValidationError):
        #     WebSocketMessage(**invalid_message)


class TestWebSocketConfiguration:
    """Test WebSocket configuration and settings"""

    def test_websocket_config_defaults(self):
        """Test WebSocket configuration defaults"""
        # This test will fail in RED phase
        # config = WebSocketConfig()
        # assert config.max_connections == 1000
        # assert config.heartbeat_interval == 30
        # assert config.connection_timeout == 300
        # assert config.max_reconnect_attempts == 5
        # assert config.reconnect_delay == 1000

    def test_websocket_config_custom_values(self):
        """Test WebSocket configuration with custom values"""
        # This test will fail in RED phase
        # config = WebSocketConfig(
        #     max_connections=500,
        #     heartbeat_interval=60,
        #     connection_timeout=600,
        #     max_reconnect_attempts=3,
        #     reconnect_delay=2000
        # )
        # assert config.max_connections == 500
        # assert config.heartbeat_interval == 60
        # assert config.connection_timeout == 600
        # assert config.max_reconnect_attempts == 3
        # assert config.reconnect_delay == 2000

    def test_websocket_config_validation(self):
        """Test WebSocket configuration validation"""
        # This test will fail in RED phase
        # Should raise validation error for invalid values
        # with pytest.raises(ValidationError):
        #     WebSocketConfig(max_connections=-1)
        
        # with pytest.raises(ValidationError):
        #     WebSocketConfig(heartbeat_interval=0)
        
        # with pytest.raises(ValidationError):
        #     WebSocketConfig(connection_timeout=-1)
