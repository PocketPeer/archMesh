"""
Unit tests for AuthService - TDD Implementation
Following Red-Green-Refactor cycle for user authentication
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.core.exceptions import AuthenticationError, ValidationError


class TestAuthService:
    """Test cases for AuthService - TDD Implementation"""
    
    @pytest.fixture
    def auth_service(self):
        """Create a test instance of AuthService"""
        return AuthService()
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return {
            "email": "test@example.com",
            "password": "secure_password123",
            "name": "Test User"
        }
    
    @pytest.fixture
    def sample_user(self, sample_user_data):
        """Create a sample user object"""
        return User(
            id="user-123",
            email=sample_user_data["email"],
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_verified=True
        )

    # RED PHASE: Write failing tests first
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, sample_user_data, sample_user):
        """Test successful user authentication"""
        # Arrange
        with patch.object(auth_service, '_get_user_by_email', return_value=sample_user):
            with patch.object(auth_service, '_verify_password', return_value=True):
                with patch.object(auth_service, '_generate_tokens') as mock_generate:
                    mock_generate.return_value = {
                        "access_token": "mock_access_token",
                        "refresh_token": "mock_refresh_token"
                    }
                    
                    # Act
                    result = await auth_service.authenticate_user(sample_user_data)
                    
                    # Assert
                    assert result["success"] is True
                    assert "access_token" in result["data"]
                    assert "refresh_token" in result["data"]
                    assert result["data"]["user"]["email"] == sample_user_data["email"]
                    assert result["data"]["user"]["id"] == str(sample_user.id)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self, auth_service, sample_user_data):
        """Test authentication with non-existent email"""
        # Arrange
        with patch.object(auth_service, '_get_user_by_email', return_value=None):
            # Act
            result = await auth_service.authenticate_user(sample_user_data)
            
            # Assert
            assert result["success"] is False
            assert "Invalid credentials" in result["error"]
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, auth_service, sample_user_data, sample_user):
        """Test authentication with invalid password"""
        # Arrange
        with patch.object(auth_service, '_get_user_by_email', return_value=sample_user):
            with patch.object(auth_service, '_verify_password', return_value=False):
                # Act
                result = await auth_service.authenticate_user(sample_user_data)
                
                # Assert
                assert result["success"] is False
                assert "Invalid credentials" in result["error"]
    
    def test_authenticate_user_inactive_account(self, auth_service, sample_user_data):
        """Test authentication with inactive account"""
        # Arrange
        inactive_user = User(
            id="user-123",
            email=sample_user_data["email"],
            hashed_password="$2b$12$hashed_password",
            is_active=False,
            is_verified=True
        )
        
        with patch.object(auth_service, '_get_user_by_email', return_value=inactive_user):
            # Act
            result = auth_service.authenticate_user(sample_user_data)
            
            # Assert
            assert result["success"] is False
            assert "Account is inactive" in result["error"]
    
    @pytest.mark.asyncio
    async def test_authenticate_user_unverified_account(self, auth_service, sample_user_data):
        """Test authentication with unverified account"""
        # Arrange
        unverified_user = User(
            id="user-123",
            email=sample_user_data["email"],
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_verified=False
        )
        
        with patch.object(auth_service, '_get_user_by_email', return_value=unverified_user):
            # Act
            result = await auth_service.authenticate_user(sample_user_data)
            
            # Assert
            assert result["success"] is False
            assert "Account not verified" in result["error"]
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, sample_user_data):
        """Test successful user registration"""
        # Arrange
        with patch.object(auth_service, '_get_user_by_email', return_value=None):
            with patch.object(auth_service, '_hash_password') as mock_hash:
                mock_hash.return_value = "hashed_password"
                with patch.object(auth_service, '_create_user') as mock_create:
                    mock_create.return_value = User(
                        id="user-123",
                        email=sample_user_data["email"],
                        hashed_password="hashed_password",
                        is_active=True,
                        is_verified=False
                    )
                    with patch.object(auth_service, '_send_verification_email') as mock_send:
                        mock_send.return_value = True
                        
                        # Act
                        result = await auth_service.register_user(sample_user_data)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["data"]["email"] == sample_user_data["email"]
                        assert result["data"]["is_verified"] is False
                        mock_send.assert_called_once()
    
    def test_register_user_email_already_exists(self, auth_service, sample_user_data, sample_user):
        """Test registration with existing email"""
        # Arrange
        with patch.object(auth_service, '_get_user_by_email', return_value=sample_user):
            # Act
            result = auth_service.register_user(sample_user_data)
            
            # Assert
            assert result["success"] is False
            assert "Email already registered" in result["error"]
    
    def test_register_user_weak_password(self, auth_service, sample_user_data):
        """Test registration with weak password"""
        # Arrange
        weak_password_data = {**sample_user_data, "password": "123"}
        
        # Act
        result = auth_service.register_user(weak_password_data)
        
        # Assert
        assert result["success"] is False
        assert "Password too weak" in result["error"]
    
    def test_refresh_token_success(self, auth_service):
        """Test successful token refresh"""
        # Arrange
        refresh_token = "valid_refresh_token"
        user_id = "user-123"
        
        with patch.object(auth_service, '_decode_token', return_value={"user_id": user_id}):
            with patch.object(auth_service, '_get_user_by_id') as mock_get_user:
                mock_user = User(
                    id=user_id,
                    email="test@example.com",
                    hashed_password="hashed",
                    is_active=True,
                    is_verified=True
                )
                mock_get_user.return_value = mock_user
                with patch.object(auth_service, '_generate_tokens') as mock_generate:
                    mock_generate.return_value = {
                        "access_token": "new_access_token",
                        "refresh_token": "new_refresh_token"
                    }
                    
                    # Act
                    result = auth_service.refresh_token(refresh_token)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["data"]["access_token"] == "new_access_token"
                    assert result["data"]["refresh_token"] == "new_refresh_token"
    
    def test_refresh_token_invalid_token(self, auth_service):
        """Test token refresh with invalid token"""
        # Arrange
        invalid_token = "invalid_token"
        
        with patch.object(auth_service, '_decode_token', side_effect=AuthenticationError("Invalid token")):
            # Act
            result = auth_service.refresh_token(invalid_token)
            
            # Assert
            assert result["success"] is False
            assert "Invalid token" in result["error"]
    
    def test_logout_user_success(self, auth_service):
        """Test successful user logout"""
        # Arrange
        access_token = "valid_access_token"
        
        with patch.object(auth_service, '_decode_token', return_value={"user_id": "user-123"}):
            with patch.object(auth_service, '_blacklist_token') as mock_blacklist:
                mock_blacklist.return_value = True
                
                # Act
                result = auth_service.logout_user(access_token)
                
                # Assert
                assert result["success"] is True
                assert result["message"] == "Successfully logged out"
                mock_blacklist.assert_called_once_with(access_token)
    
    def test_verify_email_success(self, auth_service):
        """Test successful email verification"""
        # Arrange
        verification_token = "valid_verification_token"
        user_id = "user-123"
        
        with patch.object(auth_service, '_decode_token', return_value={"user_id": user_id}):
            with patch.object(auth_service, '_get_user_by_id') as mock_get_user:
                mock_user = User(
                    id=user_id,
                    email="test@example.com",
                    hashed_password="hashed",
                    is_active=True,
                    is_verified=False
                )
                mock_get_user.return_value = mock_user
                with patch.object(auth_service, '_update_user_verification') as mock_update:
                    mock_update.return_value = True
                    
                    # Act
                    result = auth_service.verify_email(verification_token)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["message"] == "Email verified successfully"
                    mock_update.assert_called_once_with(user_id, True)
    
    def test_verify_email_invalid_token(self, auth_service):
        """Test email verification with invalid token"""
        # Arrange
        invalid_token = "invalid_token"
        
        with patch.object(auth_service, '_decode_token', side_effect=AuthenticationError("Invalid token")):
            # Act
            result = auth_service.verify_email(invalid_token)
            
            # Assert
            assert result["success"] is False
            assert "Invalid verification token" in result["error"]
    
    def test_verify_email_already_verified(self, auth_service):
        """Test email verification for already verified account"""
        # Arrange
        verification_token = "valid_verification_token"
        user_id = "user-123"
        
        with patch.object(auth_service, '_decode_token', return_value={"user_id": user_id}):
            with patch.object(auth_service, '_get_user_by_id') as mock_get_user:
                mock_user = User(
                    id=user_id,
                    email="test@example.com",
                    hashed_password="hashed",
                    is_active=True,
                    is_verified=True  # Already verified
                )
                mock_get_user.return_value = mock_user
                
                # Act
                result = auth_service.verify_email(verification_token)
                
                # Assert
                assert result["success"] is False
                assert "Email already verified" in result["error"]
    
    def test_change_password_success(self, auth_service, sample_user):
        """Test successful password change"""
        # Arrange
        user_id = "user-123"
        old_password = "old_password"
        new_password = "new_secure_password"
        
        with patch.object(auth_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(auth_service, '_verify_password', return_value=True):
                with patch.object(auth_service, '_hash_password') as mock_hash:
                    mock_hash.return_value = "new_hashed_password"
                    with patch.object(auth_service, '_update_user_password') as mock_update:
                        mock_update.return_value = True
                        
                        # Act
                        result = auth_service.change_password(user_id, old_password, new_password)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["message"] == "Password changed successfully"
                        mock_update.assert_called_once_with(user_id, "new_hashed_password")
    
    def test_change_password_invalid_old_password(self, auth_service, sample_user):
        """Test password change with invalid old password"""
        # Arrange
        user_id = "user-123"
        old_password = "wrong_password"
        new_password = "new_secure_password"
        
        with patch.object(auth_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(auth_service, '_verify_password', return_value=False):
                # Act
                result = auth_service.change_password(user_id, old_password, new_password)
                
                # Assert
                assert result["success"] is False
                assert "Invalid old password" in result["error"]
    
    def test_change_password_weak_new_password(self, auth_service, sample_user):
        """Test password change with weak new password"""
        # Arrange
        user_id = "user-123"
        old_password = "old_password"
        new_password = "123"  # Weak password
        
        with patch.object(auth_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(auth_service, '_verify_password', return_value=True):
                # Act
                result = auth_service.change_password(user_id, old_password, new_password)
                
                # Assert
                assert result["success"] is False
                assert "Password too weak" in result["error"]
    
    def test_reset_password_request_success(self, auth_service, sample_user):
        """Test successful password reset request"""
        # Arrange
        email = "test@example.com"
        
        with patch.object(auth_service, '_get_user_by_email', return_value=sample_user):
            with patch.object(auth_service, '_generate_reset_token') as mock_generate:
                mock_generate.return_value = "reset_token"
                with patch.object(auth_service, '_send_reset_email') as mock_send:
                    mock_send.return_value = True
                    
                    # Act
                    result = auth_service.request_password_reset(email)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["message"] == "Password reset email sent"
                    mock_send.assert_called_once_with(email, "reset_token")
    
    def test_reset_password_request_user_not_found(self, auth_service):
        """Test password reset request for non-existent user"""
        # Arrange
        email = "nonexistent@example.com"
        
        with patch.object(auth_service, '_get_user_by_email', return_value=None):
            # Act
            result = auth_service.request_password_reset(email)
            
            # Assert
            assert result["success"] is False
            assert "User not found" in result["error"]
    
    def test_reset_password_success(self, auth_service, sample_user):
        """Test successful password reset"""
        # Arrange
        reset_token = "valid_reset_token"
        new_password = "new_secure_password"
        user_id = "user-123"
        
        with patch.object(auth_service, '_decode_token', return_value={"user_id": user_id}):
            with patch.object(auth_service, '_get_user_by_id', return_value=sample_user):
                with patch.object(auth_service, '_hash_password') as mock_hash:
                    mock_hash.return_value = "new_hashed_password"
                    with patch.object(auth_service, '_update_user_password') as mock_update:
                        mock_update.return_value = True
                        
                        # Act
                        result = auth_service.reset_password(reset_token, new_password)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["message"] == "Password reset successfully"
                        mock_update.assert_called_once_with(user_id, "new_hashed_password")
    
    def test_reset_password_invalid_token(self, auth_service):
        """Test password reset with invalid token"""
        # Arrange
        invalid_token = "invalid_token"
        new_password = "new_secure_password"
        
        with patch.object(auth_service, '_decode_token', side_effect=AuthenticationError("Invalid token")):
            # Act
            result = auth_service.reset_password(invalid_token, new_password)
            
            # Assert
            assert result["success"] is False
            assert "Invalid reset token" in result["error"]
    
    def test_reset_password_weak_password(self, auth_service, sample_user):
        """Test password reset with weak password"""
        # Arrange
        reset_token = "valid_reset_token"
        weak_password = "123"
        user_id = "user-123"
        
        with patch.object(auth_service, '_decode_token', return_value={"user_id": user_id}):
            with patch.object(auth_service, '_get_user_by_id', return_value=sample_user):
                # Act
                result = auth_service.reset_password(reset_token, weak_password)
                
                # Assert
                assert result["success"] is False
                assert "Password too weak" in result["error"]
