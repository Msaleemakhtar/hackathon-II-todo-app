"""
Context-aware MCP client wrapper for automatic user_id injection.

This module provides a wrapper around MCPServerStreamableHttp that automatically
injects user_id into all tool calls, removing the burden from the LLM to extract
and pass user_id manually.

The wrapper modifies tool schemas to remove user_id from required parameters,
and injects it automatically when tools are called.
"""

import logging
from typing import Any

from agents.mcp import MCPServerStreamableHttp

logger = logging.getLogger(__name__)


class ContextAwareMCPClient:
    """
    Wrapper around MCPServerStreamableHttp that injects user_id into all tool calls.

    This solves the problem where LLMs fail to extract user_id from prompt text
    and pass it correctly to MCP tools.

    Usage:
        async with ContextAwareMCPClient(url, user_id) as mcp_client:
            # Tools are called normally, user_id is injected automatically
            agent = Agent(mcp_servers=[mcp_client.mcp_server])
    """

    def __init__(self, url: str, user_id: str, timeout: int = 30):
        """
        Initialize context-aware MCP client.

        Args:
            url: MCP server URL
            user_id: User ID to inject into all tool calls
            timeout: Request timeout in seconds
        """
        self.url = url
        self.user_id = user_id
        self.timeout = timeout
        self.mcp_server = None
        self._original_call_tool = None

    async def __aenter__(self):
        """Enter async context - create and patch MCP server."""
        # Create underlying MCP server
        self.mcp_server = MCPServerStreamableHttp(
            name="Task Manager MCP Server (Context-Aware)",
            params={
                "url": self.url,
                "timeout": self.timeout,
            },
            cache_tools_list=True,
            max_retry_attempts=3,
        )

        # Enter the MCP server context
        await self.mcp_server.__aenter__()

        # Patch the call_tool method to inject user_id
        self._original_call_tool = self.mcp_server.call_tool
        self.mcp_server.call_tool = self._call_tool_with_context

        logger.info(f"✅ Context-aware MCP client initialized for user_id={self.user_id}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context - cleanup MCP server."""
        if self.mcp_server:
            # Restore original call_tool method
            if self._original_call_tool:
                self.mcp_server.call_tool = self._original_call_tool

            # Exit the MCP server context
            await self.mcp_server.__aexit__(exc_type, exc_val, exc_tb)

        logger.info("Context-aware MCP client cleaned up")

    async def _call_tool_with_context(self, name: str, arguments: dict[str, Any]) -> Any:
        """
        Intercept tool calls and inject user_id automatically.

        Args:
            name: Tool name
            arguments: Tool arguments from LLM

        Returns:
            Tool execution result
        """
        # Inject user_id into arguments
        modified_arguments = {"user_id": self.user_id, **arguments}

        logger.info(
            f"🔧 Injecting user_id into tool call: {name}({list(modified_arguments.keys())})"
        )

        # Call original method with injected user_id
        return await self._original_call_tool(name, modified_arguments)

    async def list_tools(self):
        """
        List available tools with modified schemas (user_id removed from parameters).

        This method modifies tool schemas to hide user_id from the LLM, since it's
        injected automatically.
        """
        if not self.mcp_server:
            raise RuntimeError("MCP server not initialized. Use 'async with' context.")

        # Get original tools list
        tools = await self.mcp_server.list_tools()

        # Modify each tool schema to remove user_id parameter
        modified_tools = []
        for tool in tools:
            # Copy tool to avoid modifying original
            modified_tool = tool.model_copy() if hasattr(tool, 'model_copy') else tool

            # Remove user_id from required parameters in schema
            if hasattr(modified_tool, 'inputSchema') and modified_tool.inputSchema:
                schema = modified_tool.inputSchema

                # Remove user_id from required list
                if 'required' in schema and 'user_id' in schema['required']:
                    schema['required'] = [r for r in schema['required'] if r != 'user_id']

                # Remove user_id from properties
                if 'properties' in schema and 'user_id' in schema['properties']:
                    del schema['properties']['user_id']

                logger.debug(f"Modified tool schema for {modified_tool.name}: removed user_id")

            modified_tools.append(modified_tool)

        logger.info(f"📋 Listed {len(modified_tools)} tools with user_id auto-injection enabled")
        return modified_tools
