"""MCP Tools for task management using FastMCP - stateless with database-backed state."""

import logging
from datetime import datetime
from typing import Any

from sqlmodel import select

from app.database import async_session_maker
from app.models.task import TaskPhaseIII

logger = logging.getLogger(__name__)

# Import FastMCP instance
from app.mcp.server import mcp

# Log tool registration on module load
logger.info("🔧 tools.py module loading - registering MCP tools...")


@mcp.tool(name="add_task", description="Create a new task for the user")
async def add_task(user_id: str, title: str, description: str = "") -> dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: User ID from JWT token
        title: Task title (1-200 characters)
        description: Optional task description

    Returns:
        dict: Created task with id, status, and title
    """
    try:
        # Validate title
        title = title.strip()
        if not title or len(title) > 200:
            # T092: Enhanced error with character count and example
            char_count = len(title)
            return {
                "status": "error",
                "message": (
                    f"Title must be 1-200 characters (you provided {char_count}). "
                    f"Example: 'Buy groceries' or 'Schedule dentist appointment'"
                ),
                "code": "INVALID_TITLE",
                "details": {
                    "current_length": char_count,
                    "max_length": 200,
                    "min_length": 1,
                },
            }

        # Create task in database
        async with async_session_maker() as session:
            task = TaskPhaseIII(
                user_id=user_id,
                title=title,
                description=description.strip() if description else None,
                completed=False,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            logger.info(f"Task created: user={user_id}, task_id={task.id}, title={title}")

            return {
                "status": "created",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
            }

    except Exception as e:
        logger.error(f"add_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}",
        }


@mcp.tool(name="list_tasks", description="List user tasks with optional status filter")
async def list_tasks(user_id: str, status: str = "all") -> list[dict[str, Any]]:
    """
    List user tasks with optional status filter.

    Args:
        user_id: User ID from JWT token
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        list: Array of tasks with id, title, description, completed, created_at
    """
    try:
        async with async_session_maker() as session:
            # Build query
            query = select(TaskPhaseIII).where(TaskPhaseIII.user_id == user_id)

            if status == "pending":
                query = query.where(TaskPhaseIII.completed.is_(False))
            elif status == "completed":
                query = query.where(TaskPhaseIII.completed.is_(True))

            query = query.order_by(TaskPhaseIII.created_at.desc())

            # Execute query
            result = await session.execute(query)
            tasks = result.scalars().all()

            logger.info(f"list_tasks: user={user_id}, status={status}, count={len(tasks)}")

            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                }
                for task in tasks
            ]

    except Exception as e:
        logger.error(f"list_tasks error: {str(e)}")
        return []


@mcp.tool(name="complete_task", description="Mark a task as completed")
async def complete_task(user_id: str, task_id: int) -> dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        user_id: User ID from JWT token
        task_id: Task ID to complete

    Returns:
        dict: Updated task status
    """
    try:
        async with async_session_maker() as session:
            # Get task
            task = await session.get(TaskPhaseIII, task_id)

            if not task:
                # T091: Enhanced error with task list suggestion
                query = (
                    select(TaskPhaseIII)
                    .where(TaskPhaseIII.user_id == user_id, TaskPhaseIII.completed.is_(False))
                    .order_by(TaskPhaseIII.created_at.desc())
                    .limit(5)
                )
                result = await session.execute(query)
                recent_tasks = result.scalars().all()

                task_suggestions = ""
                if recent_tasks:
                    task_list = "\n".join([f"  - Task #{t.id}: {t.title}" for t in recent_tasks])
                    task_suggestions = f"\n\nYour pending tasks:\n{task_list}"

                return {
                    "status": "error",
                    "message": f"Task #{task_id} not found.{task_suggestions}",
                    "code": "TASK_NOT_FOUND",
                    "details": {
                        "requested_task_id": task_id,
                        "suggestions": [{"id": t.id, "title": t.title} for t in recent_tasks],
                    },
                }

            # Validate ownership
            if task.user_id != user_id:
                return {
                    "status": "error",
                    "message": "Task does not belong to you",
                    "code": "FORBIDDEN",
                }

            # Update task
            task.completed = True
            task.updated_at = datetime.utcnow()
            await session.commit()

            logger.info(f"Task completed: user={user_id}, task_id={task_id}")

            return {
                "status": "completed",
                "task_id": task.id,
                "title": task.title,
                "completed": task.completed,
            }

    except Exception as e:
        logger.error(f"complete_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to complete task: {str(e)}",
        }


