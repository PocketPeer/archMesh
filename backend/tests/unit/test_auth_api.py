"""
Unit tests for Authentication API endpoints - TDD Implementation
Following Red-Green-Refactor cycle for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class TestAuthAPI:
    """Test cases for Authentication API endpoints - TDD Implementation"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_login_data(self):
        """Sample login data for testing"""
        return {
            "email": "test@example.com",
            "password": "secure_password123"
        }
    
    @pytest.fixture
    def sample_register_data(self):
        """Sample registration data for testing"""
        return {
            "email": "test@example.com",
            "password": "secure_password123",
            "name": "Test User"
        }
    
    @pytest.fixture
    def sample_auth_response(self):
        """Sample authentication response"""
        return {
            "success": True,
            "data": {
                "access_token": "mock_access_token",
                "refresh_token": "mock_refresh_token",
                "user": {
                    "id": "user-123",
                    "email": "test@example.com",
                    "is_active": True,
                    "is_verified": True
                }
            }
        }

    # RED PHASE: Write failing tests first
    
    @pytest.mark.asyncio
    async def test_login_endpoint_success(self, client, sample_login_data, sample_auth_response):
        """Test successful login via API"""
        # Arrange
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.authenticate_user.return_value = sample_auth_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/login", json=sample_login_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "access_token" in data["data"]
            assert "refresh_token" in data["data"]
            assert data["data"]["user"]["email"] == sample_login_data["email"]
    
    @pytest.mark.asyncio
    async def test_login_endpoint_invalid_credentials(self, client, sample_login_data):
        """Test login with invalid credentials via API"""
        # Arrange
        error_response = {
            "success": False,
            "error": "Invalid credentials"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.authenticate_user.return_value = error_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/login", json=sample_login_data)
            
            # Assert
            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert "Invalid credentials" in data["error"]
    
    @pytest.mark.asyncio
    async def test_login_endpoint_missing_fields(self, client):
        """Test login with missing required fields via API"""
        # Arrange
        incomplete_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=incomplete_data)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_login_endpoint_invalid_email_format(self, client):
        """Test login with invalid email format via API"""
        # Arrange
        invalid_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        # Act
        response = client.post("/api/v1/auth/login", json=invalid_data)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_register_endpoint_success(self, client, sample_register_data):
        """Test successful user registration via API"""
        # Arrange
        success_response = {
            "success": True,
            "data": {
                "id": "user-123",
                "email": sample_register_data["email"],
                "is_active": True,
                "is_verified": False
            }
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.register_user.return_value = success_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/register", json=sample_register_data)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert data["data"]["email"] == sample_register_data["email"]
            assert data["data"]["is_verified"] is False
    
    @pytest.mark.asyncio
    async def test_register_endpoint_email_already_exists(self, client, sample_register_data):
        """Test registration with existing email via API"""
        # Arrange
        error_response = {
            "success": False,
            "error": "Email already registered"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.register_user.return_value = error_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/register", json=sample_register_data)
            
            # Assert
            assert response.status_code == 409
            data = response.json()
            assert data["success"] is False
            assert "Email already registered" in data["error"]
    
    @pytest.mark.asyncio
    async def test_register_endpoint_weak_password(self, client):
        """Test registration with weak password via API"""
        # Arrange
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",  # Weak password
            "name": "Test User"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=weak_password_data)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_refresh_token_endpoint_success(self, client):
        """Test successful token refresh via API"""
        # Arrange
        refresh_data = {
            "refresh_token": "valid_refresh_token"
        }
        
        success_response = {
            "success": True,
            "data": {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token"
            }
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.refresh_token.return_value = success_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/refresh", json=refresh_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "access_token" in data["data"]
            assert "refresh_token" in data["data"]
    
    @pytest.mark.asyncio
    async def test_refresh_token_endpoint_invalid_token(self, client):
        """Test token refresh with invalid token via API"""
        # Arrange
        refresh_data = {
            "refresh_token": "invalid_token"
        }
        
        error_response = {
            "success": False,
            "error": "Invalid token"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.refresh_token.return_value = error_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/refresh", json=refresh_data)
            
            # Assert
            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False
            assert "Invalid token" in data["error"]
    
    @pytest.mark.asyncio
    async def test_logout_endpoint_success(self, client):
        """Test successful logout via API"""
        # Arrange
        logout_data = {
            "access_token": "valid_access_token"
        }
        
        success_response = {
            "success": True,
            "message": "Successfully logged out"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.logout_user.return_value = success_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/logout", json=logout_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Successfully logged out"
    
    @pytest.mark.asyncio
    async def test_verify_email_endpoint_success(self, client):
        """Test successful email verification via API"""
        # Arrange
        verify_data = {
            "token": "valid_verification_token"
        }
        
        success_response = {
            "success": True,
            "message": "Email verified successfully"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.verify_email.return_value = success_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/verify-email", json=verify_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Email verified successfully"
    
    @pytest.mark.asyncio
    async def test_verify_email_endpoint_invalid_token(self, client):
        """Test email verification with invalid token via API"""
        # Arrange
        verify_data = {
            "token": "invalid_token"
        }
        
        error_response = {
            "success": False,
            "error": "Invalid verification token"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.verify_email.return_value = error_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/verify-email", json=verify_data)
            
            # Assert
            assert response.status_code == 400
            data = response.json()
            assert data["success"] is False
            assert "Invalid verification token" in data["error"]
    
    @pytest.mark.asyncio
    async def test_change_password_endpoint_success(self, client):
        """Test successful password change via API"""
        # Arrange
        change_password_data = {
            "old_password": "old_password",
            "new_password": "new_secure_password"
        }
        
        success_response = {
            "success": True,
            "message": "Password changed successfully"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.change_password.return_value = success_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/change-password", json=change_password_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Password changed successfully"
    
    @pytest.mark.asyncio
    async def test_change_password_endpoint_invalid_old_password(self, client):
        """Test password change with invalid old password via API"""
        # Arrange
        change_password_data = {
            "old_password": "wrong_password",
            "new_password": "new_secure_password"
        }
        
        error_response = {
            "success": False,
            "error": "Invalid old password"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.change_password.return_value = error_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/change-password", json=change_password_data)
            
            # Assert
            assert response.status_code == 400
            data = response.json()
            assert data["success"] is False
            assert "Invalid old password" in data["error"]
    
    @pytest.mark.asyncio
    async def test_request_password_reset_endpoint_success(self, client):
        """Test successful password reset request via API"""
        # Arrange
        reset_request_data = {
            "email": "test@example.com"
        }
        
        success_response = {
            "success": True,
            "message": "Password reset email sent"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.request_password_reset.return_value = success_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/request-password-reset", json=reset_request_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Password reset email sent"
    
    @pytest.mark.asyncio
    async def test_request_password_reset_endpoint_user_not_found(self, client):
        """Test password reset request for non-existent user via API"""
        # Arrange
        reset_request_data = {
            "email": "nonexistent@example.com"
        }
        
        error_response = {
            "success": False,
            "error": "User not found"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.request_password_reset.return_value = error_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/request-password-reset", json=reset_request_data)
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False
            assert "User not found" in data["error"]
    
    @pytest.mark.asyncio
    async def test_reset_password_endpoint_success(self, client):
        """Test successful password reset via API"""
        # Arrange
        reset_password_data = {
            "token": "valid_reset_token",
            "new_password": "new_secure_password"
        }
        
        success_response = {
            "success": True,
            "message": "Password reset successfully"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.reset_password.return_value = success_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/reset-password", json=reset_password_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Password reset successfully"
    
    @pytest.mark.asyncio
    async def test_reset_password_endpoint_invalid_token(self, client):
        """Test password reset with invalid token via API"""
        # Arrange
        reset_password_data = {
            "token": "invalid_token",
            "new_password": "new_secure_password"
        }
        
        error_response = {
            "success": False,
            "error": "Invalid reset token"
        }
        
        with patch('app.api.v1.auth.AuthService') as mock_auth_service:
            mock_instance = AsyncMock()
            mock_instance.reset_password.return_value = error_response
            mock_auth_service.return_value = mock_instance
            
            # Act
            response = client.post("/api/v1/auth/reset-password", json=reset_password_data)
            
            # Assert
            assert response.status_code == 400
            data = response.json()
            assert data["success"] is False
            assert "Invalid reset token" in data["error"]
    
    @pytest.mark.asyncio
    async def test_reset_password_endpoint_weak_password(self, client):
        """Test password reset with weak password via API"""
        # Arrange
        reset_password_data = {
            "token": "valid_reset_token",
            "new_password": "123"  # Weak password
        }
        
        # Act
        response = client.post("/api/v1/auth/reset-password", json=reset_password_data)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

