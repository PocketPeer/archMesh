"""
Base agent class for all AI agents in ArchMesh.

This module provides a comprehensive base class that all AI agents inherit from,
including LLM initialization, execution tracking, cost calculation, and error handling.
"""

import asyncio
import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import httpx
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deepseek_client import ChatDeepSeek
from app.core.error_handling import (
    with_error_handling, RetryConfig, FallbackConfig, 
    LLMError, LLMTimeoutError, LLMProviderError, error_handler
)
from app.models.agent_execution import AgentExecution, AgentExecutionStatus


class BaseAgent(ABC):
    """
    Base class for all AI agents in ArchMesh.
    
    Provides:
    - LLM initialization (OpenAI, Anthropic)
    - Execution tracking and logging
    - Cost calculation per model
    - Error handling with exponential backoff retries
    - Structured output parsing
    - Token counting and usage tracking
    """

    # Model pricing per 1K tokens (as of 2024)
    MODEL_PRICING = {
        # OpenAI models
        "gpt-4o": {"prompt": 0.005, "completion": 0.015},
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
        
        # Anthropic models
        "claude-3-5-sonnet-20241022": {"prompt": 0.003, "completion": 0.015},
        "claude-3-5-haiku-20241022": {"prompt": 0.0008, "completion": 0.004},
        "claude-3-opus-20240229": {"prompt": 0.015, "completion": 0.075},
        "claude-3-sonnet-20240229": {"prompt": 0.003, "completion": 0.015},
        "claude-3-haiku-20240307": {"prompt": 0.00025, "completion": 0.00125},
        
        # DeepSeek models (local - no cost)
        "deepseek-r1": {"prompt": 0.0, "completion": 0.0},
        "deepseek-coder": {"prompt": 0.0, "completion": 0.0},
        "deepseek-chat": {"prompt": 0.0, "completion": 0.0},
    }

    def __init__(
        self,
        agent_type: str,
        agent_version: str = "1.0.0",
        llm_provider: str = "deepseek",
        llm_model: str = "deepseek-r1",
        temperature: float = 0.7,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize base agent.
        
        Args:
            agent_type: Type of agent (e.g., "document_analyzer", "requirement_extractor")
            agent_version: Version of the agent
            llm_provider: LLM provider ("openai" or "anthropic")
            llm_model: Specific model to use
            temperature: LLM temperature setting
            max_retries: Maximum number of retry attempts
            timeout_seconds: Request timeout in seconds
            max_tokens: Maximum tokens for completion
        """
        self.agent_type = agent_type
        self.agent_version = agent_version
        self.llm_provider = llm_provider.lower()
        self.llm_model = llm_model
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Execution tracking
        self.current_execution_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        
        logger.info(
            f"Initialized {agent_type} agent",
            extra={
                "agent_type": agent_type,
                "agent_version": agent_version,
                "llm_provider": llm_provider,
                "llm_model": llm_model,
                "temperature": temperature,
            }
        )

    def _initialize_llm(self) -> Union[ChatOpenAI, ChatAnthropic, ChatDeepSeek]:
        """
        Initialize LLM based on provider.
        
        Returns:
            Initialized LLM instance
            
        Raises:
            ValueError: If provider is not supported
        """
        try:
            from app.config import settings
            
            # Prepare common parameters
            llm_params = {
                "model": self.llm_model,
                "temperature": self.temperature,
                "timeout": self.timeout_seconds,
            }
            
            # Only add max_tokens if it's not None
            if self.max_tokens is not None:
                llm_params["max_tokens"] = self.max_tokens
            
            if self.llm_provider == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not found in environment variables")
                llm_params["api_key"] = settings.openai_api_key
                return ChatOpenAI(**llm_params)
            elif self.llm_provider == "anthropic":
                if not settings.anthropic_api_key:
                    raise ValueError("Anthropic API key not found in environment variables")
                llm_params["api_key"] = settings.anthropic_api_key
                return ChatAnthropic(**llm_params)
            elif self.llm_provider == "deepseek":
                # Use DeepSeek local client
                llm_params["base_url"] = settings.deepseek_base_url
                llm_params["model"] = settings.deepseek_model
                return ChatDeepSeek(**llm_params)
            elif self.llm_provider == "ollama":
                # Use Ollama for fast local models
                llm_params["base_url"] = settings.ollama_base_url
                llm_params["model"] = self.llm_model
                return ChatDeepSeek(**llm_params)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
                
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {str(e)}",
                extra={
                    "provider": self.llm_provider,
                    "model": self.llm_model,
                    "error": str(e),
                }
            )
            raise

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        
        Must be implemented by subclasses.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Dictionary containing the agent's output
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement execute method")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the agent's system prompt.
        
        Must be implemented by subclasses.
        
        Returns:
            System prompt string
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement get_system_prompt method")

    @with_error_handling(
        retry_config=RetryConfig(max_retries=3, base_delay=1.0, max_delay=30.0),
        fallback_config=FallbackConfig(enable_provider_fallback=True, enable_model_fallback=True)
    )
    async def _call_llm(
        self,
        messages: List[Union[SystemMessage, HumanMessage, AIMessage]],
        **kwargs
    ) -> str:
        """
        Call LLM with enhanced error handling, retry logic, and fallback mechanisms.
        
        Args:
            messages: List of messages to send to LLM
            **kwargs: Additional arguments for LLM call
            
        Returns:
            LLM response text
            
        Raises:
            Exception: If all retry attempts and fallbacks fail
        """
        try:
            logger.debug(
                f"LLM call with provider: {self.llm_provider}, model: {self.llm_model}",
                extra={
                    "agent_type": self.agent_type,
                    "provider": self.llm_provider,
                    "model": self.llm_model,
                }
            )
            
            # Make the LLM call with timeout
            response = await asyncio.wait_for(
                self.llm.ainvoke(messages, **kwargs),
                timeout=self.timeout_seconds
            )
            
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            logger.debug(
                f"LLM call successful",
                extra={
                    "agent_type": self.agent_type,
                    "provider": self.llm_provider,
                    "model": self.llm_model,
                    "response_length": len(content),
                }
            )
            
            # Debug: Log the actual response for troubleshooting
            logger.debug(f"LLM Response: {content[:1000]}...")
            
            return content
            
        except asyncio.TimeoutError as e:
            error_handler.log_error(
                LLMTimeoutError(f"LLM call timed out after {self.timeout_seconds}s", self.llm_provider, self.llm_model),
                {"agent_type": self.agent_type, "timeout": self.timeout_seconds}
            )
            raise LLMTimeoutError(f"LLM call timed out after {self.timeout_seconds}s", self.llm_provider, self.llm_model)
        
        except Exception as e:
            error_handler.log_error(
                LLMProviderError(f"LLM call failed: {str(e)}", self.llm_provider, self.llm_model),
                {"agent_type": self.agent_type, "error": str(e)}
            )
            raise LLMProviderError(f"LLM call failed: {str(e)}", self.llm_provider, self.llm_model)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling markdown code blocks and malformed JSON.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            ValueError: If JSON parsing fails
        """
        logger.debug(f"Parsing JSON response: {response[:200]}...")
        
        try:
            # First, try to parse as-is
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parsing failed: {e}")
        
        # Try to extract JSON from markdown code blocks
        json_patterns = [
            r'```json\s*\n(.*?)\n```',  # ```json ... ```
            r'```\s*\n(.*?)\n```',      # ``` ... ```
            r'`([^`]+)`',               # `...`
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON-like content in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON at the beginning of the response
        lines = response.strip().split('\n')
        json_start = -1
        json_end = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start >= 0:
            # Find the matching closing brace
            brace_count = 0
            for i in range(json_start, len(lines)):
                line = lines[i].strip()
                for char in line:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i
                            break
                if json_end >= 0:
                    break
            
            if json_end >= 0:
                json_lines = lines[json_start:json_end + 1]
                json_text = '\n'.join(json_lines)
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass
        
        # Try to fix common JSON issues
        try:
            # Remove any trailing commas or incomplete structures
            cleaned_response = response.strip()
            
            # Try to find the last complete JSON object
            brace_count = 0
            last_brace = -1
            for i, char in enumerate(cleaned_response):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        last_brace = i
                        break
            
            if last_brace > 0:
                json_part = cleaned_response[:last_brace + 1]
                try:
                    return json.loads(json_part)
                except json.JSONDecodeError:
                    pass
            
            # Try to fix incomplete JSON by adding missing closing braces
            if cleaned_response.count('{') > cleaned_response.count('}'):
                missing_braces = cleaned_response.count('{') - cleaned_response.count('}')
                fixed_response = cleaned_response + '}' * missing_braces
                try:
                    return json.loads(fixed_response)
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            logger.warning(f"JSON repair attempt failed: {e}")
        
        # If all else fails, raise an error with more context
        logger.error(f"Could not parse JSON from response. Response length: {len(response)}")
        logger.error(f"Response content: {response[:1000]}...")
        raise ValueError(f"Could not parse JSON from response. Response: {response[:500]}...")

    async def log_execution(
        self,
        session_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        duration: float,
        tokens_used: Dict[str, int],
        status: str,
        error: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> str:
        """
        Log execution to database.
        
        Args:
            session_id: Workflow session ID
            input_data: Input data for the execution
            output_data: Output data from the execution
            duration: Execution duration in seconds
            tokens_used: Dictionary with 'prompt_tokens' and 'completion_tokens'
            status: Execution status ('success', 'failure', 'timeout')
            error: Error message if execution failed
            db: Database session (optional, will create if not provided)
            
        Returns:
            Execution ID
        """
        execution_id = str(uuid4())
        
        try:
            # Calculate cost
            cost_usd = self.calculate_cost(
                tokens_used.get('prompt_tokens', 0),
                tokens_used.get('completion_tokens', 0)
            )
            
            # Create execution record
            execution = AgentExecution(
                id=execution_id,
                session_id=session_id,
                agent_type=self.agent_type,
                agent_version=self.agent_version,
                input_data=input_data,
                output_data=output_data,
                llm_provider=self.llm_provider,
                llm_model=self.llm_model,
                prompt_tokens=tokens_used.get('prompt_tokens'),
                completion_tokens=tokens_used.get('completion_tokens'),
                cost_usd=cost_usd,
                duration_seconds=duration,
                status=AgentExecutionStatus(status),
                error_message=error,
                started_at=self.start_time or datetime.utcnow(),
                completed_at=datetime.utcnow()
            )
            
            # Use provided db session or create new one
            if db:
                db.add(execution)
                await db.commit()
            else:
                async with get_db() as db_session:
                    db_session.add(execution)
                    await db_session.commit()
            
            logger.info(
                f"Logged agent execution: {execution_id}",
                extra={
                    "execution_id": execution_id,
                    "agent_type": self.agent_type,
                    "session_id": session_id,
                    "status": status,
                    "duration": duration,
                    "cost_usd": cost_usd,
                    "tokens_used": tokens_used,
                }
            )
            
            return execution_id
            
        except Exception as e:
            logger.error(
                f"Failed to log execution: {str(e)}",
                extra={
                    "execution_id": execution_id,
                    "agent_type": self.agent_type,
                    "session_id": session_id,
                    "error": str(e),
                }
            )
            raise

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate cost based on tokens and model.
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            
        Returns:
            Cost in USD
        """
        if self.llm_model not in self.MODEL_PRICING:
            logger.warning(
                f"Unknown model pricing for {self.llm_model}, using default rates",
                extra={"model": self.llm_model}
            )
            # Default pricing (roughly GPT-4 rates)
            prompt_cost = 0.03 / 1000
            completion_cost = 0.06 / 1000
        else:
            pricing = self.MODEL_PRICING[self.llm_model]
            prompt_cost = pricing["prompt"] / 1000
            completion_cost = pricing["completion"] / 1000
        
        total_cost = (prompt_tokens * prompt_cost) + (completion_tokens * completion_cost)
        
        logger.debug(
            f"Calculated cost: ${total_cost:.6f}",
            extra={
                "model": self.llm_model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "prompt_cost_per_1k": prompt_cost * 1000,
                "completion_cost_per_1k": completion_cost * 1000,
                "total_cost": total_cost,
            }
        )
        
        return round(total_cost, 6)

    async def _execute_with_tracking(
        self,
        session_id: str,
        input_data: Dict[str, Any],
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Execute agent with full tracking and logging.
        
        Args:
            session_id: Workflow session ID
            input_data: Input data for the agent
            db: Database session (optional)
            
        Returns:
            Agent output data
        """
        self.current_execution_id = str(uuid4())
        self.start_time = datetime.utcnow()
        
        try:
            logger.info(
                f"Starting agent execution: {self.current_execution_id}",
                extra={
                    "execution_id": self.current_execution_id,
                    "agent_type": self.agent_type,
                    "session_id": session_id,
                }
            )
            
            # Execute the agent
            output_data = await self.execute(input_data)
            
            # Calculate duration
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            
            # Estimate token usage (this is approximate)
            # In a real implementation, you'd get actual token counts from the LLM
            estimated_tokens = self._estimate_tokens(input_data, output_data)
            
            # Log successful execution
            await self.log_execution(
                session_id=session_id,
                input_data=input_data,
                output_data=output_data,
                duration=duration,
                tokens_used=estimated_tokens,
                status="success",
                db=db
            )
            
            logger.info(
                f"Agent execution completed successfully: {self.current_execution_id}",
                extra={
                    "execution_id": self.current_execution_id,
                    "agent_type": self.agent_type,
                    "session_id": session_id,
                    "duration": duration,
                }
            )
            
            return output_data
            
        except Exception as e:
            # Calculate duration
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            
            # Log failed execution
            await self.log_execution(
                session_id=session_id,
                input_data=input_data,
                output_data={},
                duration=duration,
                tokens_used={"prompt_tokens": 0, "completion_tokens": 0},
                status="failure",
                error=str(e),
                db=db
            )
            
            logger.error(
                f"Agent execution failed: {self.current_execution_id}",
                extra={
                    "execution_id": self.current_execution_id,
                    "agent_type": self.agent_type,
                    "session_id": session_id,
                    "duration": duration,
                    "error": str(e),
                }
            )
            
            raise

    def _estimate_tokens(self, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Estimate token usage for input and output data.
        
        This is a rough estimation. In production, you'd want to use
        the actual token counts from the LLM response.
        
        Args:
            input_data: Input data
            output_data: Output data
            
        Returns:
            Dictionary with estimated token counts
        """
        # Rough estimation: 1 token ≈ 4 characters for English text
        input_text = json.dumps(input_data, separators=(',', ':'))
        output_text = json.dumps(output_data, separators=(',', ':'))
        
        prompt_tokens = max(1, len(input_text) // 4)
        completion_tokens = max(1, len(output_text) // 4)
        
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information.
        
        Returns:
            Dictionary with agent metadata
        """
        return {
            "agent_type": self.agent_type,
            "agent_version": self.agent_version,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "temperature": self.temperature,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "max_tokens": self.max_tokens,
        }
