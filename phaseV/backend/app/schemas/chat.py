from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request schema."""

    message: str = Field(..., min_length=1, description="User message content")
    conversation_id: int | None = Field(
        None, description="Existing conversation ID to continue, or None for new conversation"
    )
    user_id: str | None = Field(None, description="User ID (optional, for testing without JWT)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Show me my tasks",
                "conversation_id": None,
                "user_id": "test_user",
            }
        }


class ToolCall(BaseModel):
    """Tool call schema for MCP tool invocations."""

    name: str = Field(..., description="MCP tool name")
    arguments: dict[str, Any] = Field(..., description="Tool input arguments")
    result: Any = Field(..., description="Tool execution result")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "list_tasks",
                "arguments": {"user_id": "user_123", "status": "all"},
                "result": [
                    {"id": 1, "title": "Buy groceries", "completed": False},
                    {"id": 2, "title": "Write report", "completed": True},
                ],
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema."""

    conversation_id: int = Field(..., description="Conversation ID for this exchange")
    response: str = Field(..., description="AI assistant response")
    tool_calls: list[ToolCall] = Field(
        default_factory=list, description="MCP tools invoked during processing"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "response": "I found 2 tasks for you. One is pending and one is completed.",
                "tool_calls": [
                    {
                        "name": "list_tasks",
                        "arguments": {"user_id": "user_123", "status": "all"},
                        "result": [
                            {"id": 1, "title": "Buy groceries", "completed": False},
                            {"id": 2, "title": "Write report", "completed": True},
                        ],
                    }
                ],
            }
        }
