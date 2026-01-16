"""
Dapr state management operations with idempotency helpers.
"""
from typing import Any, Dict, Optional
from .client import DaprClient


async def get_last_poll_timestamp(dapr_client: DaprClient) -> Optional[Dict[str, Any]]:
    """Get the last poll timestamp for notification service"""
    return await dapr_client.get_state(
        store_name="statestore-postgres",
        key="notification:last_poll"
    )


async def save_last_poll_timestamp(dapr_client: DaprClient, timestamp: str) -> None:
    """Save the last poll timestamp for notification service"""
    await dapr_client.save_state(
        store_name="statestore-postgres",
        key="notification:last_poll",
        value={"timestamp": timestamp},
        metadata={"ttl": "3600"}  # Auto-expire after 1 hour
    )


async def check_reminder_processed(dapr_client: DaprClient, task_id: int) -> bool:
    """Check if a reminder for a task has already been processed"""
    state_key = f"reminder:task:{task_id}"
    existing = await dapr_client.get_state(
        store_name="statestore-postgres",
        key=state_key
    )
    return existing is not None


async def mark_reminder_processed(dapr_client: DaprClient, task_id: int, user_id: int) -> None:
    """Mark a reminder for a task as processed"""
    state_key = f"reminder:task:{task_id}"
    await dapr_client.save_state(
        store_name="statestore-postgres",
        key=state_key,
        value={
            "processed_at": "",
            "user_id": user_id
        },
        metadata={"ttl": "86400"}  # Expire after 24 hours
    )


async def get_processed_reminder(dapr_client: DaprClient, task_id: int) -> Optional[Dict[str, Any]]:
    """Get the processed reminder state for a task"""
    state_key = f"reminder:task:{task_id}"
    return await dapr_client.get_state(
        store_name="statestore-postgres",
        key=state_key
    )


async def delete_processed_reminder(dapr_client: DaprClient, task_id: int) -> None:
    """Delete the processed reminder state for a task"""
    state_key = f"reminder:task:{task_id}"
    await dapr_client.delete_state(
        store_name="statestore-postgres",
        key=state_key
    )