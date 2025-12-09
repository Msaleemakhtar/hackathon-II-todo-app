from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .tag import Tag
    from .task import Task


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
        default_factory=datetime.utcnow,
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
