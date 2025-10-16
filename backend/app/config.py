"""
Application configuration using pydantic-settings.

This module handles all environment-based configuration with validation
and type hints for the ArchMesh PoC application.
"""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="ArchMesh PoC", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment")

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins",
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5433/archmesh",
        description="Database connection URL",
    )
    database_pool_size: int = Field(default=10, description="Database pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow")

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6380/0", description="Redis connection URL"
    )
    redis_max_connections: int = Field(
        default=10, description="Redis max connections"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log format",
    )

    # AI/LLM Settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key"
    )
    default_llm_provider: str = Field(
        default="openai", description="Default LLM provider"
    )
    default_llm_model: str = Field(
        default="gpt-4", description="Default LLM model"
    )

    # File Processing
    max_file_size: int = Field(
        default=50 * 1024 * 1024, description="Max file size in bytes (50MB)"
    )
    allowed_file_types: list[str] = Field(
        default=[".pdf", ".docx", ".pptx", ".txt"],
        description="Allowed file types",
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed_envs = ["development", "staging", "production"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of: {allowed_envs}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    @field_validator("default_llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider."""
        allowed_providers = ["openai", "anthropic"]
        if v not in allowed_providers:
            raise ValueError(f"LLM provider must be one of: {allowed_providers}")
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.database_url.replace("+asyncpg", "")


# Global settings instance
settings = Settings()
