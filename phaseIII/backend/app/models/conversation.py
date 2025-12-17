"""Conversation model for Phase III chat sessions."""
from datetime import datetime

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """Conversation between user and AI assistant."""

    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth JWT")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "ba_user_abc123",
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:15:00Z",
            }
        }
