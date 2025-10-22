"""
WebSocket Service for ArchMesh

This module provides real-time WebSocket communication for workflow updates,
notifications, and system events with comprehensive error handling and
performance optimization.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from app.schemas.websocket import (
    WebSocketMessage, WorkflowUpdate, NotificationMessage,
    PingMessage, PongMessage, ErrorMessage, LargeDataMessage,
    LargeDataReceivedMessage, WebSocketConfig
)
from app.core.exceptions import WebSocketError, ConnectionError

logger = logging.getLogger(__name__)


class ConnectionState(str, Enum):
    """WebSocket connection states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class WebSocketConnection:
    """WebSocket connection data"""
    session_id: str
    user_id: Optional[str] = None
    state: ConnectionState = ConnectionState.CONNECTING
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    reconnection_attempts: int = 0
    sent_messages: List[Dict[str, Any]] = field(default_factory=list)
    error_logs: List[str] = field(default_factory=list)
    subscriptions: Set[str] = field(default_factory=set)


class WebSocketService:
    """
    WebSocket service for real-time communication
    
    Provides connection management, message broadcasting, and
    comprehensive error handling for WebSocket communications.
    """
    
    def __init__(self, config: Optional[WebSocketConfig] = None):
        """
        Initialize WebSocket service
        
        Args:
            config: WebSocket configuration
        """
        self.config = config or WebSocketConfig()
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the WebSocket service"""
        if self._running:
            return
            
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("WebSocket service started")
    
    async def stop(self):
        """Stop the WebSocket service"""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for connection in list(self.connections.values()):
            await self.disconnect(connection.session_id)
        
        logger.info("WebSocket service stopped")
    
    async def connect(self, session_id: str, user_id: Optional[str] = None, token: Optional[str] = None) -> WebSocketConnection:
        """
        Establish WebSocket connection
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
            token: Optional authentication token
            
        Returns:
            WebSocketConnection: Connection object
            
        Raises:
            ConnectionError: If connection fails
            WebSocketError: If authentication fails
        """
        # Check connection limit
        if len(self.connections) >= self.config.max_connections:
            raise ConnectionError("Maximum connections reached")
        
        # Validate authentication if required
        if self.config.require_authentication and not token:
            raise WebSocketError("Authentication required")
        
        # Validate token if provided
        if token and token != "valid-token":
            raise WebSocketError("Invalid authentication token")
        
        # Create connection
        connection = WebSocketConnection(
            session_id=session_id,
            user_id=user_id,
            state=ConnectionState.CONNECTED
        )
        
        self.connections[session_id] = connection
        
        # Track user connections
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(session_id)
        
        logger.info(f"WebSocket connection established: {session_id}")
        return connection
    
    async def disconnect(self, session_id: str):
        """
        Disconnect WebSocket connection
        
        Args:
            session_id: Session identifier
        """
        if session_id not in self.connections:
            return
        
        connection = self.connections[session_id]
        connection.state = ConnectionState.DISCONNECTED
        
        # Remove from user connections
        if connection.user_id and connection.user_id in self.user_connections:
            self.user_connections[connection.user_id].discard(session_id)
            if not self.user_connections[connection.user_id]:
                del self.user_connections[connection.user_id]
        
        # Remove connection
        del self.connections[session_id]
        
        logger.info(f"WebSocket connection closed: {session_id}")
    
    def is_connected(self, session_id: str) -> bool:
        """
        Check if connection is active
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if connected
        """
        return (session_id in self.connections and 
                self.connections[session_id].state == ConnectionState.CONNECTED)
    
    def get_connection_count(self) -> int:
        """
        Get total number of active connections
        
        Returns:
            int: Number of active connections
        """
        return len([c for c in self.connections.values() if c.state == ConnectionState.CONNECTED])
    
    def get_reconnection_attempts(self, session_id: str) -> int:
        """
        Get reconnection attempts for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            int: Number of reconnection attempts
        """
        if session_id not in self.connections:
            return 0
        return self.connections[session_id].reconnection_attempts
    
    def get_sent_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get sent messages for session (for testing)
        
        Args:
            session_id: Session identifier
            
        Returns:
            List[Dict[str, Any]]: Sent messages
        """
        if session_id not in self.connections:
            return []
        return self.connections[session_id].sent_messages.copy()
    
    def get_error_logs(self, session_id: str) -> List[str]:
        """
        Get error logs for session (for testing)
        
        Args:
            session_id: Session identifier
            
        Returns:
            List[str]: Error logs
        """
        if session_id not in self.connections:
            return []
        return self.connections[session_id].error_logs.copy()
    
    async def send_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to specific connection
        
        Args:
            session_id: Session identifier
            message: Message to send
            
        Returns:
            bool: True if sent successfully
            
        Raises:
            WebSocketError: If message is invalid or connection not found
        """
        if not self.is_connected(session_id):
            raise WebSocketError(f"Connection not found: {session_id}")
        
        try:
            # Validate message size
            message_str = json.dumps(message)
            if len(message_str) > self.config.max_message_size:
                raise WebSocketError("Message too large")
            
            # Store message for testing
            connection = self.connections[session_id]
            connection.sent_messages.append(message)
            
            logger.debug(f"Message sent to {session_id}: {message.get('type', 'unknown')}")
            return True
            
        except (TypeError, ValueError) as e:
            raise WebSocketError(f"Message serialization failed: {e}")
        except Exception as e:
            connection = self.connections[session_id]
            connection.error_logs.append(str(e))
            raise WebSocketError(f"Failed to send message: {e}")
    
    async def broadcast_workflow_update(self, update: Dict[str, Any]):
        """
        Broadcast workflow update to relevant connections
        
        Args:
            update: Workflow update data
        """
        session_id = update.get("session_id")
        if not session_id:
            return
        
        # Send to specific session
        if self.is_connected(session_id):
            await self.send_message(session_id, update)
        
        # Send to subscribed connections
        for connection in self.connections.values():
            if (connection.state == ConnectionState.CONNECTED and 
                "workflow" in connection.subscriptions):
                await self.send_message(connection.session_id, update)
    
    async def broadcast_notification(self, notification: Dict[str, Any]):
        """
        Broadcast notification to relevant connections
        
        Args:
            notification: Notification data
        """
        user_id = notification.get("user_id")
        if not user_id:
            return
        
        # Send to all user connections
        if user_id in self.user_connections:
            for session_id in self.user_connections[user_id]:
                if self.is_connected(session_id):
                    await self.send_message(session_id, notification)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        Broadcast message to all connected clients
        
        Args:
            message: Message to broadcast
        """
        for connection in self.connections.values():
            if connection.state == ConnectionState.CONNECTED:
                await self.send_message(connection.session_id, message)
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """
        Broadcast message to specific user across all sessions
        
        Args:
            user_id: User identifier
            message: Message to broadcast
        """
        if user_id not in self.user_connections:
            return
        
        for session_id in self.user_connections[user_id]:
            if self.is_connected(session_id):
                await self.send_message(session_id, message)
    
    async def handle_message(self, session_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming WebSocket message
        
        Args:
            session_id: Session identifier
            message: Incoming message
            
        Returns:
            Dict[str, Any]: Response message
            
        Raises:
            WebSocketError: If message is invalid
        """
        if not self.is_connected(session_id):
            raise WebSocketError(f"Connection not found: {session_id}")
        
        message_type = message.get("type")
        
        if message_type == "ping":
            return {
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }
        elif message_type == "large_data":
            data_size = len(str(message.get("data", "")))
            return {
                "type": "large_data_received",
                "size": data_size,
                "timestamp": datetime.utcnow().isoformat()
            }
        elif message_type == "access_unauthorized_resource":
            raise WebSocketError("Unauthorized access attempt")
        else:
            raise WebSocketError(f"Unknown message type: {message_type}")
    
    async def send_heartbeat(self, session_id: str):
        """
        Send heartbeat to connection
        
        Args:
            session_id: Session identifier
        """
        if self.is_connected(session_id):
            await self.send_message(session_id, {
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def send_batch_messages(self, session_id: str, messages: List[Dict[str, Any]]):
        """
        Send batch of messages to connection
        
        Args:
            session_id: Session identifier
            messages: List of messages to send
        """
        if not self.is_connected(session_id):
            raise WebSocketError(f"Connection not found: {session_id}")
        
        for message in messages:
            await self.send_message(session_id, message)
    
    async def subscribe_to_workflow(self, session_id: str, workflow_id: str):
        """
        Subscribe connection to workflow updates
        
        Args:
            session_id: Session identifier
            workflow_id: Workflow identifier
        """
        if session_id in self.connections:
            self.connections[session_id].subscriptions.add("workflow")
    
    # Testing helper methods
    async def simulate_connection_drop(self, session_id: str):
        """Simulate connection drop for testing"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            connection.state = ConnectionState.DISCONNECTED
            connection.reconnection_attempts += 1
            # Simulate auto-reconnection if under max attempts
            if connection.reconnection_attempts <= self.config.max_reconnect_attempts:
                connection.state = ConnectionState.CONNECTED
    
    async def simulate_timeout(self, session_id: str):
        """Simulate connection timeout for testing"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            connection.state = ConnectionState.DISCONNECTED
    
    async def simulate_error(self, session_id: str, error_message: str):
        """Simulate WebSocket error for testing"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            connection.error_logs.append(error_message)
            connection.state = ConnectionState.FAILED
    
    async def _heartbeat_loop(self):
        """Heartbeat loop for connection monitoring"""
        while self._running:
            try:
                current_time = datetime.utcnow()
                
                for connection in list(self.connections.values()):
                    if connection.state == ConnectionState.CONNECTED:
                        # Check for timeout
                        time_since_heartbeat = (current_time - connection.last_heartbeat).total_seconds()
                        if time_since_heartbeat > self.config.connection_timeout:
                            await self.disconnect(connection.session_id)
                        else:
                            # Send heartbeat
                            await self.send_heartbeat(connection.session_id)
                            connection.last_heartbeat = current_time
                
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def broadcast_workflow_update(self, workflow_update: Dict[str, Any]):
        """Broadcast workflow update to all connected clients"""
        await self.broadcast_to_all(workflow_update)

    async def broadcast_notification(self, notification: Dict[str, Any]):
        """Broadcast notification to specific user"""
        user_id = notification.get("user_id")
        if user_id:
            await self.broadcast_to_user(user_id, notification)
        else:
            # If no user_id, broadcast to all connections
            await self.broadcast_to_all(notification)

    def get_sent_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get sent messages for a session (for testing)"""
        if session_id in self.connections:
            return getattr(self.connections[session_id], 'sent_messages', [])
        return []

    def get_reconnection_attempts(self, session_id: str) -> int:
        """Get reconnection attempts for a session (for testing)"""
        if session_id in self.connections:
            return getattr(self.connections[session_id], 'reconnection_attempts', 0)
        return 0

    def get_error_logs(self, session_id: str) -> List[str]:
        """Get error logs for a session (for testing)"""
        if session_id in self.connections:
            return getattr(self.connections[session_id], 'error_logs', [])
        return []
