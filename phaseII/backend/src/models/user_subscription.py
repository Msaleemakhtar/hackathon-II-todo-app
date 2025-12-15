"""UserSubscription model for web push notifications."""
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel, text
from src.utils.timezone_utils import get_utc_now

if TYPE_CHECKING:
    from .user import User


class UserSubscriptionBase(SQLModel):
    """Base model for user subscriptions."""

    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    endpoint: str = Field(max_length=500, unique=True)
    p256dh_key: str = Field(max_length=200, description="P-256 Diffie-Hellman public key")
    auth_key: str = Field(max_length=100, description="Authentication secret")
    is_active: bool = Field(default=True, index=True)


class UserSubscription(UserSubscriptionBase, table=True):
    """UserSubscription entity for managing web push notification subscriptions."""

    __tablename__ = "user_subscriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: get_utc_now().replace(tzinfo=None),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: get_utc_now().replace(tzinfo=None),
        nullable=False,
        sa_column_kwargs={"onupdate": text("CURRENT_TIMESTAMP")},
    )

    # Relationships
    user: "User" = Relationship(back_populates="subscriptions")


class UserSubscriptionRead(UserSubscriptionBase):
    """UserSubscription read schema."""

    id: int
    created_at: datetime
    updated_at: datetime


class UserSubscriptionCreate(SQLModel):
    """UserSubscription creation schema."""

    endpoint: str = Field(max_length=500)
    p256dh_key: str = Field(max_length=200, description="P-256 Diffie-Hellman public key")
    auth_key: str = Field(max_length=100, description="Authentication secret")


class UserSubscriptionUpdate(SQLModel):
    """UserSubscription update schema."""

    is_active: bool
