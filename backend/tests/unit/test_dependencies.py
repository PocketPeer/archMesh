"""
Unit tests for the Dependencies module.

This module tests the dependency injection functionality including:
- Database session dependencies
- Redis cache dependencies
- Settings dependencies
- Query parameter dependencies
- Environment-based dependencies
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    get_database_session,
    get_redis_cache,
    get_settings,
    CommonQueryParams,
    get_common_query_params,
    require_debug_mode,
    require_production_mode
)


class TestDatabaseDependencies:
    """Test cases for database-related dependencies."""

    @pytest.mark.asyncio
    async def test_get_database_session_success(self):
        """Test successful database session retrieval."""
        # Mock the get_db generator
        mock_session = AsyncMock(spec=AsyncSession)
        
        async def mock_get_db():
            yield mock_session
        
        with patch('app.dependencies.get_db', mock_get_db):
            # Test the dependency
            sessions = []
            async for session in get_database_session():
                sessions.append(session)
            
            assert len(sessions) == 1
            assert sessions[0] == mock_session

    @pytest.mark.asyncio
    async def test_get_database_session_multiple_sessions(self):
        """Test database session dependency with multiple sessions."""
        # Mock multiple sessions
        mock_session1 = AsyncMock(spec=AsyncSession)
        mock_session2 = AsyncMock(spec=AsyncSession)
        
        async def mock_get_db():
            yield mock_session1
            yield mock_session2
        
        with patch('app.dependencies.get_db', mock_get_db):
            # Test the dependency
            sessions = []
            async for session in get_database_session():
                sessions.append(session)
            
            assert len(sessions) == 2
            assert sessions[0] == mock_session1
            assert sessions[1] == mock_session2

    @pytest.mark.asyncio
    async def test_get_database_session_empty(self):
        """Test database session dependency with no sessions."""
        async def mock_get_db():
            # Empty generator
            if False:
                yield
        
        with patch('app.dependencies.get_db', mock_get_db):
            # Test the dependency
            sessions = []
            async for session in get_database_session():
                sessions.append(session)
            
            assert len(sessions) == 0


class TestRedisDependencies:
    """Test cases for Redis-related dependencies."""

    @pytest.mark.asyncio
    async def test_get_redis_cache_success(self):
        """Test successful Redis cache retrieval."""
        mock_cache = Mock()
        
        with patch('app.dependencies.get_cache', return_value=mock_cache):
            result = await get_redis_cache()
            
            assert result == mock_cache

    @pytest.mark.asyncio
    async def test_get_redis_cache_async(self):
        """Test Redis cache dependency with async get_cache."""
        mock_cache = Mock()
        
        async def mock_get_cache():
            return mock_cache
        
        with patch('app.dependencies.get_cache', mock_get_cache):
            result = await get_redis_cache()
            
            assert result == mock_cache


class TestSettingsDependencies:
    """Test cases for settings-related dependencies."""

    def test_get_settings_success(self):
        """Test successful settings retrieval."""
        with patch('app.dependencies.settings') as mock_settings:
            result = get_settings()
            
            assert result == mock_settings

    def test_get_settings_returns_actual_settings(self):
        """Test that get_settings returns the actual settings object."""
        from app.dependencies import settings
        
        result = get_settings()
        
        assert result == settings


class TestCommonQueryParams:
    """Test cases for CommonQueryParams class."""

    def test_common_query_params_default_values(self):
        """Test CommonQueryParams with default values."""
        params = CommonQueryParams()
        
        assert params.skip == 0
        assert params.limit == 100
        assert params.search is None

    def test_common_query_params_custom_values(self):
        """Test CommonQueryParams with custom values."""
        params = CommonQueryParams(skip=10, limit=50, search="test")
        
        assert params.skip == 10
        assert params.limit == 50
        assert params.search == "test"

    def test_common_query_params_skip_validation(self):
        """Test CommonQueryParams skip validation (negative values)."""
        params = CommonQueryParams(skip=-5)
        
        # Should be clamped to 0
        assert params.skip == 0

    def test_common_query_params_limit_validation_min(self):
        """Test CommonQueryParams limit validation (minimum value)."""
        params = CommonQueryParams(limit=0)
        
        # Should be clamped to 1
        assert params.limit == 1

    def test_common_query_params_limit_validation_max(self):
        """Test CommonQueryParams limit validation (maximum value)."""
        params = CommonQueryParams(limit=200)
        
        # Should be clamped to 100
        assert params.limit == 100

    def test_common_query_params_limit_validation_negative(self):
        """Test CommonQueryParams limit validation (negative value)."""
        params = CommonQueryParams(limit=-10)
        
        # Should be clamped to 1
        assert params.limit == 1

    def test_common_query_params_search_none(self):
        """Test CommonQueryParams with search=None."""
        params = CommonQueryParams(search=None)
        
        assert params.search is None

    def test_common_query_params_search_empty_string(self):
        """Test CommonQueryParams with empty search string."""
        params = CommonQueryParams(search="")
        
        assert params.search == ""

    def test_common_query_params_search_whitespace(self):
        """Test CommonQueryParams with whitespace search string."""
        params = CommonQueryParams(search="  test  ")
        
        assert params.search == "  test  "


class TestGetCommonQueryParams:
    """Test cases for get_common_query_params function."""

    def test_get_common_query_params_default_values(self):
        """Test get_common_query_params with default values."""
        params = get_common_query_params()
        
        assert isinstance(params, CommonQueryParams)
        assert params.skip == 0
        assert params.limit == 100
        assert params.search is None

    def test_get_common_query_params_custom_values(self):
        """Test get_common_query_params with custom values."""
        params = get_common_query_params(skip=20, limit=75, search="custom")
        
        assert isinstance(params, CommonQueryParams)
        assert params.skip == 20
        assert params.limit == 75
        assert params.search == "custom"

    def test_get_common_query_params_validation(self):
        """Test get_common_query_params with validation."""
        params = get_common_query_params(skip=-10, limit=150, search="test")
        
        assert isinstance(params, CommonQueryParams)
        assert params.skip == 0  # Clamped
        assert params.limit == 100  # Clamped
        assert params.search == "test"

    def test_get_common_query_params_boundary_values(self):
        """Test get_common_query_params with boundary values."""
        # Test minimum valid values
        params = get_common_query_params(skip=0, limit=1)
        assert params.skip == 0
        assert params.limit == 1
        
        # Test maximum valid values
        params = get_common_query_params(skip=0, limit=100)
        assert params.skip == 0
        assert params.limit == 100


class TestEnvironmentDependencies:
    """Test cases for environment-based dependencies."""

    def test_require_debug_mode_success(self):
        """Test require_debug_mode when debug is enabled."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.debug = True
            
            result = require_debug_mode()
            
            assert result is None

    def test_require_debug_mode_failure(self):
        """Test require_debug_mode when debug is disabled."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.debug = False
            
            with pytest.raises(HTTPException) as exc_info:
                require_debug_mode()
            
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "Debug mode is required" in exc_info.value.detail

    def test_require_debug_mode_false_value(self):
        """Test require_debug_mode with explicit False value."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.debug = False
            
            with pytest.raises(HTTPException) as exc_info:
                require_debug_mode()
            
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_require_production_mode_success(self):
        """Test require_production_mode when in production."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.is_production = True
            
            result = require_production_mode()
            
            assert result is None

    def test_require_production_mode_failure(self):
        """Test require_production_mode when not in production."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.is_production = False
            
            with pytest.raises(HTTPException) as exc_info:
                require_production_mode()
            
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "Production mode is required" in exc_info.value.detail

    def test_require_production_mode_false_value(self):
        """Test require_production_mode with explicit False value."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.is_production = False
            
            with pytest.raises(HTTPException) as exc_info:
                require_production_mode()
            
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN

    def test_require_production_mode_none_value(self):
        """Test require_production_mode with None value."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.is_production = None
            
            with pytest.raises(HTTPException) as exc_info:
                require_production_mode()
            
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestDependencyIntegration:
    """Integration tests for dependencies."""

    @pytest.mark.asyncio
    async def test_database_and_redis_dependencies_together(self):
        """Test using database and Redis dependencies together."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_cache = Mock()
        
        async def mock_get_db():
            yield mock_session
        
        with patch('app.dependencies.get_db', mock_get_db):
            with patch('app.dependencies.get_cache', return_value=mock_cache):
                # Test both dependencies
                db_sessions = []
                async for session in get_database_session():
                    db_sessions.append(session)
                
                cache = await get_redis_cache()
                
                assert len(db_sessions) == 1
                assert db_sessions[0] == mock_session
                assert cache == mock_cache

    def test_settings_and_query_params_together(self):
        """Test using settings and query params dependencies together."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.debug = True
            
            # Test both dependencies
            settings_result = get_settings()
            query_params = get_common_query_params(skip=10, limit=50)
            
            assert settings_result == mock_settings
            assert isinstance(query_params, CommonQueryParams)
            assert query_params.skip == 10
            assert query_params.limit == 50

    def test_environment_dependencies_with_different_settings(self):
        """Test environment dependencies with different settings configurations."""
        # Test debug mode enabled, production disabled
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.debug = True
            mock_settings.is_production = False
            
            # Debug mode should pass
            debug_result = require_debug_mode()
            assert debug_result is None
            
            # Production mode should fail
            with pytest.raises(HTTPException):
                require_production_mode()

        # Test debug mode disabled, production enabled
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.debug = False
            mock_settings.is_production = True
            
            # Debug mode should fail
            with pytest.raises(HTTPException):
                require_debug_mode()
            
            # Production mode should pass
            prod_result = require_production_mode()
            assert prod_result is None


