"""FastMCP server entry point for standalone execution with stateless HTTP transport."""
import asyncio
import logging

# Import tools to register them with the server
import app.mcp.tools  # noqa: F401
from app.mcp.server import mcp_server_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the FastMCP server with stateless HTTP transport."""
    logger.info("Starting FastMCP server with stateless HTTP transport...")
    logger.info(f"Registered tools: {mcp_server_manager.get_registered_tools()}")

    try:
        await mcp_server_manager.start()
    except KeyboardInterrupt:
        logger.info("FastMCP server stopped by user")
    except Exception as e:
        logger.error(f"FastMCP server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
