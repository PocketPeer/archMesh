"""
WebSocket configuration schema for ArchMesh

This module defines the configuration schema for WebSocket service
including connection limits, timeouts, and retry settings.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional


class WebSocketConfig(BaseModel):
    """WebSocket configuration schema"""
    
    # Connection settings
    max_connections: int = Field(default=1000, ge=1, le=10000, description="Maximum concurrent connections")
    heartbeat_interval: int = Field(default=30, ge=5, le=300, description="Heartbeat interval in seconds")
    connection_timeout: int = Field(default=300, ge=60, le=3600, description="Connection timeout in seconds")
    
    # Reconnection settings
    max_reconnect_attempts: int = Field(default=5, ge=1, le=20, description="Maximum reconnection attempts")
    reconnect_delay: int = Field(default=1000, ge=100, le=10000, description="Reconnection delay in milliseconds")
    
    # Message settings
    max_message_size: int = Field(default=1024 * 1024, ge=1024, le=10 * 1024 * 1024, description="Maximum message size in bytes")
    message_queue_size: int = Field(default=100, ge=10, le=1000, description="Message queue size per connection")
    
    # Security settings
    require_authentication: bool = Field(default=True, description="Require authentication for connections")
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins")
    
    # Performance settings
    enable_compression: bool = Field(default=True, description="Enable WebSocket compression")
    compression_threshold: int = Field(default=1024, ge=512, le=8192, description="Compression threshold in bytes")
    
    @validator('max_connections')
    def validate_max_connections(cls, v):
        if v <= 0:
            raise ValueError('max_connections must be positive')
        return v
    
    @validator('heartbeat_interval')
    def validate_heartbeat_interval(cls, v):
        if v <= 0:
            raise ValueError('heartbeat_interval must be positive')
        return v
    
    @validator('connection_timeout')
    def validate_connection_timeout(cls, v):
        if v <= 0:
            raise ValueError('connection_timeout must be positive')
        return v
    
    @validator('max_reconnect_attempts')
    def validate_max_reconnect_attempts(cls, v):
        if v <= 0:
            raise ValueError('max_reconnect_attempts must be positive')
        return v
    
    @validator('reconnect_delay')
    def validate_reconnect_delay(cls, v):
        if v <= 0:
            raise ValueError('reconnect_delay must be positive')
        return v

