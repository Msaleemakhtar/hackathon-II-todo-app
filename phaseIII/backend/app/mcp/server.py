"""MCP server manager with tool registration using FastMCP."""
from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP


class MCPServerManager:
    """Manager for MCP server and tool registration."""

    def __init__(self) -> None:
        """Initialize FastMCP server with stateless HTTP transport."""
        self.server = FastMCP("todo-mcp-server", stateless_http=True)
        self.tools_registered: list[str] = []

    def register_tool(self, name: str, description: str, handler: Callable[..., Any]) -> None:
        """
        Register an MCP tool.

        Args:
            name: Tool name
            description: Tool description
            handler: Tool handler function
        """
        # Tool registration handled via @self.server.tool() decorator
        self.tools_registered.append(name)

    async def start(self) -> None:
        """Start the FastMCP server with stateless HTTP transport."""
        await self.server.run_streamable_http_async()

    def get_registered_tools(self) -> list[str]:
        """Get list of registered tool names."""
        return self.tools_registered.copy()


# Global FastMCP server instance
mcp_server_manager = MCPServerManager()
