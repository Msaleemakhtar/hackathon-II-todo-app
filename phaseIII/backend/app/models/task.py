from datetime import datetime

from sqlmodel import Field, SQLModel


class TaskPhaseIII(SQLModel, table=True):
    """
    Task model for Phase III conversational task management.
    Completely separate from Phase II tasks table.
    """

    __tablename__ = "tasks_phaseiii"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False, nullable=False)
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
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:00:00Z",
            }
        }
