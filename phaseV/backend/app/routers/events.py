"""
Events router for handling Dapr subscriptions and CloudEvents.
"""
from fastapi import APIRouter, Request
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events")


@router.get("/dapr/subscribe")
async def get_subscriptions():
    """
    Dapr calls this endpoint to discover subscriptions.
    """
    return [
        {
            "pubsubname": "pubsub",
            "topic": "task-reminders",
            "route": "/events/reminder-sent",
            "metadata": {
                "rawPayload": "false"  # Use CloudEvents format
            }
        },
        {
            "pubsubname": "pubsub",
            "topic": "task-recurrence",
            "route": "/events/task-completed",
            "metadata": {
                "rawPayload": "false"  # Use CloudEvents format
            }
        }
    ]


@router.post("/reminder-sent")
async def handle_reminder_event(request: Request):
    """
    Dapr sends CloudEvents to this endpoint.
    Extract data field from CloudEvents envelope.
    """
    cloud_event: Dict[str, Any] = await request.json()
    
    # Validate CloudEvent structure
    if not validate_cloud_event(cloud_event):
        logger.error(f"Invalid CloudEvent received: {cloud_event}")
        return {"status": "ERROR", "message": "Invalid CloudEvent format"}
    
    # Extract original event data from CloudEvents envelope
    event_data = cloud_event.get("data", {})
    
    # Extract task and user IDs
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    
    if not task_id or not user_id:
        logger.error(f"Missing task_id or user_id in event: {event_data}")
        return {"status": "ERROR", "message": "Missing required fields"}
    
    logger.info(f"Processing reminder event for task {task_id}, user {user_id}")
    
    # Process the reminder event using existing service logic
    from app.services.email_delivery_service import process_reminder_event
    await process_reminder_event(task_id, user_id, event_data)
    
    return {"status": "SUCCESS"}


@router.post("/task-completed")
async def handle_task_completed_event(request: Request):
    """
    Handle task completed events for recurring tasks.
    """
    cloud_event: Dict[str, Any] = await request.json()
    
    # Validate CloudEvent structure
    if not validate_cloud_event(cloud_event):
        logger.error(f"Invalid CloudEvent received: {cloud_event}")
        return {"status": "ERROR", "message": "Invalid CloudEvent format"}
    
    # Extract original event data from CloudEvents envelope
    event_data = cloud_event.get("data", {})
    
    # Extract task and user IDs
    task_id = event_data.get("task_id")
    user_id = event_data.get("user_id")
    
    if not task_id or not user_id:
        logger.error(f"Missing task_id or user_id in event: {event_data}")
        return {"status": "ERROR", "message": "Missing required fields"}
    
    logger.info(f"Processing task completed event for task {task_id}, user {user_id}")
    
    # Process the task completed event for recurrence
    from app.services.recurring_task_service import process_task_completion
    await process_task_completion(task_id, user_id, event_data)
    
    return {"status": "SUCCESS"}


def validate_cloud_event(cloud_event: Dict[str, Any]) -> bool:
    """
    Validate CloudEvent structure before processing.
    """
    required_fields = ["specversion", "id", "source", "type", "data"]
    for field in required_fields:
        if field not in cloud_event:
            logger.error(f"Missing required CloudEvent field: {field}")
            return False
    
    if cloud_event.get("specversion") != "1.0":
        logger.error(f"Invalid CloudEvents version: {cloud_event.get('specversion')}")
        return False
    
    return True