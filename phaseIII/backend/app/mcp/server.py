"""FastMCP Server for Phase III conversational task management."""

import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Create FastMCP instance with stateless HTTP transport
mcp = FastMCP(name="phaseiii-task-manager", stateless_http=True)

logger.info("FastMCP Server initialized: phaseiii-task-manager (stateless HTTP)")


def get_mcp_app():
    """Get the Starlette MCP app for mounting in FastAPI."""
    return mcp.streamable_http_app()


def get_mcp_instance():
    """Get the FastMCP instance for tool registration."""
    return mcp
