"""
DeepSeek LLM client for local model integration.

This module provides a client for interacting with local DeepSeek models
via Ollama or similar local LLM servers.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from loguru import logger


class DeepSeekClient:
    """
    Client for interacting with local DeepSeek models.
    
    Supports both Ollama and OpenAI-compatible API endpoints.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "deepseek-r1",
        timeout: int = 300,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize DeepSeek client.
        
        Args:
            base_url: Base URL for the local LLM server
            model: Model name to use
            timeout: Request timeout in seconds
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Determine if this is an Ollama server or OpenAI-compatible
        self.is_ollama = "11434" in base_url or "ollama" in base_url.lower()
        
    async def _make_request(
        self, 
        endpoint: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make HTTP request to the local LLM server.
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            
        Returns:
            Response data
            
        Raises:
            httpx.HTTPError: If request fails
        """
        url = urljoin(self.base_url, endpoint)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling DeepSeek API: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error calling DeepSeek API: {e}")
                raise
    
    def _format_messages_for_ollama(self, messages: List[BaseMessage]) -> str:
        """
        Format messages for Ollama API.
        
        Args:
            messages: List of messages
            
        Returns:
            Formatted prompt string
        """
        formatted_parts = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                formatted_parts.append(f"System: {message.content}")
            elif isinstance(message, HumanMessage):
                formatted_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                formatted_parts.append(f"Assistant: {message.content}")
        
        return "\n\n".join(formatted_parts)
    
    def _format_messages_for_openai(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """
        Format messages for OpenAI-compatible API.
        
        Args:
            messages: List of messages
            
        Returns:
            Formatted messages list
        """
        formatted_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                formatted_messages.append({"role": "system", "content": message.content})
            elif isinstance(message, HumanMessage):
                formatted_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                formatted_messages.append({"role": "assistant", "content": message.content})
        
        return formatted_messages
    
    async def generate(
        self, 
        messages: List[BaseMessage],
        **kwargs
    ) -> AIMessage:
        """
        Generate response from DeepSeek model.
        
        Args:
            messages: List of input messages
            **kwargs: Additional parameters
            
        Returns:
            AI response message
            
        Raises:
            Exception: If generation fails
        """
        try:
            if self.is_ollama:
                return await self._generate_ollama(messages, **kwargs)
            else:
                return await self._generate_openai_compatible(messages, **kwargs)
        except Exception as e:
            logger.error(f"Failed to generate response from DeepSeek: {e}")
            raise
    
    async def _generate_ollama(
        self, 
        messages: List[BaseMessage],
        **kwargs
    ) -> AIMessage:
        """
        Generate response using Ollama API.
        
        Args:
            messages: List of input messages
            **kwargs: Additional parameters
            
        Returns:
            AI response message
        """
        prompt = self._format_messages_for_ollama(messages)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
            }
        }
        
        if self.max_tokens:
            payload["options"]["num_predict"] = self.max_tokens
        
        response = await self._make_request("/api/generate", payload)
        
        if "response" not in response:
            raise ValueError("Invalid response from Ollama API")
        
        return AIMessage(content=response["response"])
    
    async def _generate_openai_compatible(
        self, 
        messages: List[BaseMessage],
        **kwargs
    ) -> AIMessage:
        """
        Generate response using OpenAI-compatible API.
        
        Args:
            messages: List of input messages
            **kwargs: Additional parameters
            
        Returns:
            AI response message
        """
        formatted_messages = self._format_messages_for_openai(messages)
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": False,
        }
        
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
        
        response = await self._make_request("/v1/chat/completions", payload)
        
        if "choices" not in response or not response["choices"]:
            raise ValueError("Invalid response from OpenAI-compatible API")
        
        content = response["choices"][0]["message"]["content"]
        return AIMessage(content=content)
    
    async def health_check(self) -> bool:
        """
        Check if the DeepSeek server is healthy.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            if self.is_ollama:
                # Check Ollama health
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(f"{self.base_url}/api/tags")
                    return response.status_code == 200
            else:
                # Check OpenAI-compatible health
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(f"{self.base_url}/v1/models")
                    return response.status_code == 200
        except Exception as e:
            logger.warning(f"DeepSeek health check failed: {e}")
            return False


class ChatDeepSeek:
    """
    LangChain-compatible wrapper for DeepSeek client.
    
    This class provides a LangChain-compatible interface for the DeepSeek client,
    allowing it to be used as a drop-in replacement for other LLM providers.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "deepseek-r1",
        temperature: float = 0.7,
        timeout: int = 300,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize ChatDeepSeek.
        
        Args:
            base_url: Base URL for the local LLM server
            model: Model name to use
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            max_tokens: Maximum tokens to generate
        """
        self.client = DeepSeekClient(
            base_url=base_url,
            model=model,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.max_tokens = max_tokens
    
    async def agenerate(
        self, 
        messages: List[List[BaseMessage]], 
        **kwargs
    ) -> List[AIMessage]:
        """
        Async generate method compatible with LangChain.
        
        Args:
            messages: List of message lists
            **kwargs: Additional parameters
            
        Returns:
            List of AI response messages
        """
        results = []
        for message_list in messages:
            result = await self.client.generate(message_list, **kwargs)
            results.append(result)
        return results
    
    def generate(
        self, 
        messages: List[List[BaseMessage]], 
        **kwargs
    ) -> List[AIMessage]:
        """
        Sync generate method compatible with LangChain.
        
        Args:
            messages: List of message lists
            **kwargs: Additional parameters
            
        Returns:
            List of AI response messages
        """
        return asyncio.run(self.agenerate(messages, **kwargs))
    
    async def ainvoke(
        self, 
        messages: Union[List[BaseMessage], str], 
        **kwargs
    ) -> AIMessage:
        """
        Async invoke method compatible with LangChain.
        
        Args:
            messages: Messages or prompt string
            **kwargs: Additional parameters
            
        Returns:
            AI response message
        """
        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]
        
        return await self.client.generate(messages, **kwargs)
    
    def invoke(
        self, 
        messages: Union[List[BaseMessage], str], 
        **kwargs
    ) -> AIMessage:
        """
        Sync invoke method compatible with LangChain.
        
        Args:
            messages: Messages or prompt string
            **kwargs: Additional parameters
            
        Returns:
            AI response message
        """
        return asyncio.run(self.ainvoke(messages, **kwargs))
