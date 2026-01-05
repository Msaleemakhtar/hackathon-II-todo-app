"""Standalone FastMCP HTTP Server for Phase III Task Management.

This script runs the FastMCP server as a standalone HTTP service,
separate from the FastAPI backend. It enables MCP tools to be accessed
via HTTP transport while avoiding routing conflicts with FastAPI.

Usage:
    python -m app.mcp.standalone

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (required)
    MCP_HOST: Host to bind (default: 0.0.0.0)
    MCP_PORT: Port to listen (default: 8001)
    LOG_LEVEL: Logging level (default: INFO)
"""

import asyncio
import logging
import os
import signal
from typing import NoReturn

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def initialize_kafka_producer() -> None:
    """Initialize Kafka producer for event publishing."""
    from app.kafka.producer import kafka_producer

    try:
        await kafka_producer.start()
        logger.info("Kafka producer initialized successfully in MCP server")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        logger.warning("Continuing without Kafka - event publishing will be disabled")


async def shutdown_kafka_producer() -> None:
    """Shutdown Kafka producer gracefully."""
    from app.kafka.producer import kafka_producer

    try:
        await kafka_producer.stop()
        logger.info("Kafka producer stopped gracefully")
    except Exception as e:
        logger.error(f"Error stopping Kafka producer: {e}")


def run_mcp_server() -> NoReturn:
    """Run the MCP server using FastMCP's streamable HTTP transport."""
    # Import server and tools
    # Tools are registered via decorators when module loads
    import app.mcp.tools  # noqa: F401 - Import needed for tool registration
    from app.mcp.server import mcp

    # Get configuration from environment
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8001"))

    logger.info(f"Starting MCP Server: {mcp.name}")
    logger.info(f"Listening on {host}:{port}")

    # Setup shutdown handler
    shutdown_initiated = False

    def signal_handler(sig, frame):
        nonlocal shutdown_initiated
        if shutdown_initiated:
            return
        shutdown_initiated = True
        logger.info(f"Received signal {sig}, shutting down...")
        # Kafka producer will be stopped by lifespan handler
        exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("MCP tools will be registered when server starts")
    logger.info("MCP HTTP transport enabled (stateless)")
    logger.info("MCP routes will be available at:")
    logger.info("  - /mcp (MCP protocol)")

    # Configure host and port via settings
    mcp.settings.host = host
    mcp.settings.port = port

    # NOTE: Kafka producer will be lazy-initialized on first use
    # Attempting to pre-initialize it here causes event loop conflicts
    logger.info("Kafka producer will be initialized on first event publish")

    # Run using FastMCP's streamable HTTP transport
    # This properly initializes the session manager and task groups
    mcp.run(transport="streamable-http")


def main() -> NoReturn:
    """Entry point for the MCP server."""
    run_mcp_server()


if __name__ == "__main__":
    main()
