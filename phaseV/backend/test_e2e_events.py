#!/usr/bin/env python3
"""
End-to-End Event-Driven Architecture Test Script

Tests the complete flow:
1. Create a task → TaskCreatedEvent published to task-events topic
2. Create a task with reminder → ReminderSentEvent published to task-reminders topic
3. Complete a recurring task → TaskCompletedEvent published to task-recurrence topic
"""

import asyncio
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.database import async_session_maker
from app.kafka.events import TaskCreatedEvent
from app.kafka.producer import kafka_producer
from app.models.task import PriorityLevel, TaskPhaseIII
from app.services import task_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_task_creation_event():
    """Test 1: Create task and verify event published to task-events topic."""
    logger.info("=" * 80)
    logger.info("TEST 1: Task Creation Event Flow")
    logger.info("=" * 80)

    try:
        # Start Kafka producer
        logger.info("Starting Kafka producer...")
        await kafka_producer.start()
        logger.info("✅ Kafka producer started")

        # Create a test task
        test_user_id = "test-user-e2e"
        task_title = f"E2E Test Task - {datetime.now(UTC).isoformat()}"

        logger.info(f"Creating task: {task_title}")
        async with async_session_maker() as session:
            task = await task_service.create_task(
                session=session,
                user_id=test_user_id,
                title=task_title,
                description="This is an end-to-end test task to verify event publishing",
                priority=PriorityLevel.HIGH,
            )
            logger.info(f"✅ Task created with ID: {task.id}")

        logger.info("✅ TaskCreatedEvent should have been published to 'task-events' topic")
        logger.info(f"   Check notification-service logs for event processing")

        return task.id

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        raise


async def test_reminder_event(task_id: int):
    """Test 2: Create task with reminder and check notification service processing."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 2: Task Reminder Event Flow")
    logger.info("=" * 80)

    try:
        # Create task with due date in the past to trigger immediate reminder
        test_user_id = "test-user-e2e"
        reminder_time = datetime.now(UTC) - timedelta(minutes=5)  # 5 minutes ago
        task_title = f"E2E Reminder Test - {datetime.now(UTC).isoformat()}"

        logger.info(f"Creating task with reminder due: {reminder_time}")
        async with async_session_maker() as session:
            task = await task_service.create_task(
                session=session,
                user_id=test_user_id,
                title=task_title,
                description="Task with past due date to trigger reminder",
                priority=PriorityLevel.MEDIUM,
                due_date=reminder_time.replace(tzinfo=None),  # Make naive for DB
            )
            logger.info(f"✅ Task created with ID: {task.id}, due_date: {task.due_date}")

        logger.info("✅ Notification service should detect this task in its polling loop")
        logger.info("   It will publish ReminderSentEvent to 'task-reminders' topic")
        logger.info(f"   Check notification-service and email-delivery logs")

        return task.id

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        raise


async def test_recurring_task_event():
    """Test 3: Complete recurring task and verify event published to task-recurrence topic."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 3: Recurring Task Event Flow")
    logger.info("=" * 80)

    try:
        # Create recurring task
        test_user_id = "test-user-e2e"
        task_title = f"E2E Recurring Test - {datetime.now(UTC).isoformat()}"
        recurrence_rule = "FREQ=DAILY"  # Daily recurrence

        logger.info(f"Creating recurring task with rule: {recurrence_rule}")
        async with async_session_maker() as session:
            task = await task_service.create_task(
                session=session,
                user_id=test_user_id,
                title=task_title,
                description="Recurring task for E2E testing",
                priority=PriorityLevel.MEDIUM,
                recurrence_rule=recurrence_rule,
            )
            logger.info(f"✅ Recurring task created with ID: {task.id}")

            # Now complete the task to trigger recurrence event
            logger.info(f"Completing task {task.id} to trigger recurrence...")
            updated_task = await task_service.update_task(
                session=session,
                task=task,
                completed=True,
            )
            logger.info(f"✅ Task marked as completed")

        logger.info("✅ TaskCompletedEvent should have been published to 'task-recurrence' topic")
        logger.info(f"   Check recurring-service logs for event processing")
        logger.info(f"   A new task instance should be created by recurring-service")

        return task.id

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        raise


async def main():
    """Run all end-to-end tests."""
    logger.info("🚀 Starting End-to-End Event-Driven Architecture Tests")
    logger.info("")

    try:
        # Test 1: Task Creation Event
        task_id_1 = await test_task_creation_event()
        await asyncio.sleep(2)  # Wait for event processing

        # Test 2: Reminder Event
        task_id_2 = await test_reminder_event(task_id_1)
        await asyncio.sleep(2)  # Wait for event processing

        # Test 3: Recurring Task Event
        task_id_3 = await test_recurring_task_event()
        await asyncio.sleep(2)  # Wait for event processing

        logger.info("")
        logger.info("=" * 80)
        logger.info("🎉 ALL TESTS COMPLETED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Verification Steps:")
        logger.info("1. Check notification-service logs: kubectl logs -n todo-phasev <notification-pod> --tail=50")
        logger.info("2. Check email-delivery logs: kubectl logs -n todo-phasev <email-delivery-pod> --tail=50")
        logger.info("3. Check recurring-service logs: kubectl logs -n todo-phasev <recurring-service-pod> --tail=50")
        logger.info("4. Verify new recurring task created in database")

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Stop Kafka producer
        logger.info("")
        logger.info("Stopping Kafka producer...")
        await kafka_producer.stop()
        logger.info("✅ Kafka producer stopped")


if __name__ == "__main__":
    asyncio.run(main())
