"""
Enhanced error handling and fallback mechanisms for ArchMesh.

This module provides robust error handling, retry logic, and fallback mechanisms
for LLM operations and workflow execution.
"""

import asyncio
import random
from typing import Any, Callable, Dict, List, Optional, Type, Union
from functools import wraps
from loguru import logger
from enum import Enum

from app.config import settings


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message)
        self.severity = severity
        self.provider = provider
        self.model = model


class LLMTimeoutError(LLMError):
    """Exception for LLM timeout errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message, ErrorSeverity.HIGH, provider, model)


class LLMRateLimitError(LLMError):
    """Exception for LLM rate limit errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM, provider, model)


class LLMProviderError(LLMError):
    """Exception for LLM provider errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message, ErrorSeverity.HIGH, provider, model)


class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class FallbackConfig:
    """Configuration for fallback mechanisms."""
    
    def __init__(self, enable_provider_fallback: bool = True,
                 enable_model_fallback: bool = True,
                 fallback_providers: Optional[List[str]] = None,
                 fallback_models: Optional[Dict[str, List[str]]] = None):
        self.enable_provider_fallback = enable_provider_fallback
        self.enable_model_fallback = enable_model_fallback
        self.fallback_providers = fallback_providers or ["openai", "anthropic", "deepseek"]
        self.fallback_models = fallback_models or {
            "openai": ["gpt-4", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            "deepseek": ["deepseek-r1", "deepseek-coder", "deepseek-chat"]
        }


def calculate_retry_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for retry attempt with exponential backoff and jitter."""
    delay = min(
        config.base_delay * (config.exponential_base ** attempt),
        config.max_delay
    )
    
    if config.jitter:
        # Add random jitter to prevent thundering herd
        jitter_factor = random.uniform(0.5, 1.5)
        delay *= jitter_factor
    
    return delay


def is_retryable_error(error: Exception) -> bool:
    """Determine if an error is retryable."""
    retryable_errors = (
        LLMTimeoutError,
        LLMRateLimitError,
        ConnectionError,
        TimeoutError,
        asyncio.TimeoutError
    )
    
    # Check for specific error messages that indicate retryable conditions
    retryable_messages = [
        "timeout",
        "rate limit",
        "connection",
        "network",
        "temporary",
        "service unavailable",
        "internal server error"
    ]
    
    if isinstance(error, retryable_errors):
        return True
    
    error_message = str(error).lower()
    return any(msg in error_message for msg in retryable_messages)


def get_fallback_provider(current_provider: str, config: FallbackConfig) -> Optional[str]:
    """Get the next fallback provider."""
    if not config.enable_provider_fallback:
        return None
    
    try:
        current_index = config.fallback_providers.index(current_provider)
        if current_index < len(config.fallback_providers) - 1:
            return config.fallback_providers[current_index + 1]
    except ValueError:
        # Current provider not in fallback list, return first available
        return config.fallback_providers[0] if config.fallback_providers else None
    
    return None


def get_fallback_model(provider: str, current_model: str, config: FallbackConfig) -> Optional[str]:
    """Get the next fallback model for a provider."""
    if not config.enable_model_fallback:
        return None
    
    provider_models = config.fallback_models.get(provider, [])
    try:
        current_index = provider_models.index(current_model)
        if current_index < len(provider_models) - 1:
            return provider_models[current_index + 1]
    except ValueError:
        # Current model not in fallback list, return first available
        return provider_models[0] if provider_models else None
    
    return None


