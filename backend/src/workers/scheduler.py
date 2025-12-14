"""
Background scheduler for processing task reminders using APScheduler.

This worker runs as part of the FastAPI application lifecycle and processes
pending reminders every minute.
"""

import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..core.database import AsyncSessionLocal
from ..models.reminder import Reminder
from ..models.task import Task
from ..models.user import User
from ..services.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


async def process_pending_reminders():
    """
    Process all pending reminders that are due.

    This function:
    1. Queries all reminders where is_sent=False and remind_at <= now()
    2. For each reminder, sends the appropriate notification(s)
    3. Marks the reminder as sent
    4. Handles errors gracefully and logs failures
    """
    try:
        logger.info("Starting reminder processing cycle")

        # Get database session
        async with AsyncSessionLocal() as db:
            # Query pending reminders
            now = datetime.utcnow()
            statement = select(Reminder).where(
                Reminder.is_sent == False,  # noqa: E712
                Reminder.remind_at <= now
            )
            result = await db.execute(statement)
            pending_reminders = list(result.scalars().all())

            logger.info(f"Found {len(pending_reminders)} pending reminders to process")

            if not pending_reminders:
                return

            # Process each reminder
            notification_service = NotificationService(db)
            processed_count = 0
            failed_count = 0

            for reminder in pending_reminders:
                try:
                    # Get task and user details
                    task_statement = select(Task).where(Task.id == reminder.task_id)
                    task_result = await db.execute(task_statement)
                    task = task_result.scalar_one_or_none()

                    user_statement = select(User).where(User.id == reminder.user_id)
                    user_result = await db.execute(user_statement)
                    user = user_result.scalar_one_or_none()

                    if not task or not user:
                        logger.warning(
                            f"Reminder {reminder.id}: task or user not found "
                            f"(task_id={reminder.task_id}, user_id={reminder.user_id})"
                        )
                        # Mark as sent to prevent retries
                        await notification_service.mark_as_sent(reminder.id, reminder.user_id)
                        failed_count += 1
                        continue

                    # Prepare notification content
                    title = f"Task Reminder: {task.title}"
                    body = reminder.message or f"Your task '{task.title}' is due soon!"

                    # Additional data for browser notifications
                    notification_data = {
                        "task_id": task.id,
                        "task_title": task.title,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                    }

                    # Send notifications based on channel
                    success = False

                    if reminder.channel in ["browser", "both"]:
                        browser_success = await notification_service.send_browser_notification(
                            user_id=reminder.user_id,
                            title=title,
                            body=body,
                            data=notification_data
                        )
                        success = success or browser_success

                    if reminder.channel in ["email", "both"]:
                        email_success = await notification_service.send_email_notification(
                            user_email=user.email,
                            subject=title,
                            body=body
                        )
                        success = success or email_success

                    # Mark as sent regardless of success to prevent infinite retries
                    # Log if it failed
                    if success:
                        logger.info(
                            f"Successfully sent reminder {reminder.id} for task {task.id} "
                            f"via {reminder.channel}"
                        )
                        processed_count += 1
                    else:
                        logger.error(
                            f"Failed to send reminder {reminder.id} for task {task.id} "
                            f"via {reminder.channel}"
                        )
                        failed_count += 1

                    # Mark as sent
                    await notification_service.mark_as_sent(reminder.id, reminder.user_id)

                except Exception as e:
                    logger.error(f"Error processing reminder {reminder.id}: {e}", exc_info=True)
                    failed_count += 1
                    # Continue with next reminder

            logger.info(
                f"Reminder processing complete: {processed_count} successful, "
                f"{failed_count} failed"
            )

    except Exception as e:
        logger.error(f"Error in reminder processing cycle: {e}", exc_info=True)


def start_scheduler():
    """
    Start the background scheduler for reminder processing.

    This should be called during FastAPI application startup.
    """
    global _scheduler

    if _scheduler is not None:
        logger.warning("Scheduler already running")
        return

    try:
        _scheduler = AsyncIOScheduler()

        # Schedule reminder processing every minute
        _scheduler.add_job(
            process_pending_reminders,
            trigger=CronTrigger(minute="*"),  # Every minute
            id="process_reminders",
            name="Process pending task reminders",
            replace_existing=True,
            max_instances=1,  # Prevent overlapping executions
        )

        _scheduler.start()
        logger.info("Reminder scheduler started successfully")

    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}", exc_info=True)
        raise


def stop_scheduler():
    """
    Stop the background scheduler.

    This should be called during FastAPI application shutdown.
    """
    global _scheduler

    if _scheduler is None:
        logger.warning("Scheduler not running")
        return

    try:
        _scheduler.shutdown(wait=True)
        _scheduler = None
        logger.info("Reminder scheduler stopped successfully")

    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}", exc_info=True)


def get_scheduler_status() -> dict:
    """
    Get the current status of the scheduler.

    Returns:
        Dictionary with scheduler status information
    """
    global _scheduler

    if _scheduler is None:
        return {
            "running": False,
            "jobs": []
        }

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        })

    return {
        "running": _scheduler.running,
        "jobs": jobs
    }
