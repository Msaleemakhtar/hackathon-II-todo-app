"""Pydantic schemas for reminder API endpoints."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator, field_serializer


class ReminderBase(BaseModel):
    """Base schema for reminder with common fields."""

    task_id: int = Field(..., description="ID of the task to remind about", ge=1)
    remind_at: datetime = Field(..., description="When to send the reminder")
    channel: str = Field(
        default="browser",
        description="Notification channel to use",
        pattern="^(browser|email|both)$"
    )
    message: Optional[str] = Field(
        None,
        description="Custom message for the reminder",
        max_length=500
    )

    @field_validator("remind_at")
    @classmethod
    def validate_remind_at_future(cls, v: datetime) -> datetime:
        """Validate that remind_at is in the future."""
        # Normalize both datetimes to timezone-naive UTC for comparison
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        remind_at_naive = v.replace(tzinfo=None) if v.tzinfo else v

        if remind_at_naive <= now:
            raise ValueError("Reminder time must be in the future")

        # Return timezone-naive datetime for database storage
        return remind_at_naive


class ReminderCreate(ReminderBase):
    """Schema for creating a new reminder."""

    pass


class ReminderUpdate(BaseModel):
    """Schema for updating an existing reminder."""

    remind_at: Optional[datetime] = Field(None, description="New time for the reminder")
    channel: Optional[str] = Field(
        None,
        description="New notification channel to use",
        pattern="^(browser|email|both)$"
    )
    message: Optional[str] = Field(
        None,
        description="New custom message for the reminder",
        max_length=500
    )
    snoozed_until: Optional[datetime] = Field(
        None,
        description="When to snooze the reminder until"
    )

    @field_validator("remind_at")
    @classmethod
    def validate_remind_at_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate that remind_at is in the future if provided."""
        if v is not None:
            # Normalize both datetimes to timezone-naive UTC for comparison
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            remind_at_naive = v.replace(tzinfo=None) if v.tzinfo else v

            if remind_at_naive <= now:
                raise ValueError("Reminder time must be in the future")

            # Return timezone-naive datetime for database storage
            return remind_at_naive
        return v


class ReminderRead(BaseModel):
    """Schema for reading a reminder.

    Note: This doesn't inherit from ReminderBase to avoid the future-date validator
    which would fail when reading past reminders.
    """

    id: int = Field(..., description="Unique identifier for the reminder")
    task_id: int = Field(..., description="ID of the task to remind about")
    user_id: str = Field(..., description="ID of the user who owns the reminder")
    remind_at: datetime = Field(..., description="When to send the reminder")
    channel: str = Field(..., description="Notification channel to use")
    message: Optional[str] = Field(None, description="Custom message for the reminder")
    is_sent: bool = Field(..., description="Whether the reminder has been sent")
    sent_at: Optional[datetime] = Field(
        None,
        description="When the reminder was sent (if sent)"
    )
    snoozed_until: Optional[datetime] = Field(
        None,
        description="When the reminder is snoozed until"
    )
    created_at: datetime = Field(..., description="When the reminder was created")
    updated_at: datetime = Field(..., description="When the reminder was last updated")

    model_config = {"from_attributes": True}

    @field_serializer("remind_at", "sent_at", "snoozed_until", "created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime as ISO format with Z suffix to indicate UTC time."""
        if value is not None:
            # For naive datetimes (which we store in UTC), treat them as UTC and append 'Z'
            return value.isoformat() + "Z"
        return value
