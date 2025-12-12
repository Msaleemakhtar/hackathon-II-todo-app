from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class CategoryBase(SQLModel):
    name: str = Field(min_length=1, max_length=50, index=True)
    type: str = Field(regex="^(priority|status)$")  # Enum-like constraint
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color code
    is_default: bool = Field(default=False)  # Protected defaults

    user_id: str = Field(foreign_key="users.id", index=True)


class Category(CategoryBase, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="categories")


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CategoryCreate(SQLModel):
    name: str = Field(min_length=1, max_length=50)
    type: str = Field(regex="^(priority|status)$")
    color: Optional[str] = Field(default=None, max_length=7)


class CategoryUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)
