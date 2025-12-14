"""API router for authentication endpoints."""

from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.config import settings
from src.core.database import get_db
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_better_auth_token,
    sync_user_with_better_auth,
)
from src.models.user import User
from src.schemas.auth import RegisterRequest

router = APIRouter()


class LoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str = Field(min_length=1)  # In Better Auth integration, we might verify


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class BetterAuthExchangeRequest(BaseModel):
    """Schema for exchanging Better Auth token for backend tokens."""
    better_auth_token: str


class UserProfile(BaseModel):
    """Schema for user profile response."""
    id: str
    email: str
    name: Optional[str] = None


@router.post("/auth/token", response_model=TokenResponse)
async def exchange_better_auth_token(
    request: BetterAuthExchangeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Exchange a Better Auth JWT token for backend API tokens.
    
    This endpoint is used to sync the Better Auth session with backend tokens.
    """
    try:
        # Verify the Better Auth token
        better_auth_payload = verify_better_auth_token(request.better_auth_token)
        
        # Extract user info from Better Auth token
        better_auth_user_id = better_auth_payload.get("userId") or better_auth_payload.get("sub")
        email = better_auth_payload.get("email")
        name = better_auth_payload.get("name", better_auth_payload.get("email", "").split("@")[0])
        
        if not better_auth_user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Better Auth token: missing required fields"
            )
        
        # Ensure user exists in FastAPI user table (sync if needed)
        user = await sync_user_with_better_auth(db, better_auth_user_id, email, name)
        
        # Create backend tokens for API access
        access_token = create_access_token(data={"sub": user.id, "email": user.email})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Better Auth token: {str(e)}"
        )


@router.get("/auth/me", response_model=UserProfile)
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Get current authenticated user profile.
    This endpoint validates the backend JWT token.
    """
    from src.core.security import get_current_user_from_token
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = auth_header.removeprefix("Bearer ").strip()
    
    try:
        payload = verify_better_auth_token(token)
        user_id = payload.get("sub")
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return UserProfile(id=user.id, email=user.email, name=user.name)
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    # In the Better Auth implementation, we might need to validate the refresh token differently
    # For now, we'll use a simplified approach
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token functionality not implemented in Better Auth integration"
    )


# Legacy endpoints for backwards compatibility (not recommended for use with Better Auth)
@router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Legacy registration endpoint - not recommended when using Better Auth.
    Better Auth handles registration on the frontend.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use Better Auth for registration - this endpoint is not recommended"
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Legacy login endpoint - not recommended when using Better Auth.
    Better Auth handles login on the frontend.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Use Better Auth for login - this endpoint is not recommended"
    )