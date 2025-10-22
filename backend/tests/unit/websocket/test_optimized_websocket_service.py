"""
Tests for Optimized WebSocket Service

This module tests the optimized WebSocket service with connection pooling,
message processing optimization, and performance monitoring.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.services.websocket.optimized_websocket_service import OptimizedWebSocketService
from app.services.websocket.connection_pool import ConnectionPool
from app.services.websocket.message_processor import MessageProcessor, MessagePriority
from app.schemas.websocket import WebSocketConfig
from app.core.exceptions import WebSocketError, ConnectionError


@pytest.fixture
def optimized_websocket_service():
    """Create optimized WebSocket service for testing"""
    config = WebSocketConfig(
        max_connections=100,
        heartbeat_interval=30,
        connection_timeout=300,
        max_reconnect_attempts=5,
        require_authentication=False
    )
    return OptimizedWebSocketService(config)


@pytest.fixture
def sample_workflow_update():
    """Sample workflow update message"""
    return {
        "type": "workflow_update",
        "workflow_id": "workflow-123",
        "status": "in_progress",
        "stage": "architecture_design",
        "progress": 50,
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture
def sample_notification_message():
    """Sample notification message"""
    return {
        "type": "notification",
        "id": "notif-123",
        "user_id": "user-123",
        "title": "Workflow Update",
        "message": "Your workflow requires human review",
        "category": "workflow_review",
        "priority": "high",
        "action": {
            "label": "Review Now",
            "url": "/projects/123/workflows/session-123/review"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


class TestOptimizedWebSocketService:
    """Test cases for optimized WebSocket service"""
    
    @pytest.mark.asyncio
    async def test_service_startup_and_shutdown(self, optimized_websocket_service):
        """Test service startup and shutdown"""
        # Start service
        await optimized_websocket_service.start()
        assert optimized_websocket_service.running is True
        
        # Stop service
        await optimized_websocket_service.stop()
        assert optimized_websocket_service.running is False
    
    @pytest.mark.asyncio
    async def test_connection_establishment(self, optimized_websocket_service):
        """Test WebSocket connection establishment"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        user_id = "user-123"
        token = "valid-token"
        
        # Establish connection
        connection = await optimized_websocket_service.connect(session_id, user_id=user_id, token=token)
        
        # Verify connection
        assert connection is not None
        assert connection.session_id == session_id
        assert connection.user_id == user_id
        
        # Check connection count
        count = await optimized_websocket_service.get_connection_count()
        assert count == 1
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_connection_authentication(self, optimized_websocket_service):
        """Test connection authentication"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        token = "invalid-token"
        
        # Should fail with invalid token
        with pytest.raises(WebSocketError):
            await optimized_websocket_service.connect(session_id, token=token)
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_message_sending(self, optimized_websocket_service):
        """Test message sending"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        token = "valid-token"
        
        # Establish connection
        await optimized_websocket_service.connect(session_id, token=token)
        
        # Send message
        message = {
            "type": "test_message",
            "content": "Hello, WebSocket!"
        }
        
        success = await optimized_websocket_service.send_message(session_id, message)
        assert success is True
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_message_broadcasting(self, optimized_websocket_service):
        """Test message broadcasting"""
        await optimized_websocket_service.start()
        
        # Establish multiple connections
        session_ids = ["session-1", "session-2", "session-3"]
        for session_id in session_ids:
            await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Broadcast message
        message = {
            "type": "broadcast",
            "content": "Broadcast message"
        }
        
        await optimized_websocket_service.broadcast_message(message)
        
        # Verify all connections received the message
        count = await optimized_websocket_service.get_connection_count()
        assert count == 3
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_user_specific_messaging(self, optimized_websocket_service):
        """Test user-specific messaging"""
        await optimized_websocket_service.start()
        
        user_id = "user-123"
        session_ids = ["session-1", "session-2"]
        
        # Establish connections for same user
        for session_id in session_ids:
            await optimized_websocket_service.connect(session_id, user_id=user_id, token="valid-token")
        
        # Send message to user
        message = {
            "type": "user_message",
            "content": "User-specific message"
        }
        
        await optimized_websocket_service.send_to_user(user_id, message)
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_workflow_update_broadcasting(self, optimized_websocket_service, sample_workflow_update):
        """Test workflow update broadcasting"""
        await optimized_websocket_service.start()
        
        # Establish connection
        session_id = "test-session-123"
        await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Broadcast workflow update
        await optimized_websocket_service.broadcast_workflow_update(sample_workflow_update)
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_notification_broadcasting(self, optimized_websocket_service, sample_notification_message):
        """Test notification broadcasting"""
        await optimized_websocket_service.start()
        
        # Establish connection
        session_id = "test-session-123"
        user_id = "user-123"
        await optimized_websocket_service.connect(session_id, user_id=user_id, token="valid-token")
        
        # Broadcast notification
        await optimized_websocket_service.broadcast_notification(sample_notification_message)
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_connection_disconnection(self, optimized_websocket_service):
        """Test connection disconnection"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Verify connection exists
        count = await optimized_websocket_service.get_connection_count()
        assert count == 1
        
        # Disconnect
        await optimized_websocket_service.disconnect(session_id)
        
        # Verify connection removed
        count = await optimized_websocket_service.get_connection_count()
        assert count == 0
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_heartbeat_functionality(self, optimized_websocket_service):
        """Test heartbeat functionality"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Send heartbeat
        await optimized_websocket_service.send_heartbeat(session_id)
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, optimized_websocket_service):
        """Test metrics collection"""
        await optimized_websocket_service.start()
        
        # Establish connection
        session_id = "test-session-123"
        await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Get metrics
        metrics = await optimized_websocket_service.get_metrics()
        
        assert metrics.total_connections >= 1
        assert metrics.active_connections >= 1
        assert metrics.uptime_seconds >= 0
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_health_check(self, optimized_websocket_service):
        """Test health check functionality"""
        await optimized_websocket_service.start()
        
        # Perform health check
        health = await optimized_websocket_service.health_check()
        
        assert "status" in health
        assert "service" in health
        assert "connection_pool" in health
        assert "message_processor" in health
        assert health["status"] in ["healthy", "degraded"]
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_message_priority_handling(self, optimized_websocket_service):
        """Test message priority handling"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Send messages with different priorities
        normal_message = {"type": "normal", "content": "Normal priority"}
        high_message = {"type": "high", "content": "High priority"}
        critical_message = {"type": "critical", "content": "Critical priority"}
        
        await optimized_websocket_service.send_message(session_id, normal_message, MessagePriority.NORMAL)
        await optimized_websocket_service.send_message(session_id, high_message, MessagePriority.HIGH)
        await optimized_websocket_service.send_message(session_id, critical_message, MessagePriority.CRITICAL)
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_batch_message_processing(self, optimized_websocket_service):
        """Test batch message processing"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Send batch of messages
        messages = [
            {"type": "batch_1", "content": "Message 1"},
            {"type": "batch_2", "content": "Message 2"},
            {"type": "batch_3", "content": "Message 3"}
        ]
        
        await optimized_websocket_service.send_batch_messages(session_id, messages)
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_connection_simulation_methods(self, optimized_websocket_service):
        """Test connection simulation methods for testing"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Test simulation methods
        await optimized_websocket_service.simulate_connection_drop(session_id)
        await optimized_websocket_service.simulate_timeout(session_id)
        await optimized_websocket_service.simulate_error(session_id, "Test error")
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_workflow_subscription(self, optimized_websocket_service):
        """Test workflow subscription"""
        await optimized_websocket_service.start()
        
        session_id = "test-session-123"
        workflow_id = "workflow-456"
        
        await optimized_websocket_service.subscribe_to_workflow(session_id, workflow_id)
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, optimized_websocket_service):
        """Test performance under load"""
        await optimized_websocket_service.start()
        
        # Create multiple connections
        session_ids = [f"session-{i}" for i in range(10)]
        for session_id in session_ids:
            await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Send messages concurrently
        tasks = []
        for session_id in session_ids:
            message = {"type": "load_test", "content": f"Message for {session_id}"}
            task = optimized_websocket_service.send_message(session_id, message)
            tasks.append(task)
        
        # Wait for all messages to be processed
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all connections are still active
        count = await optimized_websocket_service.get_connection_count()
        assert count == 10
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, optimized_websocket_service):
        """Test error handling"""
        await optimized_websocket_service.start()
        
        # Test sending message to non-existent connection
        with pytest.raises(WebSocketError):
            await optimized_websocket_service.send_message("non-existent", {"type": "test"})
        
        await optimized_websocket_service.stop()
    
    @pytest.mark.asyncio
    async def test_service_metrics_accuracy(self, optimized_websocket_service):
        """Test service metrics accuracy"""
        await optimized_websocket_service.start()
        
        # Initial metrics
        initial_metrics = await optimized_websocket_service.get_metrics()
        initial_connections = initial_metrics.total_connections
        
        # Add connections
        session_ids = ["session-1", "session-2", "session-3"]
        for session_id in session_ids:
            await optimized_websocket_service.connect(session_id, token="valid-token")
        
        # Check updated metrics
        updated_metrics = await optimized_websocket_service.get_metrics()
        assert updated_metrics.total_connections == initial_connections + 3
        assert updated_metrics.active_connections == 3
        
        await optimized_websocket_service.stop()

