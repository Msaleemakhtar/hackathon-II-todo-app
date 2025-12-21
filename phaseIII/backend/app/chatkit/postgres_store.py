"""
PostgreSQL implementation of ChatKit Store interface.

This module maps ChatKit threads and items to our existing PostgreSQL database:
- Threads → Conversation table
- Items → Message table
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from chatkit.server import Store
from chatkit.types import (
    ThreadMetadata,
    ThreadItem,
    Page,
    UserMessageItem,
    AssistantMessageItem,
    Attachment,
    AssistantMessageContent,
    UserMessageTextContent,
)

from app.database import async_session_maker
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService

logger = logging.getLogger(__name__)


class PostgresStore(Store):
    """
    ChatKit Store backed by PostgreSQL.

    Maps ChatKit concepts to database:
    - ChatKit Thread ID → Conversation.external_id
    - Internal Thread ID → Conversation.id
    - ThreadItem → Message
    """

    @staticmethod
    def _extract_text_content(content: Any) -> str:
        """
        Extract text from ChatKit content structure.

        Content can be:
        - A string: return as-is
        - A list of content objects: extract text from each
        - Other: convert to string
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Extract text from content objects
            texts = []
            for item in content:
                if hasattr(item, 'text'):
                    texts.append(item.text)
                elif isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
                else:
                    texts.append(str(item))
            return ' '.join(texts)
        else:
            return str(content)

    async def save_thread(
        self,
        thread: ThreadMetadata,
        context: dict[str, Any],
    ) -> None:
        """
        Save or update a thread in the database.

        Args:
            thread: ThreadMetadata from ChatKit
            context: Contains user_id from JWT authentication
        """
        logger.info(f"💾 save_thread() called - thread_id={thread.id if thread else 'None'}")

        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id not found in context")

        async with async_session_maker() as db:
            # Check if conversation exists by external_id (ChatKit thread ID)
            if thread.id:
                conversation = await ConversationService.get_conversation_by_external_id(
                    db=db, external_id=thread.id, user_id=user_id
                )

                if conversation:
                    # Update existing conversation
                    await ConversationService.update_conversation_timestamp(
                        db=db, conversation_id=conversation.id
                    )
                    logger.info(f"✅ Updated conversation: {conversation.id} (external_id={thread.id})")
                else:
                    # Create new conversation with external_id
                    conversation = await ConversationService.create_conversation(
                        db=db,
                        user_id=user_id,
                        external_id=thread.id,
                    )
                    logger.info(f"✅ Created conversation: {conversation.id} with external_id={thread.id}")
            else:
                # No thread ID, create new conversation
                conversation = await ConversationService.create_conversation(
                    db=db,
                    user_id=user_id,
                    external_id=None,
                )
                logger.info(f"✅ Created conversation: {conversation.id} (no external_id)")

    async def load_thread(
        self,
        thread_id: str,
        context: dict[str, Any],
    ) -> ThreadMetadata:
        """
        Load a thread from the database.

        Args:
            thread_id: ChatKit thread ID (stored in Conversation.external_id)
            context: Contains user_id from JWT authentication

        Returns:
            ThreadMetadata for the thread
        """
        logger.info(f"📂 load_thread() called - thread_id={thread_id}")

        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id not found in context")

        async with async_session_maker() as db:
            # Try to find by external_id first
            conversation = await ConversationService.get_conversation_by_external_id(
                db=db, external_id=thread_id, user_id=user_id
            )

            if not conversation:
                # Try finding by internal ID
                try:
                    conversation = await ConversationService.get_conversation(
                        db=db, conversation_id=int(thread_id), user_id=user_id
                    )
                except (ValueError, TypeError):
                    logger.error(f"❌ Thread not found: {thread_id}")
                    raise Exception(f"Thread not found: {thread_id}")

            if not conversation:
                logger.error(f"❌ Thread not found: {thread_id}")
                raise Exception(f"Thread not found: {thread_id}")

            logger.info(f"✅ Thread loaded: id={conversation.id}, external_id={conversation.external_id}")
            return ThreadMetadata(
                id=conversation.external_id or str(conversation.id),
                title=conversation.title or "New Chat",  # Provide default title if None
                created_at=conversation.created_at if conversation.created_at else datetime.now(timezone.utc),
                updated_at=conversation.updated_at if conversation.updated_at else datetime.now(timezone.utc),
            )

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadItem]:
        """
        Load thread items (messages) with pagination.

        Args:
            thread_id: ChatKit thread ID
            after: Cursor for pagination
            limit: Max items to return
            order: Sort order
            context: Contains user_id

        Returns:
            Page of ThreadItems
        """
        logger.info(f"📜 load_thread_items() called - thread_id={thread_id}, limit={limit}")

        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id not found in context")

        async with async_session_maker() as db:
            # Find conversation
            conversation = await ConversationService.get_conversation_by_external_id(
                db=db, external_id=thread_id, user_id=user_id
            )

            if not conversation:
                # Try internal ID
                try:
                    conversation = await ConversationService.get_conversation(
                        db=db, conversation_id=int(thread_id), user_id=user_id
                    )
                except (ValueError, TypeError):
                    logger.warning(f"❌ Thread not found for load_thread_items: {thread_id}")
                    return Page(data=[], has_more=False)

            if not conversation:
                logger.warning(f"❌ Thread not found for load_thread_items: {thread_id}")
                return Page(data=[], has_more=False)

            # Load messages
            messages = await MessageService.get_messages_by_conversation(
                db=db, conversation_id=conversation.id, user_id=user_id
            )

            logger.info(f"📊 Found {len(messages)} messages for thread {thread_id}")

            # Convert to ThreadItems
            # Note: ChatKit SDK expects specific fields for UserMessageItem/AssistantMessageItem
            # We return simple text content since we only store text in the database
            items = []
            for msg in messages:
                logger.info(f"   Processing message: id={msg.id}, role={msg.role}, content={msg.content[:50]}...")
                if msg.role == MessageRole.USER:
                    item = UserMessageItem(
                        thread_id=thread_id,
                        id=str(msg.id),
                        content=[UserMessageTextContent(text=msg.content)],
                        created_at=msg.created_at if msg.created_at else datetime.now(timezone.utc),
                        attachments=[],  # Empty list for attachments
                        quoted_text='',  # Empty string for quoted_text
                        inference_options={'tool_choice': None, 'model': None},  # Proper inference options
                    )
                    items.append(item)
                    logger.info(f"   ✅ Created UserMessageItem: {item.model_dump()}")
                elif msg.role == MessageRole.ASSISTANT:
                    # CRITICAL: Explicitly set all AssistantMessageContent fields
                    # to force inclusion in serialization
                    item = AssistantMessageItem(
                        thread_id=thread_id,
                        id=str(msg.id),
                        content=[AssistantMessageContent(
                            text=msg.content,
                            type="output_text",  # Explicitly set
                            annotations=[]  # Explicitly set
                        )],
                        created_at=msg.created_at if msg.created_at else datetime.now(timezone.utc),
                    )
                    items.append(item)
                    logger.info(f"   ✅ Created AssistantMessageItem: {item.model_dump()}")

            logger.info(f"✅ Thread items loaded: thread_id={thread_id}, count={len(items)}, returning={min(len(items), limit)}")
            logger.info(f"📤 Returning Page with {len(items[:limit])} items")
            return Page(data=items[:limit], has_more=len(items) > limit)

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict[str, Any],
    ) -> None:
        """
        Add a new item to a thread.

        Args:
            thread_id: ChatKit thread ID
            item: ThreadItem to add
            context: Contains user_id
        """
        await self.save_item(thread_id, item, context)

    async def save_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict[str, Any],
    ) -> None:
        """
        Save or update a thread item.

        Args:
            thread_id: ChatKit thread ID
            item: ThreadItem to save
            context: Contains user_id
        """
        logger.info(f"💾 save_item() called - thread_id={thread_id}, item_type={type(item).__name__}")

        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id not found in context")

        async with async_session_maker() as db:
            # Find conversation
            conversation = await ConversationService.get_conversation_by_external_id(
                db=db, external_id=thread_id, user_id=user_id
            )

            if not conversation:
                # Try internal ID
                try:
                    conversation = await ConversationService.get_conversation(
                        db=db, conversation_id=int(thread_id), user_id=user_id
                    )
                except (ValueError, TypeError):
                    logger.error(f"Thread not found for save_item: {thread_id}")
                    raise Exception(f"Thread not found: {thread_id}")

            if not conversation:
                raise Exception(f"Thread not found: {thread_id}")

            # Determine role and extract text content
            if isinstance(item, UserMessageItem):
                role = MessageRole.USER
                content = self._extract_text_content(item.content)
            elif isinstance(item, AssistantMessageItem):
                role = MessageRole.ASSISTANT
                content = self._extract_text_content(item.content)
            else:
                logger.warning(f"Unknown item type: {type(item)}")
                return

            # Save message
            logger.info(f"💾 Saving {role} message to conversation {conversation.id}")
            if role == MessageRole.USER:
                msg = await MessageService.create_user_message(
                    db=db,
                    conversation_id=conversation.id,
                    user_id=user_id,
                    content=content,
                )
                logger.info(f"✅ Saved USER message: id={msg.id}, content={content[:50]}...")
            else:
                msg = await MessageService.create_assistant_message(
                    db=db,
                    conversation_id=conversation.id,
                    user_id=user_id,
                    content=content,
                )
                logger.info(f"✅ Saved ASSISTANT message: id={msg.id}, content={content[:50]}...")

    async def load_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict[str, Any],
    ) -> ThreadItem:
        """Load a specific thread item by ID."""
        # TODO: Implement if needed
        raise NotImplementedError("load_item not implemented")

    async def delete_thread(
        self,
        thread_id: str,
        context: dict[str, Any],
    ) -> None:
        """Delete a thread and all its items."""
        # TODO: Implement if needed
        raise NotImplementedError("delete_thread not implemented")

    async def delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict[str, Any],
    ) -> None:
        """Delete a specific thread item."""
        # TODO: Implement if needed
        raise NotImplementedError("delete_thread_item not implemented")

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadMetadata]:
        """Load a page of threads."""
        logger.info(f"📋 load_threads() called - limit={limit}, order={order}")

        user_id = context.get("user_id")
        if not user_id:
            raise ValueError("user_id not found in context")

        async with async_session_maker() as db:
            # Get user's conversations from database
            conversations = await ConversationService.list_conversations(
                db=db, user_id=user_id
            )

            logger.info(f"📋 Found {len(conversations)} conversations for user {user_id}")

            # Convert to ThreadMetadata
            threads = []
            for conv in conversations:
                thread = ThreadMetadata(
                    id=conv.external_id or str(conv.id),
                    title=conv.title or "New Chat",
                    created_at=conv.created_at if conv.created_at else datetime.now(timezone.utc),
                    updated_at=conv.updated_at if conv.updated_at else datetime.now(timezone.utc),
                )
                threads.append(thread)
                logger.info(f"   Thread: id={thread.id}, title={thread.title}")

            # Apply limit
            limited_threads = threads[:limit]
            logger.info(f"📤 Returning {len(limited_threads)} threads")

            return Page(data=limited_threads, has_more=len(threads) > limit)

    async def save_attachment(
        self,
        attachment: Attachment,
        context: dict[str, Any],
    ) -> None:
        """Save attachment metadata."""
        # TODO: Implement if needed
        raise NotImplementedError("save_attachment not implemented")

    async def load_attachment(
        self,
        attachment_id: str,
        context: dict[str, Any],
    ) -> Attachment:
        """Load attachment metadata."""
        # TODO: Implement if needed
        raise NotImplementedError("load_attachment not implemented")

    async def delete_attachment(
        self,
        attachment_id: str,
        context: dict[str, Any],
    ) -> None:
        """Delete attachment metadata."""
        # TODO: Implement if needed
        raise NotImplementedError("delete_attachment not implemented")
