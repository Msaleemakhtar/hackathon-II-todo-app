#!/usr/bin/env python3
"""Manually publish ReminderSentEvent to Kafka to trigger email delivery."""

import asyncio
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import async_session_maker
from app.kafka.events import ReminderSentEvent
from app.kafka.producer import kafka_producer
from app.services import task_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def publish_reminder_event_for_task(task_id: int):
    """Publish ReminderSentEvent for a specific task."""
    logger.info("=" * 80)
    logger.info("MANUAL REMINDER EVENT PUBLISHER")
    logger.info("=" * 80)

    try:
        # Start Kafka producer
        logger.info("Starting Kafka producer...")
        await kafka_producer.start()
        logger.info("✅ Kafka producer started")

        # Fetch task from database
        logger.info(f"Fetching task {task_id} from database...")
        async with async_session_maker() as session:
            task = await task_service.get_task(session, task_id)
            if not task:
                logger.error(f"❌ Task {task_id} not found")
                return

            logger.info(f"✅ Task found: {task.title}")
            logger.info(f"   User ID: {task.user_id}")
            logger.info(f"   Due date: {task.due_date}")
            logger.info(f"   Priority: {task.priority}")
            logger.info(f"   Reminder sent: {task.reminder_sent}")

        # Create ReminderSentEvent with correct schema
        logger.info("\nCreating ReminderSentEvent...")
        event = ReminderSentEvent(
            task_id=task.id,
            user_id=int(task.user_id),
            task_title=task.title,  # Correct field name
            task_description=task.description or '',
            task_due_date=task.due_date if task.due_date else datetime.now(UTC),  # Correct field name
            task_priority=task.priority.value if task.priority else 'medium',
            reminder_time=datetime.now(UTC),  # Required field
            timestamp=datetime.now(UTC).isoformat()
        )
        logger.info("✅ Event created successfully")
        logger.info(f"   Event type: {event.event_type}")
        logger.info(f"   Task ID: {event.task_id}")
        logger.info(f"   Task title: {event.task_title}")
        logger.info(f"   Task due date: {event.task_due_date}")
        logger.info(f"   Reminder time: {event.reminder_time}")

        # Publish to task-reminders topic
        logger.info("\n📤 Publishing event to 'task-reminders' topic...")
        await kafka_producer.publish_event('task-reminders', event, wait=True)
        logger.info("✅ Event published successfully!")

        logger.info("\n" + "=" * 80)
        logger.info("🎉 REMINDER EVENT PUBLISHED!")
        logger.info("=" * 80)
        logger.info("\nNext steps:")
        logger.info("1. Email delivery service will consume the event")
        logger.info("2. Email will be sent to: saleemakhtar864@gmail.com")
        logger.info("3. Check your inbox for the reminder email!")
        logger.info("\nMonitor email-delivery logs:")
        logger.info("  kubectl logs -n todo-phasev -l app=email-delivery --follow")

    except Exception as e:
        logger.error(f"❌ Failed to publish event: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Stop Kafka producer
        logger.info("\nStopping Kafka producer...")
        await kafka_producer.stop()
        logger.info("✅ Kafka producer stopped")


async def main():
    """Run the event publisher."""
    task_id = 188  # Real task from database verification
    await publish_reminder_event_for_task(task_id)


if __name__ == "__main__":
    asyncio.run(main())
