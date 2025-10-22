"""
REFACTOR Phase 1: Context Aggregator Performance Optimization Tests

Tests for advanced caching, parallel processing, and smart filtering
in the Context Aggregator component.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
import time
import json

from app.vibe_coding.context_aggregator import ContextAggregator, ContextAggregatorConfig
from app.vibe_coding.models import (
    ContextSource, ContextAggregationRequest, ContextAggregationResponse,
    UnifiedContext, ContextQualityMetrics
)
from app.core.exceptions import ContextGatherError


class TestContextAggregatorCaching:
    """Test advanced caching system for Context Aggregator"""
    
    @pytest.fixture
    def cache_config(self):
        """Cache configuration for testing"""
        return {
            "l1_cache_size": 100,
            "l1_ttl": 300,
            "l2_redis_enabled": True,
            "l2_redis_ttl": 1800,
            "l3_db_enabled": True,
            "l3_db_ttl": 3600,
            "cache_warming_enabled": True,
            "cache_analytics_enabled": True
        }
    
    @pytest.fixture
    def context_aggregator_with_cache(self, cache_config):
        """Context aggregator with caching enabled"""
        config = ContextAggregatorConfig(
            max_context_size=10000,
            quality_threshold=0.7,
            timeout=30,
            **cache_config
        )
        return ContextAggregator(config)
    
    @pytest.mark.asyncio
    async def test_multi_level_cache_hit(self, context_aggregator_with_cache):
        """Test cache hit across multiple levels"""
        # Mock cache responses
        with patch.object(context_aggregator_with_cache, '_get_from_l1_cache', return_value=None), \
             patch.object(context_aggregator_with_cache, '_get_from_l2_cache', return_value={"cached": "data"}), \
             patch.object(context_aggregator_with_cache, '_set_to_l1_cache') as mock_l1_set:
            
            result = await context_aggregator_with_cache._get_from_cache("test_key")
            
            assert result == {"cached": "data"}
            mock_l1_set.assert_called_once_with("test_key", {"cached": "data"})
    
    @pytest.mark.asyncio
    async def test_cache_miss_and_store(self, context_aggregator_with_cache):
        """Test cache miss and subsequent storage"""
        with patch.object(context_aggregator_with_cache, '_get_from_l1_cache', return_value=None), \
             patch.object(context_aggregator_with_cache, '_get_from_l2_cache', return_value=None), \
             patch.object(context_aggregator_with_cache, '_get_from_l3_cache', return_value=None), \
             patch.object(context_aggregator_with_cache, '_set_to_l1_cache') as mock_l1_set, \
             patch.object(context_aggregator_with_cache, '_set_to_l2_cache') as mock_l2_set, \
             patch.object(context_aggregator_with_cache, '_set_to_l3_cache') as mock_l3_set:
            
            result = await context_aggregator_with_cache._get_from_cache("test_key")
            assert result is None
            
            # Store data
            test_data = {"new": "data"}
            await context_aggregator_with_cache._set_to_cache("test_key", test_data)
            
            mock_l1_set.assert_called_with("test_key", test_data)
            mock_l2_set.assert_called_with("test_key", test_data)
            mock_l3_set.assert_called_with("test_key", test_data)
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, context_aggregator_with_cache):
        """Test cache invalidation strategies"""
        with patch.object(context_aggregator_with_cache, '_invalidate_l1_cache') as mock_l1_inv, \
             patch.object(context_aggregator_with_cache, '_invalidate_l2_cache') as mock_l2_inv, \
             patch.object(context_aggregator_with_cache, '_invalidate_l3_cache') as mock_l3_inv:
            
            await context_aggregator_with_cache._invalidate_cache("test_key")
            
            mock_l1_inv.assert_called_once_with("test_key")
            mock_l2_inv.assert_called_once_with("test_key")
            mock_l3_inv.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_cache_warming(self, context_aggregator_with_cache):
        """Test cache warming functionality"""
        with patch.object(context_aggregator_with_cache, '_warm_cache_for_project') as mock_warm:
            await context_aggregator_with_cache.warm_cache("project_123")
            mock_warm.assert_called_once_with("project_123")
    
    @pytest.mark.asyncio
    async def test_cache_analytics(self, context_aggregator_with_cache):
        """Test cache analytics and monitoring"""
        with patch.object(context_aggregator_with_cache, '_get_cache_stats') as mock_stats:
            mock_stats.return_value = {
                "l1_hits": 50,
                "l1_misses": 10,
                "l2_hits": 30,
                "l2_misses": 20,
                "l3_hits": 15,
                "l3_misses": 5,
                "hit_ratio": 0.85
            }
            
            stats = await context_aggregator_with_cache.get_cache_analytics()
            
            assert stats["hit_ratio"] == 0.85
            assert stats["l1_hits"] == 50
            assert stats["total_requests"] == 60


class TestContextAggregatorParallelProcessing:
    """Test parallel context processing capabilities"""
    
    @pytest.fixture
    def parallel_config(self):
        """Parallel processing configuration"""
        return {
            "max_workers": 4,
            "batch_size": 10,
            "streaming_enabled": True,
            "progress_tracking_enabled": True,
            "cancellation_enabled": True
        }
    
    @pytest.fixture
    def context_aggregator_parallel(self, parallel_config):
        """Context aggregator with parallel processing"""
        config = ContextAggregatorConfig(
            max_context_size=10000,
            quality_threshold=0.7,
            timeout=30,
            **parallel_config
        )
        return ContextAggregator(config)
    
    @pytest.mark.asyncio
    async def test_parallel_context_gathering(self, context_aggregator_parallel):
        """Test parallel gathering from multiple sources"""
        with patch.object(context_aggregator_parallel, '_gather_project_context', new_callable=AsyncMock) as mock_project, \
             patch.object(context_aggregator_parallel, '_gather_dependencies_context', new_callable=AsyncMock) as mock_deps, \
             patch.object(context_aggregator_parallel, '_gather_architecture_context', new_callable=AsyncMock) as mock_arch:
            
            mock_project.return_value = {"project": "data"}
            mock_deps.return_value = {"dependencies": "data"}
            mock_arch.return_value = {"architecture": "data"}
            
            start_time = time.time()
            result = await context_aggregator_parallel._gather_context_parallel({
                "project_id": "test_project",
                "include_dependencies": True,
                "include_architecture": True
            })
            end_time = time.time()
            
            # Should complete faster than sequential processing
            assert end_time - start_time < 1.0
            assert "project" in result
            assert "dependencies" in result
            assert "architecture" in result
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, context_aggregator_parallel):
        """Test batch processing of multiple requests"""
        requests = [
            ContextAggregationRequest(
                project_id=f"project_{i}",
                sources=[ContextSource.PROJECT_STRUCTURE],
                include_dependencies=True
            ) for i in range(5)
        ]
        
        with patch.object(context_aggregator_parallel, 'aggregate_context', new_callable=AsyncMock) as mock_aggregate:
            mock_aggregate.return_value = ContextAggregationResponse(
                unified_context=UnifiedContext(
                    project_id="test",
                    project_structure={},
                    dependencies={},
                    architecture={},
                    quality_score=0.8
                ),
                quality_metrics=ContextQualityMetrics(
                    completeness=0.8,
                    accuracy=0.9,
                    relevance=0.7
                ),
                processing_time=0.5
            )
            
            results = await context_aggregator_parallel.process_batch(requests)
            
            assert len(results) == 5
            assert all(result.success for result in results)
    
    @pytest.mark.asyncio
    async def test_streaming_context_processing(self, context_aggregator_parallel):
        """Test streaming context processing for large datasets"""
        async def mock_stream_generator():
            for i in range(3):
                yield {"chunk": i, "data": f"chunk_data_{i}"}
        
        with patch.object(context_aggregator_parallel, '_stream_context_data', return_value=mock_stream_generator()):
            chunks = []
            async for chunk in context_aggregator_parallel._stream_context_processing("large_project"):
                chunks.append(chunk)
            
            assert len(chunks) == 3
            assert chunks[0]["chunk"] == 0
            assert chunks[2]["chunk"] == 2
    
    @pytest.mark.asyncio
    async def test_progress_tracking(self, context_aggregator_parallel):
        """Test progress tracking during processing"""
        with patch.object(context_aggregator_parallel, '_update_progress') as mock_progress:
            await context_aggregator_parallel._track_progress("task_123", 0.5, "Processing context")
            mock_progress.assert_called_once_with("task_123", 0.5, "Processing context")
    
    @pytest.mark.asyncio
    async def test_cancellation_support(self, context_aggregator_parallel):
        """Test cancellation support for long-running operations"""
        with patch.object(context_aggregator_parallel, '_check_cancellation', return_value=True):
            with pytest.raises(ContextGatherError, match="Operation cancelled"):
                await context_aggregator_parallel._process_with_cancellation("task_123")


class TestContextAggregatorSmartFiltering:
    """Test smart context filtering and optimization"""
    
    @pytest.fixture
    def smart_config(self):
        """Smart filtering configuration"""
        return {
            "relevance_scoring_enabled": True,
            "context_compression_enabled": True,
            "context_versioning_enabled": True,
            "quality_metrics_enabled": True,
            "max_context_items": 100
        }
    
    @pytest.fixture
    def context_aggregator_smart(self, smart_config):
        """Context aggregator with smart filtering"""
        config = ContextAggregatorConfig(
            max_context_size=10000,
            quality_threshold=0.7,
            timeout=30,
            **smart_config
        )
        return ContextAggregator(config)
    
    @pytest.mark.asyncio
    async def test_relevance_scoring(self, context_aggregator_smart):
        """Test intelligent context relevance scoring"""
        context_items = [
            {"type": "file", "path": "src/main.py", "relevance": 0.9},
            {"type": "file", "path": "docs/README.md", "relevance": 0.3},
            {"type": "config", "path": "config.json", "relevance": 0.7}
        ]
        
        with patch.object(context_aggregator_smart, '_calculate_relevance_score') as mock_score:
            mock_score.side_effect = lambda item: item["relevance"]
            
            filtered = await context_aggregator_smart._filter_by_relevance(context_items, threshold=0.5)
            
            assert len(filtered) == 2
            assert all(item["relevance"] >= 0.5 for item in filtered)
    
    @pytest.mark.asyncio
    async def test_context_compression(self, context_aggregator_smart):
        """Test context compression and summarization"""
        large_context = {
            "files": [{"path": f"file_{i}.py", "content": "x" * 1000} for i in range(10)],
            "dependencies": [{"name": f"dep_{i}", "version": "1.0.0"} for i in range(20)]
        }
        
        with patch.object(context_aggregator_smart, '_compress_context') as mock_compress:
            mock_compress.return_value = {
                "files_summary": "10 Python files",
                "dependencies_summary": "20 dependencies"
            }
            
            compressed = await context_aggregator_smart._compress_large_context(large_context)
            
            assert "files_summary" in compressed
            assert "dependencies_summary" in compressed
            assert len(compressed) < len(large_context)
    
    @pytest.mark.asyncio
    async def test_context_versioning(self, context_aggregator_smart):
        """Test context versioning and diffing"""
        old_context = {"version": "1.0", "data": "old"}
        new_context = {"version": "1.1", "data": "new"}
        
        with patch.object(context_aggregator_smart, '_calculate_context_diff') as mock_diff:
            mock_diff.return_value = {
                "added": ["new_field"],
                "modified": ["data"],
                "removed": []
            }
            
            diff = await context_aggregator_smart._get_context_diff(old_context, new_context)
            
            assert "added" in diff
            assert "modified" in diff
            assert "removed" in diff
    
    @pytest.mark.asyncio
    async def test_quality_metrics_calculation(self, context_aggregator_smart):
        """Test context quality metrics calculation"""
        context = {
            "completeness": 0.8,
            "accuracy": 0.9,
            "relevance": 0.7,
            "freshness": 0.6
        }
        
        with patch.object(context_aggregator_smart, '_calculate_quality_metrics') as mock_metrics:
            mock_metrics.return_value = ContextQualityMetrics(
                completeness=0.8,
                accuracy=0.9,
                relevance=0.7,
                freshness=0.6,
                overall_score=0.75
            )
            
            metrics = await context_aggregator_smart._assess_context_quality(context)
            
            assert metrics.overall_score == 0.75
            assert metrics.completeness == 0.8
    
    @pytest.mark.asyncio
    async def test_context_size_optimization(self, context_aggregator_smart):
        """Test context size optimization and truncation"""
        large_context = {"data": "x" * 15000}  # Exceeds max size
        
        with patch.object(context_aggregator_smart, '_optimize_context_size') as mock_optimize:
            mock_optimize.return_value = {"data": "x" * 5000}  # Optimized size
            
            optimized = await context_aggregator_smart._optimize_context(large_context)
            
            assert len(str(optimized)) < len(str(large_context))
            assert "data" in optimized


class TestContextAggregatorIntegration:
    """Test integration of all REFACTOR features"""
    
    @pytest.fixture
    def full_config(self):
        """Full configuration with all REFACTOR features"""
        return {
            "l1_cache_size": 100,
            "l1_ttl": 300,
            "l2_redis_enabled": True,
            "l2_redis_ttl": 1800,
            "l3_db_enabled": True,
            "l3_db_ttl": 3600,
            "cache_warming_enabled": True,
            "cache_analytics_enabled": True,
            "max_workers": 4,
            "batch_size": 10,
            "streaming_enabled": True,
            "progress_tracking_enabled": True,
            "cancellation_enabled": True,
            "relevance_scoring_enabled": True,
            "context_compression_enabled": True,
            "context_versioning_enabled": True,
            "quality_metrics_enabled": True,
            "max_context_items": 100
        }
    
    @pytest.fixture
    def context_aggregator_full(self, full_config):
        """Context aggregator with all REFACTOR features"""
        config = ContextAggregatorConfig(
            max_context_size=10000,
            quality_threshold=0.7,
            timeout=30,
            **full_config
        )
        return ContextAggregator(config)
    
    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, context_aggregator_full):
        """Test complete workflow with all REFACTOR features"""
        request = ContextAggregationRequest(
            project_id="integration_test",
            sources=[ContextSource.PROJECT_STRUCTURE, ContextSource.DEPENDENCIES],
            include_dependencies=True,
            include_architecture=True
        )
        
        with patch.object(context_aggregator_full, '_get_from_cache', return_value=None), \
             patch.object(context_aggregator_full, '_gather_context_parallel', return_value={"test": "data"}), \
             patch.object(context_aggregator_full, '_filter_by_relevance', return_value=[{"test": "data"}]), \
             patch.object(context_aggregator_full, '_compress_large_context', return_value={"compressed": "data"}), \
             patch.object(context_aggregator_full, '_assess_context_quality', return_value=ContextQualityMetrics(
                 completeness=0.8, accuracy=0.9, relevance=0.7, freshness=0.6, overall_score=0.75
             )), \
             patch.object(context_aggregator_full, '_set_to_cache') as mock_cache_set:
            
            result = await context_aggregator_full.aggregate_context(request)
            
            assert result.success
            assert result.unified_context is not None
            assert result.quality_metrics.overall_score == 0.75
            mock_cache_set.assert_called()
    
    @pytest.mark.asyncio
    async def test_performance_benchmarking(self, context_aggregator_full):
        """Test performance benchmarking capabilities"""
        with patch.object(context_aggregator_full, '_benchmark_operation') as mock_benchmark:
            mock_benchmark.return_value = {
                "operation": "aggregate_context",
                "duration": 0.5,
                "memory_usage": 1024,
                "cpu_usage": 0.3
            }
            
            benchmark = await context_aggregator_full.benchmark_performance("aggregate_context")
            
            assert benchmark["duration"] == 0.5
            assert benchmark["memory_usage"] == 1024
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, context_aggregator_full):
        """Test health monitoring and diagnostics"""
        with patch.object(context_aggregator_full, '_get_health_status') as mock_health:
            mock_health.return_value = {
                "status": "healthy",
                "cache_status": "operational",
                "processing_status": "operational",
                "memory_usage": 0.6,
                "active_workers": 2
            }
            
            health = await context_aggregator_full.get_health_status()
            
            assert health["status"] == "healthy"
            assert health["cache_status"] == "operational"
            assert health["processing_status"] == "operational"
