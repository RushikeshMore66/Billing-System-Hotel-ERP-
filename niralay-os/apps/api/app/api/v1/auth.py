"""
Authentication router for NiralayOS — /api/v1/auth/*

Endpoints:
    POST /auth/login
    POST /auth/logout
    POST /auth/refresh
    GET  /auth/me
    POST /auth/change-password
    POST /auth/forgot-password
    POST /auth/reset-password
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.base import SuccessResponse
from app.services.auth import AuthService
from app.services.audit import AuditService
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    description="Returns JWT access + refresh token pair. Account locks after 5 failed attempts.",
)
def login(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> SuccessResponse[TokenResponse]:
    svc = AuthService(db)
    tokens = svc.login(
        email=body.email,
        password=body.password,
        ip_address=_get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    return SuccessResponse.of(data=tokens, message="Login successful")


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
@router.post(
    "/logout",
    response_model=SuccessResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Logout and revoke current session",
)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[MessageResponse]:
    jti: str = getattr(request.state, "jti", "")
    AuthService(db).logout(jti=jti)
    return SuccessResponse.of(data=MessageResponse(message="Logged out successfully"))


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------
@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token",
    description="Provide a valid refresh token to receive a new access+refresh token pair.",
)
def refresh_tokens(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse[TokenResponse]:
    tokens = AuthService(db).refresh(raw_refresh_token=body.refresh_token)
    return SuccessResponse.of(data=tokens, message="Tokens refreshed")


# ---------------------------------------------------------------------------
# Current user
# ---------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=SuccessResponse[CurrentUserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get authenticated user profile",
)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[CurrentUserResponse]:
    data = CurrentUserResponse(
        id=current_user.id,
        uuid=current_user.uuid,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar=current_user.avatar,
        department=current_user.department,
        designation=current_user.designation,
        status=current_user.status,
        is_superuser=current_user.is_superuser,
        roles=current_user.role_names,
        permissions=current_user.permission_codes,
    )
    return SuccessResponse.of(data=data, message="User profile retrieved")


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------
@router.post(
    "/change-password",
    response_model=SuccessResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Change password for authenticated user",
)
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[MessageResponse]:
    user_svc = UserService(db)
    user_svc.change_password(
        user=current_user,
        current_password=body.current_password,
        new_password=body.new_password,
    )
    audit = AuditService(db)
    audit.log(
        "PASSWORD_CHANGED",
        actor_id=current_user.id,
        actor_uuid=str(current_user.uuid),
        resource_type="user",
        resource_id=str(current_user.uuid),
    )
    return SuccessResponse.of(data=MessageResponse(message="Password changed successfully"))


# ---------------------------------------------------------------------------
# Forgot password
# ---------------------------------------------------------------------------
@router.post(
    "/forgot-password",
    response_model=SuccessResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Request a password reset link",
    description="Sends a reset token to the registered email. Always returns 200 to prevent email enumeration.",
)
def forgot_password(
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse[MessageResponse]:
    AuthService(db).initiate_password_reset(email=body.email)
    # Always return success to prevent email enumeration
    return SuccessResponse.of(
        data=MessageResponse(message="If that email is registered, a reset link has been sent.")
    )


# ---------------------------------------------------------------------------
# Reset password
# ---------------------------------------------------------------------------
@router.post(
    "/reset-password",
    response_model=SuccessResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Complete password reset using token",
)
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> SuccessResponse[MessageResponse]:
    AuthService(db).complete_password_reset(
        token=body.token,
        new_password=body.new_password,
    )
    return SuccessResponse.of(data=MessageResponse(message="Password reset successfully. Please log in again."))
