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

    async def start(self, max_retries: int = 3, retry_delay: int = 5) -> None:
        """
        Initialize Kafka producer in background thread with retry logic.

        Args:
            max_retries: Maximum initialization attempts (default: 3)
            retry_delay: Seconds to wait between retries (default: 5)
        """
        logger.info("=" * 80)
        logger.info("KAFKA PRODUCER INITIALIZATION")
        logger.info("=" * 80)
        logger.info(f"Bootstrap Servers: {config.KAFKA_BOOTSTRAP_SERVERS}")
        logger.info(f"Security Protocol: {config.KAFKA_SECURITY_PROTOCOL}")
        logger.info(f"SASL Mechanism: {config.KAFKA_SASL_MECHANISM}")
        logger.info(f"SASL Username: {config.KAFKA_SASL_USERNAME}")
        logger.info(f"Initialization Timeout: {config.KAFKA_PRODUCER_INIT_TIMEOUT_SECONDS}s")
        logger.info(f"Max Retries: {max_retries}")
        logger.info("=" * 80)

        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Kafka producer initialization attempt {attempt}/{max_retries}")

                # Create SSL context
                ssl_context = config.get_kafka_ssl_context()

                # Initialize producer in MAIN event loop
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
                self._is_healthy = True

                # Start background event loop AFTER successful producer initialization
                if not self._background_loop or not self._background_thread:
                    self._start_background_loop()
                    logger.info("Kafka background event loop started")

                logger.info(f"✅ Kafka producer initialized successfully on attempt {attempt}")
                logger.info("Skipping topic creation (topics managed externally)")
                return  # Success - exit retry loop

            except Exception as e:
                last_exception = e
                logger.error(f"❌ Kafka producer initialization attempt {attempt}/{max_retries} failed: {e}")
                self._is_healthy = False

                # Don't call stop() on failed producer - just discard it
                # Calling stop() on a producer that failed to start can corrupt connection state
                if self._producer:
                    self._producer = None
                    logger.debug("Discarded failed producer instance")

                # DON'T clean up background loop between retries - keep it running
                # Only clean up on final failure
                if attempt >= max_retries:
                    logger.error(f"Failed to start Kafka producer after {max_retries} attempts")
                    # Clean up background loop on final failure
                    if self._background_loop and self._background_thread:
                        try:
                            self._background_loop.call_soon_threadsafe(self._background_loop.stop)
                            self._background_thread.join(timeout=2.0)
                        except Exception as cleanup_error:
                            logger.warning(f"Error cleaning up background loop: {cleanup_error}")
                    self._background_loop = None
                    self._background_thread = None
                    raise last_exception
                else:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)

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
        """Start persistent background event loop in separate thread with exception handling."""

        def run_loop(loop):
            """Run event loop with comprehensive error handling."""
            try:
                asyncio.set_event_loop(loop)
                logger.info(f"Background event loop started in thread: {threading.current_thread().name}")

                # Set exception handler for coroutines
                def exception_handler(loop, context):
                    msg = context.get("exception", context["message"])
                    logger.error(
                        f"Background loop exception: {msg}",
                        extra={"context": context},
                        exc_info=context.get("exception")
                    )

                loop.set_exception_handler(exception_handler)
                loop.run_forever()

            except Exception as e:
                logger.critical(f"Background event loop crashed: {e}", exc_info=True)
                self._is_healthy = False
            finally:
                logger.warning("Background event loop stopped")
                try:
                    loop.close()
                except Exception as e:
                    logger.error(f"Error closing background loop: {e}")

        self._background_loop = asyncio.new_event_loop()
        self._background_thread = threading.Thread(
            target=run_loop,
            args=(self._background_loop,),
            daemon=True,
            name="kafka-producer-background-loop"
        )
        self._background_thread.start()
        logger.info(f"Started background thread: {self._background_thread.name}")

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
        Publish event to Kafka topic.

        Uses producer.send_and_wait() which waits for broker acknowledgment.

        Args:
            topic: Kafka topic name
            event: Pydantic event model
            key: Optional partition key (defaults to task_id if available)
            wait: If True, wait for publish to complete before returning (default: False)

        Returns:
            True if message published successfully, False otherwise
        """
        # Lazy initialization: initialize producer on first use
        if not self._producer:
            logger.info("Kafka producer not initialized - attempting lazy initialization...")
            try:
                await self.start()
                logger.info("Lazy initialization successful")
            except Exception as e:
                logger.error(f"Lazy initialization failed: {e}")
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

            # When wait=True, publish directly in current event loop for synchronous behavior
            # When wait=False, use background thread for fire-and-forget
            if wait:
                # Synchronous publish in current event loop
                logger.info(f"📤 Publishing {event.event_type} synchronously (key: {partition_key}, event_id: {event.event_id})")
                try:
                    logger.info(f"⏳ Calling send_and_wait for {event.event_type}...")
                    record_metadata = await self._producer.send_and_wait(topic=topic, value=event_json, key=key_bytes)
                    logger.info(
                        f"✅ Published {event.event_type} to {topic} "
                        f"partition {record_metadata.partition} offset {record_metadata.offset} "
                        f"(key: {partition_key})"
                    )
                    return True
                except Exception as e:
                    logger.error(f"Failed to publish {event.event_type} to {topic}: {e} (event_id: {event.event_id})")
                    return False
            else:
                # Fire-and-forget: submit to persistent background event loop
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
                        return True
                    except asyncio.CancelledError:
                        logger.warning(f"❌ Background task CANCELLED for {event.event_type} (event_id: {event.event_id})")
                        raise
                    except Exception as e:
                        logger.error(f"Failed to publish {event.event_type} to {topic}: {e} (event_id: {event.event_id})")
                        return False
                    finally:
                        logger.info(f"🏁 Background task FINISHED for {event.event_type} (event_id: {event.event_id})")

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
        Check Kafka producer health including background thread status.

        Returns True if all checks pass:
        - Producer is initialized
        - Health flag is set
        - Background thread is alive
        - Background event loop is running
        """
        try:
            # Basic checks
            if self._producer is None:
                logger.warning("Health check failed: Producer not initialized")
                return False

            if not self._is_healthy:
                logger.warning("Health check failed: Health flag is False")
                return False

            # Background thread checks
            if self._background_thread is None:
                logger.error("Health check failed: Background thread is None")
                return False

            if not self._background_thread.is_alive():
                logger.error("Health check failed: Background thread is dead")
                self._is_healthy = False
                return False

            # Background event loop checks
            if self._background_loop is None:
                logger.error("Health check failed: Background loop is None")
                return False

            if self._background_loop.is_closed():
                logger.error("Health check failed: Background loop is closed")
                self._is_healthy = False
                return False

            if not self._background_loop.is_running():
                logger.error("Health check failed: Background loop is not running")
                self._is_healthy = False
                return False

            return True

        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            return False

    def get_background_thread_status(self) -> dict:
        """Get detailed status of background thread for diagnostics."""
        return {
            "thread_exists": self._background_thread is not None,
            "thread_alive": self._background_thread.is_alive() if self._background_thread else False,
            "thread_name": self._background_thread.name if self._background_thread else None,
            "loop_exists": self._background_loop is not None,
            "loop_running": self._background_loop.is_running() if self._background_loop else False,
            "loop_closed": self._background_loop.is_closed() if self._background_loop else None,
            "producer_exists": self._producer is not None,
            "is_healthy": self._is_healthy,
        }

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
