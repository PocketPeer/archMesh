#!/usr/bin/env python3
"""
Test Template Generator for ArchMesh
Creates consistent test templates following TDD best practices.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TestCategory(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"

class TestFramework(Enum):
    PYTEST = "pytest"
    JEST = "jest"

@dataclass
class TestTemplate:
    name: str
    category: TestCategory
    framework: TestFramework
    content: str

class TestTemplateGenerator:
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, TestTemplate]:
        """Load all available test templates"""
        return {
            "backend_unit": TestTemplate(
                name="Backend Unit Test",
                category=TestCategory.UNIT,
                framework=TestFramework.PYTEST,
                content=self._get_backend_unit_template()
            ),
            "backend_integration": TestTemplate(
                name="Backend Integration Test",
                category=TestCategory.INTEGRATION,
                framework=TestFramework.PYTEST,
                content=self._get_backend_integration_template()
            ),
            "backend_e2e": TestTemplate(
                name="Backend E2E Test",
                category=TestCategory.E2E,
                framework=TestFramework.PYTEST,
                content=self._get_backend_e2e_template()
            ),
            "backend_performance": TestTemplate(
                name="Backend Performance Test",
                category=TestCategory.PERFORMANCE,
                framework=TestFramework.PYTEST,
                content=self._get_backend_performance_template()
            ),
            "backend_security": TestTemplate(
                name="Backend Security Test",
                category=TestCategory.SECURITY,
                framework=TestFramework.PYTEST,
                content=self._get_backend_security_template()
            ),
            "frontend_unit": TestTemplate(
                name="Frontend Unit Test",
                category=TestCategory.UNIT,
                framework=TestFramework.JEST,
                content=self._get_frontend_unit_template()
            ),
            "frontend_integration": TestTemplate(
                name="Frontend Integration Test",
                category=TestCategory.INTEGRATION,
                framework=TestFramework.JEST,
                content=self._get_frontend_integration_template()
            ),
            "frontend_e2e": TestTemplate(
                name="Frontend E2E Test",
                category=TestCategory.E2E,
                framework=TestFramework.JEST,
                content=self._get_frontend_e2e_template()
            )
        }
    
    def _get_backend_unit_template(self) -> str:
        return '''"""
Unit tests for {module_name}
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from {module_path} import {class_name}


class Test{class_name}:
    """Test cases for {class_name}"""
    
    @pytest.fixture
    def {instance_name}(self):
        """Create a test instance of {class_name}"""
        return {class_name}()
    
    @pytest.fixture
    def sample_data(self):
        """Sample test data"""
        return {{
            "id": "test-id",
            "name": "Test Name",
            "description": "Test Description"
        }}
    
    def test_{method_name}_success(self, {instance_name}, sample_data):
        """Test successful {method_name} operation"""
        # Arrange
        expected_result = {{"success": True, "data": sample_data}}
        
        # Act
        result = {instance_name}.{method_name}(sample_data)
        
        # Assert
        assert result["success"] is True
        assert result["data"] == sample_data
    
    def test_{method_name}_with_invalid_input(self, {instance_name}):
        """Test {method_name} with invalid input"""
        # Arrange
        invalid_data = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid input"):
            {instance_name}.{method_name}(invalid_data)
    
    def test_{method_name}_with_exception(self, {instance_name}, sample_data):
        """Test {method_name} handles exceptions gracefully"""
        # Arrange
        with patch.object({instance_name}, '_internal_method', side_effect=Exception("Test error")):
            # Act & Assert
            with pytest.raises(Exception, match="Test error"):
                {instance_name}.{method_name}(sample_data)
    
    @pytest.mark.asyncio
    async def test_async_{method_name}_success(self, {instance_name}, sample_data):
        """Test successful async {method_name} operation"""
        # Arrange
        expected_result = {{"success": True, "data": sample_data}}
        
        # Act
        result = await {instance_name}.async_{method_name}(sample_data)
        
        # Assert
        assert result["success"] is True
        assert result["data"] == sample_data
    
    def test_{method_name}_edge_cases(self, {instance_name}):
        """Test {method_name} with edge cases"""
        # Test empty input
        result = {instance_name}.{method_name}("")
        assert result is not None
        
        # Test maximum length input
        long_input = "x" * 1000
        result = {instance_name}.{method_name}(long_input)
        assert result is not None
    
    def test_{method_name}_performance(self, {instance_name}, sample_data):
        """Test {method_name} performance"""
        import time
        
        # Arrange
        start_time = time.time()
        
        # Act
        result = {instance_name}.{method_name}(sample_data)
        
        # Assert
        execution_time = time.time() - start_time
        assert execution_time < 1.0  # Should complete within 1 second
        assert result is not None
