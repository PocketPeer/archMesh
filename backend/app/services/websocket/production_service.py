"""
Production WebSocket Service

This module provides the production-ready WebSocket service that integrates
all scalability components for high-volume production deployment.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field

from app.schemas.websocket import WebSocketConfig
from app.core.exceptions import WebSocketError, ConnectionError
from .optimized_websocket_service import OptimizedWebSocketService
from .async_processor import AsyncMessageProcessor, ProcessingPriority
from .cache_manager import CacheManager, CacheType
from .load_balancer import LoadBalancer, LoadBalanceStrategy
from .error_handler import WebSocketErrorHandler
from .logger import WebSocketLogger

logger = logging.getLogger(__name__)


@dataclass
class ProductionMetrics:
    """Production service metrics"""
    total_connections: int = 0
    active_connections: int = 0
    messages_processed: int = 0
    messages_per_second: float = 0.0
    average_response_time: float = 0.0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0
    worker_utilization: float = 0.0
    server_health_score: float = 1.0
    uptime_seconds: float = 0.0
    last_activity: datetime = field(default_factory=datetime.utcnow)


class ProductionWebSocketService:
    """
    Production-ready WebSocket service with full scalability integration
    
    Integrates:
    - Optimized WebSocket service
    - Async message processor
    - Cache manager
    - Load balancer
    - Error handler
    - Enhanced logger
    """
    
    def __init__(
        self,
        websocket_config: Optional[WebSocketConfig] = None,
        redis_client=None,
        enable_auto_scaling: bool = True,
        enable_caching: bool = True,
        enable_load_balancing: bool = True,
        enable_monitoring: bool = True
    ):
        """
        Initialize production WebSocket service
        
        Args:
            websocket_config: WebSocket configuration
            redis_client: Redis client for caching
            enable_auto_scaling: Enable automatic scaling
            enable_caching: Enable caching
            enable_load_balancing: Enable load balancing
            enable_monitoring: Enable monitoring
        """
        self.config = websocket_config or WebSocketConfig()
        self.redis_client = redis_client
        self.enable_auto_scaling = enable_auto_scaling
        self.enable_caching = enable_caching
        self.enable_load_balancing = enable_load_balancing
        self.enable_monitoring = enable_monitoring
        
        # Initialize components
        self.websocket_service = OptimizedWebSocketService(self.config)
        self.async_processor = AsyncMessageProcessor(
            max_workers=20,
            auto_scale=enable_auto_scaling
        )
        self.cache_manager = CacheManager(
            redis_client=redis_client,
            enable_compression=True
        ) if enable_caching else None
        self.load_balancer = LoadBalancer(
            strategy=LoadBalanceStrategy.LEAST_CONNECTIONS
        ) if enable_load_balancing else None
        self.error_handler = WebSocketErrorHandler()
        self.logger = WebSocketLogger("production_websocket")
        
        # Production state
        self.running = False
        self.start_time = datetime.utcnow()
        self.metrics = ProductionMetrics()
        
        # Message handlers
        self.message_handlers: Dict[str, callable] = {}
        
        # Health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.performance_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
    
    async def start(self):
        """Start the production WebSocket service"""
        if self.running:
            return
        
        self.running = True
        self.start_time = datetime.utcnow()
        
        # Start all components
        await self.websocket_service.start()
        await self.async_processor.start()
        
        if self.cache_manager:
            await self.cache_manager.start()
        
        if self.load_balancer:
            await self.load_balancer.start()
        
        # Register message handlers
        self._register_message_handlers()
        
        # Start monitoring tasks
        if self.enable_monitoring:
            self.health_check_task = asyncio.create_task(self._health_monitoring_loop())
            self.metrics_task = asyncio.create_task(self._metrics_collection_loop())
        
        self.logger.log_connection_event("service_started", "production", "system")
        logger.info("Production WebSocket service started")
    
    async def stop(self):
        """Stop the production WebSocket service"""
        self.running = False
        
        # Stop monitoring tasks
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.metrics_task:
            self.metrics_task.cancel()
            try:
                await self.metrics_task
            except asyncio.CancelledError:
                pass
        
        # Stop all components
        await self.websocket_service.stop()
        await self.async_processor.stop()
        
        if self.cache_manager:
            await self.cache_manager.stop()
        
        if self.load_balancer:
            await self.load_balancer.stop()
        
        self.logger.log_connection_event("service_stopped", "production", "system")
        logger.info("Production WebSocket service stopped")
    
    def _register_message_handlers(self):
        """Register message handlers for async processing"""
        # Workflow update handler
        async def workflow_update_handler(message, session_id, user_id):
            await self._handle_workflow_update(message, session_id, user_id)
        
        # Notification handler
        async def notification_handler(message, session_id, user_id):
            await self._handle_notification(message, session_id, user_id)
        
        # Chat message handler
        async def chat_handler(message, session_id, user_id):
            await self._handle_chat_message(message, session_id, user_id)
        
        # Register handlers
        self.async_processor.register_handler("workflow_update", workflow_update_handler)
        self.async_processor.register_handler("notification", notification_handler)
        self.async_processor.register_handler("chat", chat_handler)
    
    async def connect(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        token: Optional[str] = None
    ):
        """
        Establish WebSocket connection with production optimizations
        
        Args:
            session_id: Session identifier
            user_id: Optional user identifier
            token: Optional authentication token
        """
        try:
            # Select server if load balancing is enabled
            server_info = None
            if self.load_balancer:
                server_info = await self.load_balancer.select_server(
                    session_id=session_id,
                    user_id=user_id
                )
                if not server_info:
                    raise ConnectionError("No available servers")
            
            # Connect to WebSocket service
            connection = await self.websocket_service.connect(
                session_id=session_id,
                user_id=user_id,
                token=token
            )
            
            # Record connection in load balancer
            if self.load_balancer and server_info:
                await self.load_balancer.record_connection(server_info.server_id, session_id)
            
            # Cache connection state
            if self.cache_manager:
                await self.cache_manager.set(
                    key=f"connection:{session_id}",
                    value={
                        "user_id": user_id,
                        "connected_at": datetime.utcnow().isoformat(),
                        "server_id": server_info.server_id if server_info else None
                    },
                    cache_type=CacheType.CONNECTION_STATE
                )
            
            # Log connection
            self.logger.log_connection_event(
                "connected",
                session_id,
                user_id,
                {"server_id": server_info.server_id if server_info else None}
            )
            
            self.metrics.total_connections += 1
            self.metrics.active_connections += 1
            self.metrics.last_activity = datetime.utcnow()
            
            return connection
            
        except Exception as e:
            self.logger.log_error_event(e, session_id, user_id, "connect")
            raise
    
    async def disconnect(self, session_id: str):
        """
        Disconnect WebSocket connection with cleanup
        
        Args:
            session_id: Session identifier
        """
        try:
            # Get connection info from cache
            server_id = None
            if self.cache_manager:
                connection_data = await self.cache_manager.get(
                    key=f"connection:{session_id}",
                    cache_type=CacheType.CONNECTION_STATE
                )
                if connection_data:
                    server_id = connection_data.get("server_id")
            
            # Disconnect from WebSocket service
            await self.websocket_service.disconnect(session_id)
            
            # Record disconnection in load balancer
            if self.load_balancer and server_id:
                await self.load_balancer.record_disconnection(server_id, session_id)
            
            # Remove from cache
            if self.cache_manager:
                await self.cache_manager.delete(
                    key=f"connection:{session_id}",
                    cache_type=CacheType.CONNECTION_STATE
                )
            
            # Log disconnection
            self.logger.log_connection_event("disconnected", session_id)
            
            self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
            self.metrics.last_activity = datetime.utcnow()
            
        except Exception as e:
            self.logger.log_error_event(e, session_id, None, "disconnect")
            raise
    
    async def send_message(
        self,
        session_id: str,
        message: Dict[str, Any],
        priority: ProcessingPriority = ProcessingPriority.NORMAL
    ):
        """
        Send message with production optimizations
        
        Args:
            session_id: Session identifier
            message: Message to send
            priority: Message priority
        """
        try:
            # Get user ID from cache
            user_id = None
            if self.cache_manager:
                connection_data = await self.cache_manager.get(
                    key=f"connection:{session_id}",
                    cache_type=CacheType.CONNECTION_STATE
                )
                if connection_data:
                    user_id = connection_data.get("user_id")
            
            # Queue message for async processing
            task_id = await self.async_processor.queue_message(
                message=message,
                session_id=session_id,
                user_id=user_id,
                priority=priority
            )
            
            # Log message
            self.logger.log_message_event(
                "queued",
                session_id,
                message.get("type", "unknown"),
                user_id,
                additional_data={"task_id": task_id, "priority": priority.value}
            )
            
            self.metrics.messages_processed += 1
            self.metrics.last_activity = datetime.utcnow()
            
        except Exception as e:
            self.logger.log_error_event(e, session_id, None, "send_message")
            raise
    
    async def broadcast_message(
        self,
        message: Dict[str, Any],
        user_ids: Optional[List[str]] = None,
        priority: ProcessingPriority = ProcessingPriority.NORMAL
    ):
        """
        Broadcast message to multiple users
        
        Args:
            message: Message to broadcast
            user_ids: Optional list of user IDs to broadcast to
            priority: Message priority
        """
        try:
            # Get active connections
            if user_ids:
                # Broadcast to specific users
                for user_id in user_ids:
                    # Get user sessions from cache
                    if self.cache_manager:
                        user_sessions = await self.cache_manager.get(
                            key=f"user_sessions:{user_id}",
                            cache_type=CacheType.USER_SESSIONS
                        )
                        if user_sessions:
                            for session_id in user_sessions:
                                await self.send_message(session_id, message, priority)
            else:
                # Broadcast to all active connections
                await self.websocket_service.broadcast_to_all(message)
            
            self.logger.log_message_event(
                "broadcast",
                "all",
                message.get("type", "unknown"),
                additional_data={"user_count": len(user_ids) if user_ids else "all"}
            )
            
        except Exception as e:
            self.logger.log_error_event(e, None, None, "broadcast_message")
            raise
    
    async def _handle_workflow_update(self, message: Dict[str, Any], session_id: str, user_id: Optional[str]):
        """Handle workflow update message"""
        try:
            # Send to WebSocket service
            await self.websocket_service.send_message(session_id, message)
            
            # Cache workflow state
            if self.cache_manager:
                workflow_id = message.get("workflow_id")
                if workflow_id:
                    await self.cache_manager.set(
                        key=f"workflow:{workflow_id}",
                        value=message,
                        cache_type=CacheType.WORKFLOW_STATE
                    )
            
            self.logger.log_message_event(
                "workflow_update_sent",
                session_id,
                "workflow_update",
                user_id
            )
            
        except Exception as e:
            self.logger.log_error_event(e, session_id, user_id, "handle_workflow_update")
            raise
    
    async def _handle_notification(self, message: Dict[str, Any], session_id: str, user_id: Optional[str]):
        """Handle notification message"""
        try:
            # Send to WebSocket service
            await self.websocket_service.send_message(session_id, message)
            
            # Cache notification
            if self.cache_manager:
                notification_id = message.get("notification_id")
                if notification_id:
                    await self.cache_manager.set(
                        key=f"notification:{notification_id}",
                        value=message,
                        cache_type=CacheType.NOTIFICATION_QUEUE
                    )
            
            self.logger.log_message_event(
                "notification_sent",
                session_id,
                "notification",
                user_id
            )
            
        except Exception as e:
            self.logger.log_error_event(e, session_id, user_id, "handle_notification")
            raise
    
    async def _handle_chat_message(self, message: Dict[str, Any], session_id: str, user_id: Optional[str]):
        """Handle chat message"""
        try:
            # Send to WebSocket service
            await self.websocket_service.send_message(session_id, message)
            
            # Cache message history
            if self.cache_manager:
                chat_id = message.get("chat_id")
                if chat_id:
                    await self.cache_manager.set(
                        key=f"chat:{chat_id}",
                        value=message,
                        cache_type=CacheType.MESSAGE_HISTORY
                    )
            
            self.logger.log_message_event(
                "chat_sent",
                session_id,
                "chat",
                user_id
            )
            
        except Exception as e:
            self.logger.log_error_event(e, session_id, user_id, "handle_chat_message")
            raise
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        while self.running:
            try:
                await asyncio.sleep(10)  # Collect every 10 seconds
                await self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            # Check WebSocket service health
            ws_health = await self.websocket_service.health_check()
            
            # Check async processor health
            processor_health = await self.async_processor.health_check()
            
            # Check cache manager health
            cache_health = None
            if self.cache_manager:
                cache_health = await self.cache_manager.health_check()
            
            # Check load balancer health
            lb_health = None
            if self.load_balancer:
                lb_health = await self.load_balancer.health_check()
            
            # Calculate overall health score
            health_scores = [
                ws_health.get("status") == "healthy",
                processor_health.get("status") == "healthy"
            ]
            
            if cache_health:
                health_scores.append(cache_health.get("status") == "healthy")
            
            if lb_health:
                health_scores.append(lb_health.get("status") == "healthy")
            
            self.metrics.server_health_score = sum(health_scores) / len(health_scores)
            
            # Log health status
            self.logger.log_performance_event(
                "health_check",
                0.1,  # Simulated duration
                metrics={
                    "websocket_status": ws_health.get("status"),
                    "processor_status": processor_health.get("status"),
                    "cache_status": cache_health.get("status") if cache_health else "disabled",
                    "load_balancer_status": lb_health.get("status") if lb_health else "disabled",
                    "overall_health_score": self.metrics.server_health_score
                }
            )
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.metrics.server_health_score = 0.0
    
    async def _collect_metrics(self):
        """Collect and update metrics"""
        try:
            # Update uptime
            self.metrics.uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
            
            # Get component metrics
            processor_metrics = self.async_processor.get_metrics()
            
            # Update message metrics
            self.metrics.messages_per_second = processor_metrics.throughput_per_second
            self.metrics.average_response_time = processor_metrics.average_processing_time
            self.metrics.error_rate = processor_metrics.error_rate
            
            # Update worker utilization
            worker_metrics = self.async_processor.get_worker_metrics()
            if worker_metrics:
                total_workers = len(worker_metrics)
                busy_workers = sum(1 for w in worker_metrics.values() if w.state.value == "busy")
                self.metrics.worker_utilization = busy_workers / total_workers if total_workers > 0 else 0
            
            # Update cache hit rate
            if self.cache_manager:
                cache_metrics = self.cache_manager.get_metrics()
                self.metrics.cache_hit_rate = cache_metrics.hit_rate
            
            # Store performance history
            performance_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "active_connections": self.metrics.active_connections,
                "messages_per_second": self.metrics.messages_per_second,
                "average_response_time": self.metrics.average_response_time,
                "error_rate": self.metrics.error_rate,
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "worker_utilization": self.metrics.worker_utilization,
                "server_health_score": self.metrics.server_health_score
            }
            
            self.performance_history.append(performance_data)
            if len(self.performance_history) > self.max_history_size:
                self.performance_history = self.performance_history[-self.max_history_size:]
            
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
    
    def get_metrics(self) -> ProductionMetrics:
        """Get current production metrics"""
        return self.metrics
    
    def get_performance_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get performance history"""
        return self.performance_history[-limit:]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            # Get component health
            ws_health = await self.websocket_service.health_check()
            processor_health = await self.async_processor.health_check()
            
            cache_health = None
            if self.cache_manager:
                cache_health = await self.cache_manager.health_check()
            
            lb_health = None
            if self.load_balancer:
                lb_health = await self.load_balancer.health_check()
            
            # Determine overall status
            component_statuses = [
                ws_health.get("status"),
                processor_health.get("status")
            ]
            
            if cache_health:
                component_statuses.append(cache_health.get("status"))
            
            if lb_health:
                component_statuses.append(lb_health.get("status"))
            
            if "critical" in component_statuses:
                overall_status = "critical"
            elif "degraded" in component_statuses:
                overall_status = "degraded"
            else:
                overall_status = "healthy"
            
            return {
                "status": overall_status,
                "uptime_seconds": self.metrics.uptime_seconds,
                "metrics": {
                    "total_connections": self.metrics.total_connections,
                    "active_connections": self.metrics.active_connections,
                    "messages_processed": self.metrics.messages_processed,
                    "messages_per_second": self.metrics.messages_per_second,
                    "average_response_time": self.metrics.average_response_time,
                    "error_rate": self.metrics.error_rate,
                    "cache_hit_rate": self.metrics.cache_hit_rate,
                    "worker_utilization": self.metrics.worker_utilization,
                    "server_health_score": self.metrics.server_health_score
                },
                "components": {
                    "websocket_service": ws_health,
                    "async_processor": processor_health,
                    "cache_manager": cache_health,
                    "load_balancer": lb_health
                },
                "configuration": {
                    "auto_scaling": self.enable_auto_scaling,
                    "caching": self.enable_caching,
                    "load_balancing": self.enable_load_balancing,
                    "monitoring": self.enable_monitoring
                }
            }
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "status": "critical",
                "error": str(e),
                "uptime_seconds": self.metrics.uptime_seconds
            }

