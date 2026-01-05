"""Test script for email delivery service (logging mode)."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.kafka.events import ReminderSentEvent
from app.kafka.producer import kafka_producer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_reminder_event():
    """Test publishing a reminder event to Kafka."""

    logger.info("🧪 Starting email delivery service test...")

    try:
        # Start Kafka producer
        await kafka_producer.start()
        logger.info("✅ Kafka producer started")

        # Create test reminder event
        now = datetime.now(timezone.utc)
        due_date = now + timedelta(minutes=30)

        test_event = ReminderSentEvent(
            user_id=1,
            task_id=999,
            task_title="Test Email Notification",
            task_description="This is a test reminder to verify email delivery service",
            task_due_date=due_date,
            task_priority="high",
            reminder_time=now,
        )

        logger.info(f"📧 Publishing test ReminderSentEvent:")
        logger.info(f"   - Task ID: {test_event.task_id}")
        logger.info(f"   - Title: {test_event.task_title}")
        logger.info(f"   - Priority: {test_event.task_priority}")
        logger.info(f"   - Due: {test_event.task_due_date}")

        # Publish to Kafka
        await kafka_producer.publish_event(
            topic="task-reminders",
            event=test_event,
            key=str(test_event.task_id),
        )

        logger.info("✅ Test event published to Kafka topic 'task-reminders'")
        logger.info("")
        logger.info("🎯 Next steps:")
        logger.info("   1. Start email delivery service: uvicorn app.services.email_delivery_service_standalone:app --port 8003")
        logger.info("   2. Watch logs for email processing")
        logger.info("   3. Check Redpanda Console for consumer group activity")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)

    finally:
        # Stop Kafka producer
        await kafka_producer.stop()
        logger.info("Kafka producer stopped")


if __name__ == "__main__":
    asyncio.run(test_reminder_event())
