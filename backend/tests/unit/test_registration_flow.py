"""
Unit tests for User Registration Flow - TDD Implementation
Following Red-Green-Refactor cycle for registration flow, email validation, and account activation
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.registration_service import RegistrationService
from app.models.user import User
from app.schemas.registration import RegistrationRequest, EmailVerificationRequest, AccountActivationRequest
from app.core.exceptions import RegistrationError, EmailValidationError, AccountActivationError


class TestRegistrationFlow:
    """Test cases for User Registration Flow - TDD Implementation"""
    
    @pytest.fixture
    def registration_service(self):
        """Create a test instance of RegistrationService"""
        return RegistrationService()
    
    @pytest.fixture
    def sample_registration_data(self):
        """Sample registration data for testing"""
        return {
            "email": "newuser@example.com",
            "password": "SecurePassword123",
            "name": "New User",
            "company": "Test Company",
            "role": "developer"
        }
    
    @pytest.fixture
    def sample_user(self, sample_registration_data):
        """Create a sample user object"""
        return User(
            id="user-456",
            email=sample_registration_data["email"],
            hashed_password="$2b$12$hashed_password",
            is_active=False,  # Not activated yet
            is_verified=False  # Not verified yet
        )

    # RED PHASE: Write failing tests first
    
    @pytest.mark.asyncio
    async def test_register_new_user_success(self, registration_service, sample_registration_data):
        """Test successful registration of new user"""
        # Arrange
        with patch.object(registration_service, '_check_email_availability', return_value=True):
            with patch.object(registration_service, '_validate_registration_data', return_value=True):
                with patch.object(registration_service, '_create_pending_user') as mock_create:
                    mock_create.return_value = User(
                        id="user-456",
                        email=sample_registration_data["email"],
                        hashed_password="hashed_password",
                        is_active=False,
                        is_verified=False
                    )
                    with patch.object(registration_service, '_send_verification_email') as mock_send:
                        mock_send.return_value = True
                        
                        # Act
                        result = await registration_service.register_user(sample_registration_data)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["data"]["email"] == sample_registration_data["email"]
                        assert result["data"]["is_active"] is False
                        assert result["data"]["is_verified"] is False
                        assert "verification_email_sent" in result["data"]
                        mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_user_email_already_exists(self, registration_service, sample_registration_data):
        """Test registration with existing email"""
        # Arrange
        with patch.object(registration_service, '_check_email_availability', return_value=False):
            # Act
            result = await registration_service.register_user(sample_registration_data)
            
            # Assert
            assert result["success"] is False
            assert "Email already registered" in result["error"]
    
    @pytest.mark.asyncio
    async def test_register_user_invalid_email_format(self, registration_service):
        """Test registration with invalid email format"""
        # Arrange
        invalid_data = {
            "email": "invalid-email-format",
            "password": "SecurePassword123",
            "name": "Test User"
        }
        
        with patch.object(registration_service, '_validate_registration_data', side_effect=EmailValidationError("Invalid email format")):
            # Act
            result = await registration_service.register_user(invalid_data)
            
            # Assert
            assert result["success"] is False
            assert "Invalid email format" in result["error"]
    
    @pytest.mark.asyncio
    async def test_register_user_weak_password(self, registration_service):
        """Test registration with weak password"""
        # Arrange
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",  # Weak password
            "name": "Test User"
        }
        
        with patch.object(registration_service, '_validate_registration_data', side_effect=RegistrationError("Password too weak")):
            # Act
            result = await registration_service.register_user(weak_password_data)
            
            # Assert
            assert result["success"] is False
            assert "Password too weak" in result["error"]
    
    @pytest.mark.asyncio
    async def test_register_user_missing_required_fields(self, registration_service):
        """Test registration with missing required fields"""
        # Arrange
        incomplete_data = {
            "email": "test@example.com"
            # Missing password and name
        }
        
        with patch.object(registration_service, '_validate_registration_data', side_effect=RegistrationError("Missing required fields")):
            # Act
            result = await registration_service.register_user(incomplete_data)
            
            # Assert
            assert result["success"] is False
            assert "Missing required fields" in result["error"]
    
    @pytest.mark.asyncio
    async def test_verify_email_success(self, registration_service):
        """Test successful email verification"""
        # Arrange
        verification_token = "valid_verification_token"
        user_id = "user-456"
        
        with patch.object(registration_service, '_decode_verification_token', return_value={"user_id": user_id}):
            with patch.object(registration_service, '_get_user_by_id') as mock_get_user:
                mock_user = User(
                    id=user_id,
                    email="test@example.com",
                    hashed_password="hashed",
                    is_active=False,
                    is_verified=False
                )
                mock_get_user.return_value = mock_user
                with patch.object(registration_service, '_update_user_verification') as mock_update:
                    mock_update.return_value = True
                    
                    # Act
                    result = await registration_service.verify_email(verification_token)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["message"] == "Email verified successfully"
                    assert result["data"]["is_verified"] is True
                    mock_update.assert_called_once_with(user_id, True)
    
    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, registration_service):
        """Test email verification with invalid token"""
        # Arrange
        invalid_token = "invalid_token"
        
        with patch.object(registration_service, '_decode_verification_token', side_effect=EmailValidationError("Invalid verification token")):
            # Act
            result = await registration_service.verify_email(invalid_token)
            
            # Assert
            assert result["success"] is False
            assert "Invalid verification token" in result["error"]
    
    @pytest.mark.asyncio
    async def test_verify_email_already_verified(self, registration_service):
        """Test email verification for already verified account"""
        # Arrange
        verification_token = "valid_verification_token"
        user_id = "user-456"
        
        with patch.object(registration_service, '_decode_verification_token', return_value={"user_id": user_id}):
            with patch.object(registration_service, '_get_user_by_id') as mock_get_user:
                mock_user = User(
                    id=user_id,
                    email="test@example.com",
                    hashed_password="hashed",
                    is_active=False,
                    is_verified=True  # Already verified
                )
                mock_get_user.return_value = mock_user
                
                # Act
                result = await registration_service.verify_email(verification_token)
                
                # Assert
                assert result["success"] is False
                assert "Email already verified" in result["error"]
    
    @pytest.mark.asyncio
    async def test_activate_account_success(self, registration_service, sample_user):
        """Test successful account activation"""
        # Arrange
        activation_token = "valid_activation_token"
        user_id = "user-456"
        
        with patch.object(registration_service, '_decode_activation_token', return_value={"user_id": user_id}):
            with patch.object(registration_service, '_get_user_by_id', return_value=sample_user):
                with patch.object(registration_service, '_update_user_activation') as mock_update:
                    mock_update.return_value = True
                    
                    # Act
                    result = await registration_service.activate_account(activation_token)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["message"] == "Account activated successfully"
                    assert result["data"]["is_active"] is True
                    mock_update.assert_called_once_with(user_id, True)
    
    @pytest.mark.asyncio
    async def test_activate_account_invalid_token(self, registration_service):
        """Test account activation with invalid token"""
        # Arrange
        invalid_token = "invalid_token"
        
        with patch.object(registration_service, '_decode_activation_token', side_effect=AccountActivationError("Invalid activation token")):
            # Act
            result = await registration_service.activate_account(invalid_token)
            
            # Assert
            assert result["success"] is False
            assert "Invalid activation token" in result["error"]
    
    @pytest.mark.asyncio
    async def test_activate_account_already_active(self, registration_service):
        """Test account activation for already active account"""
        # Arrange
        activation_token = "valid_activation_token"
        user_id = "user-456"
        
        with patch.object(registration_service, '_decode_activation_token', return_value={"user_id": user_id}):
            with patch.object(registration_service, '_get_user_by_id') as mock_get_user:
                mock_user = User(
                    id=user_id,
                    email="test@example.com",
                    hashed_password="hashed",
                    is_active=True,  # Already active
                    is_verified=True
                )
                mock_get_user.return_value = mock_user
                
                # Act
                result = await registration_service.activate_account(activation_token)
                
                # Assert
                assert result["success"] is False
                assert "Account already active" in result["error"]
    
    @pytest.mark.asyncio
    async def test_resend_verification_email_success(self, registration_service):
        """Test successful resend of verification email"""
        # Arrange
        email = "test@example.com"
        
        with patch.object(registration_service, '_get_user_by_email') as mock_get_user:
            mock_user = User(
                id="user-456",
                email=email,
                hashed_password="hashed",
                is_active=False,
                is_verified=False
            )
            mock_get_user.return_value = mock_user
            with patch.object(registration_service, '_send_verification_email') as mock_send:
                mock_send.return_value = True
                
                # Act
                result = await registration_service.resend_verification_email(email)
                
                # Assert
                assert result["success"] is True
                assert result["message"] == "Verification email sent"
                mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_resend_verification_email_user_not_found(self, registration_service):
        """Test resend verification email for non-existent user"""
        # Arrange
        email = "nonexistent@example.com"
        
        with patch.object(registration_service, '_get_user_by_email', return_value=None):
            # Act
            result = await registration_service.resend_verification_email(email)
            
            # Assert
            assert result["success"] is False
            assert "User not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_resend_verification_email_already_verified(self, registration_service):
        """Test resend verification email for already verified user"""
        # Arrange
        email = "test@example.com"
        
        with patch.object(registration_service, '_get_user_by_email') as mock_get_user:
            mock_user = User(
                id="user-456",
                email=email,
                hashed_password="hashed",
                is_active=False,
                is_verified=True  # Already verified
            )
            mock_get_user.return_value = mock_user
            
            # Act
            result = await registration_service.resend_verification_email(email)
            
            # Assert
            assert result["success"] is False
            assert "Email already verified" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_registration_status_success(self, registration_service, sample_user):
        """Test successful retrieval of registration status"""
        # Arrange
        user_id = "user-456"
        
        with patch.object(registration_service, '_get_user_by_id', return_value=sample_user):
            # Act
            result = await registration_service.get_registration_status(user_id)
            
            # Assert
            assert result["success"] is True
            assert result["data"]["user_id"] == user_id
            assert result["data"]["is_verified"] is False
            assert result["data"]["is_active"] is False
            assert "registration_stage" in result["data"]
    
    @pytest.mark.asyncio
    async def test_get_registration_status_user_not_found(self, registration_service):
        """Test get registration status for non-existent user"""
        # Arrange
        user_id = "nonexistent-user"
        
        with patch.object(registration_service, '_get_user_by_id', return_value=None):
            # Act
            result = await registration_service.get_registration_status(user_id)
            
            # Assert
            assert result["success"] is False
            assert "User not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_cancel_registration_success(self, registration_service, sample_user):
        """Test successful cancellation of registration"""
        # Arrange
        user_id = "user-456"
        
        with patch.object(registration_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(registration_service, '_delete_pending_user') as mock_delete:
                mock_delete.return_value = True
                
                # Act
                result = await registration_service.cancel_registration(user_id)
                
                # Assert
                assert result["success"] is True
                assert result["message"] == "Registration cancelled successfully"
                mock_delete.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_cancel_registration_user_not_found(self, registration_service):
        """Test cancel registration for non-existent user"""
        # Arrange
        user_id = "nonexistent-user"
        
        with patch.object(registration_service, '_get_user_by_id', return_value=None):
            # Act
            result = await registration_service.cancel_registration(user_id)
            
            # Assert
            assert result["success"] is False
            assert "User not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_cancel_registration_active_user(self, registration_service):
        """Test cancel registration for already active user"""
        # Arrange
        user_id = "user-456"
        active_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,  # Already active
            is_verified=True
        )
        
        with patch.object(registration_service, '_get_user_by_id', return_value=active_user):
            # Act
            result = await registration_service.cancel_registration(user_id)
            
            # Assert
            assert result["success"] is False
            assert "Cannot cancel active account" in result["error"]

