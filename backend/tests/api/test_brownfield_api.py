"""
API tests for the Brownfield endpoints.

These tests verify the REST API endpoints for brownfield analysis
and knowledge base operations.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from uuid import uuid4
import json

from app.main import app
from app.schemas.brownfield import (
    RepositoryAnalysisRequest,
    RepositoryAnalysisResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse
)


class TestBrownfieldAPI:
    """Test the Brownfield API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_project_id(self):
        """Sample project ID for testing."""
        return str(uuid4())

    @pytest.fixture
    def sample_repository_analysis_request(self, sample_project_id):
        """Sample repository analysis request."""
        return {
            'project_id': sample_project_id,
            'repository_url': 'https://github.com/test/repo',
            'branch': 'main',
            'github_token': 'ghp_test_token'
        }

    @pytest.fixture
    def sample_knowledge_search_request(self, sample_project_id):
        """Sample knowledge search request."""
        return {
            'query': 'microservices architecture with Node.js',
            'project_id': sample_project_id,
            'top_k': 5
        }

    @pytest.fixture
    def mock_github_analyzer(self):
        """Mock GitHub analyzer agent."""
        mock_analyzer = Mock()
        mock_analyzer.execute = AsyncMock(return_value={
            'repository_url': 'https://github.com/test/repo',
            'services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'type': 'service',
                    'technology': 'Node.js',
                    'description': 'User management service'
                }
            ],
            'dependencies': [],
            'technology_stack': {'Node.js': 1},
            'quality_score': 0.85,
            'analysis_metadata': {
                'analyzed_at': '2023-01-01T00:00:00Z',
                'services_count': 1,
                'dependencies_count': 0,
                'technologies_detected': ['Node.js']
            }
        })
        return mock_analyzer

    @pytest.fixture
    def mock_kb_service(self):
        """Mock knowledge base service."""
        mock_kb = Mock()
        mock_kb.index_repository_analysis = AsyncMock(return_value={
            'indexed_chunks': 10,
            'created_nodes': 5,
            'created_relationships': 3
        })
        mock_kb.search_similar_architectures = AsyncMock(return_value=[
            {
                'id': 'chunk-1',
                'similarity_score': 0.95,
                'metadata': {
                    'project_id': 'test-project',
                    'chunk_type': 'architecture',
                    'content': 'Microservices architecture with Node.js'
                }
            }
        ])
        mock_kb.get_service_dependencies = AsyncMock(return_value=[
            {
                'service': {'name': 'user-service', 'technology': 'Node.js'},
                'dependencies': [
                    {'name': 'user-database', 'type': 'database-call'}
                ]
            }
        ])
        mock_kb.get_context_for_new_feature = AsyncMock(return_value={
            'similar_features': [
                {
                    'feature_name': 'user-notifications',
                    'implementation_approach': 'event-driven',
                    'technologies_used': ['Node.js', 'Kafka']
                }
            ],
            'existing_services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'technology': 'Node.js'
                }
            ],
            'integration_patterns': [
                {
                    'pattern': 'event-driven',
                    'description': 'Use message queues for async communication'
                }
            ],
            'recommendations': [
                'Use event-driven architecture for notifications',
                'Implement message queues for reliability'
            ]
        })
        return mock_kb

    @patch('app.api.v1.brownfield.GitHubAnalyzerAgent')
    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_analyze_repository_success(self, mock_kb_class, mock_github_class, 
                                       client, sample_repository_analysis_request, 
                                       mock_github_analyzer, mock_kb_service):
        """Test successful repository analysis."""
        # Setup mocks
        mock_github_class.return_value = mock_github_analyzer
        mock_kb_class.return_value = mock_kb_service
        
        response = client.post(
            '/api/v1/brownfield/analyze-repository',
            json=sample_repository_analysis_request
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data['status'] == 'accepted'
        assert 'task_id' in data
        assert data['message'] == 'Repository analysis started'

    def test_analyze_repository_invalid_url(self, client, sample_project_id):
        """Test repository analysis with invalid URL."""
        request_data = {
            'project_id': sample_project_id,
            'repository_url': 'invalid-url',
            'branch': 'main'
        }
        
        response = client.post(
            '/api/v1/brownfield/analyze-repository',
            json=request_data
        )
        
        assert response.status_code == 422  # Validation error

    def test_analyze_repository_missing_project_id(self, client):
        """Test repository analysis without project ID."""
        request_data = {
            'repository_url': 'https://github.com/test/repo',
            'branch': 'main'
        }
        
        response = client.post(
            '/api/v1/brownfield/analyze-repository',
            json=request_data
        )
        
        assert response.status_code == 422  # Validation error

    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_search_knowledge_success(self, mock_kb_class, client, 
                                    sample_knowledge_search_request, mock_kb_service):
        """Test successful knowledge search."""
        # Setup mock
        mock_kb_class.return_value = mock_kb_service
        
        response = client.post(
            '/api/v1/brownfield/search-knowledge',
            json=sample_knowledge_search_request
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['query'] == sample_knowledge_search_request['query']
        assert 'results' in data
        assert len(data['results']) > 0

    def test_search_knowledge_missing_query(self, client, sample_project_id):
        """Test knowledge search without query."""
        request_data = {
            'project_id': sample_project_id,
            'top_k': 5
        }
        
        response = client.post(
            '/api/v1/brownfield/search-knowledge',
            json=request_data
        )
        
        assert response.status_code == 422  # Validation error

    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_get_architecture_graph_success(self, mock_kb_class, client, 
                                          sample_project_id, mock_kb_service):
        """Test successful architecture graph retrieval."""
        # Setup mock
        mock_kb_class.return_value = mock_kb_service
        
        response = client.get(f'/api/v1/brownfield/project/{sample_project_id}/architecture-graph')
        
        assert response.status_code == 200
        data = response.json()
        assert 'nodes' in data
        assert 'edges' in data
        assert 'metadata' in data

    def test_get_architecture_graph_invalid_project_id(self, client):
        """Test architecture graph with invalid project ID."""
        response = client.get('/api/v1/brownfield/project/invalid-id/architecture-graph')
        
        assert response.status_code == 422  # Validation error

    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_get_project_context_success(self, mock_kb_class, client, 
                                       sample_project_id, mock_kb_service):
        """Test successful project context retrieval."""
        # Setup mock
        mock_kb_class.return_value = mock_kb_service
        
        response = client.get(f'/api/v1/brownfield/project/{sample_project_id}/context')
        
        assert response.status_code == 200
        data = response.json()
        assert 'project_id' in data
        assert 'context' in data
        assert 'similar_features' in data['context']
        assert 'existing_services' in data['context']
        assert 'integration_patterns' in data['context']
        assert 'recommendations' in data['context']

    def test_get_project_context_invalid_project_id(self, client):
        """Test project context with invalid project ID."""
        response = client.get('/api/v1/brownfield/project/invalid-id/context')
        
        assert response.status_code == 422  # Validation error

    @patch('app.api.v1.brownfield.GitHubAnalyzerAgent')
    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_analyze_repository_background_task(self, mock_kb_class, mock_github_class,
                                               sample_repository_analysis_request,
                                               mock_github_analyzer, mock_kb_service):
        """Test the background task for repository analysis."""
        from app.api.v1.brownfield import index_analysis_results
        
        # Setup mocks
        mock_github_class.return_value = mock_github_analyzer
        mock_kb_class.return_value = mock_kb_service
        
        # Mock the analysis result
        analysis_result = {
            'repository_url': 'https://github.com/test/repo',
            'services': [],
            'dependencies': [],
            'technology_stack': {},
            'quality_score': 0.85,
            'analysis_metadata': {
                'analyzed_at': '2023-01-01T00:00:00Z',
                'services_count': 0,
                'dependencies_count': 0,
                'technologies_detected': []
            }
        }
        
        # Test the background task
        result = index_analysis_results(
            sample_repository_analysis_request['project_id'],
            analysis_result
        )
        
        # Verify knowledge base indexing was called
        mock_kb_service.index_repository_analysis.assert_called_once()

    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_search_knowledge_with_filters(self, mock_kb_class, client, 
                                         sample_project_id, mock_kb_service):
        """Test knowledge search with filters."""
        # Setup mock
        mock_kb_class.return_value = mock_kb_service
        
        request_data = {
            'query': 'authentication service',
            'project_id': sample_project_id,
            'top_k': 3,
            'filters': {
                'chunk_type': 'service',
                'technologies': ['Node.js']
            }
        }
        
        response = client.post(
            '/api/v1/brownfield/search-knowledge',
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['query'] == request_data['query']
        assert 'results' in data

    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_search_knowledge_error_handling(self, mock_kb_class, client, 
                                           sample_knowledge_search_request):
        """Test knowledge search error handling."""
        # Setup mock to raise an exception
        mock_kb_service = Mock()
        mock_kb_service.search_similar_architectures = AsyncMock(
            side_effect=Exception('Search failed')
        )
        mock_kb_class.return_value = mock_kb_service
        
        response = client.post(
            '/api/v1/brownfield/search-knowledge',
            json=sample_knowledge_search_request
        )
        
        assert response.status_code == 500
        data = response.json()
        assert 'error' in data

    @patch('app.api.v1.brownfield.GitHubAnalyzerAgent')
    def test_analyze_repository_error_handling(self, mock_github_class, client,
                                             sample_repository_analysis_request):
        """Test repository analysis error handling."""
        # Setup mock to raise an exception
        mock_github_analyzer = Mock()
        mock_github_analyzer.execute = AsyncMock(
            side_effect=Exception('Analysis failed')
        )
        mock_github_class.return_value = mock_github_analyzer
        
        response = client.post(
            '/api/v1/brownfield/analyze-repository',
            json=sample_repository_analysis_request
        )
        
        assert response.status_code == 202  # Still accepted, but task will fail
        data = response.json()
        assert data['status'] == 'accepted'

    def test_analyze_repository_validation(self, client, sample_project_id):
        """Test repository analysis request validation."""
        # Test with empty request
        response = client.post('/api/v1/brownfield/analyze-repository', json={})
        assert response.status_code == 422
        
        # Test with invalid branch name
        request_data = {
            'project_id': sample_project_id,
            'repository_url': 'https://github.com/test/repo',
            'branch': ''  # Empty branch name
        }
        response = client.post('/api/v1/brownfield/analyze-repository', json=request_data)
        assert response.status_code == 422

    def test_search_knowledge_validation(self, client, sample_project_id):
        """Test knowledge search request validation."""
        # Test with empty query
        request_data = {
            'project_id': sample_project_id,
            'query': '',  # Empty query
            'top_k': 5
        }
        response = client.post('/api/v1/brownfield/search-knowledge', json=request_data)
        assert response.status_code == 422
        
        # Test with invalid top_k
        request_data = {
            'project_id': sample_project_id,
            'query': 'test query',
            'top_k': -1  # Invalid top_k
        }
        response = client.post('/api/v1/brownfield/search-knowledge', json=request_data)
        assert response.status_code == 422

    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_get_architecture_graph_empty_result(self, mock_kb_class, client, 
                                               sample_project_id):
        """Test architecture graph with empty result."""
        # Setup mock to return empty result
        mock_kb_service = Mock()
        mock_kb_service.get_service_dependencies = AsyncMock(return_value=[])
        mock_kb_class.return_value = mock_kb_service
        
        response = client.get(f'/api/v1/brownfield/project/{sample_project_id}/architecture-graph')
        
        assert response.status_code == 200
        data = response.json()
        assert data['nodes'] == []
        assert data['edges'] == []

    @patch('app.api.v1.brownfield.KnowledgeBaseService')
    def test_get_project_context_empty_result(self, mock_kb_class, client, 
                                            sample_project_id):
        """Test project context with empty result."""
        # Setup mock to return empty result
        mock_kb_service = Mock()
        mock_kb_service.get_context_for_new_feature = AsyncMock(return_value={
            'similar_features': [],
            'existing_services': [],
            'integration_patterns': [],
            'recommendations': []
        })
        mock_kb_class.return_value = mock_kb_service
        
        response = client.get(f'/api/v1/brownfield/project/{sample_project_id}/context')
        
        assert response.status_code == 200
        data = response.json()
        assert data['context']['similar_features'] == []
        assert data['context']['existing_services'] == []
        assert data['context']['integration_patterns'] == []
        assert data['context']['recommendations'] == []

    def test_api_endpoints_exist(self, client):
        """Test that all brownfield API endpoints exist."""
        # Test analyze repository endpoint
        response = client.post('/api/v1/brownfield/analyze-repository', json={})
        assert response.status_code in [422, 500]  # Should not be 404
        
        # Test search knowledge endpoint
        response = client.post('/api/v1/brownfield/search-knowledge', json={})
        assert response.status_code in [422, 500]  # Should not be 404
        
        # Test architecture graph endpoint
        response = client.get('/api/v1/brownfield/project/test/architecture-graph')
        assert response.status_code in [200, 422, 500]  # Should not be 404
        
        # Test project context endpoint
        response = client.get('/api/v1/brownfield/project/test/context')
        assert response.status_code in [200, 422, 500]  # Should not be 404
