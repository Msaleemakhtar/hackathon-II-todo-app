"""TaskOrder model for drag-and-drop functionality."""
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel, text
from src.utils.timezone_utils import get_utc_now

if TYPE_CHECKING:
    from .task import Task


class TaskOrderBase(SQLModel):
    """Base model for task ordering."""

    task_id: int = Field(foreign_key="tasks.id", ondelete="CASCADE", primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    sort_order: int = Field(ge=0, index=True)


class TaskOrder(TaskOrderBase, table=True):
    """TaskOrder entity for persisting user-defined task sort positions."""

    __tablename__ = "task_orders"

    updated_at: datetime = Field(
        default_factory=lambda: get_utc_now().replace(tzinfo=None),
        nullable=False,
        sa_column_kwargs={"onupdate": text("CURRENT_TIMESTAMP")},
    )

    # Relationships
    task: "Task" = Relationship(back_populates="task_order")


class TaskOrderRead(TaskOrderBase):
    """TaskOrder read schema."""

    updated_at: datetime


class TaskOrderCreate(TaskOrderBase):
    """TaskOrder creation schema."""

    pass


class TaskOrderUpdate(SQLModel):
    """TaskOrder update schema."""

    sort_order: int = Field(ge=0)
