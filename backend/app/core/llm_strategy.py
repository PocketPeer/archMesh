"""
LLM Selection Strategy for ArchMesh PoC.

This module provides intelligent LLM selection based on task type, environment,
and performance requirements. It implements the task-specific LLM optimization
strategy as defined in the requirements.
"""

from typing import Dict, Tuple, Optional
from enum import Enum
from loguru import logger

from app.config import settings


class TaskType(Enum):
    """Enumeration of supported task types."""
    REQUIREMENTS_PARSING = "requirements"
    ARCHITECTURE_DESIGN = "architecture"
    CODE_GENERATION = "code_generation"
    GITHUB_ANALYSIS = "github_analysis"
    ADR_WRITING = "adr_writing"
    DEVELOPMENT = "development"
    TESTING = "testing"


class LLMStrategy:
    """
    Intelligent LLM selection strategy based on task requirements.
    
    This class implements the task-specific LLM optimization strategy:
    - Requirements Parsing: DeepSeek R1 (Excellent)
    - Architecture Design: Claude Opus (Best)
    - Code Generation: GPT-4 (Best)
    - GitHub Analysis: DeepSeek R1 (Excellent)
    - ADR Writing: Claude Sonnet (Best)
    - Development/Testing: DeepSeek (Free and capable)
    """
    
    # Task-specific LLM recommendations based on performance analysis
    TASK_LLM_MAPPING = {
        TaskType.REQUIREMENTS_PARSING: {
            "excellent": ("deepseek", "deepseek-r1"),
            "good": ("anthropic", "claude-3-5-sonnet-20241022"),
            "fallback": ("openai", "gpt-4")
        },
        TaskType.ARCHITECTURE_DESIGN: {
            "best": ("anthropic", "claude-3-5-opus-20241022"),
            "excellent": ("anthropic", "claude-3-5-sonnet-20241022"),
            "good": ("deepseek", "deepseek-r1"),
            "fallback": ("openai", "gpt-4")
        },
        TaskType.CODE_GENERATION: {
            "best": ("openai", "gpt-4"),
            "good": ("deepseek", "deepseek-r1"),
            "fallback": ("anthropic", "claude-3-5-sonnet-20241022")
        },
        TaskType.GITHUB_ANALYSIS: {
            "excellent": ("deepseek", "deepseek-r1"),
            "good": ("anthropic", "claude-3-5-sonnet-20241022"),
            "fallback": ("openai", "gpt-4")
        },
        TaskType.ADR_WRITING: {
            "best": ("anthropic", "claude-3-5-sonnet-20241022"),
            "excellent": ("anthropic", "claude-3-5-opus-20241022"),
            "good": ("deepseek", "deepseek-r1"),
            "fallback": ("openai", "gpt-4")
        },
        TaskType.DEVELOPMENT: {
            "best": ("deepseek", "deepseek-r1"),  # Free and capable
            "fast": ("ollama", "llama3.2:3b"),  # Fast local fallback
            "fallback": ("openai", "gpt-4")
        },
        TaskType.TESTING: {
            "best": ("deepseek", "deepseek-r1"),  # Free and capable
            "fast": ("ollama", "llama3.2:3b"),  # Fast local fallback
            "fallback": ("openai", "gpt-4")
        }
    }
    
    @classmethod
    def get_llm_for_task(
        cls,
        task_type: TaskType,
        environment: Optional[str] = None,
        use_fallback: bool = False
    ) -> Tuple[str, str]:
        """
        Get the optimal LLM configuration for a specific task.
        
        Args:
            task_type: The type of task to perform
            environment: Environment context (development, production)
            use_fallback: Whether to use fallback options if primary is unavailable
            
        Returns:
            Tuple of (provider, model) for the task
            
        Raises:
            ValueError: If task_type is not supported
        """
        if task_type not in cls.TASK_LLM_MAPPING:
            raise ValueError(f"Unsupported task type: {task_type}")
        
        # Get environment context
        env = environment or settings.environment
        is_dev = env == "development"
        
        # Get task-specific mapping
        task_mapping = cls.TASK_LLM_MAPPING[task_type]
        
        # In development, prefer DeepSeek for cost-effectiveness
        if is_dev and not use_fallback:
            # For development, prioritize DeepSeek for most tasks
            if task_type in [TaskType.DEVELOPMENT, TaskType.TESTING]:
                return task_mapping.get("best", ("deepseek", "deepseek-r1"))
            elif "excellent" in task_mapping and task_mapping["excellent"][0] == "deepseek":
                return task_mapping["excellent"]
            elif "good" in task_mapping and task_mapping["good"][0] == "deepseek":
                return task_mapping["good"]
        
        # Select based on priority: best > excellent > good > fallback
        for priority in ["best", "excellent", "good", "fallback"]:
            if priority in task_mapping:
                provider, model = task_mapping[priority]
                
                # Check if provider is available
                if cls._is_provider_available(provider):
                    logger.debug(
                        f"Selected {provider}/{model} for {task_type.value} task",
                        extra={
                            "task_type": task_type.value,
                            "provider": provider,
                            "model": model,
                            "priority": priority,
                            "environment": env
                        }
                    )
                    return provider, model
        
        # Ultimate fallback
        return ("deepseek", "deepseek-r1")
    
    @classmethod
    def _is_provider_available(cls, provider: str) -> bool:
        """
        Check if a provider is available based on API keys and configuration.
        
        Args:
            provider: The LLM provider to check
            
        Returns:
            True if provider is available, False otherwise
        """
        try:
            if provider == "openai":
                return bool(settings.openai_api_key)
            elif provider == "anthropic":
                return bool(settings.anthropic_api_key)
            elif provider == "deepseek":
                # DeepSeek is always available if base URL is configured
                return bool(settings.deepseek_base_url)
            elif provider == "ollama":
                # Ollama is available if local server is running
                return True  # Assume Ollama is available locally
            else:
                return False
        except Exception as e:
            logger.warning(f"Error checking provider availability: {str(e)}")
            return False
    
    @classmethod
    def get_task_recommendations(cls) -> Dict[str, Dict[str, str]]:
        """
        Get LLM recommendations for all supported tasks.
        
        Returns:
            Dictionary mapping task types to their LLM recommendations
        """
        recommendations = {}
        
        for task_type in TaskType:
            task_mapping = cls.TASK_LLM_MAPPING[task_type]
            
            # Get primary recommendation
            primary_config = None
            for priority in ["best", "excellent", "good"]:
                if priority in task_mapping:
                    primary_config = task_mapping[priority]
                    break
            
            if primary_config:
                primary_str = f"{primary_config[0]}/{primary_config[1]}"
            else:
                primary_str = "unknown/unknown"
            
            recommendations[task_type.value] = {
                "primary": primary_str,
                "alternatives": [
                    f"{config[0]}/{config[1]}" 
                    for priority, config in task_mapping.items() 
                    if priority != "best" and priority != "excellent"
                ]
            }
        
        return recommendations
    
    @classmethod
    def get_environment_strategy(cls, environment: str) -> Dict[str, str]:
        """
        Get LLM strategy recommendations for a specific environment.
        
        Args:
            environment: The environment (development, production)
            
        Returns:
            Dictionary with environment-specific strategy
        """
        if environment == "development":
            return {
                "strategy": "Cost-optimized with DeepSeek preference",
                "reasoning": "Development environment prioritizes cost-effectiveness while maintaining quality",
                "primary_provider": "deepseek",
                "fallback_provider": "openai",
                "notes": "DeepSeek R1 provides excellent performance for most tasks at no cost"
            }
        elif environment == "production":
            return {
                "strategy": "Performance-optimized with task-specific selection",
                "reasoning": "Production environment prioritizes best-in-class performance for each task",
                "primary_provider": "varies_by_task",
                "fallback_provider": "deepseek",
                "notes": "Each task uses the optimal LLM based on performance analysis"
            }
        else:
            return {
                "strategy": "Balanced approach",
                "reasoning": "Unknown environment, using balanced approach",
                "primary_provider": "deepseek",
                "fallback_provider": "openai",
                "notes": "Default to cost-effective option with fallback"
            }


def get_optimal_llm_for_task(task_type: str, environment: Optional[str] = None) -> Tuple[str, str]:
    """
    Convenience function to get optimal LLM for a task.
    
    Args:
        task_type: String representation of task type
        environment: Optional environment context
        
    Returns:
        Tuple of (provider, model)
    """
    try:
        task_enum = TaskType(task_type)
        return LLMStrategy.get_llm_for_task(task_enum, environment)
    except ValueError:
        logger.warning(f"Unknown task type: {task_type}, using default")
        return LLMStrategy.get_llm_for_task(TaskType.DEVELOPMENT, environment)


def get_llm_recommendations() -> Dict[str, Dict[str, str]]:
    """
    Get comprehensive LLM recommendations for all tasks.
    
    Returns:
        Dictionary with task-specific LLM recommendations
    """
    return LLMStrategy.get_task_recommendations()
