"""AI Agent Orchestrator using OpenAI Agents SDK with Gemini backend and MCP tools."""

import logging
from datetime import datetime
from typing import Any

from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServerStreamableHttp
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class AgentService:
    """
    AI Agent orchestrator using OpenAI Agents SDK.

    Architecture:
    - LiteLLM with Gemini for natural language understanding
    - OpenAI Agents SDK Runner for tool orchestration
    - MCP tools via HTTP transport (stateless)
    - Async context managers for proper resource management

    This implements the proper OpenAI Agents SDK pattern with MCP integration.
    """

    def __init__(self):
        """Initialize agent service with LiteLLM (OpenAI or Gemini)."""
        # Prefer OpenAI if available, fallback to Gemini
        if settings.openai_api_key:
            self.model = LitellmModel(
                model="gpt-3.5-turbo",  # Most cost-effective model for testing
                api_key=settings.openai_api_key,
            )
            logger.info("Agent service initialized with GPT-3.5-turbo via LiteLLM and OpenAI Agents SDK")
        elif settings.gemini_api_key:
            self.model = LitellmModel(
                model="gemini/gemini-2.0-flash",  # Fast, cost-effective Gemini 2.0 model
                api_key=settings.gemini_api_key,
            )
            logger.info("Agent service initialized with Gemini 2.0 via LiteLLM and OpenAI Agents SDK")
        else:
            raise ValueError("Either OPENAI_API_KEY or GEMINI_API_KEY must be set in environment")

    def _get_system_instructions(self) -> str:
        """Get system instructions for the agent."""
        return """You are a helpful AI task manager assistant. You help users manage their tasks through natural conversation.

You have access to 5 tools for task management:
- add_task: Create a new task
- list_tasks: List user's tasks (all, pending, or completed)
- complete_task: Mark a task as completed
- delete_task: Delete a task
- update_task: Update a task's title or description

Guidelines:
1. Be conversational and friendly
2. When users reference tasks ambiguously, ask for clarification
3. Provide helpful suggestions after completing actions
4. If an error occurs, explain it clearly and suggest next steps
5. Always confirm actions (e.g., "Task #1 'Buy milk' has been completed")
6. IMPORTANT: Always pass the user_id to ALL tool calls - it's available in the context
"""

    async def process_message(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]],
        user_id: str,
    ) -> dict[str, Any]:
        """
        Process user message with AI agent using OpenAI Agents SDK Runner.

        Args:
            user_message: User's input message
            conversation_history: Previous conversation messages
            user_id: User ID for tool invocations

        Returns:
            dict: Agent response with content and tool calls

        Flow:
            1. Create MCP server connection via async context manager
            2. Create agent with MCP tools (auto-discovered from server)
            3. Use Runner to execute agent with user message
            4. Agent automatically decides which tools to call
            5. Return natural language response
        """
        try:
            # Create MCP server connection using async context manager
            # Uses configurable URL (localhost for dev, Docker service name for containers)
            async with MCPServerStreamableHttp(
                name="Task Manager MCP Server",
                params={
                    "url": settings.mcp_server_url,
                    "timeout": 30,
                },
                cache_tools_list=True,
                max_retry_attempts=3,
            ) as mcp_server:
                # Create agent with MCP tools
                # The SDK automatically discovers tools from the MCP server
                agent = Agent(
                    name="TaskManagerAgent",
                    instructions=self._get_system_instructions(),
                    model=self.model,
                    mcp_servers=[mcp_server],  # MCP tools auto-discovered!
                )

                # Build context message with user_id and conversation history
                context_message = self._build_context_message(
                    user_message, conversation_history, user_id
                )

                # Run agent with Runner - SDK handles everything!
                result = await Runner.run(
                    agent,
                    input=context_message,
                )

                # Return response
                return {
                    "content": result.final_output,
                    "tool_calls": [],  # SDK handles tool calls internally
                    "finish_reason": "stop",
                }

        except Exception as e:
            logger.error(f"Agent processing error: {str(e)}")

            # Enhanced error handling from User Story 3
            if "API" in str(e) or "rate limit" in str(e).lower():
                raise HTTPException(
                    status_code=503,
                    detail={
                        "detail": (
                            "The AI service is temporarily unavailable. "
                            "This is usually temporary. Please wait 30 seconds and try again.\n\n"
                            "If the problem persists:\n"
                            "  - Check your internet connection\n"
                            "  - Verify the AI service is configured correctly\n"
                            "  - Contact support if the issue continues"
                        ),
                        "code": "AI_SERVICE_UNAVAILABLE",
                        "retry_after": 30,
                        "timestamp": datetime.utcnow().isoformat(),
                        "suggestions": [
                            "Wait 30 seconds and retry your request",
                            "Check system status",
                            "Try a simpler request first",
                        ],
                    },
                ) from e

            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}") from e

    def _build_context_message(
        self, user_message: str, conversation_history: list[dict[str, str]], user_id: str
    ) -> str:
        """
        Build context message with user_id and conversation history.

        The SDK handles conversation context automatically, but we need to
        inject the user_id so tools can use it.
        """
        # Format conversation history
        history_text = ""
        if conversation_history:
            history_lines = [
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-10:]  # Last 10 messages
            ]
            history_text = "\n".join(history_lines)

        # Build full context message
        # IMPORTANT: Include user_id so the LLM knows to pass it to tools
        if history_text:
            return f"""Context:
- User ID: {user_id} (IMPORTANT: Use this user_id for ALL tool calls)

Recent conversation:
{history_text}

Current user message: {user_message}"""
        else:
            return f"""Context:
- User ID: {user_id} (IMPORTANT: Use this user_id for ALL tool calls)

User message: {user_message}"""


# Global agent service instance
agent_service = AgentService()
