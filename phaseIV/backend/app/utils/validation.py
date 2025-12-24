"""Validation utilities for user input with sanitization to prevent injection attacks."""

import html
import re

from fastapi import HTTPException, status

# Maximum lengths for security
MAX_MESSAGE_LENGTH = 10000  # 10K characters for chat messages
MAX_TITLE_LENGTH = 200


def validate_task_title(title: str) -> str:
    """
    Validate and sanitize task title (T125).

    Security measures:
    - Sanitizes input to prevent XSS and injection attacks
    - Enforces maximum title length
    - Removes dangerous control characters

    Args:
        title: Raw task title input

    Returns:
        str: Validated, sanitized, and trimmed title

    Raises:
        HTTPException: If validation fails
    """
    # Sanitize input (T125 - input sanitization)
    title = sanitize_text_input(title, max_length=MAX_TITLE_LENGTH)

    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "Title is required and cannot be empty or contain only whitespace",
                "code": "INVALID_TITLE",
                "field": "title",
            },
        )

    if len(title) > MAX_TITLE_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": f"Title cannot exceed {MAX_TITLE_LENGTH} characters",
                "code": "INVALID_TITLE",
                "field": "title",
                "max_length": MAX_TITLE_LENGTH,
            },
        )

    return title


def sanitize_text_input(text: str, max_length: int | None = None) -> str:
    """
    Sanitize user text input to prevent injection attacks.

    Protections:
    - Removes null bytes and control characters
    - Strips leading/trailing whitespace
    - HTML entity encoding for special characters
    - Enforces maximum length

    Args:
        text: Raw user input
        max_length: Maximum allowed length (optional)

    Returns:
        str: Sanitized text safe for storage and display
    """
    if not text:
        return ""

    # Remove null bytes and control characters (except newlines, tabs)
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    # Enforce maximum length
    if max_length and len(text) > max_length:
        text = text[:max_length]

    # HTML entity encode for XSS prevention
    # This prevents <script> tags and other HTML injection
    text = html.escape(text)

    return text


def validate_message_content(content: str) -> str:
    """
    Validate and sanitize message content (T125).

    Security measures:
    - Sanitizes input to prevent XSS and injection attacks
    - Enforces maximum message length
    - Removes dangerous control characters

    Args:
        content: Raw message content

    Returns:
        str: Validated, sanitized, and trimmed content

    Raises:
        HTTPException: If validation fails
    """
    # Sanitize input (T125 - input sanitization)
    content = sanitize_text_input(content, max_length=MAX_MESSAGE_LENGTH)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "Message is required and cannot be empty or contain only whitespace",
                "code": "INVALID_MESSAGE",
                "field": "content",
            },
        )

    if len(content) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters",
                "code": "MESSAGE_TOO_LONG",
                "field": "content",
                "max_length": MAX_MESSAGE_LENGTH,
            },
        )

    return content


def validate_conversation_ownership(conversation_user_id: str, jwt_user_id: str) -> None:
    """
    Validate that conversation belongs to the authenticated user.

    Args:
        conversation_user_id: User ID from conversation record
        jwt_user_id: User ID from JWT token

    Raises:
        HTTPException: If user IDs don't match
    """
    if conversation_user_id != jwt_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": "Conversation access denied",
                "code": "CONVERSATION_ACCESS_DENIED",
            },
        )
