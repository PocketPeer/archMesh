"""
Connection Pool for WebSocket Service

This module provides optimized connection pool management for WebSocket connections
with health monitoring, connection lifecycle management, and performance optimization.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List, Any
from dataclasses import dataclass, field
from collections import defaultdict

from app.services.websocket.websocket_service import WebSocketConnection, ConnectionState

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolMetrics:
    """Metrics for connection pool performance"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_creation_time: float = 0.0
    connection_cleanup_time: float = 0.0
    last_cleanup: datetime = field(default_factory=datetime.utcnow)


class ConnectionPool:
    """
    Optimized connection pool for WebSocket connections
    
    Provides efficient connection management with:
    - Connection pooling and reuse
    - Health monitoring and cleanup
    - Performance metrics collection
    - Automatic connection lifecycle management
    """
    
    def __init__(self, max_connections: int = 1000, cleanup_interval: int = 300):
        """
        Initialize connection pool
        
        Args:
            max_connections: Maximum number of connections to maintain
            cleanup_interval: Interval in seconds for cleanup operations
        """
        self.max_connections = max_connections
        self.cleanup_interval = cleanup_interval
        
        # Connection storage
        self.connections: Dict[str, WebSocketConnection] = {}
        self.connection_groups: Dict[str, Set[str]] = defaultdict(set)
        self.idle_connections: Set[str] = set()
        self.failed_connections: Set[str] = set()
        
        # Performance tracking
        self.metrics = ConnectionPoolMetrics()
        self.connection_times: Dict[str, datetime] = {}
        self.last_activity: Dict[str, datetime] = {}
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the connection pool with cleanup task"""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Connection pool started")
    
    async def stop(self):
        """Stop the connection pool and cleanup task"""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup all connections
        await self._cleanup_all_connections()
        logger.info("Connection pool stopped")
    
    async def get_connection(self, session_id: str, user_id: Optional[str] = None) -> WebSocketConnection:
        """
        Get or create a connection from the pool
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
            
        Returns:
            WebSocketConnection: Connection object
            
        Raises:
            ConnectionError: If connection limit exceeded
        """
        start_time = datetime.utcnow()
        
        # Check if connection already exists
        if session_id in self.connections:
            connection = self.connections[session_id]
            if connection.state == ConnectionState.CONNECTED:
                self.last_activity[session_id] = start_time
                return connection
            else:
                # Remove failed connection
                await self._remove_connection(session_id)
        
        # Check connection limit
        if len(self.connections) >= self.max_connections:
            await self._cleanup_idle_connections()
            if len(self.connections) >= self.max_connections:
                raise ConnectionError("Maximum connections reached")
        
        # Create new connection
        connection = WebSocketConnection(
            session_id=session_id,
            user_id=user_id,
            state=ConnectionState.CONNECTED
        )
        
        # Add to pool
        self.connections[session_id] = connection
        self.connection_times[session_id] = start_time
        self.last_activity[session_id] = start_time
        
        # Group by user
        if user_id:
            self.connection_groups[user_id].add(session_id)
        
        # Update metrics
        self.metrics.total_connections += 1
        self.metrics.active_connections += 1
        self.metrics.connection_creation_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.debug(f"Connection created: {session_id}")
        return connection
    
    async def return_connection(self, session_id: str):
        """
        Return connection to pool (mark as idle)
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.connections:
            connection = self.connections[session_id]
            if connection.state == ConnectionState.CONNECTED:
                self.idle_connections.add(session_id)
                self.metrics.idle_connections = len(self.idle_connections)
                logger.debug(f"Connection returned to pool: {session_id}")
    
    async def remove_connection(self, session_id: str):
        """
        Remove connection from pool
        
        Args:
            session_id: Session identifier
        """
        await self._remove_connection(session_id)
    
    async def _remove_connection(self, session_id: str):
        """Internal method to remove connection"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            
            # Remove from groups
            if connection.user_id:
                self.connection_groups[connection.user_id].discard(session_id)
                if not self.connection_groups[connection.user_id]:
                    del self.connection_groups[connection.user_id]
            
            # Remove from tracking
            self.connections.pop(session_id, None)
            self.idle_connections.discard(session_id)
            self.failed_connections.discard(session_id)
            self.connection_times.pop(session_id, None)
            self.last_activity.pop(session_id, None)
            
            # Update metrics
            self.metrics.total_connections = max(0, self.metrics.total_connections - 1)
            self.metrics.active_connections = len(self.connections)
            self.metrics.idle_connections = len(self.idle_connections)
            
            logger.debug(f"Connection removed: {session_id}")
    
    async def get_user_connections(self, user_id: str) -> List[WebSocketConnection]:
        """
        Get all connections for a specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            List[WebSocketConnection]: List of user connections
        """
        connections = []
        for session_id in self.connection_groups.get(user_id, set()):
            if session_id in self.connections:
                connection = self.connections[session_id]
                if connection.state == ConnectionState.CONNECTED:
                    connections.append(connection)
        return connections
    
    async def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.connections)
    
    async def get_idle_connection_count(self) -> int:
        """Get number of idle connections"""
        return len(self.idle_connections)
    
    async def get_metrics(self) -> ConnectionPoolMetrics:
        """Get connection pool metrics"""
        self.metrics.active_connections = len(self.connections)
        self.metrics.idle_connections = len(self.idle_connections)
        self.metrics.failed_connections = len(self.failed_connections)
        return self.metrics
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_idle_connections()
                await self._cleanup_failed_connections()
                self.metrics.last_cleanup = datetime.utcnow()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _cleanup_idle_connections(self):
        """Cleanup idle connections"""
        current_time = datetime.utcnow()
        idle_timeout = timedelta(minutes=30)  # 30 minutes idle timeout
        
        idle_to_remove = []
        for session_id in self.idle_connections:
            if session_id in self.last_activity:
                if current_time - self.last_activity[session_id] > idle_timeout:
                    idle_to_remove.append(session_id)
        
        for session_id in idle_to_remove:
            await self._remove_connection(session_id)
            logger.info(f"Cleaned up idle connection: {session_id}")
    
    async def _cleanup_failed_connections(self):
        """Cleanup failed connections"""
        failed_to_remove = []
        for session_id in self.failed_connections:
            if session_id in self.connections:
                connection = self.connections[session_id]
                if connection.state in [ConnectionState.FAILED, ConnectionState.DISCONNECTED]:
                    failed_to_remove.append(session_id)
        
        for session_id in failed_to_remove:
            await self._remove_connection(session_id)
            logger.info(f"Cleaned up failed connection: {session_id}")
    
    async def _cleanup_all_connections(self):
        """Cleanup all connections"""
        for session_id in list(self.connections.keys()):
            await self._remove_connection(session_id)
        logger.info("All connections cleaned up")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on connection pool
        
        Returns:
            Dict[str, Any]: Health check results
        """
        current_time = datetime.utcnow()
        
        # Check connection states
        healthy_connections = 0
        unhealthy_connections = 0
        
        for connection in self.connections.values():
            if connection.state == ConnectionState.CONNECTED:
                healthy_connections += 1
            else:
                unhealthy_connections += 1
        
        # Check for stale connections
        stale_connections = 0
        stale_timeout = timedelta(hours=1)  # 1 hour stale timeout
        
        for session_id, last_activity in self.last_activity.items():
            if current_time - last_activity > stale_timeout:
                stale_connections += 1
        
        health_status = {
            "status": "healthy" if unhealthy_connections == 0 and stale_connections == 0 else "degraded",
            "total_connections": len(self.connections),
            "healthy_connections": healthy_connections,
            "unhealthy_connections": unhealthy_connections,
            "idle_connections": len(self.idle_connections),
            "stale_connections": stale_connections,
            "connection_groups": len(self.connection_groups),
            "last_cleanup": self.metrics.last_cleanup.isoformat(),
            "uptime": (current_time - self.connection_times.get(min(self.connection_times.keys(), default=current_time), current_time)).total_seconds()
        }
        
        return health_status
