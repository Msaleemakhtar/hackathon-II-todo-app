"""Message model for Phase III conversation messages."""
from datetime import datetime

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """Message in a conversation (user or assistant)."""

    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(
        foreign_key="conversations.id", index=True, nullable=False
    )
    user_id: str = Field(index=True, nullable=False, description="User ID (redundant isolation)")
    role: str = Field(
        nullable=False, description="Message sender role (user or assistant)"
    )
    content: str = Field(nullable=False, description="Message content")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": "ba_user_abc123",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2025-12-17T10:00:00Z",
            }
        }
