"""Pydantic schemas for task operations."""
from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    user_id: str = Field(..., description="User ID from JWT token")
    title: str = Field(..., min_length=1, max_length=200, description="Task title (1-200 chars)")
    description: str | None = Field(None, max_length=1000, description="Task description (≤1000 chars)")


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskList(BaseModel):
    """Schema for list of tasks."""

    tasks: list[TaskResponse]
    total: int