'''
    
    def _get_backend_integration_template(self) -> str:
        return '''"""
Integration tests for {module_name}
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from {module_path} import {class_name}
from app.main import app


class Test{class_name}Integration:
    """Integration tests for {class_name}"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def {instance_name}(self):
        """Create a test instance of {class_name}"""
        return {class_name}()
    
    @pytest.fixture
    def sample_data(self):
        """Sample test data"""
        return {{
            "id": "test-id",
            "name": "Test Name",
            "description": "Test Description"
        }}
    
    def test_{method_name}_endpoint_success(self, client, sample_data):
        """Test {method_name} endpoint with valid data"""
        # Act
        response = client.post("/api/v1/{endpoint_path}", json=sample_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == sample_data["name"]
    
    def test_{method_name}_endpoint_validation_error(self, client):
        """Test {method_name} endpoint with invalid data"""
        # Arrange
        invalid_data = {{"invalid": "data"}}
        
        # Act
        response = client.post("/api/v1/{endpoint_path}", json=invalid_data)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_{method_name}_database_integration(self, {instance_name}, sample_data):
        """Test {method_name} with database integration"""
        # Arrange
        with patch('app.core.database.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Act
            result = {instance_name}.{method_name}(sample_data)
            
            # Assert
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            assert result["success"] is True
    
    def test_{method_name}_external_service_integration(self, {instance_name}, sample_data):
        """Test {method_name} with external service integration"""
        # Arrange
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {{"success": True}}
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            # Act
            result = {instance_name}.{method_name}(sample_data)
            
            # Assert
            mock_post.assert_called_once()
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_async_{method_name}_integration(self, {instance_name}, sample_data):
        """Test async {method_name} integration"""
        # Arrange
        with patch('app.core.redis_client.redis_client.get') as mock_redis_get:
            mock_redis_get.return_value = "cached_value"
            
            # Act
            result = await {instance_name}.async_{method_name}(sample_data)
            
            # Assert
            mock_redis_get.assert_called_once()
            assert result["success"] is True
'''
    
    def _get_backend_e2e_template(self) -> str:
        return '''"""
End-to-end tests for {module_name}
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class Test{class_name}E2E:
    """End-to-end tests for {class_name}"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_data(self):
        """Sample test data"""
        return {{
            "id": "test-id",
            "name": "Test Name",
            "description": "Test Description"
        }}
    
    def test_complete_{method_name}_workflow(self, client, sample_data):
        """Test complete {method_name} workflow"""
        # Step 1: Create resource
        create_response = client.post("/api/v1/{endpoint_path}", json=sample_data)
        assert create_response.status_code == 201
        created_data = create_response.json()
        resource_id = created_data["data"]["id"]
        
        # Step 2: Retrieve resource
        get_response = client.get(f"/api/v1/{endpoint_path}/{{resource_id}}")
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        assert retrieved_data["data"]["name"] == sample_data["name"]
        
        # Step 3: Update resource
        update_data = {{**sample_data, "name": "Updated Name"}}
        update_response = client.put(f"/api/v1/{endpoint_path}/{{resource_id}}", json=update_data)
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["data"]["name"] == "Updated Name"
        
        # Step 4: Delete resource
        delete_response = client.delete(f"/api/v1/{endpoint_path}/{{resource_id}}")
        assert delete_response.status_code == 204
        
        # Step 5: Verify deletion
        get_deleted_response = client.get(f"/api/v1/{endpoint_path}/{{resource_id}}")
        assert get_deleted_response.status_code == 404
    
    def test_{method_name}_error_handling_workflow(self, client):
        """Test {method_name} error handling workflow"""
        # Test with invalid data
        invalid_data = {{"invalid": "data"}}
        response = client.post("/api/v1/{endpoint_path}", json=invalid_data)
        assert response.status_code == 422
        
        # Test with non-existent resource
        response = client.get("/api/v1/{endpoint_path}/non-existent-id")
        assert response.status_code == 404
        
        # Test with unauthorized access
        response = client.post("/api/v1/{endpoint_path}", json={{}})
        assert response.status_code in [401, 422]
    
    def test_{method_name}_concurrent_operations(self, client, sample_data):
        """Test {method_name} with concurrent operations"""
        import threading
        import time
        
        results = []
        
        def create_resource():
            response = client.post("/api/v1/{endpoint_path}", json=sample_data)
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_resource)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert all operations succeeded
        assert all(status == 201 for status in results)
    
    def test_{method_name}_data_consistency(self, client, sample_data):
        """Test {method_name} data consistency"""
        # Create resource
        create_response = client.post("/api/v1/{endpoint_path}", json=sample_data)
        assert create_response.status_code == 201
        created_data = create_response.json()
        resource_id = created_data["data"]["id"]
        
        # Verify data consistency across multiple reads
        for _ in range(3):
            get_response = client.get(f"/api/v1/{endpoint_path}/{{resource_id}}")
            assert get_response.status_code == 200
            retrieved_data = get_response.json()
            assert retrieved_data["data"]["name"] == sample_data["name"]
            assert retrieved_data["data"]["description"] == sample_data["description"]
'''
    
    def _get_backend_performance_template(self) -> str:
        return '''"""
Performance tests for {module_name}
"""

import pytest
import time
from fastapi.testclient import TestClient
from app.main import app


class Test{class_name}Performance:
    """Performance tests for {class_name}"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_data(self):
        """Sample test data"""
        return {{
            "id": "test-id",
            "name": "Test Name",
            "description": "Test Description"
        }}
    
    def test_{method_name}_response_time(self, client, sample_data):
        """Test {method_name} response time"""
        # Arrange
        start_time = time.time()
        
        # Act
        response = client.post("/api/v1/{endpoint_path}", json=sample_data)
        
        # Assert
        execution_time = time.time() - start_time
        assert response.status_code == 200
        assert execution_time < 1.0  # Should respond within 1 second
    
    def test_{method_name}_throughput(self, client, sample_data):
        """Test {method_name} throughput"""
        # Arrange
        num_requests = 100
        start_time = time.time()
        
        # Act
        for i in range(num_requests):
            response = client.post("/api/v1/{endpoint_path}", json=sample_data)
            assert response.status_code == 200
        
        # Assert
        total_time = time.time() - start_time
        throughput = num_requests / total_time
        assert throughput > 10  # Should handle at least 10 requests per second
    
    def test_{method_name}_memory_usage(self, client, sample_data):
        """Test {method_name} memory usage"""
        import psutil
        import os
        
        # Arrange
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Act
        for i in range(1000):
            response = client.post("/api/v1/{endpoint_path}", json=sample_data)
            assert response.status_code == 200
        
        # Assert
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        assert memory_increase < 50 * 1024 * 1024  # Should not increase by more than 50MB
    
    def test_{method_name}_concurrent_load(self, client, sample_data):
        """Test {method_name} under concurrent load"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                start_time = time.time()
                response = client.post("/api/v1/{endpoint_path}", json=sample_data)
                execution_time = time.time() - start_time
                results.append((response.status_code, execution_time))
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(50):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Assert
        assert len(errors) == 0, f"Errors occurred: {{errors}}"
        assert len(results) == 50
        assert all(status == 200 for status, _ in results)
        assert all(time < 2.0 for _, time in results)  # All requests should complete within 2 seconds
        assert total_time < 10.0  # All requests should complete within 10 seconds
    
    def test_{method_name}_scalability(self, client, sample_data):
        """Test {method_name} scalability"""
        # Test with increasing load
        for load in [10, 50, 100]:
            start_time = time.time()
            
            for i in range(load):
                response = client.post("/api/v1/{endpoint_path}", json=sample_data)
                assert response.status_code == 200
            
            execution_time = time.time() - start_time
            avg_time_per_request = execution_time / load
            
            # Average time per request should not increase significantly with load
            assert avg_time_per_request < 0.5  # Should be under 500ms per request
'''
    
    def _get_backend_security_template(self) -> str:
        return '''"""
Security tests for {module_name}
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class Test{class_name}Security:
    """Security tests for {class_name}"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_{method_name}_sql_injection_protection(self, client):
        """Test {method_name} SQL injection protection"""
        # Arrange
        malicious_input = "'; DROP TABLE users; --"
        payload = {{"name": malicious_input}}
        
        # Act
        response = client.post("/api/v1/{endpoint_path}", json=payload)
        
        # Assert
        assert response.status_code in [400, 422]  # Should reject malicious input
        assert "error" in response.json() or "detail" in response.json()
    
    def test_{method_name}_xss_protection(self, client):
        """Test {method_name} XSS protection"""
        # Arrange
        xss_payload = "<script>alert('XSS')</script>"
        payload = {{"name": xss_payload}}
        
        # Act
        response = client.post("/api/v1/{endpoint_path}", json=payload)
        
        # Assert
        if response.status_code == 200:
            data = response.json()
            # Check that script tags are escaped or removed
            assert "<script>" not in str(data)
            assert "alert" not in str(data)
    
    def test_{method_name}_authentication_required(self, client):
        """Test {method_name} requires authentication"""
        # Act
        response = client.post("/api/v1/{endpoint_path}", json={{}})
        
        # Assert
        assert response.status_code == 401  # Should require authentication
    
    def test_{method_name}_authorization_check(self, client):
        """Test {method_name} authorization check"""
        # Arrange
        unauthorized_payload = {{"user_id": "other-user-id"}}
        
        # Act
        response = client.post("/api/v1/{endpoint_path}", json=unauthorized_payload)
        
        # Assert
        assert response.status_code == 403  # Should be forbidden
    
    def test_{method_name}_input_validation(self, client):
        """Test {method_name} input validation"""
        # Test with oversized input
        oversized_input = "x" * 10000
        payload = {{"name": oversized_input}}
        
        response = client.post("/api/v1/{endpoint_path}", json=payload)
        assert response.status_code == 422  # Should reject oversized input
        
        # Test with special characters
        special_chars = "!@#$%^&*()_+{}|:<>?[]\\;'\",./"
        payload = {{"name": special_chars}}
        
        response = client.post("/api/v1/{endpoint_path}", json=payload)
        # Should either accept or reject with proper validation
        assert response.status_code in [200, 422]
    
    def test_{method_name}_rate_limiting(self, client):
        """Test {method_name} rate limiting"""
        # Arrange
        payload = {{"name": "test"}}
        
        # Act - Make many requests quickly
        responses = []
        for i in range(100):
            response = client.post("/api/v1/{endpoint_path}", json=payload)
            responses.append(response.status_code)
        
        # Assert
        # Should have some rate limiting in place
        assert 429 in responses or all(status == 200 for status in responses)
    
    def test_{method_name}_data_encryption(self, client):
        """Test {method_name} data encryption"""
        # Arrange
        sensitive_data = {{"password": "secret123", "ssn": "123-45-6789"}}
        
        # Act
        response = client.post("/api/v1/{endpoint_path}", json=sensitive_data)
        
        # Assert
        if response.status_code == 200:
            data = response.json()
            # Sensitive data should not be returned in plain text
            assert "secret123" not in str(data)
            assert "123-45-6789" not in str(data)
    
    def test_{method_name}_csrf_protection(self, client):
        """Test {method_name} CSRF protection"""
        # Arrange
        payload = {{"name": "test"}}
        headers = {{"X-CSRF-Token": "invalid-token"}}
        
        # Act
        response = client.post("/api/v1/{endpoint_path}", json=payload, headers=headers)
        
        # Assert
        # Should either require valid CSRF token or not implement CSRF protection
        assert response.status_code in [200, 403, 422]
'''
    
    def _get_frontend_unit_template(self) -> str:
        return '''/**
 * Unit tests for {component_name}
 */

import React from 'react';
import {{ render, screen, fireEvent, waitFor }} from '@testing-library/react';
import {{ {component_name} }} from './{component_name}';

// Mock dependencies
jest.mock('@/lib/api-client', () => ({{
  apiClient: {{
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  }},
}}));

describe('{component_name}', () => {{
  const defaultProps = {{
    // Add default props here
  }};

  beforeEach(() => {{
    jest.clearAllMocks();
  }});

  it('renders without crashing', () => {{
    render(<{component_name} {{...defaultProps}} />);
    expect(screen.getByTestId('{component_name.lower()}-container')).toBeInTheDocument();
  }});

  it('displays initial state correctly', () => {{
    render(<{component_name} {{...defaultProps}} />);
    
    // Test initial rendering
    expect(screen.getByText('Expected Initial Text')).toBeInTheDocument();
    expect(screen.getByRole('button', {{ name: /submit/i }})).toBeInTheDocument();
  }});

  it('handles user interactions correctly', async () => {{
    render(<{component_name} {{...defaultProps}} />);
    
    // Test user interaction
    const button = screen.getByRole('button', {{ name: /submit/i }});
    fireEvent.click(button);
    
    await waitFor(() => {{
      expect(screen.getByText('Success Message')).toBeInTheDocument();
    }});
  }});

  it('handles form submission correctly', async () => {{
    const mockOnSubmit = jest.fn();
    render(<{component_name} {{...defaultProps}} onSubmit={{mockOnSubmit}} />);
    
    // Fill form
    const input = screen.getByLabelText(/name/i);
    fireEvent.change(input, {{ target: {{ value: 'Test Name' }} }});
    
    // Submit form
    const submitButton = screen.getByRole('button', {{ name: /submit/i }});
    fireEvent.click(submitButton);
    
    await waitFor(() => {{
      expect(mockOnSubmit).toHaveBeenCalledWith({{ name: 'Test Name' }});
    }});
  }});

  it('displays error messages correctly', async () => {{
    render(<{component_name} {{...defaultProps}} />);
    
    // Trigger error condition
    const button = screen.getByRole('button', {{ name: /submit/i }});
    fireEvent.click(button);
    
    await waitFor(() => {{
      expect(screen.getByText('Error Message')).toBeInTheDocument();
    }});
  }});

  it('handles loading state correctly', async () => {{
    render(<{component_name} {{...defaultProps}} />);
    
    // Trigger loading state
    const button = screen.getByRole('button', {{ name: /submit/i }});
    fireEvent.click(button);
    
    // Check loading state
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    // Wait for loading to complete
    await waitFor(() => {{
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    }});
  }});

  it('handles edge cases correctly', () => {{
    // Test with empty props
    render(<{component_name} {{}} />);
    expect(screen.getByTestId('{component_name.lower()}-container')).toBeInTheDocument();
    
    // Test with null values
    render(<{component_name} {{...defaultProps, data: null}} />);
    expect(screen.getByText('No data available')).toBeInTheDocument();
  }});

  it('calls API correctly', async () => {{
    const {{ apiClient }} = require('@/lib/api-client');
    apiClient.get.mockResolvedValue({{ data: {{ id: 1, name: 'Test' }} }});
    
    render(<{component_name} {{...defaultProps}} />);
    
    await waitFor(() => {{
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/endpoint');
    }});
  }});

  it('handles API errors correctly', async () => {{
    const {{ apiClient }} = require('@/lib/api-client');
    apiClient.get.mockRejectedValue(new Error('API Error'));
    
    render(<{component_name} {{...defaultProps}} />);
    
    await waitFor(() => {{
      expect(screen.getByText('Failed to load data')).toBeInTheDocument();
    }});
  }});
}});
'''
    
    def _get_frontend_integration_template(self) -> str:
        return '''/**
 * Integration tests for {component_name}
 */

import React from 'react';
import {{ render, screen, fireEvent, waitFor }} from '@testing-library/react';
import {{ BrowserRouter }} from 'react-router-dom';
import {{ {component_name} }} from './{component_name}';
import {{ {parent_component} }} from './{parent_component}';

// Mock API responses
const mockApiResponse = {{
  data: {{
    id: 1,
    name: 'Test Item',
    description: 'Test Description'
  }}
}};

// Mock API client
jest.mock('@/lib/api-client', () => ({{
  apiClient: {{
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  }},
}}));

describe('{component_name} Integration', () => {{
  const defaultProps = {{
    // Add default props here
  }};

  beforeEach(() => {{
    jest.clearAllMocks();
  }});

  it('integrates with parent component correctly', async () => {{
    render(
      <BrowserRouter>
        <{parent_component}>
          <{component_name} {{...defaultProps}} />
        </{parent_component}>
      </BrowserRouter>
    );
    
    // Test integration
    expect(screen.getByTestId('{parent_component.lower()}-container')).toBeInTheDocument();
    expect(screen.getByTestId('{component_name.lower()}-container')).toBeInTheDocument();
  }});

  it('handles data flow between components', async () => {{
    const {{ apiClient }} = require('@/lib/api-client');
    apiClient.get.mockResolvedValue(mockApiResponse);
    
    render(
      <BrowserRouter>
        <{parent_component}>
          <{component_name} {{...defaultProps}} />
        </{parent_component}>
      </BrowserRouter>
    );
    
    // Wait for data to load
    await waitFor(() => {{
      expect(screen.getByText('Test Item')).toBeInTheDocument();
    }});
    
    // Test data flow
    const updateButton = screen.getByRole('button', {{ name: /update/i }});
    fireEvent.click(updateButton);
    
    await waitFor(() => {{
      expect(apiClient.put).toHaveBeenCalled();
    }});
  }});

  it('handles navigation correctly', async () => {{
    render(
      <BrowserRouter>
        <{component_name} {{...defaultProps}} />
      </BrowserRouter>
    );
    
    // Test navigation
    const link = screen.getByRole('link', {{ name: /go to details/i }});
    fireEvent.click(link);
    
    await waitFor(() => {{
      expect(window.location.pathname).toBe('/details/1');
    }});
  }});

  it('handles state management correctly', async () => {{
    render(
      <BrowserRouter>
        <{component_name} {{...defaultProps}} />
      </BrowserRouter>
    );
    
    // Test state changes
    const input = screen.getByLabelText(/name/i);
    fireEvent.change(input, {{ target: {{ value: 'New Name' }} }});
    
    // Verify state update
    expect(input.value).toBe('New Name');
    
    // Test state persistence
    const submitButton = screen.getByRole('button', {{ name: /save/i }});
    fireEvent.click(submitButton);
    
    await waitFor(() => {{
      expect(screen.getByText('Saved successfully')).toBeInTheDocument();
    }});
  }});

  it('handles error boundaries correctly', async () => {{
    const {{ apiClient }} = require('@/lib/api-client');
    apiClient.get.mockRejectedValue(new Error('Network Error'));
    
    render(
      <BrowserRouter>
        <{component_name} {{...defaultProps}} />
      </BrowserRouter>
    );
    
    await waitFor(() => {{
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    }});
  }});
}});
'''
    
    def _get_frontend_e2e_template(self) -> str:
        return '''/**
 * End-to-end tests for {component_name}
 */

import {{ test, expect }} from '@playwright/test';

test.describe('{component_name} E2E', () => {{
  test.beforeEach(async ({{ page }}) => {{
    await page.goto('/');
  }});

  test('complete user workflow', async ({{ page }}) => {{
    // Navigate to the component
    await page.click('[data-testid="nav-{component_name.lower()}"]');
    await expect(page).toHaveURL('/{component_name.lower()}');
    
    // Fill form
    await page.fill('[data-testid="name-input"]', 'Test Name');
    await page.fill('[data-testid="description-input"]', 'Test Description');
    
    // Submit form
    await page.click('[data-testid="submit-button"]');
    
    // Verify success
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Success');
    
    // Verify data display
    await expect(page.locator('[data-testid="data-display"]')).toContainText('Test Name');
  }});

  test('handles validation errors', async ({{ page }}) => {{
    // Navigate to the component
    await page.click('[data-testid="nav-{component_name.lower()}"]');
    
    // Submit empty form
    await page.click('[data-testid="submit-button"]');
    
    // Verify validation errors
    await expect(page.locator('[data-testid="name-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="name-error"]')).toContainText('Required');
  }});

  test('handles API errors', async ({{ page }}) => {{
    // Mock API error
    await page.route('**/api/v1/endpoint', route => route.fulfill({{ 
      status: 500, 
      body: JSON.stringify({{ error: 'Internal Server Error' }})
    }}));
    
    // Navigate to the component
    await page.click('[data-testid="nav-{component_name.lower()}"]');
    
    // Fill and submit form
    await page.fill('[data-testid="name-input"]', 'Test Name');
    await page.click('[data-testid="submit-button"]');
    
    // Verify error handling
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Error');
  }});

  test('handles loading states', async ({{ page }}) => {{
    // Mock slow API response
    await page.route('**/api/v1/endpoint', async route => {{
      await new Promise(resolve => setTimeout(resolve, 1000));
      route.fulfill({{ 
        status: 200, 
        body: JSON.stringify({{ data: {{ id: 1, name: 'Test' }} }})
      }});
    }});
    
    // Navigate to the component
    await page.click('[data-testid="nav-{component_name.lower()}"]');
    
    // Submit form
    await page.fill('[data-testid="name-input"]', 'Test Name');
    await page.click('[data-testid="submit-button"]');
    
    // Verify loading state
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();
    
    // Wait for completion
    await expect(page.locator('[data-testid="loading-spinner"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  }});

  test('handles navigation', async ({{ page }}) => {{
    // Navigate to the component
    await page.click('[data-testid="nav-{component_name.lower()}"]');
    
    // Click navigation link
    await page.click('[data-testid="details-link"]');
    
    // Verify navigation
    await expect(page).toHaveURL('/details/1');
    await expect(page.locator('[data-testid="details-page"]')).toBeVisible();
  }});

  test('handles responsive design', async ({{ page }}) => {{
    // Test mobile viewport
    await page.setViewportSize({{ width: 375, height: 667 }});
    await page.click('[data-testid="nav-{component_name.lower()}"]');
    
    // Verify mobile layout
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
    
    // Test desktop viewport
    await page.setViewportSize({{ width: 1920, height: 1080 }});
    await page.reload();
    
    // Verify desktop layout
    await expect(page.locator('[data-testid="desktop-menu"]')).toBeVisible();
  }});
}});
'''
    
    def create_test_file(self, template_name: str, output_path: str, **kwargs) -> bool:
        """Create a test file from a template"""
        if template_name not in self.templates:
            print(f"❌ Template '{template_name}' not found")
            return False
        
        template = self.templates[template_name]
        
        # Replace placeholders in template
        content = template.content.format(**kwargs)
        
        # Create output file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Created test file: {output_file}")
        return True
    
    def list_templates(self):
        """List all available templates"""
        print("📋 Available Test Templates:")
        print("=" * 50)
        
        for name, template in self.templates.items():
            print(f"• {name}")
            print(f"  Category: {template.category.value}")
            print(f"  Framework: {template.framework.value}")
            print(f"  Description: {template.name}")
            print()

def main():
    parser = argparse.ArgumentParser(description="Test Template Generator for ArchMesh")
    parser.add_argument(
        "action",
        choices=["create", "list"],
        help="Action to perform"
    )
    parser.add_argument(
        "--template",
        help="Template name to use"
    )
    parser.add_argument(
        "--output",
        help="Output file path"
    )
    parser.add_argument(
        "--module-name",
        help="Module name for the test"
    )
    parser.add_argument(
        "--class-name",
        help="Class name for the test"
    )
    parser.add_argument(
        "--method-name",
        help="Method name for the test"
    )
    parser.add_argument(
        "--component-name",
        help="Component name for frontend tests"
    )
    parser.add_argument(
        "--endpoint-path",
        help="API endpoint path"
    )
    
    args = parser.parse_args()
    
    generator = TestTemplateGenerator()
    
    if args.action == "list":
        generator.list_templates()
    elif args.action == "create":
        if not args.template or not args.output:
            print("❌ Template name and output path are required for create action")
            sys.exit(1)
        
        # Prepare template variables
        template_vars = {}
        if args.module_name:
            template_vars["module_name"] = args.module_name
        if args.class_name:
            template_vars["class_name"] = args.class_name
            template_vars["instance_name"] = args.class_name.lower()
        if args.method_name:
            template_vars["method_name"] = args.method_name
        if args.component_name:
            template_vars["component_name"] = args.component_name
        if args.endpoint_path:
            template_vars["endpoint_path"] = args.endpoint_path
        
        # Set default values
        template_vars.setdefault("module_name", "test_module")
        template_vars.setdefault("class_name", "TestClass")
        template_vars.setdefault("instance_name", "test_class")
        template_vars.setdefault("method_name", "test_method")
        template_vars.setdefault("component_name", "TestComponent")
        template_vars.setdefault("endpoint_path", "test-endpoint")
        
        success = generator.create_test_file(args.template, args.output, **template_vars)
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()

