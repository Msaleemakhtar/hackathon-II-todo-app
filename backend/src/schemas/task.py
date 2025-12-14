"""Pydantic schemas for Task API request/response bodies."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer

from src.schemas.tag import TagRead


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    completed: bool = Field(False, description="Completion status")
    priority: str = Field(
        "medium",
        min_length=1,
        max_length=50,
        description="Task priority (validated against user's priority categories)",
    )
    status: str = Field(
        "pending",
        min_length=1,
        max_length=50,
        description="Task status (pending, in_progress, completed)",
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")
    recurrence_rule: Optional[str] = Field(
        None, description="iCal RRULE string for recurring tasks"
    )

    @field_validator("due_date")
    @classmethod
    def remove_timezone(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Convert timezone-aware datetime to timezone-naive for database compatibility."""
        if v is not None and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class TaskUpdate(BaseModel):
    """Schema for full task update (PUT)."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    completed: bool = Field(..., description="Completion status")
    priority: str = Field(
        ..., min_length=1, max_length=50, description="Task priority (validated against user's priority categories)"
    )
    status: str = Field(
        ..., min_length=1, max_length=50, description="Task status (pending, in_progress, completed)"
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")
    recurrence_rule: Optional[str] = Field(
        None, description="iCal RRULE string for recurring tasks"
    )

    @field_validator("due_date")
    @classmethod
    def remove_timezone(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Convert timezone-aware datetime to timezone-naive for database compatibility."""
        if v is not None and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class TaskPartialUpdate(BaseModel):
    """Schema for partial task update (PATCH)."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Task title"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    completed: Optional[bool] = Field(None, description="Completion status")
    priority: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Task priority (validated against user's priority categories)"
    )
    status: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Task status (pending, in_progress, completed)"
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")
    recurrence_rule: Optional[str] = Field(
        None, description="iCal RRULE string for recurring tasks"
    )

    @field_validator("due_date")
    @classmethod
    def remove_timezone(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Convert timezone-aware datetime to timezone-naive for database compatibility."""
        if v is not None and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class TaskMinimal(BaseModel):
    """Minimal task representation for high-performance list views (FR-019).

    Contains only essential fields to minimize payload size.
    Ideal for: Virtual scrolling, quick filtering, mobile views.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    completed: bool = Field(..., description="Completion status")
    priority: str = Field(..., description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Task due date")


class TaskSummary(TaskMinimal):
    """Summary task representation for dashboard views (FR-019).

    Extends minimal with status and temporal information.
    Ideal for: Dashboard cards, overview lists, search results.
    """

    status: str = Field(..., description="Task status (pending, in_progress, completed)")
    user_id: str = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")

    @field_serializer("created_at", "updated_at", "due_date")
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime as ISO format with Z suffix to indicate UTC time."""
        if value is not None:
            # For naive datetimes (which we store in UTC), treat them as UTC and append 'Z'
            return value.isoformat() + "Z"
        return value


class TaskRead(TaskSummary):
    """Full task representation for detail views (FR-019).

    Contains all task information including relationships.
    Ideal for: Detail pages, editing, full task context.
    """

    description: Optional[str] = Field(None, description="Task description")
    recurrence_rule: Optional[str] = Field(
        None, description="iCal RRULE string for recurring tasks"
    )
    tags: List[TagRead] = Field(default_factory=list, description="Associated tags")


class PaginatedTasks(BaseModel):
    """Schema for paginated task list response."""

    items: List[TaskRead] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks matching filters")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
