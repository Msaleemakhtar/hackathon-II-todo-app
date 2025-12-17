"""complete_task MCP tool implementation."""
from typing import Any

from app.database import get_session
from app.mcp.server import mcp_server_manager
from app.mcp.validators import ValidationError, validate_task_id, validate_user_id
from app.services.task_service import TaskService


@mcp_server_manager.server.tool()
async def complete_task(arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Mark a task as completed (idempotent operation).

    Args:
        arguments: Tool arguments containing:
            - user_id: User ID from JWT token
            - task_id: Task ID to complete

    Returns:
        dict with task_id and status
    """
    try:
        # Extract and validate parameters
        user_id = validate_user_id(arguments.get("user_id"))
        task_id = validate_task_id(arguments.get("task_id"))

        # Complete task using service layer
        async for session in get_session():
            task_service = TaskService(session)
            task = await task_service.complete_task(user_id=user_id, task_id=task_id)

            if not task:
                return {
                    "detail": "Task not found",
                    "code": "TASK_NOT_FOUND"
                }

            return {
                "task_id": task.id,
                "status": "completed",
                "completed": task.completed
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
    name="complete_task",
    description="Mark a task as completed",
    handler=complete_task
)
