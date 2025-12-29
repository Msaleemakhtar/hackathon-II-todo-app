"""
TaskChatServer: ChatKit server implementation for conversational task management.

Integrates:
- ChatKit SDK for HTTP handling and event streaming
- OpenAI Agents SDK for AI orchestration
- MCP Server for tool execution (5 task management tools)
"""

import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from agents.mcp import MCPServerStreamableHttp
from chatkit.server import ChatKitServer
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)

from app.config import settings

logger = logging.getLogger(__name__)


class TaskChatServer(ChatKitServer):
    """
    ChatKit server for conversational task management.

    This server extends ChatKitServer and implements the respond() method
    to process user messages using the OpenAI Agents SDK with MCP tools.

    Architecture:
    - ChatKit SDK handles HTTP protocol and event streaming
    - OpenAI Agents SDK handles AI orchestration
    - MCP Server provides 5 task management tools
    - PostgreSQL stores conversations and messages via Store interface
    """

    def __init__(self, store):
        """
        Initialize TaskChatServer with store and AI model.

        Args:
            store: PostgresStore instance for conversation/message persistence
        """
        super().__init__(store=store)

        # Initialize LiteLLM model (copied from agent_service.py:31-46)
        # Prefer OpenAI if available, fallback to Gemini
        if settings.openai_api_key:
            self.model = LitellmModel(
                model="gpt-3.5-turbo",  # Most cost-effective model for testing
                api_key=settings.openai_api_key,
            )
            logger.info("TaskChatServer initialized with GPT-3.5-turbo via LiteLLM")
        elif settings.gemini_api_key:
            self.model = LitellmModel(
                model="gemini/gemini-2.5-pro",  # Gemini 2.5 Pro with higher quota
                api_key=settings.gemini_api_key,
            )
            logger.info("TaskChatServer initialized with Gemini 2.5 Pro via LiteLLM")
        else:
            raise ValueError("Either OPENAI_API_KEY or GEMINI_API_KEY must be set in environment")

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Process user message and stream AI response as ChatKit events.

        This is the core method called by ChatKit SDK for each user message.

        Args:
            thread: Thread metadata (conversation context)
            input: User's message
            context: Request context (contains user_id from auth middleware)

        Yields:
            ThreadStreamEvent: ChatKit events with AI response

        Flow:
            1. Extract user_id from context
            2. Connect to MCP server
            3. Create Agent with MCP tools
            4. Load conversation history from thread
            5. Build context message with user_id
            6. Run agent and get response
            7. Yield AssistantMessageItem event
        """
        logger.info(f"🚀 respond() called - thread_id={thread.id if thread else 'None'}")
        logger.info(f"   Input message: {input_user_message}")
        logger.info(f"   Context: {context}")

        if not input_user_message:
            logger.warning("No input provided to respond()")
            return

        # Extract user_id from context (injected by auth middleware)
        user_id = context.get("user_id")
        if not user_id:
            logger.error("user_id not found in context")
            raise ValueError("user_id not found in request context")

        logger.info(f"✅ Processing message for user_id={user_id}, thread_id={thread.id}")

        try:
            # Create MCP server connection (copied from agent_service.py:92-103)
            logger.info(f"🔌 Connecting to MCP server at {settings.mcp_server_url}")
            async with MCPServerStreamableHttp(
                name="Task Manager MCP Server",
                params={
                    "url": settings.mcp_server_url,
                    "timeout": 30,
                },
                cache_tools_list=True,
                max_retry_attempts=3,
            ) as mcp_server:
                logger.info("✅ MCP server connected successfully")

                # Log discovered tools
                try:
                    tools_list = await mcp_server.list_tools()
                    logger.info(f"🔍 list_tools() raw response type: {type(tools_list)}")
                    logger.info(f"🔍 list_tools() response: {tools_list}")
                    logger.info(f"🔍 has 'tools' attr: {hasattr(tools_list, 'tools')}")
                    logger.info(f"🔍 dir: {dir(tools_list)}")

                    tool_names = (
                        [tool.name for tool in tools_list.tools]
                        if hasattr(tools_list, "tools")
                        else []
                    )
                    logger.info(f"🔧 MCP tools discovered: {tool_names}")
                except Exception as e:
                    logger.error(f"❌ Could not list MCP tools: {str(e)}", exc_info=True)

                # Create agent with MCP tools (copied from agent_service.py:104-111)
                # The SDK automatically discovers tools from the MCP server
                agent = Agent(
                    name="TaskManagerAgent",
                    instructions=self._get_system_instructions(),
                    model=self.model,
                    mcp_servers=[mcp_server],  # MCP tools auto-discovered!
                )
                logger.info("🤖 Agent created with MCP tools")

                # Load conversation history from thread for agent context
                conversation_history = []
                if thread.id:
                    try:
                        # Load last 50 messages (will use last 10 in context)
                        items_page = await self.store.load_thread_items(
                            thread_id=thread.id,
                            after=None,
                            limit=50,
                            order="asc",
                            context=context,
                        )

                        # Convert ChatKit items to conversation history format
                        for item in items_page.data:
                            if hasattr(item, "content"):
                                # Extract text from ChatKit content format
                                text = self._extract_text_from_content(item.content)
                                # Determine role based on item type
                                role = (
                                    "user"
                                    if type(item).__name__ == "UserMessageItem"
                                    else "assistant"
                                )
                                conversation_history.append({"role": role, "content": text})

                        logger.info(
                            f"📜 Loaded {len(conversation_history)} messages from conversation history"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to load conversation history: {str(e)}")
                        # Continue with empty history on error

                # Build context message with user_id and conversation history
                context_message = self._build_context_message(
                    user_message=input_user_message.content,
                    user_id=user_id,
                    conversation_history=conversation_history,
                )

                # Run agent with Runner (copied from agent_service.py:118-122)
                logger.info("🤖 Running agent with OpenAI Agents SDK...")
                result = await Runner.run(
                    agent,
                    input=context_message,
                )
                logger.info(f"✅ Agent completed. Final output: {result.final_output[:100]}...")

                # Convert result to ChatKit AssistantMessageItem event
                # ChatKit expects us to yield ThreadStreamEvent with all required fields
                # CRITICAL: Explicitly set type="output_text" to ensure serialization includes it
                assistant_message = AssistantMessageItem(
                    id=f"msg_{datetime.now(UTC).timestamp()}",
                    thread_id=thread.id,
                    content=[
                        AssistantMessageContent(
                            text=result.final_output,
                            type="output_text",  # Explicitly set to force serialization
                            annotations=[],  # Explicitly set empty list
                        )
                    ],
                    created_at=datetime.now(UTC),
                )
                logger.info(
                    f"📤 Created AssistantMessageItem: id={assistant_message.id}, thread_id={assistant_message.thread_id}"
                )
                # Debug: Log the serialized content
                logger.info("🔍 Content serialization check:")
                logger.info(f"   content object: {assistant_message.content}")
                logger.info(f"   content[0] type: {type(assistant_message.content[0])}")
                logger.info(f"   content[0] dict: {assistant_message.content[0].model_dump()}")
                logger.info(f"   Full message dump: {assistant_message.model_dump_json()}")

                # CRITICAL FIX: Wrap assistant message in ThreadItemDoneEvent
                # The ChatKit SDK expects ThreadItemDoneEvent, not raw AssistantMessageItem
                # This ensures proper SSE formatting and automatic persistence
                logger.info("📤 Yielding ThreadItemDoneEvent with assistant message to ChatKit SDK")
                yield ThreadItemDoneEvent(item=assistant_message)

                logger.info(
                    f"✅ Response generated and yielded for user_id={user_id}, thread_id={thread.id}"
                )

        except Exception as e:
            logger.error(f"Error in respond(): {str(e)}", exc_info=True)

            # Provide specific error messages based on exception type
            if "ConnectError" in str(type(e).__name__) or "connection" in str(e).lower():
                error_msg = (
                    "❌ Cannot connect to the MCP server (task management tools). "
                    f"Please ensure the MCP server is running at {settings.mcp_server_url}. "
                    "You can start it with: `cd phaseIII/backend && uv run python -m app.mcp.standalone`"
                )
            else:
                error_msg = f"I encountered an error while processing your request: {str(e)}. Please try again."

            # Create error message as assistant response with all required fields
            # Explicitly set all fields to force serialization
            error_message = AssistantMessageItem(
                id=f"msg_{datetime.now(UTC).timestamp()}",
                thread_id=thread.id,
                content=[
                    AssistantMessageContent(
                        text=error_msg,
                        type="output_text",  # Explicitly set
                        annotations=[],  # Explicitly set
                    )
                ],
                created_at=datetime.now(UTC),
            )

            # Wrap error message in ThreadItemDoneEvent for proper SDK handling
            logger.info("📤 Yielding ThreadItemDoneEvent with error message to ChatKit SDK")
            yield ThreadItemDoneEvent(item=error_message)

    def _extract_text_from_content(self, content: Any) -> str:
        """
        Extract text from ChatKit content format.

        Content can be:
        - A string: return as-is
        - A list of dicts: extract text from each
        - Other: convert to string
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    texts.append(item["text"])
                elif hasattr(item, "text"):
                    texts.append(item.text)
                else:
                    texts.append(str(item))
            return " ".join(texts)
        else:
            return str(content)

    def _get_system_instructions(self) -> str:
        """
        Get system instructions for the agent.

        Copied verbatim from agent_service.py:48-66
        """
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

    def _build_context_message(
        self,
        user_message: str,
        user_id: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Build context message with user_id and conversation history.

        Adapted from agent_service.py:160-192

        Args:
            user_message: Current user message
            user_id: User ID for tool calls
            conversation_history: Optional conversation history

        Returns:
            Formatted context string for the agent
        """
        # Format conversation history if provided
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
