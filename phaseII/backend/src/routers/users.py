"""API router for user profile management endpoints."""

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.core.security import validate_path_user_id
from src.models.user import User

router = APIRouter()


class UserProfileRead(BaseModel):
    """Schema for user profile response."""
    id: str
    email: str
    name: str | None


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    name: str | None = Field(None, max_length=100)


@router.get("/{user_id}/profile", response_model=UserProfileRead)
async def get_user_profile(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get user profile information."""
    # Validate that the user_id in the path matches the JWT user_id
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalar_one_or_none()

    if not user:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserProfileRead(
        id=user.id,
        email=user.email,
        name=user.name
    )


@router.patch("/{user_id}/profile", response_model=UserProfileRead)
async def update_user_profile(
    user_id: str,
    request: Request,
    profile_data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update user profile information."""
    # Validate that the user_id in the path matches the JWT user_id
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalar_one_or_none()

    if not user:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user profile
    if profile_data.name is not None:
        user.name = profile_data.name

    await db.commit()
    await db.refresh(user)

    return UserProfileRead(
        id=user.id,
        email=user.email,
        name=user.name
    )
