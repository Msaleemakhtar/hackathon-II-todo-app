from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.exceptions import AppException
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from src.models import User
from src.schemas.auth import RegisterRequest
from src.schemas.user import UserResponse


async def register_user(db: AsyncSession, user_data: RegisterRequest) -> UserResponse:
    """Register a new user in the database."""
    # Check if user with email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
            code="EMAIL_ALREADY_EXISTS"
        )

    # Hash password
    hashed_password = await hash_password(user_data.password)

    # Create new user
    user = User(
        id=(
            f"user-{len(user_data.email)}-"
            f"{hashed_password[:5]}"  # Placeholder for actual ID generation
        ),
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


async def authenticate_user(
    db: AsyncSession, form_data: OAuth2PasswordRequestForm
) -> tuple[str, str, str]:
    """Authenticate a user and return access and refresh tokens."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not await verify_password(form_data.password, user.password_hash):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            code="INVALID_CREDENTIALS"
        )

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id, user.email)

    return access_token, refresh_token, user.id

async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
    """Refresh an access token using a valid refresh token."""
    try:
        payload = verify_token(refresh_token, expected_type="refresh")
        user_id = payload.get("sub")
        user_email = payload.get("email")
        if not user_id or not user_email:
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
                code="INVALID_TOKEN"
            )
    except ValueError as e:
        if str(e) == "TOKEN_EXPIRED":
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired. Please log in again",
                code="REFRESH_TOKEN_EXPIRED"
            )
        else:
            raise AppException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                code="INVALID_TOKEN"
            )

    # Ensure user still exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            code="INVALID_TOKEN"
        )

    return create_access_token(user.id, user.email)
