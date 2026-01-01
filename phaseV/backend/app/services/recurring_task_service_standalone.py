"""Standalone entry point for recurring task service with health check endpoint."""

import asyncio
import logging

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

# Create FastAPI app for health checks
app = FastAPI(title="Recurring Task Service", version="0.1.0")


@app.get("/health")
async def health_check():
    """
    Health check endpoint (T038).

    Verifies:
    - Service is running
    - Kafka consumer/producer are healthy
    - Database connectivity is OK
    """
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


@app.on_event("startup")
async def startup():
    """Start recurring task service on application startup (T039)."""
    logger.info("Starting recurring task service...")
    await recurring_task_service.start()
    setup_signal_handlers()


@app.on_event("shutdown")
async def shutdown():
    """Stop recurring task service on application shutdown (T036)."""
    logger.info("Shutting down recurring task service...")
    await recurring_task_service.stop()


def main():
    """Run the recurring task service standalone."""
    logger.info("Recurring Task Service v0.1.0")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")


if __name__ == "__main__":
    main()
