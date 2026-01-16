"""
Dapr pub/sub operations with high-level event publishing functions.
"""
from typing import Dict, Any
from .client import DaprClient


async def publish_task_created_event(
    dapr_client: DaprClient,
    task_id: int,
    task_data: Dict[str, Any],
    user_id: int
) -> None:
    """Publish TaskCreatedEvent via Dapr"""
    await dapr_client.publish_event(
        pubsub_name="pubsub-kafka",
        topic="task-events",
        data={
            "event_type": "created",
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": task_data.get("created_at", "")
        }
    )


async def publish_task_updated_event(
    dapr_client: DaprClient,
    task_id: int,
    task_data: Dict[str, Any],
    changes: Dict[str, Any],
    user_id: int
) -> None:
    """Publish TaskUpdatedEvent via Dapr"""
    await dapr_client.publish_event(
        pubsub_name="pubsub-kafka",
        topic="task-events",
        data={
            "event_type": "updated",
            "task_id": task_id,
            "task_data": task_data,
            "changes": changes,
            "user_id": user_id,
            "timestamp": task_data.get("updated_at", "")
        }
    )


async def publish_task_completed_event(
    dapr_client: DaprClient,
    task_id: int,
    task_data: Dict[str, Any],
    user_id: int,
    has_recurrence: bool = False
) -> None:
    """Publish TaskCompletedEvent via Dapr"""
    await dapr_client.publish_event(
        pubsub_name="pubsub-kafka",
        topic="task-events",
        data={
            "event_type": "completed",
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": task_data.get("updated_at", ""),
            "has_recurrence": has_recurrence
        }
    )


async def publish_task_deleted_event(
    dapr_client: DaprClient,
    task_id: int,
    user_id: int
) -> None:
    """Publish TaskDeletedEvent via Dapr"""
    await dapr_client.publish_event(
        pubsub_name="pubsub-kafka",
        topic="task-events",
        data={
            "event_type": "deleted",
            "task_id": task_id,
            "user_id": user_id,
            "timestamp": ""
        }
    )


async def publish_reminder_event(
    dapr_client: DaprClient,
    task_id: int,
    title: str,
    due_at: str,
    remind_at: str,
    user_id: int
) -> None:
    """Publish ReminderEvent via Dapr"""
    await dapr_client.publish_event(
        pubsub_name="pubsub-kafka",
        topic="task-reminders",
        data={
            "task_id": task_id,
            "title": title,
            "due_at": due_at,
            "remind_at": remind_at,
            "user_id": user_id
        }
    )