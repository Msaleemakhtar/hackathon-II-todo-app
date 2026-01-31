"""
Dapr pub/sub operations with high-level event publishing functions.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4

from .client import DaprClient


async def publish_task_created_event(
    dapr_client: DaprClient,
    task_id: int,
    task_data: Dict[str, Any],
    user_id: int
) -> None:
    """Publish TaskCreatedEvent via Dapr with message key for partitioning."""
    await dapr_client.publish_event(
        pubsub_name="pubsub",
        topic="task-events",
        data={
            "event_type": "created",
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": task_data.get("created_at", "")
        },
        message_key=str(task_id)
    )


async def publish_task_updated_event(
    dapr_client: DaprClient,
    task_id: int,
    task_data: Dict[str, Any],
    changes: Dict[str, Any],
    user_id: int
) -> None:
    """Publish TaskUpdatedEvent via Dapr with message key for partitioning."""
    await dapr_client.publish_event(
        pubsub_name="pubsub",
        topic="task-events",
        data={
            "event_type": "updated",
            "task_id": task_id,
            "task_data": task_data,
            "changes": changes,
            "user_id": user_id,
            "timestamp": task_data.get("updated_at", "")
        },
        message_key=str(task_id)
    )


async def publish_task_completed_event(
    dapr_client: DaprClient,
    task_id: int,
    task_data: Dict[str, Any],
    user_id: int,
    has_recurrence: bool = False
) -> None:
    """Publish TaskCompletedEvent via Dapr with message key for partitioning.

    Note: Publishes to task-recurrence topic for recurring task processing.
    """
    await dapr_client.publish_event(
        pubsub_name="pubsub",
        topic="task-recurrence",
        data={
            "event_type": "completed",
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": task_data.get("updated_at", ""),
            "has_recurrence": has_recurrence
        },
        message_key=str(task_id)
    )


async def publish_task_deleted_event(
    dapr_client: DaprClient,
    task_id: int,
    user_id: int
) -> None:
    """Publish TaskDeletedEvent via Dapr with message key for partitioning."""
    await dapr_client.publish_event(
        pubsub_name="pubsub",
        topic="task-events",
        data={
            "event_type": "deleted",
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": ""
        },
        message_key=str(task_id)
    )


async def publish_reminder_event(
    dapr_client: DaprClient,
    task_id: int,
    title: str,
    due_at: str,
    remind_at: str,
    user_id: int,
    description: Optional[str] = None,
    priority: Optional[str] = None
) -> None:
    """
    Publish ReminderSentEvent via Dapr.

    Event schema matches ReminderSentEvent (app/kafka/events.py) exactly:
    - event_id: UUID string
    - event_type: "reminder.sent"
    - timestamp: ISO datetime
    - user_id: int
    - schema_version: "1.0"
    - task_id: int
    - task_title: str
    - task_description: Optional[str]
    - task_due_date: ISO datetime
    - task_priority: Optional[str]
    - reminder_time: ISO datetime
    """
    now = datetime.now(timezone.utc)

    await dapr_client.publish_event(
        pubsub_name="pubsub",
        topic="task-reminders",
        data={
            # BaseEvent fields
            "event_id": str(uuid4()),
            "event_type": "reminder.sent",
            "timestamp": now.isoformat(),
            "user_id": user_id,
            "schema_version": "1.0",
            # ReminderSentEvent specific fields
            "task_id": task_id,
            "task_title": title,
            "task_description": description or "",
            "task_due_date": due_at,  # Already ISO format
            "task_priority": priority or "medium",
            "reminder_time": remind_at  # Already ISO format
        },
        message_key=str(task_id)
    )