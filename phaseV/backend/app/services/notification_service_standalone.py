"""Standalone entry point for notification service with health check endpoint."""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.kafka.producer import kafka_producer
from app.services.notification_service import notification_service, setup_signal_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler with graceful Kafka fallback."""
    # Startup
    logger.info("Starting Notification Service...")

    # Initialize Kafka producer FIRST (required for publishing events)
    logger.info("Initializing Kafka producer...")
    kafka_available = False
    try:
        await kafka_producer.start()
        kafka_available = True
        logger.info("✅ Kafka producer initialized successfully")
    except Exception as e:
        logger.error(f"⚠️  Kafka producer initialization failed: {e}", exc_info=True)
        logger.warning("Notification service will start in degraded mode (database polling only, no event publishing)")
        # Don't raise - allow service to start without Kafka

    # Start notification service (database polling loop)
    await notification_service.start()
    setup_signal_handlers()

    logger.info(f"Notification service started (Kafka: {'available' if kafka_available else 'unavailable'})")

    yield  # Application is ready

    # Shutdown
    logger.info("Shutting down notification service...")
    await notification_service.stop()

    # Stop Kafka producer
    logger.info("Stopping Kafka producer...")
    await kafka_producer.stop()


# Create FastAPI app with lifespan
app = FastAPI(
    title="Notification Service",
    version="0.1.0",
    lifespan=lifespan,  # ← MODERN PATTERN
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint (T020).

    Verifies:
    - Service is running
    - Kafka producer is healthy
    - Database connectivity is OK
    """
    try:
        is_healthy = await notification_service.health_check()

        if is_healthy:
            return JSONResponse(
                content={
                    "status": "healthy",
                    "service": "notification-service",
                    "version": "0.1.0",
                    "kafka": "connected",
                    "database": "connected",
                },
                status_code=200,
            )
        else:
            return JSONResponse(
                content={
                    "status": "unhealthy",
                    "service": "notification-service",
                    "version": "0.1.0",
                },
                status_code=503,
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "service": "notification-service",
                "error": str(e),
            },
            status_code=503,
        )


def main():
    """Run the notification service standalone."""
    logger.info("Notification Service v0.1.0")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")


if __name__ == "__main__":
    main()
