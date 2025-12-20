"""
ChatKit Protocol Adapter

This module provides a translation layer between ChatKit.js (frontend)
and the existing FastAPI backend. It implements the /chatkit endpoint
that ChatKit.js expects while preserving all existing backend logic.

Architecture:
  ChatKit.js → Adapter (this file) → Existing Backend → MCP Tools

Key Responsibilities:
  1. Parse ChatKit protocol requests
  2. Validate JWT authentication
  3. Convert to internal API format
  4. Call existing agent_service
  5. Convert responses to ChatKit SSE format
  6. Stream events back to frontend
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Your existing backend imports
from app.database import get_session
from app.dependencies.auth import verify_jwt_from_header
from app.services.agent_service import agent_service
from app.services.conversation_service import conversation_service
from app.services.message_service import message_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["chatkit-adapter"])


# ChatKit Type Definitions (Lightweight, inline definitions)
class MessageRole(str, Enum):
    """Message role types for ChatKit protocol."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatKitMessage(BaseModel):
    """ChatKit message format."""

    role: str
    content: str


class ChatKitThread(BaseModel):
    """ChatKit thread identifier."""

    id: str | None = None


class ChatKitRequest(BaseModel):
    """ChatKit incoming request format."""

    thread: ChatKitThread
    messages: list[ChatKitMessage]
    metadata: dict | None = None


class AssistantMessageItem(BaseModel):
    """Assistant message item for ChatKit response."""

    id: str
    role: str
    content: str
    created_at: datetime


class ThreadItemDoneEvent(BaseModel):
    """Thread item done event for ChatKit SSE."""

    item: AssistantMessageItem


async def parse_chatkit_request(request: Request) -> dict:
    """
    Parse incoming ChatKit.js request.

    ChatKit.js sends requests in this format:
    {
      "thread": {"id": "thread_123"},
      "messages": [
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Previous response"}
      ],
      "metadata": {...}
    }

    Returns:
      dict with extracted thread_id, user_message, message_history
    """
    body = await request.json()

    # Extract thread ID (ChatKit's conversation identifier)
    thread = body.get("thread", {})
    thread_id = thread.get("id")

    # Extract messages array
    messages = body.get("messages", [])

    # Find the latest user message (the current input)
    user_message = None
    message_history = []

    for msg in reversed(messages):
        if msg.get("role") == "user" and user_message is None:
            # This is the current user input
            user_message = msg.get("content", "")
        else:
            # This is conversation history
            message_history.insert(
                0, {"role": msg.get("role"), "content": msg.get("content", "")}
            )

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found in request")

    return {
        "thread_id": thread_id,
        "user_message": user_message,
        "message_history": message_history,
    }


async def event_generator(
    db: AsyncSession,
    user_id: str,
    thread_id: str | None,
    user_message: str,
    message_history: list[dict],
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events (SSE) for ChatKit.js.

    This is the core translation function that:
    1. Calls your existing backend
    2. Converts responses to ChatKit SSE format
    3. Yields events that ChatKit.js understands

    ChatKit SSE format:
      event: thread.item.done
      data: {"item": {"role": "assistant", "content": "..."}}
    """
    try:
        # Map thread_id to conversation_id in your database
        conversation_id = None
        if thread_id:
            # Try to find existing conversation by external_id
            conversation = await conversation_service.get_conversation_by_external_id(
                db, external_id=thread_id, user_id=user_id
            )
            if conversation:
                conversation_id = conversation.id

        # Call your existing agent service
        # NO CHANGES to agent_service needed!
        agent_response = await agent_service.process_message(
            user_message=user_message,
            conversation_history=message_history,
            user_id=user_id,
        )

        # Save conversation if it doesn't exist
        if not conversation_id:
            conversation = await conversation_service.create_conversation(
                db, user_id=user_id, external_id=thread_id  # Link to ChatKit thread ID
            )
            conversation_id = conversation.id

        # Save user message to database
        await message_service.create_user_message(
            db, conversation_id=conversation_id, user_id=user_id, content=user_message
        )

        # Save assistant response to database
        await message_service.create_assistant_message(
            db,
            conversation_id=conversation_id,
            user_id=user_id,
            content=agent_response["content"],
        )

        # Convert to ChatKit event format
        assistant_item = AssistantMessageItem(
            id=f"msg_{conversation_id}_{datetime.utcnow().timestamp()}",
            role=MessageRole.ASSISTANT.value,
            content=agent_response["content"],
            created_at=datetime.utcnow(),
        )

        event = ThreadItemDoneEvent(item=assistant_item)

        # Yield SSE format that ChatKit.js expects
        # Format: "event: <event_type>\ndata: <json_data>\n\n"
        yield f"event: thread.item.done\n"
        yield f"data: {event.model_dump_json()}\n\n"

    except Exception as e:
        logger.error(f"Error in ChatKit adapter: {type(e).__name__} - {str(e)}")
        # Error handling - send error event to ChatKit.js
        error_event = {"error": {"type": "agent_error", "message": str(e)}}
        yield f"event: error\n"
        yield f"data: {json.dumps(error_event)}\n\n"


@router.post("/chatkit")
async def chatkit_endpoint(request: Request, db: AsyncSession = Depends(get_session)):
    """
    ChatKit protocol endpoint.

    This is the ONLY endpoint ChatKit.js will call. It must:
    1. Accept ChatKit protocol requests
    2. Validate authentication
    3. Call existing backend
    4. Return SSE stream

    Authentication:
      ChatKit.js sends JWT in Authorization header.
      We extract and validate it using existing auth system.
    """
    # Extract JWT from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=401, detail="Missing Authorization header"
        )

    # Validate JWT and extract user_id
    # Uses your existing Better Auth validation!
    user_id = await verify_jwt_from_header(auth_header)

    # Parse ChatKit request
    parsed = await parse_chatkit_request(request)
    thread_id = parsed["thread_id"]
    user_message = parsed["user_message"]
    message_history = parsed["message_history"]

    # Return SSE stream
    # media_type="text/event-stream" tells ChatKit.js to listen for events
    return StreamingResponse(
        event_generator(
            db=db,
            user_id=user_id,
            thread_id=thread_id,
            user_message=user_message,
            message_history=message_history,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
