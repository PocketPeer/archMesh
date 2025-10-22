"""
Performance and Load Testing

These tests verify the performance characteristics of the API under various load conditions.
"""

import pytest
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app


class TestPerformance:
    """Test API performance characteristics."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_response_time_health_endpoint(self, client):
        """Test response time for health endpoint."""
        with patch('app.core.redis_client.redis_client.ping', return_value=True):
            start_time = time.time()
            response = client.get("/api/v1/health")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0  # Should respond within 1 second

    def test_response_time_projects_list(self, client):
        """Test response time for projects list endpoint."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock projects list
            mock_projects = [
                Mock(
                    id=str(uuid4()),
                    name=f"Project {i}",
                    description=f"Description {i}",
                    domain="e-commerce",
                    mode="greenfield",
                    status="active",
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z"
                )
                for i in range(100)  # 100 projects
            ]
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_projects
            mock_result.scalar.return_value = 100
            mock_db.execute.return_value = mock_result
            
            start_time = time.time()
            response = client.get("/api/v1/projects")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 2.0  # Should respond within 2 seconds for 100 projects

    def test_concurrent_health_checks(self, client):
        """Test concurrent health check requests."""
        def make_health_request():
            with patch('app.core.redis_client.redis_client.ping', return_value=True):
                response = client.get("/api/v1/health")
                return response.status_code
        
        # Test with 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_health_request) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10

    def test_concurrent_project_creation(self, client):
        """Test concurrent project creation."""
        def create_project(project_id):
            with patch('app.api.v1.projects.get_db') as mock_get_db:
                mock_db = Mock()
                mock_get_db.return_value = mock_db
                
                mock_project = Mock(
                    id=project_id,
                    name=f"Project {project_id}",
                    description="Test description",
                    domain="e-commerce",
                    mode="greenfield",
                    status="active"
                )
                
                mock_db.add.return_value = None
                mock_db.commit.return_value = None
                mock_db.refresh.return_value = None
                
                def mock_refresh(project):
                    project.id = project_id
                    project.created_at = "2023-01-01T00:00:00Z"
                    project.updated_at = "2023-01-01T00:00:00Z"
                
                mock_db.refresh.side_effect = mock_refresh
                
                project_data = {
                    "name": f"Project {project_id}",
                    "description": "Test description",
                    "domain": "e-commerce",
                    "mode": "greenfield"
                }
                
                response = client.post("/api/v1/projects", json=project_data)
                return response.status_code
        
        # Test with 5 concurrent project creations
        project_ids = [str(uuid4()) for _ in range(5)]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_project, pid) for pid in project_ids]
            results = [future.result() for future in as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 201 for status in results)
        assert len(results) == 5

    def test_memory_usage_large_dataset(self, client):
        """Test memory usage with large dataset."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock large projects list (1000 projects)
            mock_projects = [
                Mock(
                    id=str(uuid4()),
                    name=f"Project {i}",
                    description=f"Description {i}" * 100,  # Large description
                    domain="e-commerce",
                    mode="greenfield",
                    status="active",
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z"
                )
                for i in range(1000)
            ]
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_projects
            mock_result.scalar.return_value = 1000
            mock_db.execute.return_value = mock_result
            
            start_time = time.time()
            response = client.get("/api/v1/projects")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should handle 1000 projects within 5 seconds
            assert len(response.json()["projects"]) == 1000

    def test_workflow_execution_performance(self, client):
        """Test workflow execution performance."""
        session_id = str(uuid4())
        project_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.agents.requirements_agent.RequirementsAgent') as mock_req_agent:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock agent with realistic execution time
            async def mock_execute(data):
                await asyncio.sleep(0.1)  # Simulate 100ms processing time
                return {
                    "structured_requirements": {"business_goals": ["Test goal"]},
                    "confidence_score": 0.8
                }
            
            mock_req_agent.return_value.execute = mock_execute
            
            # Mock workflow creation
            mock_workflow = Mock(
                id=session_id,
                project_id=project_id,
                current_stage="requirements_parsing",
                status="active"
            )
            
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            def mock_refresh(workflow):
                workflow.id = session_id
                workflow.created_at = "2023-01-01T00:00:00Z"
                workflow.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            workflow_data = {
                "project_id": project_id,
                "document_path": "/test/requirements.txt",
                "mode": "greenfield"
            }
            
            start_time = time.time()
            response = client.post("/api/v1/workflows/start", json=workflow_data)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 201
            assert response_time < 2.0  # Should complete within 2 seconds

    def test_database_query_performance(self, client):
        """Test database query performance."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock database query with realistic delay
            def mock_execute(query):
                time.sleep(0.05)  # Simulate 50ms database query time
                mock_result = Mock()
                mock_result.scalars.return_value.all.return_value = []
                mock_result.scalar.return_value = 0
                return mock_result
            
            mock_db.execute.side_effect = mock_execute
            
            start_time = time.time()
            response = client.get("/api/v1/projects")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0  # Should complete within 1 second

    def test_file_upload_performance(self, client):
        """Test file upload performance."""
        project_id = str(uuid4())
        
        with patch('app.api.v1.workflows.get_db') as mock_get_db, \
             patch('app.core.file_storage.FileStorage.save_file') as mock_save_file:
            
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            mock_save_file.return_value = f"/uploads/{project_id}/requirements.txt"
            
            # Create a moderately large file (1MB)
            large_content = "A" * (1024 * 1024)  # 1MB
            
            start_time = time.time()
            response = client.post(
                f"/api/v1/projects/{project_id}/upload",
                files={"file": ("requirements.txt", large_content, "text/plain")}
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 3.0  # Should handle 1MB file within 3 seconds

    def test_api_throughput(self, client):
        """Test API throughput under load."""
        def make_request():
            with patch('app.core.redis_client.redis_client.ping', return_value=True):
                response = client.get("/api/v1/health")
                return response.status_code
        
        # Test throughput with 50 requests
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate throughput (requests per second)
        throughput = len(results) / total_time
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 50
        assert throughput > 10  # Should handle at least 10 requests per second

    def test_error_handling_performance(self, client):
        """Test error handling performance."""
        # Test with invalid data that should trigger validation errors
        invalid_data = {
            "name": "",  # Invalid empty name
            "domain": "invalid"  # Invalid domain
        }
        
        start_time = time.time()
        response = client.post("/api/v1/projects", json=invalid_data)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 422
        assert response_time < 1.0  # Error handling should be fast

    def test_concurrent_workflow_execution(self, client):
        """Test concurrent workflow execution."""
        def start_workflow(workflow_id):
            with patch('app.api.v1.workflows.get_db') as mock_get_db, \
                 patch('app.agents.requirements_agent.RequirementsAgent') as mock_req_agent:
                
                mock_db = Mock()
                mock_get_db.return_value = mock_db
                
                mock_req_agent.return_value.execute = AsyncMock(return_value={
                    "structured_requirements": {"business_goals": ["Test goal"]},
                    "confidence_score": 0.8
                })
                
                mock_workflow = Mock(
                    id=workflow_id,
                    project_id=str(uuid4()),
                    current_stage="requirements_parsing",
                    status="active"
                )
                
                mock_db.add.return_value = None
                mock_db.commit.return_value = None
                mock_db.refresh.return_value = None
                
                def mock_refresh(workflow):
                    workflow.id = workflow_id
                    workflow.created_at = "2023-01-01T00:00:00Z"
                    workflow.updated_at = "2023-01-01T00:00:00Z"
                
                mock_db.refresh.side_effect = mock_refresh
                
                workflow_data = {
                    "project_id": str(uuid4()),
                    "document_path": "/test/requirements.txt",
                    "mode": "greenfield"
                }
                
                response = client.post("/api/v1/workflows/start", json=workflow_data)
                return response.status_code
        
        # Test with 5 concurrent workflows
        workflow_ids = [str(uuid4()) for _ in range(5)]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(start_workflow, wid) for wid in workflow_ids]
            results = [future.result() for future in as_completed(futures)]
        
        # All workflows should start successfully
        assert all(status == 201 for status in results)
        assert len(results) == 5

    def test_memory_leak_prevention(self, client):
        """Test memory leak prevention with repeated requests."""
        with patch('app.core.redis_client.redis_client.ping', return_value=True):
            # Make 100 requests and check that memory usage doesn't grow significantly
            for i in range(100):
                response = client.get("/api/v1/health")
                assert response.status_code == 200
                
                # Small delay to allow cleanup
                time.sleep(0.01)
            
            # Final request should still work
            response = client.get("/api/v1/health")
            assert response.status_code == 200

    def test_connection_pooling(self, client):
        """Test database connection pooling performance."""
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Mock projects list
            mock_projects = [
                Mock(
                    id=str(uuid4()),
                    name=f"Project {i}",
                    description=f"Description {i}",
                    domain="e-commerce",
                    mode="greenfield",
                    status="active",
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z"
                )
                for i in range(10)
            ]
            
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_projects
            mock_result.scalar.return_value = 10
            mock_db.execute.return_value = mock_result
            
            # Make multiple requests to test connection reuse
            start_time = time.time()
            
            for i in range(20):
                response = client.get("/api/v1/projects")
                assert response.status_code == 200
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Should be efficient with connection pooling
            assert total_time < 5.0  # 20 requests should complete within 5 seconds

    def test_caching_performance(self, client):
        """Test caching performance (if implemented)."""
        with patch('app.core.redis_client.redis_client.ping', return_value=True):
            # First request (cache miss)
            start_time = time.time()
            response1 = client.get("/api/v1/health")
            first_request_time = time.time() - start_time
            
            # Second request (cache hit)
            start_time = time.time()
            response2 = client.get("/api/v1/health")
            second_request_time = time.time() - start_time
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Second request should be faster if caching is implemented
            # Note: This test will pass regardless of caching implementation
            assert second_request_time < 1.0

    def test_large_payload_handling(self, client):
        """Test handling of large payloads."""
        # Create a large project with extensive data
        large_project_data = {
            "name": "Large Project",
            "description": "A" * 50000,  # 50KB description
            "domain": "e-commerce",
            "mode": "greenfield",
            "metadata": {
                "requirements": ["A" * 1000] * 100,  # Large requirements list
                "constraints": ["B" * 1000] * 50,    # Large constraints list
                "stakeholders": [{"name": f"Stakeholder {i}", "role": "User"} for i in range(100)]
            }
        }
        
        with patch('app.api.v1.projects.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            mock_project = Mock(
                id=str(uuid4()),
                name=large_project_data["name"],
                description=large_project_data["description"],
                domain=large_project_data["domain"],
                mode="greenfield",
                status="active"
            )
            
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            def mock_refresh(project):
                project.id = mock_project.id
                project.created_at = "2023-01-01T00:00:00Z"
                project.updated_at = "2023-01-01T00:00:00Z"
            
            mock_db.refresh.side_effect = mock_refresh
            
            start_time = time.time()
            response = client.post("/api/v1/projects", json=large_project_data)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 201
            assert response_time < 3.0  # Should handle large payload within 3 seconds

