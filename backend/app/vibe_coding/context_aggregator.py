"""
Context Aggregator for Vibe Coding Tool

This module provides context aggregation capabilities for the Vibe Coding Tool.
It gathers and unifies context from various sources to provide comprehensive
information for code generation.

Features:
- Multi-source context gathering (project structure, existing code, documentation, dependencies)
- Context quality assessment and filtering
- Context deduplication and prioritization
- Performance optimization with caching
- Comprehensive error handling and recovery
- Configurable context sources and quality thresholds

Author: ArchMesh Team
Version: 1.0.0
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from app.vibe_coding.models import (
    UnifiedContext, ParsedIntent, ContextSource, 
    ContextAggregationRequest, ContextAggregationResponse
)
from app.core.exceptions import ContextGatherError, VibeCodingError
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContextAggregatorConfig:
    """Configuration for Context Aggregator"""
    max_context_sources: int = 10
    context_timeout: int = 30
    enable_caching: bool = True
    cache_size: int = 50
    quality_threshold: float = 0.7
    max_context_length: int = 5000
    
    def __post_init__(self):
        """Validate configuration values"""
        if self.max_context_sources <= 0:
            raise ValueError("Invalid configuration: max_context_sources must be positive")
        if self.context_timeout <= 0:
            raise ValueError("Invalid configuration: context_timeout must be positive")
        if not 0.0 <= self.quality_threshold <= 1.0:
            raise ValueError("Invalid configuration: quality_threshold must be between 0.0 and 1.0")
        if self.max_context_length <= 0:
            raise ValueError("Invalid configuration: max_context_length must be positive")


class ContextAggregator:
    """
    Context Aggregator for gathering and unifying context from multiple sources.
    
    This class provides comprehensive context aggregation capabilities with:
    - Multi-source context gathering (project, code, docs, dependencies)
    - Context quality assessment and filtering
    - Context deduplication and prioritization
    - Performance optimization with caching
    - Comprehensive error handling and recovery
    """
    
    def __init__(self, config: Optional[ContextAggregatorConfig] = None):
        """
        Initialize Context Aggregator with configuration.
        
        Args:
            config: Optional configuration for the aggregator
        """
        # Initialize configuration
        self.config = config or ContextAggregatorConfig()
        
        # Initialize performance tracking
        self._aggregation_stats = {
            "total_aggregations": 0,
            "successful_aggregations": 0,
            "failed_aggregations": 0,
            "average_aggregation_time": 0.0
        }
        
        # Initialize cache
        self._cache = {}
        
        logger.info(f"Initialized Context Aggregator with config: {self.config}")
    
    async def aggregate_context(self, intent: ParsedIntent) -> UnifiedContext:
        """
        Aggregate context from multiple sources for the given intent.
        
        Args:
            intent: Parsed intent for context gathering
            
        Returns:
            UnifiedContext: Aggregated and unified context
            
        Raises:
            ContextGatherError: If context aggregation fails
        """
        start_time = time.time()
        self._aggregation_stats["total_aggregations"] += 1
        
        try:
            # Validate intent
            self._validate_intent(intent)
            
            # Check cache first (if enabled)
            if self.config.enable_caching:
                cached_result = self._get_cached_result(intent)
                if cached_result:
                    logger.debug(f"Cache hit for intent: {intent.action} {intent.target}")
                    return cached_result
            
            # Gather context from all sources
            context_sources = await self._gather_all_context_sources(intent)
            
            # Unify and process context
            unified_context = self._unify_context(intent, context_sources)
            
            # Cache result (if enabled)
            if self.config.enable_caching:
                self._cache_result(intent, unified_context)
            
            # Update performance stats
            aggregation_time = time.time() - start_time
            self._update_performance_stats(aggregation_time, success=True)
            
            logger.info(f"Successfully aggregated context for {intent.action} {intent.target} (took {aggregation_time:.2f}s)")
            return unified_context
            
        except Exception as e:
            # Update performance stats
            aggregation_time = time.time() - start_time
            self._update_performance_stats(aggregation_time, success=False)
            
            logger.error(f"Failed to aggregate context: {str(e)} (took {aggregation_time:.2f}s)")
            if isinstance(e, ContextGatherError):
                raise
            else:
                raise ContextGatherError(f"Context aggregation failed: {str(e)}")
    
    async def _gather_all_context_sources(self, intent: ParsedIntent) -> Dict[str, Any]:
        """
        Gather context from all available sources.
        
        Args:
            intent: Parsed intent for context gathering
            
        Returns:
            Dict containing context from all sources
        """
        context_sources = {}
        
        # Define context gathering tasks
        tasks = [
            self._gather_project_context(intent),
            self._gather_code_context(intent),
            self._gather_documentation_context(intent),
            self._gather_dependency_context(intent)
        ]
        
        # Execute all tasks with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.context_timeout
            )
            
            # Process results
            source_names = ["project_structure", "existing_code", "documentation", "dependencies"]
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Failed to gather context from {source_names[i]}: {result}")
                    context_sources[source_names[i]] = {}
                else:
                    context_sources[source_names[i]] = result
            
        except asyncio.TimeoutError:
            raise ContextGatherError("Context aggregation timeout")
        
        return context_sources
    
    async def _gather_project_context(self, intent: ParsedIntent) -> Dict[str, Any]:
        """
        Gather project structure context.
        
        Args:
            intent: Parsed intent for context gathering
            
        Returns:
            Dict containing project structure context
        """
        # Mock implementation for now
        # In production, this would analyze the actual project structure
        return {
            "files": ["app/main.py", "app/models/user.py", "app/auth/"],
            "frameworks": ["fastapi", "sqlalchemy"],
            "patterns": ["repository", "service layer"],
            "architecture": "layered",
            "language": intent.language,
            "framework": intent.framework
        }
    
    async def _gather_code_context(self, intent: ParsedIntent) -> Dict[str, Any]:
        """
        Gather existing code context.
        
        Args:
            intent: Parsed intent for context gathering
            
        Returns:
            Dict containing existing code context
        """
        # Mock implementation for now
        # In production, this would analyze existing code patterns
        return {
            "similar_endpoints": [
                {"path": "/api/v1/users", "method": "GET", "auth_required": True},
                {"path": "/api/v1/profile", "method": "PUT", "auth_required": True}
            ],
            "auth_patterns": ["JWT", "OAuth2", "session-based"],
            "code_patterns": ["dependency injection", "async/await"],
            "similar_functions": []
        }
    
    async def _gather_documentation_context(self, intent: ParsedIntent) -> Dict[str, Any]:
        """
        Gather documentation context.
        
        Args:
            intent: Parsed intent for context gathering
            
        Returns:
            Dict containing documentation context
        """
        # Mock implementation for now
        # In production, this would search documentation and examples
        return {
            "api_docs": "FastAPI authentication guide",
            "examples": ["JWT implementation", "OAuth2 setup"],
            "best_practices": ["secure endpoints", "token validation"],
            "tutorials": ["FastAPI authentication tutorial"],
            "references": ["FastAPI docs", "JWT RFC"]
        }
    
    async def _gather_dependency_context(self, intent: ParsedIntent) -> Dict[str, Any]:
        """
        Gather dependency context.
        
        Args:
            intent: Parsed intent for context gathering
            
        Returns:
            Dict containing dependency context
        """
        # Mock implementation for now
        # In production, this would analyze package.json, requirements.txt, etc.
        return {
            "installed_packages": ["fastapi", "python-jose", "passlib"],
            "version_constraints": ["fastapi>=0.68.0", "python-jose>=3.3.0"],
            "compatible_versions": ["fastapi==0.104.1", "python-jose==3.3.0"],
            "missing_packages": [],
            "conflicts": []
        }
    
    def _unify_context(self, intent: ParsedIntent, context_sources: Dict[str, Any]) -> UnifiedContext:
        """
        Unify context from multiple sources into a single UnifiedContext object.
        
        Args:
            intent: Parsed intent
            context_sources: Context from all sources
            
        Returns:
            UnifiedContext: Unified context object
        """
        # Filter and prioritize context
        filtered_context = self._filter_context(context_sources)
        
        # Deduplicate context
        deduplicated_context = self._deduplicate_context(filtered_context)
        
        # Assess quality
        quality_score = self._assess_context_quality(deduplicated_context, intent)
        
        # Truncate if too long
        if len(str(deduplicated_context)) > self.config.max_context_length:
            deduplicated_context = self._truncate_context(deduplicated_context)
        
        # Create UnifiedContext
        unified_context = UnifiedContext(
            intent=intent,
            project_structure=deduplicated_context.get("project_structure", {}),
            existing_code=deduplicated_context.get("existing_code", {}),
            documentation=deduplicated_context.get("documentation", {}),
            dependencies=deduplicated_context.get("dependencies", {}),
            quality_score=quality_score,
            timestamp=datetime.utcnow()
        )
        
        return unified_context
    
    def _filter_context(self, context_sources: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter context based on quality and relevance.
        
        Args:
            context_sources: Raw context from all sources
            
        Returns:
            Dict containing filtered context
        """
        filtered = {}
        
        for source_name, source_data in context_sources.items():
            if self._is_context_relevant(source_data):
                filtered[source_name] = source_data
        
        return filtered
    
    def _is_context_relevant(self, context_data: Any) -> bool:
        """
        Check if context data is relevant and meets quality threshold.
        
        Args:
            context_data: Context data to evaluate
            
        Returns:
            bool: True if context is relevant
        """
        if not context_data:
            return False
        
        # Basic relevance check
        if isinstance(context_data, dict):
            return len(context_data) > 0
        
        return True
    
    def _deduplicate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove duplicate entries from context.
        
        Args:
            context: Context to deduplicate
            
        Returns:
            Dict containing deduplicated context
        """
        deduplicated = {}
        
        for source_name, source_data in context.items():
            if isinstance(source_data, dict):
                deduplicated[source_name] = self._deduplicate_dict(source_data)
            elif isinstance(source_data, list):
                deduplicated[source_name] = list(set(source_data))
            else:
                deduplicated[source_name] = source_data
        
        return deduplicated
    
    def _deduplicate_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove duplicate values from dictionary.
        
        Args:
            data: Dictionary to deduplicate
            
        Returns:
            Dict with deduplicated values
        """
        deduplicated = {}
        
        for key, value in data.items():
            if isinstance(value, list):
                deduplicated[key] = self._deduplicate_list(value)
            elif isinstance(value, dict):
                deduplicated[key] = self._deduplicate_dict(value)
            else:
                deduplicated[key] = value
        
        return deduplicated
    
    def _deduplicate_list(self, data: List[Any]) -> List[Any]:
        """
        Remove duplicate values from list, handling unhashable types.
        
        Args:
            data: List to deduplicate
            
        Returns:
            List with deduplicated values
        """
        if not data:
            return data
        
        # Check if all items are hashable
        try:
            return list(set(data))
        except TypeError:
            # Handle unhashable types (like dicts)
            seen = []
            result = []
            for item in data:
                if item not in seen:
                    seen.append(item)
                    result.append(item)
            return result
    
    def _assess_context_quality(self, context: Dict[str, Any], intent: ParsedIntent) -> float:
        """
        Assess the quality of aggregated context.
        
        Args:
            context: Aggregated context
            intent: Parsed intent
            
        Returns:
            float: Quality score between 0.0 and 1.0
        """
        quality_factors = []
        
        # Check if we have context from all major sources
        source_count = len([k for k in context.keys() if context[k]])
        quality_factors.append(min(source_count / 4.0, 1.0))
        
        # Check relevance to intent
        relevance_score = self._calculate_relevance_score(context, intent)
        quality_factors.append(relevance_score)
        
        # Check context completeness
        completeness_score = self._calculate_completeness_score(context, intent)
        quality_factors.append(completeness_score)
        
        # Calculate weighted average with higher weights for better scores
        weights = [0.2, 0.5, 0.3]  # source_count, relevance, completeness
        quality_score = sum(factor * weight for factor, weight in zip(quality_factors, weights))
        
        # Boost score for high-quality context
        if quality_score > 0.6:
            quality_score = min(quality_score * 1.2, 1.0)
        
        return min(max(quality_score, 0.0), 1.0)
    
    def _calculate_relevance_score(self, context: Dict[str, Any], intent: ParsedIntent) -> float:
        """
        Calculate relevance score based on intent.
        
        Args:
            context: Aggregated context
            intent: Parsed intent
            
        Returns:
            float: Relevance score between 0.0 and 1.0
        """
        relevance_score = 0.0
        
        # Check if context matches intent language/framework
        if context.get("project_structure", {}).get("language") == intent.language:
            relevance_score += 0.3
        
        if context.get("project_structure", {}).get("framework") == intent.framework:
            relevance_score += 0.3
        
        # Check if we have relevant examples
        if context.get("existing_code", {}).get("similar_endpoints"):
            relevance_score += 0.2
        
        if context.get("documentation", {}).get("examples"):
            relevance_score += 0.2
        
        return min(relevance_score, 1.0)
    
    def _calculate_completeness_score(self, context: Dict[str, Any], intent: ParsedIntent) -> float:
        """
        Calculate completeness score based on intent requirements.
        
        Args:
            context: Aggregated context
            intent: Parsed intent
            
        Returns:
            float: Completeness score between 0.0 and 1.0
        """
        completeness_score = 0.0
        
        # Check if we have project structure
        if context.get("project_structure"):
            completeness_score += 0.25
        
        # Check if we have existing code patterns
        if context.get("existing_code"):
            completeness_score += 0.25
        
        # Check if we have documentation
        if context.get("documentation"):
            completeness_score += 0.25
        
        # Check if we have dependencies
        if context.get("dependencies"):
            completeness_score += 0.25
        
        return completeness_score
    
    def _truncate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Truncate context to fit within max length limit.
        
        Args:
            context: Context to truncate
            
        Returns:
            Dict containing truncated context
        """
        # Simple truncation - in production, this would be more sophisticated
        truncated = {}
        current_length = 0
        
        for key, value in context.items():
            if isinstance(value, dict):
                # For dict values, truncate the dict itself
                truncated_value = self._truncate_dict_value(value, self.config.max_context_length - current_length)
                truncated[key] = truncated_value
                current_length += len(str(truncated_value))
            else:
                value_str = str(value)
                if current_length + len(value_str) <= self.config.max_context_length:
                    truncated[key] = value
                    current_length += len(value_str)
                else:
                    # Truncate this value
                    remaining = self.config.max_context_length - current_length
                    if remaining > 100:  # Only add if we have meaningful space
                        truncated[key] = value_str[:remaining] + "..."
                    break
        
        return truncated
    
    def _truncate_dict_value(self, value: Dict[str, Any], max_length: int) -> Dict[str, Any]:
        """
        Truncate a dictionary value to fit within length limit.
        
        Args:
            value: Dictionary to truncate
            max_length: Maximum length allowed
            
        Returns:
            Dict containing truncated value
        """
        truncated = {}
        current_length = 0
        
        for k, v in value.items():
            item_str = f"{k}: {v}"
            if current_length + len(item_str) <= max_length:
                truncated[k] = v
                current_length += len(item_str)
            else:
                break
        
        return truncated
    
    def _validate_intent(self, intent: ParsedIntent) -> None:
        """
        Validate the parsed intent.
        
        Args:
            intent: Parsed intent to validate
            
        Raises:
            ContextGatherError: If intent is invalid
        """
        if not intent or not intent.action or not intent.target:
            raise ContextGatherError("Invalid intent provided")
        
        if intent.confidence_score < 0.1:
            raise ContextGatherError("Intent confidence too low for context aggregation")
    
    def _get_cached_result(self, intent: ParsedIntent) -> Optional[UnifiedContext]:
        """
        Get cached context aggregation result.
        
        Args:
            intent: Parsed intent to look up
            
        Returns:
            UnifiedContext or None if not cached
        """
        cache_key = self._generate_cache_key(intent)
        return self._cache.get(cache_key)
    
    def _cache_result(self, intent: ParsedIntent, context: UnifiedContext) -> None:
        """
        Cache context aggregation result.
        
        Args:
            intent: Parsed intent
            context: Unified context result
        """
        cache_key = self._generate_cache_key(intent)
        self._cache[cache_key] = context
        
        # Limit cache size
        if len(self._cache) > self.config.cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
    
    def _generate_cache_key(self, intent: ParsedIntent) -> str:
        """
        Generate cache key for intent.
        
        Args:
            intent: Parsed intent
            
        Returns:
            str: Cache key
        """
        return f"{intent.action}_{intent.target}_{intent.language}_{intent.framework}"
    
    def _update_performance_stats(self, aggregation_time: float, success: bool) -> None:
        """
        Update performance statistics.
        
        Args:
            aggregation_time: Time taken for aggregation
            success: Whether aggregation was successful
        """
        if success:
            self._aggregation_stats["successful_aggregations"] += 1
        else:
            self._aggregation_stats["failed_aggregations"] += 1
        
        # Update average aggregation time
        total_successful = self._aggregation_stats["successful_aggregations"]
        if total_successful > 0:
            current_avg = self._aggregation_stats["average_aggregation_time"]
            self._aggregation_stats["average_aggregation_time"] = (
                (current_avg * (total_successful - 1) + aggregation_time) / total_successful
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Dict containing performance metrics
        """
        stats = self._aggregation_stats.copy()
        if stats["total_aggregations"] > 0:
            stats["success_rate"] = stats["successful_aggregations"] / stats["total_aggregations"]
        else:
            stats["success_rate"] = 0.0
        
        return stats
