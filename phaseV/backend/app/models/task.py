from datetime import datetime
from enum import Enum as PyEnum

import sqlalchemy as sa
from sqlmodel import Column, Field, SQLModel


class PriorityLevel(str, PyEnum):
    """Priority levels for tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskPhaseIII(SQLModel, table=True):
    """
    Task model for Phase V advanced task management.
    Enhanced from Phase III with priority, categories, tags, due dates, and search.
    """

    __tablename__ = "tasks_phaseiii"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False, nullable=False)
    priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM,
        sa_column=Column(
            sa.Enum(
                PriorityLevel,
                name="priority_level",
                values_callable=lambda x: [e.value for e in x],
            ),
            nullable=False,
        ),
    )
    due_date: datetime | None = Field(default=None, nullable=True)
    category_id: int | None = Field(default=None, foreign_key="categories.id", nullable=True)
    recurrence_rule: str | None = Field(default=None, nullable=True)
    reminder_sent: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "medium",
                "due_date": "2025-12-20T18:00:00Z",
                "category_id": 1,
                "recurrence_rule": None,
                "reminder_sent": False,
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:00:00Z",
            }
        }
