"""add_task MCP tool implementation."""
from typing import Any

from app.database import get_session
from app.mcp.server import mcp_server_manager
from app.mcp.validators import (
    ValidationError,
    validate_description,
    validate_title,
    validate_user_id,
)
from app.services.task_service import TaskService


@mcp_server_manager.server.tool()
async def add_task(arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Create a new task for the authenticated user.

    Args:
        arguments: Tool arguments containing:
            - user_id: User ID from JWT token
            - title: Task title (1-200 characters)
            - description: Optional task description (≤1000 characters)

    Returns:
        dict with task_id, status, and title

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Extract and validate parameters
        user_id = validate_user_id(arguments.get("user_id"))
        title = validate_title(arguments.get("title"))
        description = validate_description(arguments.get("description"))

        # Create task using service layer
        async for session in get_session():
            task_service = TaskService(session)
            task = await task_service.create_task(
                user_id=user_id,
                title=title,
                description=description
            )

            # Return response matching contract
            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title
            }

        # This should never be reached but satisfies type checker
        return {"detail": "Database session error", "code": "SESSION_ERROR"}

    except ValidationError as e:
        # Return error response matching contract
        error_response = {
            "detail": e.message,
            "code": e.code
        }
        if e.field:
            error_response["field"] = e.field
        return error_response

    except Exception:
        # Handle unexpected errors
        return {
            "detail": "Database connection failed",
            "code": "DATABASE_ERROR"
        }


# Register tool with MCP server
mcp_server_manager.register_tool(
    name="add_task",
    description="Create a new task for the authenticated user",
    handler=add_task
)
