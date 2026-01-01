"""Kafka producer manager for event publishing."""

import asyncio
import logging
import threading
from typing import Optional

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import KafkaError

from app.kafka import config
from app.kafka.events import BaseEvent

logger = logging.getLogger(__name__)


class KafkaProducerManager:
    """Manages Kafka producer lifecycle and event publishing."""

    def __init__(self) -> None:
        self._producer: Optional[AIOKafkaProducer] = None
        self._admin_client: Optional[AIOKafkaAdminClient] = None
        self._is_healthy = False
        self._background_tasks: set[asyncio.Task] = set()

        # Persistent background thread for Kafka publishing (survives HTTP request lifecycle)
        self._background_loop: Optional[asyncio.AbstractEventLoop] = None
        self._background_thread: Optional[threading.Thread] = None

    async def start(self) -> None:
        """Initialize Kafka producer in background thread for thread-safe operation."""
        try:
            # Start persistent background event loop FIRST
            self._start_background_loop()
            logger.info("Kafka background event loop started")

            # Initialize producer IN the background thread's event loop
            async def init_producer():
                # Get SSL context if using SASL_SSL
                ssl_context = config.get_kafka_ssl_context()

                # Initialize producer in background thread's event loop
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                    security_protocol=config.KAFKA_SECURITY_PROTOCOL,
                    sasl_mechanism=config.KAFKA_SASL_MECHANISM,
                    sasl_plain_username=config.KAFKA_SASL_USERNAME,
                    sasl_plain_password=config.KAFKA_SASL_PASSWORD,
                    ssl_context=ssl_context,
                    **config.KAFKA_PRODUCER_CONFIG,
                )
                await self._producer.start()
                logger.info("Kafka producer started successfully in background thread")
                self._is_healthy = True

            # Submit producer initialization to background loop and wait for completion
            future = asyncio.run_coroutine_threadsafe(init_producer(), self._background_loop)
            future.result(timeout=30)  # Wait up to 30 seconds for initialization

            logger.info("Skipping topic creation (topics managed externally)")

        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            self._is_healthy = False
            raise

    async def stop(self) -> None:
        """Gracefully shutdown Kafka producer."""
        # Stop producer in background thread where it was created
        if self._producer and self._background_loop:
            async def stop_producer():
                await self._producer.stop()
                logger.info("Kafka producer stopped")

            future = asyncio.run_coroutine_threadsafe(stop_producer(), self._background_loop)
            try:
                future.result(timeout=5.0)
            except Exception as e:
                logger.error(f"Error stopping producer: {e}")

        # Stop background event loop
        if self._background_loop and self._background_thread:
            self._background_loop.call_soon_threadsafe(self._background_loop.stop)
            self._background_thread.join(timeout=5.0)
            logger.info("Kafka background event loop stopped")

        self._is_healthy = False

    def _start_background_loop(self) -> None:
        """Start persistent background event loop in separate thread."""

        def run_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self._background_loop = asyncio.new_event_loop()
        self._background_thread = threading.Thread(target=run_loop, args=(self._background_loop,), daemon=True)
        self._background_thread.start()

    async def _create_topics(self) -> None:
        """Programmatically create Kafka topics if they don't exist."""
        try:
            # Get SSL context if using SASL_SSL
            ssl_context = config.get_kafka_ssl_context()

            self._admin_client = AIOKafkaAdminClient(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                security_protocol=config.KAFKA_SECURITY_PROTOCOL,
                sasl_mechanism=config.KAFKA_SASL_MECHANISM,
                sasl_plain_username=config.KAFKA_SASL_USERNAME,
                sasl_plain_password=config.KAFKA_SASL_PASSWORD,
                ssl_context=ssl_context,
            )
            await self._admin_client.start()

            # Get existing topics
            existing_topics = await self._admin_client.list_topics()

            # Create topics that don't exist
            topics_to_create = []
            for topic_name, topic_config in config.KAFKA_TOPICS.items():
                if topic_name not in existing_topics:
                    new_topic = NewTopic(
                        name=topic_name,
                        num_partitions=int(topic_config["num_partitions"]),
                        replication_factor=int(topic_config["replication_factor"]),
                        topic_configs={"retention.ms": str(topic_config["retention_ms"])},
                    )
                    topics_to_create.append(new_topic)
                    logger.info(f"Creating topic: {topic_name}")

            if topics_to_create:
                await self._admin_client.create_topics(topics_to_create, validate_only=False)
                logger.info(f"Created {len(topics_to_create)} Kafka topics")
            else:
                logger.info("All Kafka topics already exist")

        except KafkaError as e:
            logger.warning(f"Failed to create topics: {e}")
            # Don't raise - topics might already exist or be auto-created
        finally:
            if self._admin_client:
                await self._admin_client.close()

    async def _send_async(
        self, topic: str, value: bytes, key: Optional[bytes], partition_key: str, event_type: str, event_id: str
    ) -> None:
        """Background task to send message to Kafka with acknowledgment."""
        import time

        start_time = time.perf_counter()
        try:
            result = await self._producer.send_and_wait(topic=topic, value=value, key=key)
            latency_ms = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
            logger.info(
                f"✅ Published {event_type} to {topic} partition {result.partition} offset {result.offset} "
                f"(key: {partition_key}, latency: {latency_ms:.2f}ms)"
            )
        except Exception as e:
            logger.error(f"Failed to publish {event_type} to {topic}: {e} (event_id: {event_id})")

    def _task_done_callback(self, task: asyncio.Task) -> None:
        """
        Remove completed task from tracking set.

        This callback is automatically invoked when a background task completes,
        preventing memory leaks by removing the task reference from the set.
        """
        self._background_tasks.discard(task)

        # Log any exceptions that occurred during task execution
        try:
            task.result()  # Raises exception if task failed
        except asyncio.CancelledError:
            pass  # Expected during shutdown
        except Exception as e:
            logger.error(f"Background task failed: {e}")

    async def publish_event(
        self, topic: str, event: BaseEvent, key: Optional[str] = None, wait: bool = False
    ) -> bool:
        """
        Publish event to Kafka topic using true fire-and-forget.

        Uses producer.send() which returns immediately and buffers the message.
        aiokafka handles delivery in background without blocking the HTTP request.

        Args:
            topic: Kafka topic name
            event: Pydantic event model
            key: Optional partition key (defaults to task_id if available)
            wait: Ignored (kept for API compatibility)

        Returns:
            True if message buffered successfully, False otherwise
        """
        if not self._producer:
            logger.error("Kafka producer not initialized")
            return False

        try:
            # Serialize event to JSON
            event_json = event.model_dump_json().encode("utf-8")

            # Use task_id as partition key if available and no key provided
            partition_key = key
            if partition_key is None and hasattr(event, "task_id"):
                partition_key = str(event.task_id)

            # Encode partition key
            key_bytes = partition_key.encode("utf-8") if partition_key else None

            # Submit to persistent background event loop (survives HTTP session termination)
            async def send_with_logging():
                logger.info(f"🚀 Background task STARTED for {event.event_type} (event_id: {event.event_id})")
                try:
                    logger.info(f"⏳ Calling send_and_wait for {event.event_type}...")
                    record_metadata = await self._producer.send_and_wait(topic=topic, value=event_json, key=key_bytes)
                    logger.info(
                        f"✅ Published {event.event_type} to {topic} "
                        f"partition {record_metadata.partition} offset {record_metadata.offset} "
                        f"(key: {partition_key})"
                    )
                except asyncio.CancelledError:
                    logger.warning(f"❌ Background task CANCELLED for {event.event_type} (event_id: {event.event_id})")
                    raise
                except Exception as e:
                    logger.error(f"Failed to publish {event.event_type} to {topic}: {e} (event_id: {event.event_id})")
                finally:
                    logger.info(f"🏁 Background task FINISHED for {event.event_type} (event_id: {event.event_id})")

            # Schedule coroutine on persistent background loop (NOT current request loop)
            if self._background_loop:
                future = asyncio.run_coroutine_threadsafe(send_with_logging(), self._background_loop)
                logger.info(f"📤 Queued {event.event_type} for {topic} (key: {partition_key}, event_id: {event.event_id}) [background_thread]")
                return True
            else:
                logger.error("Kafka background event loop not initialized")
                return False

        except KafkaError as e:
            logger.error(
                f"Failed to buffer {event.event_type} for {topic}: {e} (event_id: {event.event_id})"
            )
            return False
        except Exception as e:
            logger.error(f"Unexpected error buffering event: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Check Kafka producer health.

        Returns True if producer is initialized and healthy flag is set.
        Avoids cross-event-loop complexity by trusting the internal health flag.
        """
        return self._producer is not None and self._is_healthy

    def get_pending_tasks_count(self) -> int:
        """
        Get count of pending background tasks for monitoring.

        Returns:
            Number of background tasks currently in flight
        """
        return len(self._background_tasks)

    async def reconnect(self) -> bool:
        """
        Attempt to reconnect to Kafka broker.

        Returns:
            True if reconnection succeeded, False otherwise
        """
        logger.info("Attempting Kafka reconnection...")
        try:
            await self.stop()
            await asyncio.sleep(5)  # Wait before retry
            await self.start()
            logger.info("Kafka reconnection successful")
            return True
        except Exception as e:
            logger.error(f"Kafka reconnection failed: {e}")
            return False


# Global producer instance
kafka_producer = KafkaProducerManager()
