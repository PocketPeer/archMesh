"""
Production Configuration for WebSocket Services

This module provides production-ready configuration templates
and deployment settings for the WebSocket services.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from app.schemas.websocket import WebSocketConfig
from app.services.websocket.async_processor import ProcessingPriority
from app.services.websocket.cache_manager import CacheType
from app.services.websocket.load_balancer import LoadBalanceStrategy


class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentSize(str, Enum):
    """Deployment sizes"""
    SMALL = "small"      # < 100 concurrent users
    MEDIUM = "medium"    # 100-1000 concurrent users
    LARGE = "large"      # 1000-10000 concurrent users
    ENTERPRISE = "enterprise"  # > 10000 concurrent users


@dataclass
class ProductionConfig:
    """Production configuration for WebSocket services"""
    
    # Environment settings
    environment: Environment = Environment.PRODUCTION
    deployment_size: DeploymentSize = DeploymentSize.MEDIUM
    
    # WebSocket configuration
    websocket_config: WebSocketConfig = field(default_factory=lambda: WebSocketConfig(
        max_connections=1000,
        max_message_size=4096,
        heartbeat_interval=30,
        connection_timeout=300,
        require_authentication=True,
        max_reconnect_attempts=5,
        reconnect_delay=1.0
    ))
    
    # Async processor configuration
    async_processor_config: Dict[str, Any] = field(default_factory=lambda: {
        "max_workers": 20,
        "queue_size": 50000,
        "processing_timeout": 30.0,
        "auto_scale": True,
        "scale_threshold": 0.8,
        "min_workers": 5,
        "max_workers_limit": 100
    })
    
    # Cache configuration
    cache_config: Dict[str, Any] = field(default_factory=lambda: {
        "default_ttl": 3600,
        "max_memory_mb": 512,
        "compression_threshold": 1024,
        "cleanup_interval": 300,
        "enable_compression": True
    })
    
    # Load balancer configuration
    load_balancer_config: Dict[str, Any] = field(default_factory=lambda: {
        "strategy": LoadBalanceStrategy.LEAST_CONNECTIONS,
        "health_check_interval": 30,
        "health_check_timeout": 5,
        "max_retries": 3,
        "retry_delay": 1.0,
        "circuit_breaker_threshold": 5,
        "circuit_breaker_timeout": 60
    })
    
    # Monitoring configuration
    monitoring_config: Dict[str, Any] = field(default_factory=lambda: {
        "health_check_interval": 30,
        "metrics_collection_interval": 10,
        "performance_history_limit": 1000,
        "enable_alerting": True,
        "alert_thresholds": {
            "error_rate": 0.05,
            "response_time": 1.0,
            "memory_usage": 0.8,
            "cpu_usage": 0.8
        }
    })
    
    # Security configuration
    security_config: Dict[str, Any] = field(default_factory=lambda: {
        "enable_rate_limiting": True,
        "rate_limit_per_minute": 1000,
        "enable_cors": True,
        "allowed_origins": ["*"],
        "enable_ssl": True,
        "ssl_cert_path": None,
        "ssl_key_path": None
    })
    
    # Redis configuration
    redis_config: Dict[str, Any] = field(default_factory=lambda: {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None,
        "max_connections": 20,
        "retry_on_timeout": True,
        "socket_timeout": 5,
        "socket_connect_timeout": 5
    })
    
    # Database configuration
    database_config: Dict[str, Any] = field(default_factory=lambda: {
        "host": "localhost",
        "port": 5432,
        "database": "archmesh",
        "username": "archmesh",
        "password": None,
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30,
        "pool_recycle": 3600
    })


class ProductionConfigFactory:
    """Factory for creating production configurations"""
    
    @staticmethod
    def create_config(
        environment: Environment = Environment.PRODUCTION,
        deployment_size: DeploymentSize = DeploymentSize.MEDIUM,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> ProductionConfig:
        """
        Create production configuration based on environment and deployment size
        
        Args:
            environment: Deployment environment
            deployment_size: Deployment size
            custom_config: Custom configuration overrides
            
        Returns:
            ProductionConfig: Configured production settings
        """
        config = ProductionConfig(environment=environment, deployment_size=deployment_size)
        
        # Adjust configuration based on deployment size
        if deployment_size == DeploymentSize.SMALL:
            config.websocket_config.max_connections = 100
            config.async_processor_config["max_workers"] = 5
            config.async_processor_config["queue_size"] = 1000
            config.cache_config["max_memory_mb"] = 128
            config.load_balancer_config["health_check_interval"] = 60
            
        elif deployment_size == DeploymentSize.MEDIUM:
            config.websocket_config.max_connections = 1000
            config.async_processor_config["max_workers"] = 20
            config.async_processor_config["queue_size"] = 50000
            config.cache_config["max_memory_mb"] = 512
            config.load_balancer_config["health_check_interval"] = 30
            
        elif deployment_size == DeploymentSize.LARGE:
            config.websocket_config.max_connections = 5000
            config.async_processor_config["max_workers"] = 50
            config.async_processor_config["queue_size"] = 100000
            config.cache_config["max_memory_mb"] = 1024
            config.load_balancer_config["health_check_interval"] = 15
            
        elif deployment_size == DeploymentSize.ENTERPRISE:
            config.websocket_config.max_connections = 10000
            config.async_processor_config["max_workers"] = 100
            config.async_processor_config["queue_size"] = 500000
            config.cache_config["max_memory_mb"] = 2048
            config.load_balancer_config["health_check_interval"] = 10
        
        # Adjust configuration based on environment
        if environment == Environment.DEVELOPMENT:
            config.websocket_config.require_authentication = False
            config.security_config["enable_rate_limiting"] = False
            config.monitoring_config["enable_alerting"] = False
            
        elif environment == Environment.STAGING:
            config.websocket_config.require_authentication = True
            config.security_config["enable_rate_limiting"] = True
            config.monitoring_config["enable_alerting"] = True
            
        elif environment == Environment.PRODUCTION:
            config.websocket_config.require_authentication = True
            config.security_config["enable_rate_limiting"] = True
            config.monitoring_config["enable_alerting"] = True
            config.security_config["enable_ssl"] = True
        
        # Apply custom configuration overrides
        if custom_config:
            for key, value in custom_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        return config
    
    @staticmethod
    def get_environment_config() -> Dict[str, Any]:
        """
        Get configuration from environment variables
        
        Returns:
            Dict[str, Any]: Configuration from environment
        """
        import os
        
        return {
            "environment": os.getenv("ENVIRONMENT", Environment.PRODUCTION),
            "deployment_size": os.getenv("DEPLOYMENT_SIZE", DeploymentSize.MEDIUM),
            "redis_config": {
                "host": os.getenv("REDIS_HOST", "localhost"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "db": int(os.getenv("REDIS_DB", "0")),
                "password": os.getenv("REDIS_PASSWORD"),
                "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
            },
            "database_config": {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "archmesh"),
                "username": os.getenv("DB_USER", "archmesh"),
                "password": os.getenv("DB_PASSWORD"),
                "pool_size": int(os.getenv("DB_POOL_SIZE", "20"))
            },
            "security_config": {
                "enable_ssl": os.getenv("ENABLE_SSL", "true").lower() == "true",
                "ssl_cert_path": os.getenv("SSL_CERT_PATH"),
                "ssl_key_path": os.getenv("SSL_KEY_PATH"),
                "allowed_origins": os.getenv("ALLOWED_ORIGINS", "*").split(",")
            }
        }


# Predefined configurations for common scenarios
DEVELOPMENT_CONFIG = ProductionConfigFactory.create_config(
    environment=Environment.DEVELOPMENT,
    deployment_size=DeploymentSize.SMALL
)

STAGING_CONFIG = ProductionConfigFactory.create_config(
    environment=Environment.STAGING,
    deployment_size=DeploymentSize.MEDIUM
)

PRODUCTION_SMALL_CONFIG = ProductionConfigFactory.create_config(
    environment=Environment.PRODUCTION,
    deployment_size=DeploymentSize.SMALL
)

PRODUCTION_MEDIUM_CONFIG = ProductionConfigFactory.create_config(
    environment=Environment.PRODUCTION,
    deployment_size=DeploymentSize.MEDIUM
)

PRODUCTION_LARGE_CONFIG = ProductionConfigFactory.create_config(
    environment=Environment.PRODUCTION,
    deployment_size=DeploymentSize.LARGE
)

PRODUCTION_ENTERPRISE_CONFIG = ProductionConfigFactory.create_config(
    environment=Environment.PRODUCTION,
    deployment_size=DeploymentSize.ENTERPRISE
)


def get_production_config(
    environment: Optional[str] = None,
    deployment_size: Optional[str] = None
) -> ProductionConfig:
    """
    Get production configuration with environment variable support
    
    Args:
        environment: Environment name (development, staging, production)
        deployment_size: Deployment size (small, medium, large, enterprise)
        
    Returns:
        ProductionConfig: Configured production settings
    """
    # Get configuration from environment variables
    env_config = ProductionConfigFactory.get_environment_config()
    
    # Override with provided parameters
    if environment:
        env_config["environment"] = Environment(environment)
    if deployment_size:
        env_config["deployment_size"] = DeploymentSize(deployment_size)
    
    return ProductionConfigFactory.create_config(
        environment=env_config["environment"],
        deployment_size=env_config["deployment_size"],
        custom_config=env_config
    )

