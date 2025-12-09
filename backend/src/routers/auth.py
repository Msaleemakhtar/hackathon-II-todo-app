from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.core.exceptions import AppException
from src.models import User
from src.schemas.auth import RegisterRequest
from src.schemas.token import TokenResponse
from src.schemas.user import UserResponse
from src.services.auth_service import (
    authenticate_user,
    refresh_access_token,
    register_user,
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    return await register_user(db, user_data)

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and issue access and refresh tokens",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticate a user and issue access and refresh tokens."""
    access_token, refresh_token, user_id = await authenticate_user(db, form_data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=604800,  # 7 days
        path="/api/v1/auth"
    )
    return TokenResponse(access_token=access_token, token_type="bearer")

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Retrieve the authenticated user's profile information",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve the authenticated user's profile information."""
    return UserResponse.model_validate(current_user)

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Issue a new access token using a valid refresh token from cookie",
)
async def refresh(
    request: Request,
    refresh_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """Refresh an access token using a valid refresh token."""
    if not refresh_token:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
            code="MISSING_REFRESH_TOKEN"
        )

    new_access_token = await refresh_access_token(db, refresh_token)
    return TokenResponse(access_token=new_access_token, token_type="bearer")

@router.post(
    "/logout",
    summary="User logout",
    description="Clear the refresh token cookie (idempotent operation)",
)
async def logout(response: Response):
    """Clear the refresh token cookie, effectively logging out the user."""
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=0,  # Expire immediately
        path="/api/v1/auth"
    )
    return {"message": "Successfully logged out"}
