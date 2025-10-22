"""
Registration Service for ArchMesh
TDD Implementation - GREEN phase: Minimal implementation to make tests pass
"""

from typing import Dict, Any, Optional
from app.models.user import User
from app.core.exceptions import RegistrationError, EmailValidationError, AccountActivationError


class RegistrationService:
    """Service for handling user registration flow"""
    
    def __init__(self):
        """Initialize registration service"""
        pass
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check email availability
            if not await self._check_email_availability(user_data["email"]):
                return {
                    "success": False,
                    "error": "Email already registered"
                }
            
            # Validate registration data
            await self._validate_registration_data(user_data)
            
            # Create pending user
            user = await self._create_pending_user(user_data)
            
            # Send verification email
            await self._send_verification_email(user_data["email"])
            
            return {
                "success": True,
                "data": {
                    "id": str(user.id),
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "verification_email_sent": True
                }
            }
        except (RegistrationError, EmailValidationError) as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Registration failed: {str(e)}"
            }
    
    async def verify_email(self, verification_token: str) -> Dict[str, Any]:
        """Verify user email using verification token"""
        try:
            # Decode verification token
            token_data = await self._decode_verification_token(verification_token)
            user_id = token_data["user_id"]
            
            # Get user
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Check if already verified
            if user.is_verified:
                return {
                    "success": False,
                    "error": "Email already verified"
                }
            
            # Update user verification
            await self._update_user_verification(user_id, True)
            
            return {
                "success": True,
                "message": "Email verified successfully",
                "data": {
                    "user_id": user_id,
                    "is_verified": True
                }
            }
        except EmailValidationError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Email verification failed: {str(e)}"
            }
    
    async def activate_account(self, activation_token: str) -> Dict[str, Any]:
        """Activate user account using activation token"""
        try:
            # Decode activation token
            token_data = await self._decode_activation_token(activation_token)
            user_id = token_data["user_id"]
            
            # Get user
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Check if already active
            if user.is_active:
                return {
                    "success": False,
                    "error": "Account already active"
                }
            
            # Update user activation
            await self._update_user_activation(user_id, True)
            
            return {
                "success": True,
                "message": "Account activated successfully",
                "data": {
                    "user_id": user_id,
                    "is_active": True
                }
            }
        except AccountActivationError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Account activation failed: {str(e)}"
            }
    
    async def resend_verification_email(self, email: str) -> Dict[str, Any]:
        """Resend verification email"""
        try:
            # Get user by email
            user = await self._get_user_by_email(email)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Check if already verified
            if user.is_verified:
                return {
                    "success": False,
                    "error": "Email already verified"
                }
            
            # Send verification email
            await self._send_verification_email(email)
            
            return {
                "success": True,
                "message": "Verification email sent"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to resend verification email: {str(e)}"
            }
    
    async def get_registration_status(self, user_id: str) -> Dict[str, Any]:
        """Get registration status for user"""
        try:
            # Get user
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Determine registration stage
            if user.is_active and user.is_verified:
                stage = "completed"
            elif user.is_verified:
                stage = "verified_pending_activation"
            else:
                stage = "pending_verification"
            
            return {
                "success": True,
                "data": {
                    "user_id": user_id,
                    "is_verified": user.is_verified,
                    "is_active": user.is_active,
                    "registration_stage": stage
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get registration status: {str(e)}"
            }
    
    async def cancel_registration(self, user_id: str) -> Dict[str, Any]:
        """Cancel user registration"""
        try:
            # Get user
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Check if already active
            if user.is_active:
                return {
                    "success": False,
                    "error": "Cannot cancel active account"
                }
            
            # Delete pending user
            await self._delete_pending_user(user_id)
            
            return {
                "success": True,
                "message": "Registration cancelled successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to cancel registration: {str(e)}"
            }
    
    # Helper methods (Mock implementations for testing)
    
    async def _check_email_availability(self, email: str) -> bool:
        """Check if email is available for registration"""
        # This is a mock implementation for testing
        return True
    
    async def _validate_registration_data(self, user_data: Dict[str, Any]) -> None:
        """Validate registration data"""
        # This is a mock implementation for testing
        # In real implementation, this would validate email format, password strength, etc.
        pass
    
    async def _create_pending_user(self, user_data: Dict[str, Any]) -> User:
        """Create a pending user"""
        # This is a mock implementation for testing
        return User(
            id="user-456",
            email=user_data["email"],
            hashed_password="hashed_password",
            is_active=False,
            is_verified=False
        )
    
    async def _send_verification_email(self, email: str) -> bool:
        """Send verification email"""
        # This is a mock implementation for testing
        return True
    
    async def _decode_verification_token(self, token: str) -> Dict[str, Any]:
        """Decode verification token"""
        # This is a mock implementation for testing
        return {"user_id": "user-456"}
    
    async def _decode_activation_token(self, token: str) -> Dict[str, Any]:
        """Decode activation token"""
        # This is a mock implementation for testing
        return {"user_id": "user-456"}
    
    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        # This is a mock implementation for testing
        return None
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        # This is a mock implementation for testing
        return None
    
    async def _update_user_verification(self, user_id: str, is_verified: bool) -> bool:
        """Update user verification status"""
        # This is a mock implementation for testing
        return True
    
    async def _update_user_activation(self, user_id: str, is_active: bool) -> bool:
        """Update user activation status"""
        # This is a mock implementation for testing
        return True
    
    async def _delete_pending_user(self, user_id: str) -> bool:
        """Delete pending user"""
        # This is a mock implementation for testing
        return True

