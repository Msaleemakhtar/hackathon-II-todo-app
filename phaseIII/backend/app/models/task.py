"""TaskPhaseIII model for Phase III task management."""
from datetime import datetime

from sqlmodel import Field, SQLModel


class TaskPhaseIII(SQLModel, table=True):
    """Phase III task entity - separate from Phase II tasks."""

    __tablename__ = "tasks_phaseiii"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from Better Auth JWT")
    title: str = Field(max_length=200, nullable=False, description="Task title (1-200 chars)")
    description: str | None = Field(
        default=None, max_length=1000, description="Task description (≤1000 chars)"
    )
    completed: bool = Field(default=False, nullable=False, description="Completion status")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "ba_user_abc123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:00:00Z",
            }
        }
