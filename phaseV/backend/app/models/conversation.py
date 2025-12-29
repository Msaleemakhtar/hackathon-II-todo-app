from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session between user and AI assistant.
    Enables conversation continuity and context building.
    """

    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    external_id: str | None = Field(default=None, index=True)  # Maps to ChatKit thread_id
    title: str | None = Field(default=None)  # Optional conversation title
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship - messages in this conversation
    messages: list["Message"] = Relationship(back_populates="conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123",
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:30:00Z",
            }
        }
