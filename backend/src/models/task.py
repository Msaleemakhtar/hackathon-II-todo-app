from typing import TYPE_CHECKING, List, Optional
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel, text

if TYPE_CHECKING:
    from .user import User
    from .tag import Tag


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(default="medium", max_length=50)  # Dynamic, validated against categories
    status: str = Field(default="pending", max_length=50)  # Status workflow: pending → in_progress → completed
    due_date: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None)  # iCal RRULE string

    # Recurring task support
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id", index=True)
    is_recurring_instance: bool = Field(default=False, index=True)
    occurrence_date: Optional[datetime] = Field(default=None, index=True)

    user_id: str = Field(foreign_key="users.id", index=True)


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
        sa_column_kwargs={"onupdate": text("CURRENT_TIMESTAMP")},
    )

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"secondary": "task_tag_link"}
    )

    # Recurring task relationships
    parent_task: Optional["Task"] = Relationship(
        back_populates="child_instances",
        sa_relationship_kwargs={"remote_side": "Task.id", "foreign_keys": "[Task.parent_task_id]"}
    )
    child_instances: List["Task"] = Relationship(back_populates="parent_task")


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)
    priority: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=50)
    due_date: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None)
    parent_task_id: Optional[int] = Field(default=None)
    is_recurring_instance: Optional[bool] = Field(default=None)
    occurrence_date: Optional[datetime] = Field(default=None)