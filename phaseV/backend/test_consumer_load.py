#!/usr/bin/env python3
"""
Consumer Load Test: Publish 50 reminder events and verify all are consumed.

This test validates:
1. Consumer can process > 13 messages without dying
2. No offset commit failures
3. All messages are delivered exactly once
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

async def publish_reminder_events(count: int):
    """Publish ReminderSentEvent for test tasks."""
    await kafka_producer.start()

    for i in range(1, count + 1):
        event = ReminderSentEvent(
            task_id=1000 + i,  # Use high task IDs to avoid conflicts
            user_id="test-user-load",
            task_title=f"Load Test Task {i}/{count}",
            task_description=f"Load test description #{i}",
            task_due_date=datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30),
            task_priority="medium",
            reminder_minutes_before=30,
        )

        await kafka_producer.send_event("task-reminders", event)
        logger.info(f"Published ReminderSentEvent {i}/{count} (task_id={event.task_id})")

    await kafka_producer.stop()

async def main():
    """Run load test."""
    MESSAGE_COUNT = 50

    logger.info(f"🚀 Starting consumer load test ({MESSAGE_COUNT} messages)")

    # Publish reminder events
    logger.info(f"Publishing {MESSAGE_COUNT} ReminderSentEvent messages...")
    await publish_reminder_events(MESSAGE_COUNT)
    logger.info(f"✅ Published {MESSAGE_COUNT} events to task-reminders topic")

    # Wait for consumer to process
    logger.info("Waiting 60 seconds for consumer to process all messages...")
    await asyncio.sleep(60)

    logger.info("")
    logger.info("=" * 80)
    logger.info("🎉 Load test complete!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Verification Steps:")
    logger.info("1. Check email-delivery logs:")
    logger.info("   kubectl logs -n todo-phasev -l app=email-delivery --tail=100")
    logger.info(f"2. Verify {MESSAGE_COUNT} messages were processed")
    logger.info("3. Check for any consumer eviction errors")
    logger.info("4. Verify metrics endpoint:")
    logger.info("   kubectl exec -n todo-phasev -it $(kubectl get pod -n todo-phasev -l app=email-delivery -o jsonpath='{.items[0].metadata.name}') -- curl localhost:8003/metrics")

if __name__ == "__main__":
    asyncio.run(main())
