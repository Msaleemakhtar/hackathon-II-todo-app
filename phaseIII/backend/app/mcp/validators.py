"""Shared parameter validation functions for MCP tools."""


class ValidationError(Exception):
    """Exception raised when validation fails."""

    def __init__(self, message: str, code: str, field: str | None = None):
        self.message = message
        self.code = code
        self.field = field
        super().__init__(message)


def validate_user_id(user_id: str | None) -> str:
    """Validate user_id parameter."""
    if not user_id or not user_id.strip():
        raise ValidationError("User ID is required", "INVALID_USER_ID", "user_id")
    return user_id.strip()


def validate_title(title: str | None) -> str:
    """Validate task title parameter."""
    if not title or not title.strip():
        raise ValidationError(
            "Title is required and must be 1-200 characters", "INVALID_TITLE", "title"
        )
    title_trimmed = title.strip()
    if len(title_trimmed) > 200:
        raise ValidationError(
            "Title is required and must be 1-200 characters", "INVALID_TITLE", "title"
        )
    return title_trimmed


def validate_description(description: str | None) -> str | None:
    """Validate task description parameter."""
    if description is None or description == "":
        return None
    if len(description) > 1000:
        raise ValidationError(
            "Description cannot exceed 1000 characters", "DESCRIPTION_TOO_LONG", "description"
        )
    return description


def validate_task_id(task_id: int | None) -> int:
    """Validate task_id parameter."""
    if task_id is None or not isinstance(task_id, int) or task_id <= 0:
        raise ValidationError("Task ID must be a positive integer", "INVALID_PARAMETER", "task_id")
    return task_id


def validate_status_filter(status: str | None) -> str:
    """Validate status filter parameter."""
    if not status:
        return "all"
    if status not in {"all", "pending", "completed"}:
        raise ValidationError(
            "Status must be 'all', 'pending', or 'completed'", "INVALID_PARAMETER", "status"
        )
    return status
