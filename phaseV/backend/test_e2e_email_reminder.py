#!/usr/bin/env python3
"""
End-to-End Test: Publish a reminder event and verify email delivery.

This test:
1. Publishes a ReminderSentEvent to Kafka
2. Waits for the consumer to process it
3. Checks logs for successful email delivery
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from app.kafka.producer import kafka_producer
from app.kafka.events import ReminderSentEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_email_reminder():
    """Test end-to-end email reminder flow."""

    # Use a real task ID from the database for testing
    # Or create a test task that exists in the database
    test_task_id = 1  # Adjust this to a real task ID that exists

    logger.info("=" * 80)
    logger.info("🧪 Starting End-to-End Email Reminder Test")
    logger.info("=" * 80)

    # Start producer
    await kafka_producer.start()
    logger.info("✅ Kafka producer started")

    # Create test reminder event
    event = ReminderSentEvent(
        task_id=test_task_id,
        user_id="test-user-e2e",
        task_title="E2E Test: Complete project documentation",
        task_description="This is a test reminder to verify the email delivery system is working end-to-end.",
        task_due_date=datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1),
        task_priority="high",
        reminder_minutes_before=30,
    )

    logger.info("")
    logger.info("📧 Publishing ReminderSentEvent:")
    logger.info(f"   Task ID: {event.task_id}")
    logger.info(f"   Title: {event.task_title}")
    logger.info(f"   Priority: {event.task_priority}")
    logger.info(f"   Due: {event.task_due_date}")

    # Publish event
    await kafka_producer.send_event("task-reminders", event)
    logger.info("✅ Event published to task-reminders topic")

    # Stop producer
    await kafka_producer.stop()
    logger.info("✅ Kafka producer stopped")

    logger.info("")
    logger.info("⏳ Waiting 15 seconds for consumer to process the event...")
    await asyncio.sleep(15)

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 Test Complete - Now check the logs:")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Run this command to check email delivery logs:")
    logger.info("  kubectl logs -n todo-phasev -l app=email-delivery --tail=50 | grep -A5 -B5 'E2E Test'")
    logger.info("")
    logger.info("Expected output:")
    logger.info("  ✅ Received ReminderSentEvent for task 1")
    logger.info("  ✅ Found email for task 1")
    logger.info("  ✅ Email sent successfully to <email>")
    logger.info("  ✅ Committed offset for task 1")
    logger.info("")
    logger.info("If you see errors about 'Task X or user not found', the task_id doesn't exist in the database.")
    logger.info("In that case, create a real task first or adjust test_task_id in the script.")
    logger.info("")

if __name__ == "__main__":
    asyncio.run(test_email_reminder())
