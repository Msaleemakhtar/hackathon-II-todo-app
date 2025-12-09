from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel, text

if TYPE_CHECKING:
    from .user import User
    from .tag import Tag


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: str = Field(
        default="medium", regex="^(low|medium|high)$"
    )  # Enum like constraint
    due_date: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None)  # iCal RRULE string

    user_id: str = Field(foreign_key="users.id", index=True)


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": text("CURRENT_TIMESTAMP")},
    )

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={"secondary": "task_tag_link"}
    )


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)
    priority: Optional[str] = Field(default=None, regex="^(low|medium|high)$")
    due_date: Optional[datetime] = Field(default=None)
    recurrence_rule: Optional[str] = Field(default=None)