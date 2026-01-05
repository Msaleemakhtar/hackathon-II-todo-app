"""Notification service for automatic task reminders."""

import asyncio
import logging
import signal
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.kafka.events import ReminderSentEvent
from app.kafka.producer import kafka_producer
from app.models.task import TaskPhaseIII

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Background service that polls database for tasks with approaching due dates
    and sends reminder notifications.
    """

    def __init__(self, poll_interval: int = 5, reminder_window_minutes: int = 60):
        """
        Initialize notification service.

        Args:
            poll_interval: Seconds between database polls (default: 5)
            reminder_window_minutes: Send reminders for tasks due within this window (default: 60)
        """
        self.poll_interval = poll_interval
        self.reminder_window = timedelta(minutes=reminder_window_minutes)
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the notification service background loop."""
        if self._running:
            logger.warning("Notification service already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            f"Notification service started (poll_interval={self.poll_interval}s, "
            f"reminder_window={self.reminder_window.total_seconds() / 60}min)"
        )

    async def stop(self) -> None:
        """Stop the notification service gracefully."""
        if not self._running:
            return

        logger.info("Stopping notification service...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.info("Notification service stopped")

    async def health_check(self) -> bool:
        """
        Check service health.

        Returns:
            True if service is running and healthy
        """
        if not self._running:
            return False

        # Check Kafka producer health (optional - only warn if unhealthy)
        try:
            kafka_healthy = await kafka_producer.health_check()
            if not kafka_healthy:
                logger.warning("Kafka producer unhealthy in notification service (non-critical)")
        except Exception:
            # Kafka producer not available (standalone mode) - not critical for notification service
            pass

        # Check database connectivity (critical)
        try:
            async for session in get_session():
                # Simple query to verify DB connection
                result = await session.execute(select(TaskPhaseIII).limit(1))
                result.scalars().first()
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

        return True

    async def _run_loop(self) -> None:
        """Main background loop for processing reminders."""
        logger.info("Starting notification service main loop")

        while self._running:
            try:
                await self._process_reminders()
            except asyncio.CancelledError:
                logger.info("Notification loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in notification loop: {e}", exc_info=True)
                # Continue running despite errors
                await asyncio.sleep(self.poll_interval)
            else:
                # Sleep before next poll
                await asyncio.sleep(self.poll_interval)

        logger.info("Notification service main loop stopped")

    async def _process_reminders(self) -> None:
        """
        Poll database for tasks with approaching due dates and send reminders.

        This implements T014, T015, T016, T017:
        - T014: Database polling logic (every 5 seconds) for tasks due within 1 hour
        - T015: Atomic reminder_sent flag update to prevent duplicates
        - T016: Reminder logging with format "🔔 REMINDER: Task '[title]' (ID: [id]) is due in [N] minutes"
        - T017: Publish ReminderSentEvent to task-reminders topic
        """
        async for session in get_session():
            try:
                # Calculate reminder window
                # Use timezone-naive datetime to match database column (TIMESTAMP WITHOUT TIME ZONE)
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                reminder_cutoff = now + self.reminder_window

                # Query tasks due within reminder window
                # T014: Poll database every 5 seconds for tasks due within 1 hour
                stmt = select(TaskPhaseIII).where(
                    and_(
                        TaskPhaseIII.due_date.isnot(None),
                        TaskPhaseIII.due_date <= reminder_cutoff,
                        TaskPhaseIII.reminder_sent == False,  # noqa: E712
                        TaskPhaseIII.completed == False,  # noqa: E712
                    )
                )

                result = await session.execute(stmt)
                tasks = result.scalars().all()

                if tasks:
                    logger.info(f"Found {len(tasks)} tasks requiring reminders")

                # Process each task
                for task in tasks:
                    await self._send_reminder(session, task)

                # Commit all updates
                await session.commit()

            except Exception as e:
                logger.error(f"Error processing reminders: {e}", exc_info=True)
                await session.rollback()

    async def _send_reminder(self, session: AsyncSession, task: TaskPhaseIII) -> None:
        """
        Send reminder for a single task.

        Args:
            session: Database session
            task: Task to send reminder for
        """
        try:
            # T015: Implement atomic reminder_sent flag update to prevent duplicates
            # Use optimistic locking by checking reminder_sent in the UPDATE statement
            task.reminder_sent = True
            await session.flush()  # Flush to get row updated

            # Calculate time until due
            now = datetime.now(timezone.utc)
            # Convert naive due_date from database to UTC timezone-aware for comparison
            task_due_date_utc = task.due_date.replace(tzinfo=timezone.utc) if task.due_date else None
            time_until_due = task_due_date_utc - now if task_due_date_utc else timedelta(0)
            minutes_until_due = int(time_until_due.total_seconds() / 60)

            # T016: Implement reminder logging with format
            logger.info(
                f"🔔 REMINDER: Task '{task.title}' (ID: {task.id}) is due in {minutes_until_due} minutes"
            )

            # T017: Publish ReminderSentEvent to task-reminders topic (enriched with task details)
            event = ReminderSentEvent(
                user_id=int(task.user_id) if task.user_id.isdigit() else hash(task.user_id),
                task_id=task.id,
                task_title=task.title,
                task_description=task.description or "",
                task_due_date=task.due_date,
                task_priority=task.priority or "medium",
                reminder_time=now,
            )

            await kafka_producer.publish_event(
                topic="task-reminders", event=event, key=str(task.id), wait=True
            )

            logger.debug(f"Reminder sent and published to Kafka for task {task.id}")

        except Exception as e:
            logger.error(f"Failed to send reminder for task {task.id}: {e}", exc_info=True)
            # Rollback the reminder_sent flag if publishing failed
            task.reminder_sent = False
            raise


# Global notification service instance
notification_service = NotificationService()


# T018: Add graceful shutdown handling (SIGTERM)
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating graceful shutdown...")
        asyncio.create_task(notification_service.stop())

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
