"""Recurring task service for automatic task regeneration on completion."""

import asyncio
import logging
import signal
from datetime import datetime, timezone
from typing import Optional

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.kafka import config
from app.kafka.events import TaskCompletedEvent, TaskCreatedEvent
from app.kafka.producer import kafka_producer
from app.models.task import TaskPhaseIII
from app.utils.rrule_parser import get_next_occurrence

logger = logging.getLogger(__name__)


class RecurringTaskService:
    """
    Kafka consumer service that regenerates recurring tasks when completed.

    Listens to task-recurrence topic for TaskCompletedEvent and creates
    new task instances based on RRULE recurrence rules.
    """

    def __init__(self):
        """Initialize recurring task service."""
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the recurring task service background loop."""
        if self._running:
            logger.warning("Recurring task service already running")
            return

        # Initialize Kafka producer first (needed to publish TaskCreatedEvent)
        try:
            logger.info("Initializing Kafka producer for recurring task service...")
            await kafka_producer.start()
            logger.info("✅ Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise

        # T028: Initialize Kafka consumer for task-recurrence topic
        try:
            # Get SSL context if using SASL_SSL
            ssl_context = config.get_kafka_ssl_context()

            self._consumer = AIOKafkaConsumer(
                "task-recurrence",
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                security_protocol=config.KAFKA_SECURITY_PROTOCOL,
                sasl_mechanism=config.KAFKA_SASL_MECHANISM,
                sasl_plain_username=config.KAFKA_SASL_USERNAME,
                sasl_plain_password=config.KAFKA_SASL_PASSWORD,
                ssl_context=ssl_context,  # Required for SASL_SSL
                group_id=config.RECURRING_TASK_SERVICE_GROUP_ID,  # T056: Consumer group ID
                **config.KAFKA_CONSUMER_CONFIG,
            )
            await self._consumer.start()
            logger.info("Kafka consumer started for task-recurrence topic")

            self._running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Recurring task service started")

        except KafkaError as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise

    async def stop(self) -> None:
        """Stop the recurring task service gracefully."""
        if not self._running:
            return

        logger.info("Stopping recurring task service...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.info("Recurring task service loop stopped")

        if self._consumer:
            await self._consumer.stop()
            logger.info("Kafka consumer stopped")

        # Stop Kafka producer
        try:
            await kafka_producer.stop()
            logger.info("Kafka producer stopped")
        except Exception as e:
            logger.error(f"Error stopping Kafka producer: {e}")

    async def health_check(self) -> bool:
        """
        Check service health (T038).

        Returns:
            True if service is running and healthy
        """
        if not self._running or not self._consumer:
            return False

        # Check Kafka producer health (optional - only warn if unhealthy)
        try:
            kafka_healthy = await kafka_producer.health_check()
            if not kafka_healthy:
                logger.warning("Kafka producer unhealthy in recurring task service (non-critical)")
        except Exception:
            # Kafka producer not available (standalone mode) - not critical for consumer service
            pass

        # Check database connectivity (critical)
        try:
            async for session in get_session():
                from sqlalchemy import select

                result = await session.execute(select(TaskPhaseIII).limit(1))
                result.scalars().first()
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

        return True

    async def _run_loop(self) -> None:
        """Main background loop for processing recurring tasks."""
        logger.info("Starting recurring task service main loop")

        while self._running:
            try:
                async for msg in self._consumer:
                    if not self._running:
                        break

                    await self._process_event(msg)

            except asyncio.CancelledError:
                logger.info("Recurring task loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in recurring task loop: {e}", exc_info=True)
                # Continue running despite errors
                await asyncio.sleep(5)

        logger.info("Recurring task service main loop stopped")

    async def _process_event(self, msg) -> None:
        """
        Process a single TaskCompletedEvent from Kafka.

        Implements T028-T035:
        - T028: Kafka consumer for task-recurrence topic
        - T029: RRULE parsing with dateutil.rrule
        - T030: Next occurrence calculation
        - T031: New recurring task creation
        - T032: Invalid RRULE handling
        - T033: Skip if next occurrence is in past
        - T034: Publish TaskCreatedEvent
        - T035: Manual offset commit

        Args:
            msg: Kafka message from task-recurrence topic
        """
        try:
            # Deserialize event
            event_data = msg.value.decode("utf-8")
            import json

            event_dict = json.loads(event_data)
            event = TaskCompletedEvent(**event_dict)

            logger.info(
                f"Processing TaskCompletedEvent: task_id={event.task_id}, "
                f"recurrence_rule={event.recurrence_rule}"
            )

            # Skip if no recurrence rule
            if not event.recurrence_rule:
                logger.debug(f"Task {event.task_id} has no recurrence rule, skipping")
                await self._consumer.commit()  # T035: Manual offset commit
                return

            # T029, T030: Parse RRULE and calculate next occurrence
            next_due_date = get_next_occurrence(
                rule=event.recurrence_rule,
                from_date=event.completed_at,
                base_due_date=event.completed_at,
            )

            # T032, T033: Handle invalid RRULE or past occurrences
            if next_due_date is None:
                logger.warning(
                    f"No future occurrence for task {event.task_id} "
                    f"with rule {event.recurrence_rule}, skipping"
                )
                await self._consumer.commit()  # T035: Manual offset commit
                return

            # T031: Create new recurring task instance
            async for session in get_session():
                try:
                    # Get original task details
                    original_task = await session.get(TaskPhaseIII, event.task_id)

                    if not original_task:
                        logger.error(f"Original task {event.task_id} not found, skipping")
                        await self._consumer.commit()
                        return

                    # T054: Implement idempotent event processing (duplicate detection)
                    # Check if next occurrence already exists
                    from sqlalchemy import and_, select

                    # Convert next_due_date to naive datetime (database stores naive datetimes)
                    next_due_date_naive = next_due_date.replace(tzinfo=None) if next_due_date.tzinfo else next_due_date

                    existing_query = select(TaskPhaseIII).where(
                        and_(
                            TaskPhaseIII.user_id == original_task.user_id,
                            TaskPhaseIII.title == original_task.title,
                            TaskPhaseIII.due_date == next_due_date_naive,
                            TaskPhaseIII.recurrence_rule == original_task.recurrence_rule,
                        )
                    )
                    existing_result = await session.execute(existing_query)
                    existing_task = existing_result.scalars().first()

                    if existing_task:
                        logger.info(
                            f"Next occurrence for task {event.task_id} already exists "
                            f"(task_id={existing_task.id}), skipping (idempotent)"
                        )
                        await self._consumer.commit()
                        return

                    # Create new task with same properties
                    new_task = TaskPhaseIII(
                        user_id=original_task.user_id,
                        title=original_task.title,
                        description=original_task.description,
                        completed=False,  # New task starts incomplete
                        priority=original_task.priority,
                        due_date=next_due_date_naive,  # Use naive datetime for database
                        category_id=original_task.category_id,
                        recurrence_rule=original_task.recurrence_rule,  # Copy recurrence
                        reminder_sent=False,  # Reset reminder
                    )

                    session.add(new_task)
                    await session.commit()
                    await session.refresh(new_task)

                    logger.info(
                        f"Created new recurring task {new_task.id} from {event.task_id} "
                        f"(due: {next_due_date.isoformat()})"
                    )

                    # T034: Publish TaskCreatedEvent for new recurring task
                    try:
                        created_event = TaskCreatedEvent(
                            user_id=event.user_id,
                            task_id=new_task.id,
                            title=new_task.title,
                            description=new_task.description,
                            priority=new_task.priority.value,
                            due_date=new_task.due_date.replace(tzinfo=timezone.utc)
                            if new_task.due_date
                            else None,
                            recurrence_rule=new_task.recurrence_rule,
                            category_id=new_task.category_id,
                            tag_ids=[],  # Tags not copied in MVP
                        )

                        await kafka_producer.publish_event(
                            topic="task-events", event=created_event, key=str(new_task.id)
                        )

                        logger.info(
                            f"Published TaskCreatedEvent for new recurring task {new_task.id}"
                        )

                    except Exception as e:
                        logger.error(f"Failed to publish TaskCreatedEvent: {e}")
                        # Continue - event publishing is non-blocking

                    # T035: Commit offset after successful processing
                    await self._consumer.commit()

                except Exception as e:
                    logger.error(f"Failed to create recurring task: {e}", exc_info=True)
                    await session.rollback()
                    # Don't commit offset - retry on next run
                    raise

        except Exception as e:
            logger.error(f"Failed to process event: {e}", exc_info=True)
            # T032: Log error, skip event, continue processing
            # Commit offset to skip this malformed event
            try:
                await self._consumer.commit()
            except Exception as commit_error:
                logger.error(f"Failed to commit offset: {commit_error}")


# Global recurring task service instance
recurring_task_service = RecurringTaskService()


# T036: Add graceful shutdown handling (SIGTERM)
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating graceful shutdown...")
        asyncio.create_task(recurring_task_service.stop())

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
