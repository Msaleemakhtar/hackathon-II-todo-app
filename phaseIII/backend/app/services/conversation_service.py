"""Conversation service for managing chat sessions."""

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.conversation import Conversation
from app.models.message import Message

logger = logging.getLogger(__name__)


class ConversationService:
    """Service layer for conversation management."""

    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: str,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(user_id=user_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        logger.info(f"Conversation created: conversation_id={conversation.id}, user_id={user_id}")
        return conversation

    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: str,
    ) -> Conversation | None:
        """Get a conversation by ID (with user ownership validation)."""
        conversation = await db.get(Conversation, conversation_id)
        if conversation and conversation.user_id == user_id:
            return conversation
        return None

    @staticmethod
    async def get_conversation_with_messages(
        db: AsyncSession,
        conversation_id: int,
        user_id: str,
        limit: int = 20,
    ) -> tuple[Conversation | None, list[Message]]:
        """
        Load conversation and last N messages for AI context.

        Returns:
            tuple: (conversation, messages) or (None, []) if not found
        """
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        if not conversation:
            return None, []

        # Load last N messages in chronological order
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(query)
        messages = list(result.scalars().all())
        messages.reverse()  # Chronological order for AI context

        logger.info(
            f"Loaded conversation: conversation_id={conversation_id}, messages={len(messages)}"
        )

        return conversation, messages

    @staticmethod
    async def update_conversation_timestamp(
        db: AsyncSession,
        conversation_id: int,
    ) -> None:
        """Update conversation updated_at timestamp."""
        conversation = await db.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            await db.commit()

    @staticmethod
    async def list_conversations(
        db: AsyncSession,
        user_id: str,
    ) -> list[Conversation]:
        """List user's conversations ordered by most recent."""
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )

        result = await db.execute(query)
        return list(result.scalars().all())


# Global service instance
conversation_service = ConversationService()
