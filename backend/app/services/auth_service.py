"""
Authentication Service for ArchMesh
TDD Implementation - GREEN phase: Minimal implementation to make tests pass
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from passlib.context import CryptContext
from app.core.exceptions import AuthenticationError, ValidationError
from app.models.user import User

# Deprecated in-memory user store removed in favor of DB-backed persistence


class AuthService:
    """Authentication service for user management"""
    
    def __init__(self):
        self.secret_key = "your-secret-key"  # Should be from environment
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60
        self.refresh_token_expire_days = 7
        # Switch to pbkdf2_sha256 to avoid bcrypt backend issues and 72-byte limits
        self.password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    async def authenticate_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        try:
            user = await self._get_user_by_email(user_data["email"])
            
            if not user:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
            
            if not user.is_active:
                return {
                    "success": False,
                    "error": "Account is inactive"
                }
            
            if not user.is_verified:
                return {
                    "success": False,
                    "error": "Account not verified"
                }
            
            if not self._verify_password(user_data["password"], user.hashed_password):
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
            
            tokens = self._generate_tokens(user)
            
            return {
                "success": True,
                "data": {
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified
                    }
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Authentication failed: {str(e)}"
            }
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self._get_user_by_email(user_data["email"])
            if existing_user:
                return {
                    "success": False,
                    "error": "Email already registered"
                }
            
            # Validate password strength
            if not self._validate_password_strength(user_data["password"]):
                return {
                    "success": False,
                    "error": "Password too weak"
                }
            
            # Hash password
            hashed_password = self._hash_password(user_data["password"])
            
            # Create user
            user = await self._create_user({
                "email": user_data["email"],
                "password": hashed_password,
                "name": user_data.get("name", ""),
                "is_active": True,
                # Temporarily set verified to True until email verification is wired
                "is_verified": True
            })
            
            # Send verification email
            await self._send_verification_email(user.email)
            
            return {
                "success": True,
                "data": {
                    "id": str(user.id),
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Registration failed: {str(e)}"
            }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            payload = self._decode_token(refresh_token)
            user_id = payload["user_id"]
            
            user = await self._get_user_by_id(user_id)
            if not user or not user.is_active:
                return {
                    "success": False,
                    "error": "Invalid token"
                }
            
            tokens = self._generate_tokens(user)
            
            return {
                "success": True,
                "data": {
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Token refresh failed: {str(e)}"
            }
    
    async def logout_user(self, access_token: str) -> Dict[str, Any]:
        """Logout user by blacklisting token"""
        try:
            payload = self._decode_token(access_token)
            await self._blacklist_token(access_token)
            
            return {
                "success": True,
                "message": "Successfully logged out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Logout failed: {str(e)}"
            }
    
    async def verify_email(self, verification_token: str) -> Dict[str, Any]:
        """Verify user email using verification token"""
        try:
            payload = self._decode_token(verification_token)
            user_id = payload["user_id"]
            
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "Invalid verification token"
                }
            
            if user.is_verified:
                return {
                    "success": False,
                    "error": "Email already verified"
                }
            
            await self._update_user_verification(user_id, True)
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Email verification failed: {str(e)}"
            }
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            if not self._verify_password(old_password, user.hashed_password):
                return {
                    "success": False,
                    "error": "Invalid old password"
                }
            
            if not self._validate_password_strength(new_password):
                return {
                    "success": False,
                    "error": "Password too weak"
                }
            
            hashed_new_password = self._hash_password(new_password)
            await self._update_user_password(user_id, hashed_new_password)
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Password change failed: {str(e)}"
            }
    
    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset"""
        try:
            user = await self._get_user_by_email(email)
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            reset_token = self._generate_reset_token(user)
            await self._send_reset_email(email, reset_token)
            
            return {
                "success": True,
                "message": "Password reset email sent"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Password reset request failed: {str(e)}"
            }
    
    async def reset_password(self, reset_token: str, new_password: str) -> Dict[str, Any]:
        """Reset password using reset token"""
        try:
            payload = self._decode_token(reset_token)
            user_id = payload["user_id"]
            
            user = await self._get_user_by_id(user_id)
            if not user:
                return {
                    "success": False,
                    "error": "Invalid reset token"
                }
            
            if not self._validate_password_strength(new_password):
                return {
                    "success": False,
                    "error": "Password too weak"
                }
            
            hashed_new_password = self._hash_password(new_password)
            await self._update_user_password(user_id, hashed_new_password)
            
            return {
                "success": True,
                "message": "Password reset successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Password reset failed: {str(e)}"
            }
    
    # Helper methods (to be implemented with actual database operations)
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email from the database."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
    
    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID from the database."""
        try:
            user_uuid = uuid.UUID(str(user_id))
        except Exception:
            return None
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_uuid))
            return result.scalar_one_or_none()
    
    async def _create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user in the database."""
        async with AsyncSessionLocal() as session:
            user = User(
                email=user_data["email"],
                hashed_password=user_data["password"],
                is_active=bool(user_data.get("is_active", True)),
                is_verified=bool(user_data.get("is_verified", False)),
            )
            # Derive a safe, unique-ish username from email prefix to avoid unique collisions
            email_prefix = user_data["email"].split("@")[0]
            user.username = email_prefix
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    async def _update_user_verification(self, user_id: str, is_verified: bool) -> bool:
        """Update user verification status in the database."""
        try:
            user_uuid = uuid.UUID(str(user_id))
        except Exception:
            return False
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_uuid))
            user = result.scalar_one_or_none()
            if not user:
                return False
            user.is_verified = bool(is_verified)
            await session.commit()
            return True
    
    async def _update_user_password(self, user_id: str, hashed_password: str) -> bool:
        """Update user password in the database."""
        try:
            user_uuid = uuid.UUID(str(user_id))
        except Exception:
            return False
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_uuid))
            user = result.scalar_one_or_none()
            if not user:
                return False
            user.hashed_password = hashed_password
            await session.commit()
            return True
    
    async def _blacklist_token(self, token: str) -> bool:
        """Blacklist token - to be implemented with Redis"""
        # This is a mock implementation for testing
        return True
    
    async def _send_verification_email(self, email: str) -> bool:
        """Send verification email - to be implemented with email service"""
        # This is a mock implementation for testing
        return True
    
    async def _send_reset_email(self, email: str, reset_token: str) -> bool:
        """Send password reset email - to be implemented with email service"""
        # This is a mock implementation for testing
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash password using configured context (pbkdf2_sha256)."""
        return self.password_context.hash(password)
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash using configured context."""
        return self.password_context.verify(password, hashed_password)
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate access and refresh tokens"""
        access_payload = {
            "user_id": str(user.id),
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        }
        
        refresh_payload = {
            "user_id": str(user.id),
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def _generate_reset_token(self, user: User) -> str:
        """Generate password reset token"""
        payload = {
            "user_id": str(user.id),
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

