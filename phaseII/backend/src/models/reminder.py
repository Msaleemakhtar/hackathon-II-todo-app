"""Reminder model for task notifications."""
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel, text
from src.utils.timezone_utils import get_utc_now

if TYPE_CHECKING:
    from .task import Task
    from .user import User


class ReminderBase(SQLModel):
    """Base model for reminders."""

    task_id: int = Field(foreign_key="tasks.id", ondelete="CASCADE", index=True)
    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    remind_at: datetime = Field(index=True)
    channel: str = Field(max_length=20)  # "browser", "email", or "both"
    is_sent: bool = Field(default=False, index=True)
    sent_at: Optional[datetime] = Field(default=None)
    message: Optional[str] = Field(default=None, max_length=500)
    snoozed_until: Optional[datetime] = Field(default=None)


class Reminder(ReminderBase, table=True):
    """Reminder entity for scheduling task notifications."""

    __tablename__ = "reminders"

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
    task: "Task" = Relationship(back_populates="reminders")
    user: "User" = Relationship(back_populates="reminders")


class ReminderRead(ReminderBase):
    """Reminder read schema."""

    id: int
    created_at: datetime
    updated_at: datetime


class ReminderCreate(SQLModel):
    """Reminder creation schema."""

    task_id: int
    remind_at: datetime
    channel: str = Field(max_length=20)
    message: Optional[str] = Field(default=None, max_length=500)


class ReminderUpdate(SQLModel):
    """Reminder update schema."""

    remind_at: Optional[datetime] = Field(default=None)
    channel: Optional[str] = Field(default=None, max_length=20)
    message: Optional[str] = Field(default=None, max_length=500)
    is_sent: Optional[bool] = Field(default=None)
    sent_at: Optional[datetime] = Field(default=None)
    snoozed_until: Optional[datetime] = Field(default=None)
