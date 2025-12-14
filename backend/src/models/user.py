from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel
from src.utils.timezone_utils import get_utc_now

if TYPE_CHECKING:
    from .category import Category
    from .tag import Tag
    from .task import Task
    from .reminder import Reminder
    from .user_subscription import UserSubscription


class User(SQLModel, table=True):
    """User entity with authentication credentials."""

    __tablename__ = "users"

    id: str = Field(
        primary_key=True, description="User ID (UUID string from Better Auth)"
    )
    email: str = Field(
        unique=True, index=True, nullable=False, description="User's email address"
    )
    password_hash: str = Field(nullable=False, description="Bcrypt-hashed password")
    name: Optional[str] = Field(default=None, description="User's display name")
    created_at: datetime = Field(
        default_factory=lambda: get_utc_now().replace(tzinfo=None),
        nullable=False,
        description="Account creation timestamp",
    )

    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    tags: List["Tag"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    categories: List["Category"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    reminders: List["Reminder"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    subscriptions: List["UserSubscription"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