async def retry_with_fallback(
    func: Callable,
    *args,
    retry_config: Optional[RetryConfig] = None,
    fallback_config: Optional[FallbackConfig] = None,
    **kwargs
) -> Any:
    """
    Execute a function with retry logic and fallback mechanisms.
    
    Args:
        func: Function to execute
        *args: Function arguments
        retry_config: Retry configuration
        fallback_config: Fallback configuration
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Exception: If all retries and fallbacks fail
    """
    retry_config = retry_config or RetryConfig()
    fallback_config = fallback_config or FallbackConfig()
    
    last_error = None
    current_provider = kwargs.get('llm_provider', settings.default_llm_provider)
    current_model = kwargs.get('llm_model', settings.default_llm_model)
    
    # Try with current provider and model
    for attempt in range(retry_config.max_retries + 1):
        try:
            logger.info(f"Attempt {attempt + 1}/{retry_config.max_retries + 1} with provider: {current_provider}, model: {current_model}")
            
            # Update kwargs with current provider and model
            kwargs['llm_provider'] = current_provider
            kwargs['llm_model'] = current_model
            
            result = await func(*args, **kwargs)
            logger.info(f"Success with provider: {current_provider}, model: {current_model}")
            return result
            
        except Exception as error:
            last_error = error
            logger.warning(f"Attempt {attempt + 1} failed: {str(error)}")
            
            if not is_retryable_error(error):
                logger.error(f"Non-retryable error: {str(error)}")
                break
            
            if attempt < retry_config.max_retries:
                delay = calculate_retry_delay(attempt, retry_config)
                logger.info(f"Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.warning(f"All retries exhausted for provider: {current_provider}, model: {current_model}")
                break
    
    # Try fallback models within the same provider
    if fallback_config.enable_model_fallback:
        fallback_model = get_fallback_model(current_provider, current_model, fallback_config)
        if fallback_model and fallback_model != current_model:
            logger.info(f"Trying fallback model: {fallback_model} for provider: {current_provider}")
            try:
                kwargs['llm_model'] = fallback_model
                result = await func(*args, **kwargs)
                logger.info(f"Success with fallback model: {fallback_model}")
                return result
            except Exception as error:
                logger.warning(f"Fallback model failed: {str(error)}")
                last_error = error
    
    # Try fallback providers
    if fallback_config.enable_provider_fallback:
        fallback_provider = get_fallback_provider(current_provider, fallback_config)
        if fallback_provider and fallback_provider != current_provider:
            logger.info(f"Trying fallback provider: {fallback_provider}")
            try:
                kwargs['llm_provider'] = fallback_provider
                kwargs['llm_model'] = fallback_config.fallback_models.get(fallback_provider, [""])[0]
                result = await func(*args, **kwargs)
                logger.info(f"Success with fallback provider: {fallback_provider}")
                return result
            except Exception as error:
                logger.warning(f"Fallback provider failed: {str(error)}")
                last_error = error
    
    # All attempts failed
    logger.error(f"All retry and fallback attempts failed. Last error: {str(last_error)}")
    raise last_error


def with_error_handling(
    retry_config: Optional[RetryConfig] = None,
    fallback_config: Optional[FallbackConfig] = None,
    default_return: Optional[Any] = None
):
    """
    Decorator for adding error handling, retry logic, and fallback mechanisms.
    
    Args:
        retry_config: Retry configuration
        fallback_config: Fallback configuration
        default_return: Default return value if all attempts fail
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await retry_with_fallback(
                    func, *args, 
                    retry_config=retry_config,
                    fallback_config=fallback_config,
                    **kwargs
                )
            except Exception as error:
                logger.error(f"Function {func.__name__} failed after all retries and fallbacks: {str(error)}")
                if default_return is not None:
                    logger.info(f"Returning default value: {default_return}")
                    return default_return
                raise
        
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling and monitoring."""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_history: List[Dict[str, Any]] = []
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an error with context."""
        error_key = f"{type(error).__name__}:{str(error)[:100]}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        error_record = {
            "timestamp": asyncio.get_event_loop().time(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "severity": getattr(error, 'severity', ErrorSeverity.MEDIUM).value
        }
        
        self.error_history.append(error_record)
        
        # Keep only last 1000 errors
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        logger.error(f"Error logged: {error_record}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": len(self.error_history),
            "error_counts": self.error_counts,
            "recent_errors": self.error_history[-10:] if self.error_history else []
        }
    
    def should_circuit_break(self, error_type: str, threshold: int = 5) -> bool:
        """Check if circuit breaker should be activated."""
        return self.error_counts.get(error_type, 0) >= threshold


# Global error handler instance
error_handler = ErrorHandler()
