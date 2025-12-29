"""Message service for persisting conversation messages."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.message import Message, MessageRole

logger = logging.getLogger(__name__)


class MessageService:
    """Service layer for message persistence."""

    @staticmethod
    async def create_message(
        db: AsyncSession,
        conversation_id: int,
        user_id: str,
        role: MessageRole,
        content: str,
    ) -> Message:
        """Create and persist a new message."""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        logger.info(
            f"Message created: message_id={message.id}, "
            f"conversation_id={conversation_id}, role={role}"
        )
        return message

    @staticmethod
    async def create_user_message(
        db: AsyncSession,
        conversation_id: int,
        user_id: str,
        content: str,
    ) -> Message:
        """Create a user message."""
        return await MessageService.create_message(
            db, conversation_id, user_id, MessageRole.USER, content
        )

    @staticmethod
    async def create_assistant_message(
        db: AsyncSession,
        conversation_id: int,
        user_id: str,
        content: str,
    ) -> Message:
        """Create an assistant message."""
        return await MessageService.create_message(
            db, conversation_id, user_id, MessageRole.ASSISTANT, content
        )

    @staticmethod
    async def get_messages_by_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: str,
        limit: int | None = None,
    ) -> list[Message]:
        """
        Get messages for a conversation with user ownership validation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership validation
            limit: Maximum number of messages to return (optional)

        Returns:
            List of messages ordered by creation time (oldest first)
        """
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id, Message.user_id == user_id)
            .order_by(Message.created_at.asc())
        )

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        messages = list(result.scalars().all())

        logger.info(
            f"Loaded {len(messages)} messages for conversation_id={conversation_id}, "
            f"user_id={user_id}"
        )

        return messages


# Global service instance
message_service = MessageService()
