"""
Unit tests for error handling and fallback mechanisms.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.error_handling import (
    ErrorSeverity, LLMError, LLMTimeoutError, LLMRateLimitError, LLMProviderError,
    RetryConfig, FallbackConfig, calculate_retry_delay, is_retryable_error,
    get_fallback_provider, get_fallback_model, retry_with_fallback,
    with_error_handling, ErrorHandler
)


class TestErrorClasses:
    """Test cases for error classes."""
    
    def test_llm_error_creation(self):
        """Test LLM error creation."""
        error = LLMError("Test error", ErrorSeverity.HIGH, "openai", "gpt-4")
        
        assert str(error) == "Test error"
        assert error.severity == ErrorSeverity.HIGH
        assert error.provider == "openai"
        assert error.model == "gpt-4"
    
    def test_llm_timeout_error(self):
        """Test LLM timeout error."""
        error = LLMTimeoutError("Timeout", "deepseek", "deepseek-r1")
        
        assert str(error) == "Timeout"
        assert error.severity == ErrorSeverity.HIGH
        assert error.provider == "deepseek"
        assert error.model == "deepseek-r1"
    
    def test_llm_rate_limit_error(self):
        """Test LLM rate limit error."""
        error = LLMRateLimitError("Rate limited", "openai", "gpt-4")
        
        assert str(error) == "Rate limited"
        assert error.severity == ErrorSeverity.MEDIUM
        assert error.provider == "openai"
        assert error.model == "gpt-4"
    
    def test_llm_provider_error(self):
        """Test LLM provider error."""
        error = LLMProviderError("Provider error", "anthropic", "claude-3")
        
        assert str(error) == "Provider error"
        assert error.severity == ErrorSeverity.HIGH
        assert error.provider == "anthropic"
        assert error.model == "claude-3"


class TestRetryConfig:
    """Test cases for retry configuration."""
    
    def test_retry_config_defaults(self):
        """Test retry config default values."""
        config = RetryConfig()
        
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
    
    def test_retry_config_custom(self):
        """Test retry config with custom values."""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False
        )
        
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter is False


class TestFallbackConfig:
    """Test cases for fallback configuration."""
    
    def test_fallback_config_defaults(self):
        """Test fallback config default values."""
        config = FallbackConfig()
        
        assert config.enable_provider_fallback is True
        assert config.enable_model_fallback is True
        assert "openai" in config.fallback_providers
        assert "anthropic" in config.fallback_providers
        assert "deepseek" in config.fallback_providers
    
    def test_fallback_config_custom(self):
        """Test fallback config with custom values."""
        config = FallbackConfig(
            enable_provider_fallback=False,
            enable_model_fallback=True,
            fallback_providers=["openai", "anthropic"],
            fallback_models={
                "openai": ["gpt-4", "gpt-3.5-turbo"],
                "anthropic": ["claude-3"]
            }
        )
        
        assert config.enable_provider_fallback is False
        assert config.enable_model_fallback is True
        assert config.fallback_providers == ["openai", "anthropic"]
        assert config.fallback_models["openai"] == ["gpt-4", "gpt-3.5-turbo"]


class TestRetryDelay:
    """Test cases for retry delay calculation."""
    
    def test_calculate_retry_delay_no_jitter(self):
        """Test retry delay calculation without jitter."""
        config = RetryConfig(jitter=False, base_delay=1.0, exponential_base=2.0)
        
        # Test exponential backoff
        assert calculate_retry_delay(0, config) == 1.0
        assert calculate_retry_delay(1, config) == 2.0
        assert calculate_retry_delay(2, config) == 4.0
        assert calculate_retry_delay(3, config) == 8.0
    
    def test_calculate_retry_delay_with_jitter(self):
        """Test retry delay calculation with jitter."""
        config = RetryConfig(jitter=True, base_delay=1.0, exponential_base=2.0)
        
        # With jitter, we can't test exact values, but we can test ranges
        delay = calculate_retry_delay(0, config)
        assert 0.5 <= delay <= 1.5  # 1.0 * jitter_factor (0.5-1.5)
    
    def test_calculate_retry_delay_max_delay(self):
        """Test retry delay respects max delay."""
        config = RetryConfig(max_delay=5.0, base_delay=1.0, exponential_base=2.0, jitter=False)
        
        # Should cap at max_delay
        delay = calculate_retry_delay(10, config)
        assert delay <= 5.0


class TestRetryableError:
    """Test cases for retryable error detection."""
    
    def test_retryable_error_types(self):
        """Test that specific error types are retryable."""
        assert is_retryable_error(LLMTimeoutError("Timeout"))
        assert is_retryable_error(LLMRateLimitError("Rate limited"))
        assert is_retryable_error(ConnectionError("Connection failed"))
        assert is_retryable_error(TimeoutError("Timeout"))
        assert is_retryable_error(asyncio.TimeoutError())
    
    def test_retryable_error_messages(self):
        """Test that errors with retryable messages are detected."""
        assert is_retryable_error(Exception("Connection timeout"))
        assert is_retryable_error(Exception("Rate limit exceeded"))
        assert is_retryable_error(Exception("Network error"))
        assert is_retryable_error(Exception("Service unavailable"))
        assert is_retryable_error(Exception("Internal server error"))
    
    def test_non_retryable_errors(self):
        """Test that non-retryable errors are not detected as retryable."""
        assert not is_retryable_error(Exception("Invalid input"))
        assert not is_retryable_error(Exception("Authentication failed"))
        assert not is_retryable_error(Exception("Permission denied"))


class TestFallbackProvider:
    """Test cases for fallback provider selection."""
    
    def test_get_fallback_provider_next(self):
        """Test getting next fallback provider."""
        config = FallbackConfig(fallback_providers=["openai", "anthropic", "deepseek"])
        
        assert get_fallback_provider("openai", config) == "anthropic"
        assert get_fallback_provider("anthropic", config) == "deepseek"
        assert get_fallback_provider("deepseek", config) is None  # Last in list
    
    def test_get_fallback_provider_disabled(self):
        """Test fallback provider when disabled."""
        config = FallbackConfig(enable_provider_fallback=False)
        
        assert get_fallback_provider("openai", config) is None
    
    def test_get_fallback_provider_unknown(self):
        """Test fallback provider for unknown provider."""
        config = FallbackConfig(fallback_providers=["openai", "anthropic"])
        
        assert get_fallback_provider("unknown", config) == "openai"  # First available


class TestFallbackModel:
    """Test cases for fallback model selection."""
    
    def test_get_fallback_model_next(self):
        """Test getting next fallback model."""
        config = FallbackConfig(fallback_models={
            "openai": ["gpt-4", "gpt-3.5-turbo"],
            "anthropic": ["claude-3", "claude-2"]
        })
        
        assert get_fallback_model("openai", "gpt-4", config) == "gpt-3.5-turbo"
        assert get_fallback_model("anthropic", "claude-3", config) == "claude-2"
        assert get_fallback_model("openai", "gpt-3.5-turbo", config) is None  # Last in list
    
    def test_get_fallback_model_disabled(self):
        """Test fallback model when disabled."""
        config = FallbackConfig(enable_model_fallback=False)
        
        assert get_fallback_model("openai", "gpt-4", config) is None
    
    def test_get_fallback_model_unknown(self):
        """Test fallback model for unknown model."""
        config = FallbackConfig(fallback_models={"openai": ["gpt-4", "gpt-3.5-turbo"]})
        
        assert get_fallback_model("openai", "unknown", config) == "gpt-4"  # First available


class TestRetryWithFallback:
    """Test cases for retry with fallback mechanism."""
    
    @pytest.mark.asyncio
    async def test_retry_with_fallback_success_first_attempt(self):
        """Test successful execution on first attempt."""
        async def mock_func(*args, **kwargs):
            return "success"
        
        result = await retry_with_fallback(mock_func, "arg1", "arg2")
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_with_fallback_success_after_retry(self):
        """Test successful execution after retry."""
        call_count = 0
        
        async def mock_func(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise LLMTimeoutError("Timeout")
            return "success"
        
        config = RetryConfig(max_retries=3, base_delay=0.01)  # Fast retry for testing
        result = await retry_with_fallback(mock_func, retry_config=config)
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_with_fallback_provider_fallback(self):
        """Test fallback to different provider."""
        call_count = 0
        
        async def mock_func(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            provider = kwargs.get('llm_provider', 'unknown')
            if provider == 'deepseek':
                raise LLMProviderError("Provider error", "deepseek", "deepseek-r1")
            return f"success with {provider}"
        
        config = FallbackConfig(fallback_providers=["deepseek", "openai"], enable_model_fallback=False)
        result = await retry_with_fallback(
            mock_func, 
            retry_config=RetryConfig(max_retries=1, base_delay=0.01),
            fallback_config=config,
            llm_provider="deepseek"
        )
        
        assert result == "success with openai"
        assert call_count == 2  # One failed attempt, one successful fallback
    
    @pytest.mark.asyncio
    async def test_retry_with_fallback_all_fail(self):
        """Test when all retries and fallbacks fail."""
        async def mock_func(*args, **kwargs):
            raise LLMProviderError("Persistent error")
        
        config = RetryConfig(max_retries=1, base_delay=0.01)
        fallback_config = FallbackConfig(fallback_providers=["deepseek"])
        
        with pytest.raises(LLMProviderError):
            await retry_with_fallback(
                mock_func,
                retry_config=config,
                fallback_config=fallback_config
            )


class TestErrorHandler:
    """Test cases for error handler."""
    
    def test_error_handler_initialization(self):
        """Test error handler initialization."""
        handler = ErrorHandler()
        
        assert handler.error_counts == {}
        assert handler.error_history == []
    
    def test_log_error(self):
        """Test error logging."""
        handler = ErrorHandler()
        error = LLMTimeoutError("Test timeout", "deepseek", "deepseek-r1")
        context = {"agent_type": "test_agent"}
        
        handler.log_error(error, context)
        
        assert len(handler.error_counts) == 1
        assert len(handler.error_history) == 1
        
        error_record = handler.error_history[0]
        assert error_record["error_type"] == "LLMTimeoutError"
        assert error_record["error_message"] == "Test timeout"
        assert error_record["context"] == context
        assert error_record["severity"] == "high"
    
    def test_get_error_stats(self):
        """Test getting error statistics."""
        handler = ErrorHandler()
        
        # Log some errors
        handler.log_error(LLMTimeoutError("Timeout 1"))
        handler.log_error(LLMTimeoutError("Timeout 2"))
        handler.log_error(LLMProviderError("Provider error"))
        
        stats = handler.get_error_stats()
        
        assert stats["total_errors"] == 3
        assert len(stats["error_counts"]) == 3  # Three unique error messages
        assert len(stats["recent_errors"]) == 3
    
    def test_circuit_breaker(self):
        """Test circuit breaker functionality."""
        handler = ErrorHandler()
        
        # Should not break initially
        assert not handler.should_circuit_break("LLMTimeoutError:Timeout 0")
        
        # Log errors up to threshold
        for i in range(5):
            handler.log_error(LLMTimeoutError(f"Timeout {i}"))
        
        # Should break after threshold (checking for specific error key)
        assert handler.should_circuit_break("LLMTimeoutError:Timeout 0", threshold=1)
        assert not handler.should_circuit_break("LLMTimeoutError", threshold=6)


class TestErrorHandlingDecorator:
    """Test cases for error handling decorator."""
    
    @pytest.mark.asyncio
    async def test_with_error_handling_success(self):
        """Test decorator with successful execution."""
        @with_error_handling()
        async def mock_func(**kwargs):
            return "success"
        
        result = await mock_func()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_with_error_handling_default_return(self):
        """Test decorator with default return value."""
        @with_error_handling(default_return="default")
        async def mock_func():
            raise Exception("Error")
        
        result = await mock_func()
        assert result == "default"
    
    @pytest.mark.asyncio
    async def test_with_error_handling_raise_error(self):
        """Test decorator raises error when no default return."""
        @with_error_handling()
        async def mock_func():
            raise Exception("Error")
        
        with pytest.raises(Exception):
            await mock_func()
