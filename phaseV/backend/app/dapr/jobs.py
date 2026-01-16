"""
Dapr jobs API operations with job registration helpers.
"""
from typing import Dict, Any
from .client import DaprClient


async def register_notification_job(dapr_client: DaprClient) -> None:
    """Register the notification job with Dapr Jobs API"""
    await dapr_client.schedule_job(
        job_name="check-due-tasks",
        schedule="@every 5s",  # Every 5 seconds
        repeats=-1,  # Infinite repeats
        due_time="0s",  # Start immediately
        ttl="3600s",  # Job expires after 1 hour if not renewed
        data={"type": "notification_check"}
    )


async def register_recurring_task_job(dapr_client: DaprClient) -> None:
    """Register the recurring task job with Dapr Jobs API"""
    await dapr_client.schedule_job(
        job_name="process-recurring-tasks",
        schedule="@every 10s",  # Every 10 seconds
        repeats=-1,  # Infinite repeats
        due_time="0s",  # Start immediately
        ttl="3600s",  # Job expires after 1 hour if not renewed
        data={"type": "recurring_task_check"}
    )