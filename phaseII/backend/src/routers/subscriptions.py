"""API router for web push notification subscription management."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.database import get_db
from src.core.security import validate_path_user_id
from src.core.vapid import get_vapid_keys
from src.models.user_subscription import UserSubscription

router = APIRouter()


class SubscriptionCreate(BaseModel):
    """Schema for creating a push notification subscription."""

    endpoint: str
    p256dh_key: str
    auth_key: str


class SubscriptionRead(BaseModel):
    """Schema for reading a subscription."""

    id: int
    endpoint: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VAPIDPublicKeyResponse(BaseModel):
    """Schema for VAPID public key response."""

    public_key: str


@router.get("/vapid/public-key", response_model=VAPIDPublicKeyResponse)
async def get_vapid_public_key():
    """
    Get the VAPID public key for web push notifications.

    This endpoint is public and doesn't require authentication.
    The public key is needed by the frontend to subscribe to push notifications.

    Returns:
        VAPID public key
    """
    try:
        public_key, _ = get_vapid_keys()
        return {"public_key": public_key}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/users/{user_id}/subscriptions", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    user_id: str,
    subscription_data: SubscriptionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new push notification subscription for a user.

    **User Story 1 (P1)**: User can subscribe to browser push notifications.

    Args:
        user_id: ID of the user
        subscription_data: Subscription data from browser
        request: FastAPI request object (contains auth user)
        db: Database session

    Returns:
        Created subscription

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 409 if subscription already exists
    """
    # Validate that path user_id matches authenticated user
    await validate_path_user_id(request, user_id, db)

    # Check if subscription already exists
    statement = select(UserSubscription).where(
        UserSubscription.user_id == user_id,
        UserSubscription.endpoint == subscription_data.endpoint
    )
    result = await db.execute(statement)
    existing_subscription = result.scalar_one_or_none()

    if existing_subscription:
        # Update existing subscription
        existing_subscription.p256dh_key = subscription_data.p256dh_key
        existing_subscription.auth_key = subscription_data.auth_key
        existing_subscription.is_active = True
        existing_subscription.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

        await db.commit()
        await db.refresh(existing_subscription)

        return existing_subscription

    # Create new subscription
    subscription = UserSubscription(
        user_id=user_id,
        endpoint=subscription_data.endpoint,
        p256dh_key=subscription_data.p256dh_key,
        auth_key=subscription_data.auth_key,
        is_active=True,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )

    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    return subscription


@router.delete("/users/{user_id}/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    user_id: str,
    subscription_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a push notification subscription.

    Args:
        user_id: ID of the user
        subscription_id: ID of the subscription
        request: FastAPI request object (contains auth user)
        db: Database session

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if subscription not found
    """
    # Validate that path user_id matches authenticated user
    await validate_path_user_id(request, user_id, db)

    # Get subscription
    statement = select(UserSubscription).where(
        UserSubscription.id == subscription_id,
        UserSubscription.user_id == user_id
    )
    result = await db.execute(statement)
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription {subscription_id} not found"
        )

    # Mark as inactive instead of deleting
    subscription.is_active = False
    subscription.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.commit()
