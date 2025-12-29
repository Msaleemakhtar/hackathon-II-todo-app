from datetime import UTC, datetime

from pydantic import BaseModel, field_validator

from app.models.task import PriorityLevel


class TaskCreate(BaseModel):
    """Schema for creating a new task with Phase V advanced features."""

    title: str
    description: str | None = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    due_date: datetime | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None
    recurrence_rule: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        if len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v.strip()

    @field_validator("due_date")
    @classmethod
    def convert_to_utc(cls, v: datetime | None) -> datetime | None:
        """Convert timezone-aware datetime to UTC, or assume UTC if naive."""
        if v is None:
            return None
        # If timezone-aware, convert to UTC; if naive, assume UTC
        if v.tzinfo is not None:
            return v.astimezone(UTC).replace(tzinfo=None)
        return v

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids(cls, v: list[int] | None) -> list[int] | None:
        if v is not None and len(v) > 10:
            raise ValueError("Maximum 10 tags per task")
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    priority: PriorityLevel | None = None
    due_date: datetime | None = None
    category_id: int | None = None
    recurrence_rule: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Title cannot be empty")
            if len(v) > 200:
                raise ValueError("Title must be 200 characters or less")
            return v.strip()
        return v

    @field_validator("due_date")
    @classmethod
    def convert_to_utc(cls, v: datetime | None) -> datetime | None:
        """Convert timezone-aware datetime to UTC, or assume UTC if naive."""
        if v is None:
            return None
        if v.tzinfo is not None:
            return v.astimezone(UTC).replace(tzinfo=None)
        return v


class CategoryInfo(BaseModel):
    """Category information embedded in task responses."""

    id: int
    name: str
    color: str | None


class TagInfo(BaseModel):
    """Tag information embedded in task responses."""

    id: int
    name: str
    color: str | None


class TaskResponse(BaseModel):
    """Schema for task responses with Phase V enhancements."""

    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool
    priority: PriorityLevel
    due_date: datetime | None
    category: CategoryInfo | None = None
    tags: list[TagInfo] = []
    recurrence_rule: str | None
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime
