"""Chat API router for conversational task management."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies.auth import validate_user_id_match, verify_jwt
from app.schemas.chat import ChatRequest, ChatResponse, ToolCall
from app.services.agent_service import agent_service
from app.services.conversation_service import conversation_service
from app.services.message_service import message_service
from app.utils.validation import validate_message_content

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/api/chat-test", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_test_endpoint(
    chat_request: ChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """
    Test chat endpoint WITHOUT authentication (for development/testing only).

    Use this endpoint to test the AI agent without JWT tokens.
    In production, this should be disabled.

    Args:
        request: Chat request with message, user_id, and optional conversation_id
        db: Database session

    Returns:
        ChatResponse: AI response with conversation_id and tool calls
    """
    try:
        # Use user_id from request body instead of JWT
        user_id = chat_request.user_id or "test_user"

        # Validate message content
        message_content = validate_message_content(chat_request.message)

        # Handle conversation_id
        if chat_request.conversation_id:
            # Continue existing conversation
            conversation, messages = await conversation_service.get_conversation_with_messages(
                db, chat_request.conversation_id, user_id
            )

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation #{chat_request.conversation_id} not found",
                )

            conversation_id = conversation.id
            conversation_history = [
                {"role": msg.role.value, "content": msg.content} for msg in messages
            ]
        else:
            # Create new conversation
            conversation = await conversation_service.create_conversation(db, user_id)
            conversation_id = conversation.id
            conversation_history = []

        logger.info(f"TEST: Processing chat message: conversation_id={conversation_id}, user_id={user_id}")

        # Process message with AI agent
        agent_response = await agent_service.process_message(
            user_message=message_content,
            conversation_history=conversation_history,
            user_id=user_id,
        )

        # Store user message
        await message_service.create_user_message(db, conversation_id, user_id, message_content)

        # Store assistant response
        await message_service.create_assistant_message(
            db, conversation_id, user_id, agent_response["content"]
        )

        # Update conversation timestamp
        await conversation_service.update_conversation_timestamp(db, conversation_id)

        # Build response
        tool_calls = [
            ToolCall(
                name=call["name"],
                arguments=call["arguments"],
                result=call["result"],
            )
            for call in agent_response["tool_calls"]
        ]

        return ChatResponse(
            conversation_id=conversation_id,
            response=agent_response["content"],
            tool_calls=tool_calls,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat test endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        ) from e


@router.get("/api/{path_user_id}/conversations/{conversation_id}")
async def get_conversation_history(
    path_user_id: str,
    conversation_id: int,
    db: AsyncSession = Depends(get_session),
    jwt_user_id: str = Depends(verify_jwt),
):
    """
    Retrieve conversation history with messages (T080).

    Returns the conversation and all its messages for frontend display.

    Args:
        path_user_id: User ID from URL path
        conversation_id: Conversation ID to retrieve
        db: Database session
        jwt_user_id: User ID from JWT token

    Returns:
        dict: Conversation with messages array

    Raises:
        HTTPException: 401 (unauthorized), 403 (user_id mismatch),
                      404 (conversation not found)
    """
    try:
        # Validate user_id match
        await validate_user_id_match(path_user_id, jwt_user_id)

        # Load conversation with all messages
        conversation, messages = await conversation_service.get_conversation_with_messages(
            db,
            conversation_id,
            jwt_user_id,
            limit=100,  # Load more messages for history
        )

        if not conversation:
            # T094: Enhanced error with helpful context
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "detail": (
                        f"Conversation #{conversation_id} not found. "
                        "This could mean:\n"
                        "  - The conversation ID is incorrect\n"
                        "  - The conversation was deleted\n"
                        "  - You don't have access to this conversation\n\n"
                        "Start a new conversation or check your conversation list."
                    ),
                    "code": "CONVERSATION_NOT_FOUND",
                    "conversation_id": conversation_id,
                    "suggestions": [
                        "Start a new conversation",
                        "Check your recent conversations",
                        "Verify the conversation ID",
                    ],
                },
            )

        # Format response
        return {
            "conversation_id": conversation.id,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        ) from e


@router.post("/api/{path_user_id}/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_endpoint(
    path_user_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_session),
    jwt_user_id: str = Depends(verify_jwt),
):
    """
    Process user message and return AI assistant response.

    This endpoint:
    1. Validates JWT and user_id match (T050)
    2. Handles conversation_id (create new or continue existing) (T051)
    3. Processes message with AI agent and MCP tools (T052)
    4. Stores user and assistant messages in database (T053)
    5. Returns ChatResponse with conversation_id, response, and tool_calls (T054)

    Rate limit: 10 requests per minute per user

    Args:
        path_user_id: User ID from URL path
        request: Chat request with message and optional conversation_id
        db: Database session
        jwt_user_id: User ID from JWT token

    Returns:
        ChatResponse: AI response with conversation_id and tool calls

    Raises:
        HTTPException: 400 (invalid message), 401 (unauthorized),
                      403 (user_id mismatch), 429 (rate limit),
                      503 (AI service unavailable)
    """
    try:
        # Validate user_id match (T050)
        await validate_user_id_match(path_user_id, jwt_user_id)

        # Validate message content
        message_content = validate_message_content(request.message)

        # Handle conversation_id (T051)
        if request.conversation_id:
            # Continue existing conversation
            conversation, messages = await conversation_service.get_conversation_with_messages(
                db, request.conversation_id, jwt_user_id
            )

            if not conversation:
                # T094: Enhanced error with helpful context
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "detail": (
                            f"Conversation #{request.conversation_id} not found. "
                            "This could mean:\n"
                            "  - The conversation ID is incorrect\n"
                            "  - The conversation was deleted\n"
                            "  - You don't have access to this conversation\n\n"
                            "Try starting a new conversation instead (omit conversation_id)."
                        ),
                        "code": "CONVERSATION_NOT_FOUND",
                        "conversation_id": request.conversation_id,
                        "suggestions": [
                            "Start a new conversation (omit conversation_id)",
                            "Check your recent conversations",
                            "Verify the conversation ID",
                        ],
                    },
                )

            conversation_id = conversation.id

            # Build conversation history for AI context
            conversation_history = [
                {"role": msg.role.value, "content": msg.content} for msg in messages
            ]
        else:
            # Create new conversation
            conversation = await conversation_service.create_conversation(db, jwt_user_id)
            conversation_id = conversation.id
            conversation_history = []

        logger.info(
            f"Processing chat message: conversation_id={conversation_id}, user_id={jwt_user_id}"
        )

        # Process message with AI agent (T052)
        agent_response = await agent_service.process_message(
            user_message=message_content,
            conversation_history=conversation_history,
            user_id=jwt_user_id,
        )

        # Store user message in database (T053)
        await message_service.create_user_message(db, conversation_id, jwt_user_id, message_content)

        # Store assistant response in database (T053)
        await message_service.create_assistant_message(
            db, conversation_id, jwt_user_id, agent_response["content"]
        )

        # Update conversation timestamp
        await conversation_service.update_conversation_timestamp(db, conversation_id)

        # Build response (T054)
        tool_calls = [
            ToolCall(
                name=call["name"],
                arguments=call["arguments"],
                result=call["result"],
            )
            for call in agent_response["tool_calls"]
        ]

        response = ChatResponse(
            conversation_id=conversation_id,
            response=agent_response["content"],
            tool_calls=tool_calls,
        )

        logger.info(
            f"Chat response sent: conversation_id={conversation_id}, "
            f"tools_invoked={len(tool_calls)}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        ) from e
