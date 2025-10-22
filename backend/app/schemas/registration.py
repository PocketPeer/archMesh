"""
Pydantic schemas for user registration flow
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional


class RegistrationRequest(BaseModel):
    """Schema for user registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    company: Optional[str] = None
    role: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request"""
    token: str = Field(..., min_length=1)


class AccountActivationRequest(BaseModel):
    """Schema for account activation request"""
    token: str = Field(..., min_length=1)


class RegistrationResponse(BaseModel):
    """Schema for registration response"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None


class VerificationResponse(BaseModel):
    """Schema for email verification response"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None


class ActivationResponse(BaseModel):
    """Schema for account activation response"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None


class RegistrationStatusResponse(BaseModel):
    """Schema for registration status response"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

