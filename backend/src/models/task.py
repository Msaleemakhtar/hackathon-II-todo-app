from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .task_tag_link import TaskTagLink

if TYPE_CHECKING:
    from .tag import Tag
    from .user import User


class PriorityEnum(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(SQLModel, table=True):
    """Task entity representing a todo item."""

    __tablename__ = "tasks"

    id: int = Field(primary_key=True, description="Unique task identifier")
    title: str = Field(
        min_length=1, max_length=200, nullable=False, description="Task title"
    )
    description: Optional[str] = Field(
        default=None, max_length=1000, description="Detailed description"
    )
    completed: bool = Field(
        default=False, nullable=False, description="Completion status"
    )
    priority: str = Field(
        default="medium",
        nullable=False,
        description="Priority level: low, medium, high",
    )
    due_date: Optional[datetime] = Field(
        default=None, description="Task due date and time"
    )
    recurrence_rule: Optional[str] = Field(
        default=None, description="iCal RRULE string for recurring tasks"
    )
    user_id: str = Field(
        foreign_key="users.id", nullable=False, index=True, description="Task owner"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last modification timestamp",
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)
