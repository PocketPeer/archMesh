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
    # Local DeepSeek LLM Settings
    deepseek_base_url: str = Field(
        default="http://localhost:11434", description="DeepSeek local server URL"
    )
    deepseek_model: str = Field(
        default="deepseek-r1", description="DeepSeek model name"
    )
    
    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama server URL"
    )
    ollama_model: str = Field(
        default="llama3.2:3b", description="Ollama model name"
    )
    default_llm_provider: str = Field(
        default="deepseek", description="Default LLM provider (DeepSeek for development)"
    )
    default_llm_model: str = Field(
        default="deepseek-r1", description="Default LLM model"
    )
    
    # Task-specific LLM configurations
    requirements_llm_provider: str = Field(
        default="ollama", description="LLM provider for requirements parsing"
    )
    requirements_llm_model: str = Field(
        default="llama3.2:3b", description="LLM model for requirements parsing"
    )
    
    architecture_llm_provider: str = Field(
        default="ollama", description="LLM provider for architecture design"
    )
    architecture_llm_model: str = Field(
        default="llama3.2:3b", description="LLM model for architecture design"
    )
    
    code_generation_llm_provider: str = Field(
        default="deepseek", description="LLM provider for code generation"
    )
    code_generation_llm_model: str = Field(
        default="deepseek-r1", description="LLM model for code generation"
    )
    
    github_analysis_llm_provider: str = Field(
        default="deepseek", description="LLM provider for GitHub analysis"
    )
    github_analysis_llm_model: str = Field(
        default="deepseek-r1", description="LLM model for GitHub analysis"
    )
    
    adr_writing_llm_provider: str = Field(
        default="deepseek", description="LLM provider for ADR writing"
    )
    adr_writing_llm_model: str = Field(
        default="deepseek-r1", description="LLM model for ADR writing"
    )
    
    # Knowledge Base Service Settings
    pinecone_api_key: Optional[str] = Field(
        default=None, description="Pinecone API key for vector search"
    )
    pinecone_environment: Optional[str] = Field(
        default=None, description="Pinecone environment"
    )
    neo4j_uri: str = Field(
        default="bolt://localhost:7687", description="Neo4j connection URI"
    )
    neo4j_user: str = Field(
        default="neo4j", description="Neo4j username"
    )
    neo4j_password: str = Field(
        default="password123", description="Neo4j password"
    )
    knowledge_base_embedding_model: str = Field(
        default="all-MiniLM-L6-v2", description="Sentence transformer model for embeddings"
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
        allowed_envs = ["development", "staging", "production", "test"]
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
        allowed_providers = ["openai", "anthropic", "deepseek", "ollama"]
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
    
    def get_llm_config_for_task(self, task_type: str) -> tuple[str, str]:
        """
        Get the appropriate LLM provider and model for a specific task type.
        
        Args:
            task_type: The type of task (requirements, architecture, code_generation, etc.)
            
        Returns:
            Tuple of (provider, model) for the task
            
        Raises:
            ValueError: If task_type is not supported
        """
        # In development environment, prefer Ollama for stability, DeepSeek as fallback
        if self.is_development:
            task_configs = {
                "requirements": ("ollama", self.ollama_model),  # Use Ollama for stability
                "architecture": ("ollama", self.ollama_model),  # Use Ollama for stability
                "code_generation": ("ollama", self.ollama_model),  # Use Ollama for dev
                "github_analysis": ("ollama", self.ollama_model),  # Use Ollama for stability
                "adr_writing": ("ollama", self.ollama_model),  # Use Ollama for stability
                "development": ("ollama", self.ollama_model),  # Default to Ollama for dev
                "testing": ("ollama", self.ollama_model),  # Use Ollama for testing
            }
        else:
            # In production, use the configured task-specific models
            task_configs = {
                "requirements": (self.requirements_llm_provider, self.requirements_llm_model),
                "architecture": (self.architecture_llm_provider, self.architecture_llm_model),
                "code_generation": (self.code_generation_llm_provider, self.code_generation_llm_model),
                "github_analysis": (self.github_analysis_llm_provider, self.github_analysis_llm_model),
                "adr_writing": (self.adr_writing_llm_provider, self.adr_writing_llm_model),
                "development": (self.default_llm_provider, self.default_llm_model),
                "testing": (self.default_llm_provider, self.default_llm_model),
            }
        
        if task_type not in task_configs:
            raise ValueError(f"Unsupported task type: {task_type}. Supported types: {list(task_configs.keys())}")
        
        return task_configs[task_type]


# Global settings instance
settings = Settings()
