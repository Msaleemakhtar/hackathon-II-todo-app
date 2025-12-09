from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .task_tag_link import TaskTagLink

if TYPE_CHECKING:
    from .task import Task
    from .user import User


class Tag(SQLModel, table=True):
    """Tag entity for categorizing tasks."""

    __tablename__ = "tags"

    id: int = Field(primary_key=True, description="Unique tag identifier")
    name: str = Field(
        min_length=1, max_length=50, nullable=False, description="Tag display name"
    )
    color: Optional[str] = Field(
        default=None,
        regex="^#[0-9A-Fa-f]{6}$",
        description="Hex color code for UI display",
    )
    user_id: str = Field(
        foreign_key="users.id", nullable=False, index=True, description="Tag owner"
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tags")
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)
