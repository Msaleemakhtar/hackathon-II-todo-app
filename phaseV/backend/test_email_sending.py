#!/usr/bin/env python3
"""Test script to trigger email reminder."""

import asyncio
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import async_session_maker
from app.models.task import PriorityLevel
from app.services import task_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def create_reminder_task():
    """Create a task with past due date to trigger immediate email reminder."""

    # Create task due 10 minutes ago to trigger immediate reminder
    due_time = datetime.now(UTC) - timedelta(minutes=10)

    logger.info("Creating test task for email reminder...")
    logger.info(f"Due date: {due_time} (10 minutes ago)")

    async with async_session_maker() as session:
        task = await task_service.create_task(
            session=session,
            user_id="6626448337574572154",  # Real user ID from logs
            title=f"🔔 EMAIL TEST: Please respond to this reminder - {datetime.now(UTC).isoformat()}",
            description="This is a test email from the Todo App event-driven architecture. If you receive this, email delivery is working! ✅",
            priority=PriorityLevel.HIGH,
            due_date=due_time.replace(tzinfo=None),  # Make naive for DB
        )

        logger.info(f"✅ Task created: ID={task.id}, due_date={task.due_date}")
        logger.info(f"📧 Email should be sent to: saleemakhtar864@gmail.com")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Notification service will detect this task (polls every ~4 seconds)")
        logger.info("2. It will publish ReminderSentEvent to 'task-reminders' topic")
        logger.info("3. Email delivery service will consume the event")
        logger.info("4. Email will be sent via Gmail SMTP")
        logger.info("")
        logger.info("Monitor logs with:")
        logger.info("  kubectl logs -n todo-phasev -l app=notification-service --follow")
        logger.info("  kubectl logs -n todo-phasev -l app=email-delivery --follow")

        return task.id


async def main():
    """Run test."""
    try:
        task_id = await create_reminder_task()
        logger.info(f"\n✅ Test task created! Task ID: {task_id}")
        logger.info("⏳ Wait 5-10 seconds for email to be sent...")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
