"""Pydantic schemas for Task API request/response bodies."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

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
        pattern="^(low|medium|high)$",
        description="Task priority: low, medium, or high",
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")
    recurrence_rule: Optional[str] = Field(
        None, description="iCal RRULE string for recurring tasks"
    )


class TaskUpdate(BaseModel):
    """Schema for full task update (PUT)."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    completed: bool = Field(..., description="Completion status")
    priority: str = Field(
        ..., pattern="^(low|medium|high)$", description="Task priority"
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")
    recurrence_rule: Optional[str] = Field(
        None, description="iCal RRULE string for recurring tasks"
    )


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
        None, pattern="^(low|medium|high)$", description="Task priority"
    )
    due_date: Optional[datetime] = Field(None, description="Task due date")
    recurrence_rule: Optional[str] = Field(
        None, description="iCal RRULE string for recurring tasks"
    )


class TaskRead(BaseModel):
    """Schema for task response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Completion status")
    priority: str = Field(..., description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    recurrence_rule: Optional[str] = Field(
        None, description="iCal RRULE string for recurring tasks"
    )
    user_id: str = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    tags: List[TagRead] = Field(default_factory=list, description="Associated tags")


class PaginatedTasks(BaseModel):
    """Schema for paginated task list response."""

    items: List[TaskRead] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks matching filters")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