class TestDependencyEdgeCases:
    """Test edge cases for dependencies."""

    def test_common_query_params_extreme_values(self):
        """Test CommonQueryParams with extreme values."""
        # Very large skip value
        params = CommonQueryParams(skip=1000000)
        assert params.skip == 1000000  # No upper limit on skip
        
        # Very large limit value
        params = CommonQueryParams(limit=1000000)
        assert params.limit == 100  # Clamped to 100
        
        # Very long search string
        long_search = "a" * 10000
        params = CommonQueryParams(search=long_search)
        assert params.search == long_search

    def test_common_query_params_special_characters(self):
        """Test CommonQueryParams with special characters in search."""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        params = CommonQueryParams(search=special_chars)
        assert params.search == special_chars

    def test_common_query_params_unicode(self):
        """Test CommonQueryParams with unicode characters."""
        unicode_search = "测试 🚀 émojis"
        params = CommonQueryParams(search=unicode_search)
        assert params.search == unicode_search

    @pytest.mark.asyncio
    async def test_database_session_with_exception(self):
        """Test database session dependency when get_db raises an exception."""
        async def mock_get_db_with_exception():
            raise Exception("Database connection failed")
            yield  # This line will never be reached, but makes it an async generator
        
        with patch('app.dependencies.get_db', mock_get_db_with_exception):
            with pytest.raises(Exception, match="Database connection failed"):
                sessions = []
                async for session in get_database_session():
                    sessions.append(session)

    @pytest.mark.asyncio
    async def test_redis_cache_with_exception(self):
        """Test Redis cache dependency when get_cache raises an exception."""
        async def mock_get_cache_with_exception():
            raise Exception("Redis connection failed")
        
        with patch('app.dependencies.get_cache', mock_get_cache_with_exception):
            with pytest.raises(Exception, match="Redis connection failed"):
                await get_redis_cache()

    def test_environment_dependencies_with_none_settings(self):
        """Test environment dependencies when settings attributes are None."""
        with patch('app.dependencies.settings') as mock_settings:
            mock_settings.debug = None
            mock_settings.is_production = None
            
            # Both should fail
            with pytest.raises(HTTPException):
                require_debug_mode()
            
            with pytest.raises(HTTPException):
                require_production_mode()
