"""
Unit tests for MyAccount Service - TDD Implementation
Following Red-Green-Refactor cycle for user profile management, settings, and account information
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.myaccount_service import MyAccountService
from app.models.user import User
from app.schemas.myaccount import (
    ProfileUpdateRequest, PasswordChangeRequest, EmailChangeRequest, 
    NotificationSettingsRequest, PrivacySettingsRequest, AccountDeletionRequest
)
from app.core.exceptions import ProfileError, SettingsError, AccountError


class TestMyAccountService:
    """Test cases for MyAccount Service - TDD Implementation"""
    
    @pytest.fixture
    def myaccount_service(self):
        """Create a test instance of MyAccountService"""
        return MyAccountService()
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user object"""
        return User(
            id="user-123",
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            hashed_password="$2b$12$hashed_password",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def sample_profile_data(self):
        """Sample profile update data"""
        return {
            "first_name": "Updated",
            "last_name": "Name",
            "company": "New Company",
            "role": "senior_developer",
            "bio": "Updated bio information"
        }

    # RED PHASE: Write failing tests first
    
    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, myaccount_service, sample_user):
        """Test successful retrieval of user profile"""
        # Arrange
        user_id = "user-123"
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            # Act
            result = await myaccount_service.get_user_profile(user_id)
            
            # Assert
            assert result["success"] is True
            assert result["data"]["id"] == user_id
            assert result["data"]["email"] == sample_user.email
            assert result["data"]["first_name"] == sample_user.first_name
            assert result["data"]["last_name"] == sample_user.last_name
            assert "password" not in result["data"]  # Password should not be included
    
    @pytest.mark.asyncio
    async def test_get_user_profile_user_not_found(self, myaccount_service):
        """Test get user profile for non-existent user"""
        # Arrange
        user_id = "nonexistent-user"
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=None):
            # Act
            result = await myaccount_service.get_user_profile(user_id)
            
            # Assert
            assert result["success"] is False
            assert "User not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, myaccount_service, sample_user, sample_profile_data):
        """Test successful update of user profile"""
        # Arrange
        user_id = "user-123"
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_update_user_profile') as mock_update:
                mock_update.return_value = True
                
                # Act
                result = await myaccount_service.update_user_profile(user_id, sample_profile_data)
                
                # Assert
                assert result["success"] is True
                assert result["message"] == "Profile updated successfully"
                assert result["data"]["first_name"] == sample_profile_data["first_name"]
                assert result["data"]["last_name"] == sample_profile_data["last_name"]
                mock_update.assert_called_once_with(user_id, sample_profile_data)
    
    @pytest.mark.asyncio
    async def test_update_user_profile_invalid_data(self, myaccount_service, sample_user):
        """Test profile update with invalid data"""
        # Arrange
        user_id = "user-123"
        invalid_data = {
            "first_name": "",  # Empty first name
            "last_name": "Valid"
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_validate_profile_data', side_effect=ProfileError("Invalid profile data")):
                # Act
                result = await myaccount_service.update_user_profile(user_id, invalid_data)
                
                # Assert
                assert result["success"] is False
                assert "Invalid profile data" in result["error"]
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, myaccount_service, sample_user):
        """Test successful password change"""
        # Arrange
        user_id = "user-123"
        password_data = {
            "current_password": "old_password",
            "new_password": "NewSecurePassword123"
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_verify_current_password', return_value=True):
                with patch.object(myaccount_service, '_validate_new_password', return_value=True):
                    with patch.object(myaccount_service, '_update_user_password') as mock_update:
                        mock_update.return_value = True
                        
                        # Act
                        result = await myaccount_service.change_password(user_id, password_data)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["message"] == "Password changed successfully"
                        mock_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_password_invalid_current_password(self, myaccount_service, sample_user):
        """Test password change with invalid current password"""
        # Arrange
        user_id = "user-123"
        password_data = {
            "current_password": "wrong_password",
            "new_password": "NewSecurePassword123"
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_verify_current_password', return_value=False):
                # Act
                result = await myaccount_service.change_password(user_id, password_data)
                
                # Assert
                assert result["success"] is False
                assert "Current password is incorrect" in result["error"]
    
    @pytest.mark.asyncio
    async def test_change_password_weak_new_password(self, myaccount_service, sample_user):
        """Test password change with weak new password"""
        # Arrange
        user_id = "user-123"
        password_data = {
            "current_password": "old_password",
            "new_password": "123"  # Weak password
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_verify_current_password', return_value=True):
                with patch.object(myaccount_service, '_validate_new_password', side_effect=ProfileError("Password too weak")):
                    # Act
                    result = await myaccount_service.change_password(user_id, password_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Password too weak" in result["error"]
    
    @pytest.mark.asyncio
    async def test_change_email_success(self, myaccount_service, sample_user):
        """Test successful email change"""
        # Arrange
        user_id = "user-123"
        email_data = {
            "new_email": "newemail@example.com",
            "current_password": "current_password"
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_verify_current_password', return_value=True):
                with patch.object(myaccount_service, '_check_email_availability', return_value=True):
                    with patch.object(myaccount_service, '_send_email_verification') as mock_send:
                        mock_send.return_value = True
                        
                        # Act
                        result = await myaccount_service.change_email(user_id, email_data)
                        
                        # Assert
                        assert result["success"] is True
                        assert result["message"] == "Email change verification sent"
                        mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_email_already_exists(self, myaccount_service, sample_user):
        """Test email change with existing email"""
        # Arrange
        user_id = "user-123"
        email_data = {
            "new_email": "existing@example.com",
            "current_password": "current_password"
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_verify_current_password', return_value=True):
                with patch.object(myaccount_service, '_check_email_availability', return_value=False):
                    # Act
                    result = await myaccount_service.change_email(user_id, email_data)
                    
                    # Assert
                    assert result["success"] is False
                    assert "Email already in use" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_notification_settings_success(self, myaccount_service, sample_user):
        """Test successful retrieval of notification settings"""
        # Arrange
        user_id = "user-123"
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_get_user_notification_settings') as mock_get:
                mock_settings = {
                    "email_notifications": True,
                    "project_updates": True,
                    "security_alerts": True,
                    "marketing_emails": False
                }
                mock_get.return_value = mock_settings
                
                # Act
                result = await myaccount_service.get_notification_settings(user_id)
                
                # Assert
                assert result["success"] is True
                assert result["data"]["email_notifications"] is True
                assert result["data"]["project_updates"] is True
                assert result["data"]["security_alerts"] is True
                assert result["data"]["marketing_emails"] is False
    
    @pytest.mark.asyncio
    async def test_update_notification_settings_success(self, myaccount_service, sample_user):
        """Test successful update of notification settings"""
        # Arrange
        user_id = "user-123"
        settings_data = {
            "email_notifications": False,
            "project_updates": True,
            "security_alerts": True,
            "marketing_emails": False
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_update_user_notification_settings') as mock_update:
                mock_update.return_value = True
                
                # Act
                result = await myaccount_service.update_notification_settings(user_id, settings_data)
                
                # Assert
                assert result["success"] is True
                assert result["message"] == "Notification settings updated successfully"
                mock_update.assert_called_once_with(user_id, settings_data)
    
    @pytest.mark.asyncio
    async def test_get_privacy_settings_success(self, myaccount_service, sample_user):
        """Test successful retrieval of privacy settings"""
        # Arrange
        user_id = "user-123"
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_get_user_privacy_settings') as mock_get:
                mock_settings = {
                    "profile_visibility": "private",
                    "show_email": False,
                    "show_company": True,
                    "data_sharing": False
                }
                mock_get.return_value = mock_settings
                
                # Act
                result = await myaccount_service.get_privacy_settings(user_id)
                
                # Assert
                assert result["success"] is True
                assert result["data"]["profile_visibility"] == "private"
                assert result["data"]["show_email"] is False
                assert result["data"]["show_company"] is True
                assert result["data"]["data_sharing"] is False
    
    @pytest.mark.asyncio
    async def test_update_privacy_settings_success(self, myaccount_service, sample_user):
        """Test successful update of privacy settings"""
        # Arrange
        user_id = "user-123"
        settings_data = {
            "profile_visibility": "public",
            "show_email": True,
            "show_company": False,
            "data_sharing": True
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_update_user_privacy_settings') as mock_update:
                mock_update.return_value = True
                
                # Act
                result = await myaccount_service.update_privacy_settings(user_id, settings_data)
                
                # Assert
                assert result["success"] is True
                assert result["message"] == "Privacy settings updated successfully"
                mock_update.assert_called_once_with(user_id, settings_data)
    
    @pytest.mark.asyncio
    async def test_get_account_statistics_success(self, myaccount_service, sample_user):
        """Test successful retrieval of account statistics"""
        # Arrange
        user_id = "user-123"
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_get_user_statistics') as mock_get:
                mock_stats = {
                    "projects_created": 5,
                    "workflows_completed": 12,
                    "account_age_days": 30,
                    "last_login": "2024-01-15T10:30:00Z"
                }
                mock_get.return_value = mock_stats
                
                # Act
                result = await myaccount_service.get_account_statistics(user_id)
                
                # Assert
                assert result["success"] is True
                assert result["data"]["projects_created"] == 5
                assert result["data"]["workflows_completed"] == 12
                assert result["data"]["account_age_days"] == 30
                assert result["data"]["last_login"] == "2024-01-15T10:30:00Z"
    
    @pytest.mark.asyncio
    async def test_export_user_data_success(self, myaccount_service, sample_user):
        """Test successful export of user data"""
        # Arrange
        user_id = "user-123"
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_export_user_data') as mock_export:
                mock_export_data = {
                    "profile": {"email": "test@example.com", "name": "Test User"},
                    "projects": [{"id": "proj-1", "name": "Test Project"}],
                    "settings": {"notifications": True}
                }
                mock_export.return_value = mock_export_data
                
                # Act
                result = await myaccount_service.export_user_data(user_id)
                
                # Assert
                assert result["success"] is True
                assert result["data"]["profile"]["email"] == "test@example.com"
                assert len(result["data"]["projects"]) == 1
                assert result["data"]["settings"]["notifications"] is True
    
    @pytest.mark.asyncio
    async def test_request_account_deletion_success(self, myaccount_service, sample_user):
        """Test successful request for account deletion"""
        # Arrange
        user_id = "user-123"
        deletion_data = {
            "reason": "No longer needed",
            "password": "current_password"
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_verify_current_password', return_value=True):
                with patch.object(myaccount_service, '_send_deletion_confirmation') as mock_send:
                    mock_send.return_value = True
                    
                    # Act
                    result = await myaccount_service.request_account_deletion(user_id, deletion_data)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["message"] == "Account deletion confirmation sent"
                    mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_request_account_deletion_invalid_password(self, myaccount_service, sample_user):
        """Test account deletion request with invalid password"""
        # Arrange
        user_id = "user-123"
        deletion_data = {
            "reason": "No longer needed",
            "password": "wrong_password"
        }
        
        with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
            with patch.object(myaccount_service, '_verify_current_password', return_value=False):
                # Act
                result = await myaccount_service.request_account_deletion(user_id, deletion_data)
                
                # Assert
                assert result["success"] is False
                assert "Password is incorrect" in result["error"]
    
    @pytest.mark.asyncio
    async def test_confirm_account_deletion_success(self, myaccount_service, sample_user):
        """Test successful confirmation of account deletion"""
        # Arrange
        deletion_token = "valid_deletion_token"
        user_id = "user-123"
        
        with patch.object(myaccount_service, '_decode_deletion_token', return_value={"user_id": user_id}):
            with patch.object(myaccount_service, '_get_user_by_id', return_value=sample_user):
                with patch.object(myaccount_service, '_delete_user_account') as mock_delete:
                    mock_delete.return_value = True
                    
                    # Act
                    result = await myaccount_service.confirm_account_deletion(deletion_token)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["message"] == "Account deleted successfully"
                    mock_delete.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_confirm_account_deletion_invalid_token(self, myaccount_service):
        """Test account deletion confirmation with invalid token"""
        # Arrange
        invalid_token = "invalid_token"
        
        with patch.object(myaccount_service, '_decode_deletion_token', side_effect=AccountError("Invalid deletion token")):
            # Act
            result = await myaccount_service.confirm_account_deletion(invalid_token)
            
            # Assert
            assert result["success"] is False
            assert "Invalid deletion token" in result["error"]
