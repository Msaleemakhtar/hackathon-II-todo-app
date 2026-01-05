"""Standalone entry point for recurring task service with health check endpoint."""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.services.recurring_task_service import recurring_task_service, setup_signal_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler with retry logic and graceful Kafka fallback."""
    # Startup
    logger.info("Starting Recurring Task Service...")

    # Start recurring task service (Kafka consumer + producer) with retry logic
    MAX_RETRIES = 3
    RETRY_DELAYS = [5, 10, 20]  # Exponential backoff: 5s, 10s, 20s
    kafka_started = False

    for attempt in range(MAX_RETRIES):
        try:
            await recurring_task_service.start()
            setup_signal_handlers()
            logger.info(f"✅ Recurring task service started successfully (attempt {attempt + 1})")
            kafka_started = True
            break
        except Exception as e:
            logger.error(
                f"❌ Recurring task service init failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}",
                exc_info=True
            )
            if attempt < MAX_RETRIES - 1:
                retry_delay = RETRY_DELAYS[attempt]
                logger.info(f"Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("⚠️  All retry attempts exhausted. Service running in degraded mode.")
                logger.error("Kafka consumer NOT started - recurrence events will NOT be processed!")
                # Store failure state for health check
                app.state.kafka_failed = True
                app.state.kafka_error = str(e)

    if not kafka_started:
        logger.warning("Service will continue for health check visibility only")

    yield  # Application is ready

    # Shutdown
    logger.info("Shutting down recurring task service...")
    await recurring_task_service.stop()


# Create FastAPI app with lifespan
app = FastAPI(
    title="Recurring Task Service",
    version="0.1.0",
    lifespan=lifespan,  # ← MODERN PATTERN
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint (T038).

    Verifies:
    - Service is running
    - Kafka consumer/producer are healthy
    - Database connectivity is OK
    """
    # Check if Kafka initialization failed during startup
    if hasattr(app.state, 'kafka_failed') and app.state.kafka_failed:
        kafka_error = getattr(app.state, 'kafka_error', 'Unknown error')
        logger.warning(f"Health check: Kafka consumer failed to initialize - {kafka_error}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "service": "recurring-task-service",
                "version": "0.1.0",
                "kafka": "failed",
                "database": "unknown",
                "error": f"Kafka consumer initialization failed: {kafka_error}",
                "note": "Service in degraded mode - recurrence events NOT processed"
            },
            status_code=503,
        )

    try:
        is_healthy = await recurring_task_service.health_check()

        if is_healthy:
            return JSONResponse(
                content={
                    "status": "healthy",
                    "service": "recurring-task-service",
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
                    "service": "recurring-task-service",
                    "version": "0.1.0",
                },
                status_code=503,
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "service": "recurring-task-service",
                "error": str(e),
            },
            status_code=503,
        )


def main():
    """Run the recurring task service standalone."""
    logger.info("Recurring Task Service v0.1.0")
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")


if __name__ == "__main__":
    main()
