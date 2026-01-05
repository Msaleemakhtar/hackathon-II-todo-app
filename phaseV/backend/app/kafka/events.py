"""Event schema definitions for Kafka messages (Pydantic models)."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base event with common metadata."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int
    schema_version: str = "1.0"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "event_type": "task.created",
                    "timestamp": "2025-01-15T10:30:00Z",
                    "user_id": 42,
                    "schema_version": "1.0",
                }
            ]
        }
    }


class TaskCreatedEvent(BaseEvent):
    """Published when a new task is created via add_task MCP tool."""

    event_type: str = Field(default="task.created", frozen=True)
    task_id: int
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None  # 'low', 'medium', 'high'
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None  # iCalendar RRULE
    category_id: Optional[int] = None
    tag_ids: List[int] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event_id": "abc123",
                    "event_type": "task.created",
                    "timestamp": "2025-01-15T10:30:00Z",
                    "user_id": 42,
                    "task_id": 101,
                    "title": "Weekly team meeting",
                    "priority": "high",
                    "due_date": "2025-01-20T14:00:00Z",
                    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
                    "category_id": 5,
                    "tag_ids": [1, 3],
                }
            ]
        }
    }


class TaskCompletedEvent(BaseEvent):
    """Published when a task is marked complete, triggers recurring task generation."""

    event_type: str = Field(default="task.completed", frozen=True)
    task_id: int
    recurrence_rule: Optional[str] = None
    completed_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event_id": "def456",
                    "event_type": "task.completed",
                    "timestamp": "2025-01-15T16:45:00Z",
                    "user_id": 42,
                    "task_id": 101,
                    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
                    "completed_at": "2025-01-15T16:45:00Z",
                }
            ]
        }
    }


class TaskUpdatedEvent(BaseEvent):
    """Published when task metadata is modified via update_task MCP tool."""

    event_type: str = Field(default="task.updated", frozen=True)
    task_id: int
    updated_fields: dict  # Field name -> new value mapping

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event_id": "ghi789",
                    "event_type": "task.updated",
                    "timestamp": "2025-01-15T11:00:00Z",
                    "user_id": 42,
                    "task_id": 101,
                    "updated_fields": {"due_date": "2025-01-22T14:00:00Z", "priority": "medium"},
                }
            ]
        }
    }


class TaskDeletedEvent(BaseEvent):
    """Published when a task is deleted via delete_task MCP tool."""

    event_type: str = Field(default="task.deleted", frozen=True)
    task_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event_id": "jkl012",
                    "event_type": "task.deleted",
                    "timestamp": "2025-01-15T12:00:00Z",
                    "user_id": 42,
                    "task_id": 101,
                }
            ]
        }
    }


class ReminderSentEvent(BaseEvent):
    """Published when a reminder notification is sent for a task."""

    event_type: str = Field(default="reminder.sent", frozen=True)
    task_id: int
    task_title: str
    task_description: Optional[str] = None
    task_due_date: datetime
    task_priority: Optional[str] = None  # 'low', 'medium', 'high', 'urgent'
    reminder_time: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "event_id": "mno345",
                    "event_type": "reminder.sent",
                    "timestamp": "2025-01-20T13:00:00Z",
                    "user_id": 42,
                    "task_id": 101,
                    "task_title": "Weekly team meeting",
                    "task_description": "Discuss project progress and blockers",
                    "task_due_date": "2025-01-20T14:00:00Z",
                    "task_priority": "high",
                    "reminder_time": "2025-01-20T13:00:00Z",
                }
            ]
        }
    }
