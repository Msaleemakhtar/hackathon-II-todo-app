"""Standalone FastAPI service for email delivery (Kubernetes deployment)."""

import asyncio
import logging
import signal
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from app.services.email_delivery_service import email_delivery_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# Global background task reference
consume_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown of the email delivery service.
    Uses resilient startup - service starts even if Kafka is temporarily unavailable.
    """
    global consume_task

    logger.info("Starting Email Delivery Service...")

    # Try to start the service, but don't fail if Kafka is temporarily unavailable
    try:
        # Start the email delivery service
        await email_delivery_service.start()

        # Start consuming events in background
        consume_task = asyncio.create_task(email_delivery_service.consume_events())
        logger.info("Email delivery consumer task started in background")

    except Exception as e:
        logger.error(f"Failed to connect to Kafka during startup: {e}")
        logger.warning("Service will start in degraded mode. Kafka connection will be retried...")

        # Start a background task that retries Kafka connection
        async def retry_kafka_connection():
            retry_count = 0
            max_retries = 10
            retry_delay = 30  # seconds

            while retry_count < max_retries:
                retry_count += 1
                logger.info(f"Attempting to connect to Kafka (retry {retry_count}/{max_retries})...")
                await asyncio.sleep(retry_delay)

                try:
                    await email_delivery_service.start()

                    # Start consuming in background
                    consume_task = asyncio.create_task(email_delivery_service.consume_events())
                    logger.info("✅ Successfully connected to Kafka and started consuming")
                    return

                except Exception as retry_error:
                    logger.warning(f"Kafka connection retry {retry_count} failed: {retry_error}")

            logger.error(f"Failed to connect to Kafka after {max_retries} retries")

        # Start retry task in background (non-blocking)
        asyncio.create_task(retry_kafka_connection())

    try:
        yield

    finally:
        # Graceful shutdown
        logger.info("Shutting down Email Delivery Service...")

        # Cancel consumer task
        if consume_task:
            consume_task.cancel()
            try:
                await consume_task
            except asyncio.CancelledError:
                logger.info("Consumer task cancelled successfully")

        # Stop the service
        await email_delivery_service.stop()

        logger.info("Email Delivery Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Email Delivery Service",
    description="Kafka consumer service for sending task reminder emails",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes.

    Returns:
        dict: Service health status
    """
    is_healthy = await email_delivery_service.health_check()

    if is_healthy:
        return {
            "status": "healthy",
            "service": "email-delivery",
            "consumer_group": "email-delivery-consumer-group",
            "topic": "task-reminders",
        }
    else:
        # Return 200 but indicate unhealthy (Kubernetes will retry)
        return {
            "status": "unhealthy",
            "service": "email-delivery",
            "message": "Service dependencies not ready",
        }


@app.get("/metrics")
async def metrics():
    """Expose Prometheus-compatible metrics."""
    return {
        "email_delivery_messages_processed_total": email_delivery_service._messages_processed,
        "email_delivery_consecutive_failures": email_delivery_service._consecutive_failures,
        "email_delivery_last_poll_seconds_ago": (
            (datetime.now(timezone.utc) - email_delivery_service._last_poll_time).total_seconds()
            if email_delivery_service._last_poll_time else -1
        ),
        "email_delivery_last_commit_seconds_ago": (
            (datetime.now(timezone.utc) - email_delivery_service._last_commit_time).total_seconds()
            if email_delivery_service._last_commit_time else -1
        ),
        "email_delivery_running": email_delivery_service._running,
    }


@app.get("/")
async def root():
    """
    Root endpoint with service information.

    Returns:
        dict: Service metadata
    """
    return {
        "service": "Email Delivery Service",
        "version": "1.0.0",
        "description": "Consumes ReminderSentEvent from Kafka and delivers email notifications",
        "kafka_topic": "task-reminders",
        "consumer_group": "email-delivery-consumer-group",
        "health_endpoint": "/health",
    }


# Signal handling for graceful shutdown
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown (SIGTERM, SIGINT)."""

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating graceful shutdown...")
        # FastAPI lifespan will handle cleanup automatically

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


# Setup signal handlers
setup_signal_handlers()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "": {"handlers": ["default"], "level": "INFO"},
            },
        },
    )