@mcp.tool(name="delete_task", description="Delete a task")
async def delete_task(user_id: str, task_id: int) -> dict[str, Any]:
    """
    Delete a task.

    Args:
        user_id: User ID from JWT token
        task_id: Task ID to delete

    Returns:
        dict: Deletion status
    """
    try:
        async with async_session_maker() as session:
            # Get task
            task = await session.get(TaskPhaseIII, task_id)

            if not task:
                # T091: Enhanced error with task list suggestion
                query = (
                    select(TaskPhaseIII)
                    .where(TaskPhaseIII.user_id == user_id)
                    .order_by(TaskPhaseIII.created_at.desc())
                    .limit(5)
                )
                result = await session.execute(query)
                recent_tasks = result.scalars().all()

                task_suggestions = ""
                if recent_tasks:
                    task_list = "\n".join([f"  - Task #{t.id}: {t.title}" for t in recent_tasks])
                    task_suggestions = f"\n\nYour recent tasks:\n{task_list}"

                return {
                    "status": "error",
                    "message": f"Task #{task_id} not found.{task_suggestions}",
                    "code": "TASK_NOT_FOUND",
                    "details": {
                        "requested_task_id": task_id,
                        "suggestions": [{"id": t.id, "title": t.title} for t in recent_tasks],
                    },
                }

            # Validate ownership
            if task.user_id != user_id:
                return {
                    "status": "error",
                    "message": "Task does not belong to you",
                    "code": "FORBIDDEN",
                }

            # Delete task
            title = task.title
            await session.delete(task)
            await session.commit()

            logger.info(f"Task deleted: user={user_id}, task_id={task_id}")

            return {
                "status": "deleted",
                "task_id": task_id,
                "title": title,
            }

    except Exception as e:
        logger.error(f"delete_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to delete task: {str(e)}",
        }


@mcp.tool(name="update_task", description="Update task title and/or description")
async def update_task(
    user_id: str, task_id: int, title: str = None, description: str = None
) -> dict[str, Any]:
    """
    Update task title and/or description.

    Args:
        user_id: User ID from JWT token
        task_id: Task ID to update
        title: Optional new title
        description: Optional new description

    Returns:
        dict: Updated task status
    """
    try:
        # Validate at least one field provided
        if title is None and description is None:
            return {
                "status": "error",
                "message": "Must provide title or description to update",
                "code": "INVALID_REQUEST",
            }

        async with async_session_maker() as session:
            # Get task
            task = await session.get(TaskPhaseIII, task_id)

            if not task:
                # T091: Enhanced error with task list suggestion
                query = (
                    select(TaskPhaseIII)
                    .where(TaskPhaseIII.user_id == user_id)
                    .order_by(TaskPhaseIII.created_at.desc())
                    .limit(5)
                )
                result = await session.execute(query)
                recent_tasks = result.scalars().all()

                task_suggestions = ""
                if recent_tasks:
                    task_list = "\n".join([f"  - Task #{t.id}: {t.title}" for t in recent_tasks])
                    task_suggestions = f"\n\nYour recent tasks:\n{task_list}"

                return {
                    "status": "error",
                    "message": f"Task #{task_id} not found.{task_suggestions}",
                    "code": "TASK_NOT_FOUND",
                    "details": {
                        "requested_task_id": task_id,
                        "suggestions": [{"id": t.id, "title": t.title} for t in recent_tasks],
                    },
                }

            # Validate ownership
            if task.user_id != user_id:
                return {
                    "status": "error",
                    "message": "Task does not belong to you",
                    "code": "FORBIDDEN",
                }

            # Update fields
            if title is not None:
                title = title.strip()
                if not title or len(title) > 200:
                    return {
                        "status": "error",
                        "message": "Title must be 1-200 characters",
                        "code": "INVALID_TITLE",
                    }
                task.title = title

            if description is not None:
                task.description = description.strip() if description else None

            task.updated_at = datetime.utcnow()
            await session.commit()

            logger.info(f"Task updated: user={user_id}, task_id={task_id}")

            return {
                "status": "updated",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
            }

    except Exception as e:
        logger.error(f"update_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}",
        }


# Log tools registered
logger.info(f"✅ MCP tools registered: add_task, list_tasks, complete_task, delete_task, update_task")
logger.info(f"📊 Total tools in mcp instance: {len(mcp._tools) if hasattr(mcp, '_tools') else 'unknown'}")
