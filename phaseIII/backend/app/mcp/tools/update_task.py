"""update_task MCP tool implementation."""
from typing import Any

from app.database import get_session
from app.mcp.server import mcp_server_manager
from app.mcp.validators import (
    ValidationError,
    validate_description,
    validate_task_id,
    validate_title,
    validate_user_id,
)
from app.services.task_service import TaskService


@mcp_server_manager.server.tool()
async def update_task(arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Update task title and/or description.

    Args:
        arguments: Tool arguments containing:
            - user_id: User ID from JWT token
            - task_id: Task ID to update
            - title: Optional new title
            - description: Optional new description

    Returns:
        dict with task_id and status
    """
    try:
        # Extract and validate parameters
        user_id = validate_user_id(arguments.get("user_id"))
        task_id = validate_task_id(arguments.get("task_id"))

        # Get optional fields
        title: str | None = arguments.get("title")
        description: str | None = arguments.get("description")

        # Validate that at least one field is provided
        if title is None and description is None:
            raise ValidationError(
                "At least one field (title or description) must be provided",
                "INVALID_PARAMETER"
            )

        # Validate fields if provided
        validated_title = validate_title(title) if title is not None else None
        validated_description = validate_description(description) if description is not None else None

        # Update task using service layer
        async for session in get_session():
            task_service = TaskService(session)
            task = await task_service.update_task(
                user_id=user_id,
                task_id=task_id,
                title=validated_title,
                description=validated_description
            )

            if not task:
                return {
                    "detail": "Task not found",
                    "code": "TASK_NOT_FOUND"
                }

            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
                "description": task.description
            }

    except ValidationError as e:
        error_response = {"detail": e.message, "code": e.code}
        if e.field:
            error_response["field"] = e.field
        return error_response

    except Exception:
        return {"detail": "Database connection failed", "code": "DATABASE_ERROR"}


# Register tool
mcp_server_manager.register_tool(
    name="update_task",
    description="Update task title and/or description",
    handler=update_task
)
