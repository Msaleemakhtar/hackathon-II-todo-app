"""list_tasks MCP tool implementation."""
from typing import Any

from app.database import get_session
from app.mcp.server import mcp_server_manager
from app.mcp.validators import ValidationError, validate_status_filter, validate_user_id
from app.services.task_service import TaskService


@mcp_server_manager.server.tool()
async def list_tasks(arguments: dict[str, Any]) -> dict[str, Any]:
    """
    List tasks for the authenticated user with optional status filter.

    Args:
        arguments: Tool arguments containing:
            - user_id: User ID from JWT token
            - status: Optional filter ("all", "pending", "completed")

    Returns:
        dict with tasks array and total count
    """
    try:
        # Extract and validate parameters
        user_id = validate_user_id(arguments.get("user_id"))
        status = validate_status_filter(arguments.get("status", "all"))

        # Get tasks using service layer
        async for session in get_session():
            task_service = TaskService(session)
            tasks = await task_service.list_tasks(user_id=user_id, status=status)

            # Convert tasks to response format
            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
                for task in tasks
            ]

            return {
                "tasks": tasks_data,
                "total": len(tasks_data),
                "status": status
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
    name="list_tasks",
    description="List tasks for the authenticated user",
    handler=list_tasks
)
