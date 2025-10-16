"""
Tests for health check endpoints.

This module contains tests for all health check endpoints including
basic health, readiness, liveness, and version checks.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


class TestHealthEndpoints:
    """Test class for health check endpoints."""

    def test_health_check_sync(self):
        """Test health check endpoint with synchronous client."""
        with TestClient(app) as client:
            response = client.get("/api/v1/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data
            assert "environment" in data
            assert "checks" in data
            
            # Check checks structure
            checks = data["checks"]
            assert "database" in checks
            assert "redis" in checks
            
            # Check individual check structure
            for check_name, check_data in checks.items():
                assert "status" in check_data
                assert "details" in check_data

    @pytest.mark.asyncio
    async def test_health_check_async(self):
        """Test health check endpoint with asynchronous client."""
        async with AsyncClient(base_url="http://test") as client:
            response = await client.get("/api/v1/health")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "status" in data
            assert "timestamp" in data
            assert "version" in data
            assert "environment" in data
            assert "checks" in data

    def test_readiness_check(self):
        """Test readiness check endpoint."""
        with TestClient(app) as client:
            response = client.get("/api/v1/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "status" in data
            assert "timestamp" in data
            assert "message" in data
            
            # Status should be either "ready" or "not_ready"
            assert data["status"] in ["ready", "not_ready"]

    def test_liveness_check(self):
        """Test liveness check endpoint."""
        with TestClient(app) as client:
            response = client.get("/api/v1/health/live")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "status" in data
            assert "timestamp" in data
            assert "message" in data
            
            # Status should always be "alive" for this endpoint
            assert data["status"] == "alive"

    def test_version_info(self):
        """Test version information endpoint."""
        with TestClient(app) as client:
            response = client.get("/api/v1/health/version")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "name" in data
            assert "version" in data
            assert "environment" in data
            assert "build_time" in data
            assert "python_version" in data
            
            # Check specific values
            assert data["name"] == "ArchMesh PoC"
            assert data["version"] == "0.1.0"

    def test_root_endpoint(self):
        """Test root endpoint."""
        with TestClient(app) as client:
            response = client.get("/")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "name" in data
            assert "version" in data
            assert "environment" in data
            assert "api_prefix" in data
            
            # Check specific values
            assert data["name"] == "ArchMesh PoC"
            assert data["version"] == "0.1.0"
            assert data["api_prefix"] == "/api/v1"

    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint."""
        with TestClient(app) as client:
            response = client.get("/openapi.json")
            
            assert response.status_code == 200
            data = response.json()
            
            # Check OpenAPI structure
            assert "openapi" in data
            assert "info" in data
            assert "paths" in data
            
            # Check info section
            info = data["info"]
            assert info["title"] == "ArchMesh PoC"
            assert info["version"] == "0.1.0"
            
            # Check that health endpoints are included
            paths = data["paths"]
            assert "/api/v1/health" in paths
            assert "/api/v1/health/ready" in paths
            assert "/api/v1/health/live" in paths
            assert "/api/v1/health/version" in paths

    def test_docs_endpoint(self):
        """Test Swagger UI docs endpoint (only in debug mode)."""
        with TestClient(app) as client:
            response = client.get("/docs")
            
            # In debug mode, docs should be available
            # In production mode, this would return 404
            if response.status_code == 200:
                assert "text/html" in response.headers["content-type"]
            else:
                assert response.status_code == 404

    def test_cors_headers(self):
        """Test CORS headers are present."""
        with TestClient(app) as client:
            response = client.options("/api/v1/health")
            
            # CORS headers should be present
            assert "access-control-allow-origin" in response.headers
            assert "access-control-allow-methods" in response.headers
            assert "access-control-allow-headers" in response.headers


class TestHealthCheckIntegration:
    """Integration tests for health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_with_database_failure(self):
        """Test health check when database is unavailable."""
        # This test would require mocking the database connection
        # to simulate a failure scenario
        pass

    @pytest.mark.asyncio
    async def test_health_check_with_redis_failure(self):
        """Test health check when Redis is unavailable."""
        # This test would require mocking the Redis connection
        # to simulate a failure scenario
        pass

    def test_health_check_response_time(self):
        """Test that health check responds within acceptable time."""
        import time
        
        with TestClient(app) as client:
            start_time = time.time()
            response = client.get("/api/v1/health")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            # Health check should respond within 1 second
            assert response_time < 1.0


# Pytest configuration
@pytest.fixture
def client():
    """Create test client fixture."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create async test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
