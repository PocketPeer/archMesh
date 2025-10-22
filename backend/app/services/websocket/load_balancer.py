"""
Load Balancer for WebSocket Service

This module provides connection distribution, failover mechanisms,
and load balancing for scalable WebSocket operations.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import hashlib

from app.core.exceptions import WebSocketError, ConnectionError

logger = logging.getLogger(__name__)


class LoadBalanceStrategy(str, Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_LOAD = "least_load"
    HASH_BASED = "hash_based"
    RANDOM = "random"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"


class ServerState(str, Enum):
    """Server states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


@dataclass
class ServerInfo:
    """Server information and metrics"""
    server_id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time: float = 0.0
    error_rate: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    state: ServerState = ServerState.HEALTHY
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadBalanceMetrics:
    """Load balancing metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    server_count: int = 0
    healthy_servers: int = 0
    last_balance_time: datetime = field(default_factory=datetime.utcnow)


class LoadBalancer:
    """
    Load balancer for WebSocket connections
    
    Provides:
    - Multiple load balancing strategies
    - Server health monitoring and failover
    - Connection distribution and management
    - Performance metrics and monitoring
    - Automatic server discovery and management
    - Circuit breaker pattern for failing servers
    """
    
    def __init__(
        self,
        strategy: LoadBalanceStrategy = LoadBalanceStrategy.LEAST_CONNECTIONS,
        health_check_interval: int = 30,
        health_check_timeout: int = 5,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60
    ):
        """
        Initialize load balancer
        
        Args:
            strategy: Load balancing strategy
            health_check_interval: Health check interval in seconds
            health_check_timeout: Health check timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
            circuit_breaker_threshold: Circuit breaker failure threshold
            circuit_breaker_timeout: Circuit breaker timeout in seconds
        """
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.health_check_timeout = health_check_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        # Server management
        self.servers: Dict[str, ServerInfo] = {}
        self.server_states: Dict[str, ServerState] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Load balancing state
        self.round_robin_index = 0
        self.connection_counts: Dict[str, int] = {}
        self.server_weights: Dict[str, int] = {}
        
        # Metrics
        self.metrics = LoadBalanceMetrics()
        
        # Health check task
        self.health_check_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Performance tracking
        self.response_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
    
    async def start(self):
        """Start the load balancer"""
        if self.running:
            return
        
        self.running = True
        
        # Start health check task
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info(f"Load balancer started with strategy: {self.strategy}")
    
    async def stop(self):
        """Stop the load balancer"""
        self.running = False
        
        # Stop health check task
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Load balancer stopped")
    
    def add_server(
        self,
        server_id: str,
        host: str,
        port: int,
        weight: int = 1,
        max_connections: int = 1000,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a server to the load balancer
        
        Args:
            server_id: Unique server identifier
            host: Server hostname or IP
            port: Server port
            weight: Server weight for weighted strategies
            max_connections: Maximum connections for this server
            tags: Optional server tags
            metadata: Optional server metadata
        """
        server_info = ServerInfo(
            server_id=server_id,
            host=host,
            port=port,
            weight=weight,
            max_connections=max_connections,
            tags=tags or set(),
            metadata=metadata or {}
        )
        
        self.servers[server_id] = server_info
        self.server_states[server_id] = ServerState.HEALTHY
        self.connection_counts[server_id] = 0
        self.server_weights[server_id] = weight
        self.response_times[server_id] = []
        self.error_counts[server_id] = 0
        
        # Initialize circuit breaker
        self.circuit_breakers[server_id] = {
            "failure_count": 0,
            "last_failure": None,
            "state": "closed"
        }
        
        self.metrics.server_count += 1
        self.metrics.healthy_servers += 1
        
        logger.info(f"Added server: {server_id} ({host}:{port})")
    
    def remove_server(self, server_id: str):
        """
        Remove a server from the load balancer
        
        Args:
            server_id: Server identifier to remove
        """
        if server_id in self.servers:
            del self.servers[server_id]
            del self.server_states[server_id]
            del self.connection_counts[server_id]
            del self.server_weights[server_id]
            del self.response_times[server_id]
            del self.error_counts[server_id]
            del self.circuit_breakers[server_id]
            
            self.metrics.server_count -= 1
            if self.server_states.get(server_id) == ServerState.HEALTHY:
                self.metrics.healthy_servers -= 1
            
            logger.info(f"Removed server: {server_id}")
    
    async def select_server(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: Optional[Set[str]] = None
    ) -> Optional[ServerInfo]:
        """
        Select a server based on the load balancing strategy
        
        Args:
            session_id: Optional session identifier
            user_id: Optional user identifier
            tags: Optional tags to match
            
        Returns:
            Selected server info or None if no servers available
        """
        # Filter servers by health and tags
        available_servers = self._get_available_servers(tags)
        
        if not available_servers:
            logger.warning("No available servers for load balancing")
            return None
        
        # Select server based on strategy
        if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_servers)
        elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(available_servers)
        elif self.strategy == LoadBalanceStrategy.LEAST_LOAD:
            return self._least_load_selection(available_servers)
        elif self.strategy == LoadBalanceStrategy.HASH_BASED:
            return self._hash_based_selection(available_servers, session_id or user_id or "")
        elif self.strategy == LoadBalanceStrategy.RANDOM:
            return self._random_selection(available_servers)
        elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(available_servers)
        else:
            return self._least_connections_selection(available_servers)
    
    def _get_available_servers(self, tags: Optional[Set[str]] = None) -> List[ServerInfo]:
        """Get list of available servers"""
        available = []
        
        for server_id, server_info in self.servers.items():
            # Check server state
            if self.server_states[server_id] not in [ServerState.HEALTHY, ServerState.DEGRADED]:
                continue
            
            # Check circuit breaker
            if self._is_circuit_open(server_id):
                continue
            
            # Check connection limit
            if self.connection_counts[server_id] >= server_info.max_connections:
                continue
            
            # Check tags if specified
            if tags and not tags.issubset(server_info.tags):
                continue
            
            available.append(server_info)
        
        return available
    
    def _round_robin_selection(self, servers: List[ServerInfo]) -> ServerInfo:
        """Round robin server selection"""
        if not servers:
            return None
        
        server = servers[self.round_robin_index % len(servers)]
        self.round_robin_index += 1
        return server
    
    def _least_connections_selection(self, servers: List[ServerInfo]) -> ServerInfo:
        """Least connections server selection"""
        if not servers:
            return None
        
        return min(servers, key=lambda s: self.connection_counts[s.server_id])
    
    def _least_load_selection(self, servers: List[ServerInfo]) -> ServerInfo:
        """Least load server selection based on CPU and memory"""
        if not servers:
            return None
        
        def calculate_load(server):
            cpu_weight = 0.6
            memory_weight = 0.4
            return (server.cpu_usage * cpu_weight + server.memory_usage * memory_weight)
        
        return min(servers, key=calculate_load)
    
    def _hash_based_selection(self, servers: List[ServerInfo], key: str) -> ServerInfo:
        """Hash-based server selection for consistent routing"""
        if not servers or not key:
            return None
        
        # Use consistent hashing
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        server_index = hash_value % len(servers)
        return servers[server_index]
    
    def _random_selection(self, servers: List[ServerInfo]) -> ServerInfo:
        """Random server selection"""
        if not servers:
            return None
        
        return random.choice(servers)
    
    def _weighted_round_robin_selection(self, servers: List[ServerInfo]) -> ServerInfo:
        """Weighted round robin server selection"""
        if not servers:
            return None
        
        # Calculate total weight
        total_weight = sum(self.server_weights[s.server_id] for s in servers)
        
        # Select based on weight
        random_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for server in servers:
            current_weight += self.server_weights[server.server_id]
            if random_value <= current_weight:
                return server
        
        return servers[-1]  # Fallback
    
    async def record_connection(self, server_id: str, session_id: str):
        """Record a new connection to a server"""
        if server_id in self.connection_counts:
            self.connection_counts[server_id] += 1
            self.servers[server_id].current_connections += 1
    
    async def record_disconnection(self, server_id: str, session_id: str):
        """Record a disconnection from a server"""
        if server_id in self.connection_counts:
            self.connection_counts[server_id] = max(0, self.connection_counts[server_id] - 1)
            self.servers[server_id].current_connections = max(0, self.servers[server_id].current_connections - 1)
    
    async def record_response_time(self, server_id: str, response_time: float):
        """Record server response time"""
        if server_id in self.response_times:
            self.response_times[server_id].append(response_time)
            
            # Keep only last 100 response times
            if len(self.response_times[server_id]) > 100:
                self.response_times[server_id] = self.response_times[server_id][-100:]
            
            # Update server response time
            if server_id in self.servers:
                self.servers[server_id].response_time = sum(self.response_times[server_id]) / len(self.response_times[server_id])
    
    async def record_error(self, server_id: str):
        """Record an error for a server"""
        if server_id in self.error_counts:
            self.error_counts[server_id] += 1
            
            # Update server error rate
            if server_id in self.servers:
                total_requests = self.connection_counts[server_id] + self.error_counts[server_id]
                if total_requests > 0:
                    self.servers[server_id].error_rate = self.error_counts[server_id] / total_requests
            
            # Update circuit breaker
            self._update_circuit_breaker(server_id, failed=True)
            
            self.metrics.failed_requests += 1
        else:
            self.metrics.failed_requests += 1
    
    async def record_success(self, server_id: str):
        """Record a successful request for a server"""
        if server_id in self.servers:
            # Reset circuit breaker on success
            self._update_circuit_breaker(server_id, failed=False)
            
            self.metrics.successful_requests += 1
    
    def _is_circuit_open(self, server_id: str) -> bool:
        """Check if circuit breaker is open for a server"""
        if server_id not in self.circuit_breakers:
            return False
        
        circuit = self.circuit_breakers[server_id]
        if circuit["state"] == "open":
            # Check if we should transition to half-open
            if circuit["last_failure"] and (datetime.utcnow() - circuit["last_failure"]).total_seconds() > self.circuit_breaker_timeout:
                circuit["state"] = "half-open"
                return False
            return True
        
        return False
    
    def _update_circuit_breaker(self, server_id: str, failed: bool):
        """Update circuit breaker state for a server"""
        if server_id not in self.circuit_breakers:
            return
        
        circuit = self.circuit_breakers[server_id]
        
        if failed:
            circuit["failure_count"] += 1
            circuit["last_failure"] = datetime.utcnow()
            
            if circuit["state"] == "closed" and circuit["failure_count"] >= self.circuit_breaker_threshold:
                circuit["state"] = "open"
                self.server_states[server_id] = ServerState.UNHEALTHY
                logger.warning(f"Circuit breaker opened for server: {server_id}")
            elif circuit["state"] == "half-open":
                circuit["state"] = "open"
                self.server_states[server_id] = ServerState.UNHEALTHY
                logger.warning(f"Circuit breaker reopened for server: {server_id}")
        else:
            # Reset failure count on success
            circuit["failure_count"] = 0
            
            if circuit["state"] == "half-open":
                circuit["state"] = "closed"
                self.server_states[server_id] = ServerState.HEALTHY
                logger.info(f"Circuit breaker closed for server: {server_id}")
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while self.running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all servers"""
        for server_id, server_info in self.servers.items():
            try:
                # Simulate health check (in real implementation, this would ping the server)
                is_healthy = await self._check_server_health(server_info)
                
                if is_healthy:
                    if self.server_states[server_id] != ServerState.HEALTHY:
                        self.server_states[server_id] = ServerState.HEALTHY
                        self.metrics.healthy_servers += 1
                        logger.info(f"Server {server_id} is healthy")
                else:
                    if self.server_states[server_id] == ServerState.HEALTHY:
                        self.server_states[server_id] = ServerState.DEGRADED
                        self.metrics.healthy_servers -= 1
                        logger.warning(f"Server {server_id} is degraded")
                
                server_info.last_health_check = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Health check error for server {server_id}: {e}")
                self.server_states[server_id] = ServerState.UNHEALTHY
    
    async def _check_server_health(self, server_info: ServerInfo) -> bool:
        """Check if a server is healthy"""
        # Simulate health check (in real implementation, this would ping the server)
        # For now, we'll use a simple heuristic based on error rate and response time
        
        if server_info.error_rate > 0.1:  # 10% error rate threshold
            return False
        
        if server_info.response_time > 5.0:  # 5 second response time threshold
            return False
        
        return True
    
    def get_metrics(self) -> LoadBalanceMetrics:
        """Get load balancing metrics"""
        self.metrics.server_count = len(self.servers)
        self.metrics.healthy_servers = len([s for s in self.server_states.values() if s == ServerState.HEALTHY])
        return self.metrics
    
    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all servers"""
        status = {}
        
        for server_id, server_info in self.servers.items():
            status[server_id] = {
                "host": server_info.host,
                "port": server_info.port,
                "state": self.server_states[server_id].value,
                "current_connections": self.connection_counts[server_id],
                "max_connections": server_info.max_connections,
                "cpu_usage": server_info.cpu_usage,
                "memory_usage": server_info.memory_usage,
                "response_time": server_info.response_time,
                "error_rate": server_info.error_rate,
                "last_health_check": server_info.last_health_check.isoformat(),
                "circuit_breaker_state": self.circuit_breakers[server_id]["state"]
            }
        
        return status
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on load balancer
        
        Returns:
            Dict[str, Any]: Health check results
        """
        metrics = self.get_metrics()
        server_status = self.get_server_status()
        
        # Calculate health status
        if metrics.healthy_servers == 0:
            status = "critical"
        elif metrics.healthy_servers < metrics.server_count * 0.5:
            status = "degraded"
        elif metrics.failed_requests > metrics.successful_requests * 0.1:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "strategy": self.strategy.value,
            "metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "average_response_time": metrics.average_response_time,
                "server_count": metrics.server_count,
                "healthy_servers": metrics.healthy_servers
            },
            "servers": server_status,
            "configuration": {
                "health_check_interval": self.health_check_interval,
                "health_check_timeout": self.health_check_timeout,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "circuit_breaker_threshold": self.circuit_breaker_threshold,
                "circuit_breaker_timeout": self.circuit_breaker_timeout
            }
        }

