"""
Authentication API endpoints for ArchMesh
TDD Implementation - GREEN phase: Minimal implementation to make tests pass
"""

from fastapi import APIRouter, Depends, Response, status, HTTPException
from typing import Dict, Any
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest, RegisterRequest, RefreshTokenRequest, 
    ChangePasswordRequest, ResetPasswordRequest, ResetPasswordConfirmRequest,
    VerifyEmailRequest, LogoutRequest, AuthResponse
)

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service() -> AuthService:
    """Dependency to get AuthService instance"""
    return AuthService()


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Login user with email and password"""
    try:
        result = await auth_service.authenticate_user(login_data.dict())
        headers = {"X-Hash-Scheme": auth_service.password_context.default_scheme()}
        if result.get("success"):
            return Response(
                content=AuthResponse(**result).model_dump_json(),
                media_type="application/json",
                headers=headers,
                status_code=status.HTTP_200_OK,
            )
        else:
            error_body = {"success": False, "error": result.get("error", "Login failed")}
            return Response(
                content=AuthResponse(**error_body).model_dump_json(),
                media_type="application/json",
                headers=headers,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
    except Exception as e:
        headers = {"X-Hash-Scheme": auth_service.password_context.default_scheme()}
        return Response(
            content=AuthResponse(**{"success": False, "data": None, "error": str(e)}).model_dump_json(),
            media_type="application/json",
            headers=headers,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Register a new user"""
    try:
        result = await auth_service.register_user(register_data.dict())
        
        if result["success"]:
            # Temporary diagnostics header: active hashing scheme
            # This helps verify which scheme the live process uses
            headers = {"X-Hash-Scheme": auth_service.password_context.default_scheme()}
            return Response(
                content=AuthResponse(**result).model_dump_json(),
                media_type="application/json",
                headers=headers,
                status_code=status.HTTP_201_CREATED,
            )
        else:
            headers = {"X-Hash-Scheme": auth_service.password_context.default_scheme()}
            error_body = {"success": False, "error": result.get("error", "Registration failed")}
            code = status.HTTP_409_CONFLICT if "already registered" in result.get("error", "") else status.HTTP_400_BAD_REQUEST
            return Response(
                content=AuthResponse(**{"success": False, "data": None, "error": error_body["error"]}).model_dump_json(),
                media_type="application/json",
                headers=headers,
                status_code=code,
            )
    except Exception as e:
        headers = {"X-Hash-Scheme": auth_service.password_context.default_scheme()}
        return Response(
            content=AuthResponse(**{"success": False, "data": None, "error": str(e)}).model_dump_json(),
            media_type="application/json",
            headers=headers,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Refresh access token using refresh token"""
    try:
        result = await auth_service.refresh_token(refresh_data.refresh_token)
        
        if result["success"]:
            return AuthResponse(**result)
        else:
            raise HTTPException(status_code=401, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.post("/logout", response_model=AuthResponse)
async def logout(
    logout_data: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Logout user by blacklisting token"""
    try:
        result = await auth_service.logout_user(logout_data.access_token)
        
        if result["success"]:
            return AuthResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(
    verify_data: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Verify user email using verification token"""
    try:
        result = await auth_service.verify_email(verify_data.token)
        
        if result["success"]:
            return AuthResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    change_data: ChangePasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Change user password"""
    try:
        # TODO: Get user_id from JWT token in production
        user_id = "current_user_id"  # This should come from authenticated user
        
        result = await auth_service.change_password(
            user_id, 
            change_data.old_password, 
            change_data.new_password
        )
        
        if result["success"]:
            return AuthResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.post("/request-password-reset", response_model=AuthResponse)
async def request_password_reset(
    reset_data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Request password reset"""
    try:
        result = await auth_service.request_password_reset(reset_data.email)
        
        if result["success"]:
            return AuthResponse(**result)
        else:
            if "not found" in result["error"]:
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=400, detail=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(
    reset_data: ResetPasswordConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthResponse:
    """Reset password using reset token"""
    try:
        result = await auth_service.reset_password(
            reset_data.token, 
            reset_data.new_password
        )
        
        if result["success"]:
            return AuthResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})

