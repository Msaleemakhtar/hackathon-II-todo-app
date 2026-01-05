"""MCP Tools for task management using FastMCP - stateless with database-backed state."""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import async_session_maker
from app.kafka.events import (
    ReminderSentEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskDeletedEvent,
    TaskUpdatedEvent,
)
from app.kafka.producer import kafka_producer
from app.models.category import Category
from app.models.task import TaskPhaseIII
from app.services import task_service
from app.utils.rrule_parser import validate_rrule

logger = logging.getLogger(__name__)

# Import FastMCP instance
from app.mcp.server import mcp

# Log tool registration on module load
logger.info("🔧 tools.py module loading - registering MCP tools...")


async def force_session_sync(session: AsyncSession) -> None:
    """
    Force session to synchronize with database.

    Ensures committed changes are visible to subsequent queries,
    especially important with Neon Serverless PostgreSQL connection pooling.

    This defensive measure helps prevent read-after-write consistency issues
    where a task created in one session may not be immediately visible when
    queried from a different session due to connection pool state.

    Args:
        session: The async SQLAlchemy session to synchronize

    Raises:
        No exceptions - errors are logged but not raised to avoid breaking the main flow
    """
    try:
        await session.execute(text("SELECT 1"))
        logger.debug("Session synchronized with database")
    except Exception as e:
        logger.warning(f"Session sync failed (non-critical): {e}")


@mcp.tool(
    name="add_task",
    description="""Create a new task for the user.

NATURAL LANGUAGE PARSING GUIDE:

Due Date Extraction:
  - "due tomorrow" → Calculate tomorrow's date, convert to ISO format
  - "due 2026-1-11" or "due date is 2026-1-11" → Convert to ISO: "2026-01-11T23:59:59Z"
  - "due next Monday" → Calculate next Monday's date, convert to ISO format
  - "in 3 days" → Add 3 days to current date, convert to ISO format

Recurrence Pattern Extraction:
  - "every day" or "daily" → "FREQ=DAILY"
  - "every sunday" → "FREQ=WEEKLY;BYDAY=SU"
  - "every monday and friday" → "FREQ=WEEKLY;BYDAY=MO,FR"
  - "weekly" → "FREQ=WEEKLY"
  - "monthly" → "FREQ=MONTHLY"

ALWAYS convert natural language dates and recurrence patterns to proper formats before calling this tool.
"""
)
async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    category_id: int | None = None,
    tag_ids: list[int] | None = None,
    due_date: str | None = None,
    recurrence_rule: str | None = None,
) -> dict[str, Any]:
    """
    Create a new task for the user with optional tags, due date, and recurrence.

    Args:
        user_id: User ID from JWT token
        title: Task title (1-200 characters)
        description: Optional task description
        priority: Task priority (low, medium, high, urgent) - default: medium
        category_id: Optional category ID to assign task to
        tag_ids: Optional list of tag IDs to assign (max 10 tags)

        due_date: Due date in ISO 8601 format (e.g., "2026-01-11T23:59:59Z")
            PARSE FROM NATURAL LANGUAGE:
            - "2026-1-11" → "2026-01-11T23:59:59Z"
            - "tomorrow" → Calculate tomorrow's date and convert to ISO format
            - "next Monday" → Calculate next Monday's date and convert to ISO format
            IMPORTANT: Convert ALL date strings to proper ISO 8601 format with timezone

        recurrence_rule: iCalendar RRULE in RFC 5545 format
            CONVERT FROM NATURAL LANGUAGE:
            - "every sunday" → "FREQ=WEEKLY;BYDAY=SU"
            - "daily" or "every day" → "FREQ=DAILY"
            - "weekly on monday and friday" → "FREQ=WEEKLY;BYDAY=MO,FR"

            Day abbreviations: MO, TU, WE, TH, FR, SA, SU

            Standard RFC 5545 Examples:
            - "FREQ=DAILY" - Every day
            - "FREQ=WEEKLY;BYDAY=MO,WE,FR" - Every Monday, Wednesday, Friday
            - "FREQ=MONTHLY;BYMONTHDAY=15" - 15th of every month
            - "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25" - Every December 25th

    Returns:
        dict: Created task with id, status, title, priority, category, tags, due_date, and recurrence_rule
    """
    try:
        # Validate priority
        is_valid, error, priority_enum = task_service.validate_priority(priority)
        if not is_valid:
            return {
                "status": "error",
                "message": error,
                "code": "INVALID_PRIORITY",
            }

        # Validate tag count
        if tag_ids and len(tag_ids) > 10:
            return {
                "status": "error",
                "message": "Maximum 10 tags per task",
                "code": "TOO_MANY_TAGS",
            }

        # T022: Validate recurrence_rule against whitelist
        if recurrence_rule:
            is_valid, error_message = validate_rrule(recurrence_rule)
            if not is_valid:
                return {
                    "status": "error",
                    "message": error_message,
                    "code": "INVALID_RECURRENCE_RULE",
                }

        # Parse and convert due_date to UTC if provided
        due_date_utc = None
        if due_date:
            try:
                from datetime import datetime, time

                dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))

                # If date-only (midnight time), default to end-of-day (23:59:59)
                # This prevents reminders from being "in the past" when set earlier in the day
                if dt.time() == time(0, 0, 0):
                    dt = dt.replace(hour=23, minute=59, second=59)
                    logger.info(f"Date-only due_date detected, defaulting to end-of-day: {dt.isoformat()}")

                # Convert to UTC and make naive (as per data model)
                if dt.tzinfo is not None:
                    due_date_utc = dt.astimezone(UTC).replace(tzinfo=None)
                else:
                    due_date_utc = dt
            except (ValueError, AttributeError) as e:
                return {
                    "status": "error",
                    "message": f"Invalid due_date format. Use ISO 8601 (e.g., 2025-01-15T17:00:00-05:00): {str(e)}",
                    "code": "INVALID_DUE_DATE",
                }

        # Create task using service
        async with async_session_maker() as session:
            task = await task_service.create_task(
                session=session,
                user_id=user_id,
                title=title,
                description=description if description else None,
                priority=priority_enum,
                category_id=category_id,
                due_date=due_date_utc,
                recurrence_rule=recurrence_rule,
            )

            # Add tags atomically if provided
            if tag_ids:
                for tag_id in tag_ids:
                    await tag_service.add_tag_to_task(
                        session=session, task_id=task.id, tag_id=tag_id, user_id=user_id
                    )

            # Get category details if assigned
            category = None
            if task.category_id:
                category = await category_service.get_category_by_id(
                    session, task.category_id, user_id
                )

            # Get tags details
            tags = []
            if tag_ids:
                from app.models.tag import TagPhaseV

                result = await session.execute(select(TagPhaseV).where(TagPhaseV.id.in_(tag_ids)))
                tag_objects = result.scalars().all()
                tags = [{"id": t.id, "name": t.name, "color": t.color} for t in tag_objects]

            # Note: TaskCreatedEvent is now published by task_service.create_task()
            # No need to publish here to avoid duplicates

            # Force session sync to ensure write visibility for subsequent reads
            await force_session_sync(session)

            return {
                "status": "created",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "category": (
                    {
                        "id": category.id,
                        "name": category.name,
                        "color": category.color,
                    }
                    if category
                    else None
                ),
                "tags": tags,
                "recurrence_rule": task.recurrence_rule,
                "created_at": task.created_at.isoformat(),
            }

    except ValueError as e:
        logger.error(f"add_task validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "code": "VALIDATION_ERROR",
        }
    except Exception as e:
        logger.error(f"add_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to create task: {str(e)}",
        }


@mcp.tool(name="list_tasks", description="List user tasks with optional filters")
async def list_tasks(
    user_id: str,
    status: str = "all",
    priority: str | None = None,
    category_id: int | None = None,
    tag_ids: list[int] | None = None,
    due_before: str | None = None,
    due_after: str | None = None,
    sort_by: str = "created_at",
) -> list[dict[str, Any]]:
    """
    List user tasks with optional status, priority, category, tag, and due date filters.

    Args:
        user_id: User ID from JWT token
        status: Filter by status - "all", "pending", or "completed" (default: "all")
        priority: Filter by priority - "low", "medium", "high", "urgent" (optional)
        category_id: Filter by category ID (optional)
        tag_ids: Filter by tag IDs - tasks having ANY of these tags (OR logic) (optional)
        due_before: Filter tasks due before this date (ISO 8601 format) (optional)
        due_after: Filter tasks due after this date (ISO 8601 format) (optional)
        sort_by: Sort by field - "created_at", "due_date", "priority" (default: "created_at")

    Returns:
        list: Array of tasks with all Phase V fields including category and tags
    """
    try:
        # Validate priority if provided
        priority_enum = None
        if priority:
            is_valid, error, priority_enum = task_service.validate_priority(priority)
            if not is_valid:
                logger.warning(f"Invalid priority filter: {priority}")
                return []

        # Parse due_before and due_after if provided
        from datetime import datetime

        due_before_utc = None
        if due_before:
            try:
                dt = datetime.fromisoformat(due_before.replace("Z", "+00:00"))
                due_before_utc = dt.astimezone(UTC).replace(tzinfo=None) if dt.tzinfo else dt
            except (ValueError, AttributeError):
                logger.warning(f"Invalid due_before format: {due_before}")
                return []

        due_after_utc = None
        if due_after:
            try:
                dt = datetime.fromisoformat(due_after.replace("Z", "+00:00"))
                due_after_utc = dt.astimezone(UTC).replace(tzinfo=None) if dt.tzinfo else dt
            except (ValueError, AttributeError):
                logger.warning(f"Invalid due_after format: {due_after}")
                return []

        async with async_session_maker() as session:
            # Use service layer for basic querying
            tasks = await task_service.list_tasks(
                session=session,
                user_id=user_id,
                status=status if status != "all" else None,
                priority=priority_enum,
                category_id=category_id,
            )

            # Filter by due date range
            if due_before_utc:
                tasks = [task for task in tasks if task.due_date and task.due_date < due_before_utc]
            if due_after_utc:
                tasks = [task for task in tasks if task.due_date and task.due_date > due_after_utc]

            # Filter by tags if provided (OR logic: task has ANY of the specified tags)
            if tag_ids:
                from app.models.task_tag import TaskTags

                # Get task IDs that have any of the specified tags
                result = await session.execute(
                    select(TaskTags.task_id).where(TaskTags.tag_id.in_(tag_ids)).distinct()
                )
                matching_task_ids = {row[0] for row in result.all()}

                # Filter tasks to only those with matching tags
                tasks = [task for task in tasks if task.id in matching_task_ids]

            # Sort tasks
            if sort_by == "due_date":
                # Sort by due_date (null values last)
                tasks = sorted(
                    tasks, key=lambda t: (t.due_date is None, t.due_date or datetime.max)
                )
            elif sort_by == "priority":
                # Sort by priority (urgent -> high -> medium -> low)
                priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
                tasks = sorted(tasks, key=lambda t: priority_order.get(t.priority.value, 4))
            else:
                # Default: sort by created_at descending (already done by service)
                pass

            # Build category map for efficient lookup
            category_ids = {task.category_id for task in tasks if task.category_id}
            category_map = {}
            if category_ids:
                result = await session.execute(
                    select(Category).where(Category.id.in_(category_ids))
                )
                categories = result.scalars().all()
                category_map = {cat.id: cat for cat in categories}

            # Build tag map for efficient lookup
            from app.models.tag import TagPhaseV
            from app.models.task_tag import TaskTags

            task_ids = [task.id for task in tasks]
            task_tags_map = {}
            if task_ids:
                # Get all task-tag associations
                result = await session.execute(
                    select(TaskTags).where(TaskTags.task_id.in_(task_ids))
                )
                task_tag_assocs = result.scalars().all()

                # Get all unique tag IDs
                tag_id_set = {assoc.tag_id for assoc in task_tag_assocs}

                # Fetch tag details
                tag_map = {}
                if tag_id_set:
                    result = await session.execute(
                        select(TagPhaseV).where(TagPhaseV.id.in_(tag_id_set))
                    )
                    tags_list = result.scalars().all()
                    tag_map = {tag.id: tag for tag in tags_list}

                # Build task -> tags mapping
                for assoc in task_tag_assocs:
                    if assoc.task_id not in task_tags_map:
                        task_tags_map[assoc.task_id] = []
                    if assoc.tag_id in tag_map:
                        tag = tag_map[assoc.tag_id]
                        task_tags_map[assoc.task_id].append(
                            {"id": tag.id, "name": tag.name, "color": tag.color}
                        )

            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "category": (
                        {
                            "id": category_map[task.category_id].id,
                            "name": category_map[task.category_id].name,
                            "color": category_map[task.category_id].color,
                        }
                        if task.category_id and task.category_id in category_map
                        else None
                    ),
                    "tags": task_tags_map.get(task.id, []),
                    "recurrence_rule": task.recurrence_rule,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
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

            # T024: Publish TaskCompletedEvent to task-recurrence topic
            try:
                event = TaskCompletedEvent(
                    user_id=int(user_id) if user_id.isdigit() else hash(user_id),
                    task_id=task.id,
                    recurrence_rule=task.recurrence_rule,
                    completed_at=datetime.now(UTC),
                )
                await kafka_producer.publish_event(
                    topic="task-recurrence", event=event, key=str(task.id)
                )
                logger.info(f"Published TaskCompletedEvent for task {task.id}")
            except Exception as e:
                logger.error(f"Failed to publish TaskCompletedEvent for task {task.id}: {e}")
                # Continue - event publishing is non-blocking

            # Force session sync to ensure write visibility for subsequent reads
            await force_session_sync(session)

            return {
                "status": "completed",
                "task_id": task.id,
                "title": task.title,
                "completed": task.completed,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
            }

    except Exception as e:
        logger.error(f"complete_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to complete task: {str(e)}",
        }


@mcp.tool(name="get_task", description="Retrieve a single task by ID with full details")
async def get_task(user_id: str, task_id: int) -> dict[str, Any]:
    """
    Retrieve a single task by ID with full details including category and tags.

    Args:
        user_id: User ID from JWT token
        task_id: Task ID to retrieve

    Returns:
        dict: Task details with id, title, description, completed, priority, category, tags, due_date, etc.
    """
    try:
        async with async_session_maker() as session:
            # Get task using service
            task = await task_service.get_task_by_id(
                session=session, task_id=task_id, user_id=user_id
            )

            if not task:
                return {
                    "status": "error",
                    "message": f"Task not found: {task_id}",
                    "code": "NOT_FOUND",
                }

            # Fetch category details if present
            category_data = None
            if task.category_id:
                category = await session.get(Category, task.category_id)
                if category:
                    category_data = {
                        "id": category.id,
                        "name": category.name,
                        "color": category.color,
                    }

            # Fetch tags
            from app.models.tag import TagPhaseV
            from app.models.task_tag import TaskTags

            result = await session.execute(
                select(TaskTags).where(TaskTags.task_id == task_id)
            )
            task_tag_assocs = result.scalars().all()

            tags = []
            if task_tag_assocs:
                tag_ids = [assoc.tag_id for assoc in task_tag_assocs]
                result = await session.execute(select(TagPhaseV).where(TagPhaseV.id.in_(tag_ids)))
                tag_objects = result.scalars().all()
                tags = [{"id": tag.id, "name": tag.name, "color": tag.color} for tag in tag_objects]

            return {
                "status": "success",
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "category": category_data,
                "tags": tags,
                "recurrence_rule": task.recurrence_rule,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }

    except Exception as e:
        logger.error(f"get_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to retrieve task: {str(e)}",
            "code": "INTERNAL_ERROR",
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
            task_id_for_event = task.id  # Store before deletion
            await session.delete(task)
            await session.commit()

            logger.info(f"Task deleted: user={user_id}, task_id={task_id}")

            # T026: Publish TaskDeletedEvent to task-events topic
            try:
                event = TaskDeletedEvent(
                    user_id=int(user_id) if user_id.isdigit() else hash(user_id),
                    task_id=task_id_for_event,
                )
                await kafka_producer.publish_event(
                    topic="task-events", event=event, key=str(task_id_for_event)
                )
                logger.info(f"Published TaskDeletedEvent for task {task_id_for_event}")
            except Exception as e:
                logger.error(f"Failed to publish TaskDeletedEvent for task {task_id_for_event}: {e}")
                # Continue - event publishing is non-blocking

            # Force session sync to ensure write visibility for subsequent reads
            await force_session_sync(session)

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


@mcp.tool(name="update_task", description="Update task fields")
async def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    due_date: str | None = None,
    recurrence_rule: str | None = None,
) -> dict[str, Any]:
    """
    Update task fields including title, description, status, priority, category, due date, and recurrence.

    Args:
        user_id: User ID from JWT token
        task_id: Task ID to update
        title: Optional new title
        description: Optional new description
        completed: Optional new completed status
        priority: Optional new priority (low, medium, high, urgent)
        category_id: Optional new category ID (set to None to remove category)
        due_date: Optional new due date in ISO 8601 format (set to empty string "" to remove)
        recurrence_rule: Optional iCalendar RRULE for recurring tasks (set to empty string "" to remove)
            Examples:
            - "FREQ=DAILY" - Every day
            - "FREQ=WEEKLY;BYDAY=MO,WE,FR" - Every Monday, Wednesday, Friday
            - "FREQ=MONTHLY;BYMONTHDAY=15" - 15th of every month
            - "" - Remove recurrence

    Returns:
        dict: Updated task with all Phase V fields
    """
    try:
        # Validate at least one field provided
        if all(
            v is None
            for v in [
                title,
                description,
                completed,
                priority,
                category_id,
                due_date,
                recurrence_rule,
            ]
        ):
            return {
                "status": "error",
                "message": "Must provide at least one field to update (title, description, completed, priority, category_id, due_date, recurrence_rule)",
                "code": "INVALID_REQUEST",
            }

        # Validate priority if provided
        priority_enum = None
        if priority:
            is_valid, error, priority_enum = task_service.validate_priority(priority)
            if not is_valid:
                return {
                    "status": "error",
                    "message": error,
                    "code": "INVALID_PRIORITY",
                }

        # Parse and convert due_date to UTC if provided
        due_date_utc = None
        update_due_date = False
        if due_date is not None:
            update_due_date = True
            if due_date == "":
                # Empty string means remove due_date
                due_date_utc = None
            else:
                try:
                    from datetime import datetime

                    dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    # Convert to UTC and make naive (as per data model)
                    if dt.tzinfo is not None:
                        due_date_utc = dt.astimezone(UTC).replace(tzinfo=None)
                    else:
                        due_date_utc = dt
                except (ValueError, AttributeError) as e:
                    return {
                        "status": "error",
                        "message": f"Invalid due_date format. Use ISO 8601 (e.g., 2025-01-15T17:00:00-05:00) or empty string to remove: {str(e)}",
                        "code": "INVALID_DUE_DATE",
                    }

        # Handle recurrence_rule (empty string means remove)
        recurrence_rule_value = None
        update_recurrence = False
        if recurrence_rule is not None:
            update_recurrence = True
            if recurrence_rule == "":
                recurrence_rule_value = None
            else:
                # T025: Validate recurrence_rule against whitelist
                is_valid, error_message = validate_rrule(recurrence_rule)
                if not is_valid:
                    return {
                        "status": "error",
                        "message": error_message,
                        "code": "INVALID_RECURRENCE_RULE",
                    }
                recurrence_rule_value = recurrence_rule

        async with async_session_maker() as session:
            # Get task with validation
            task = await task_service.get_task_by_id(session, task_id, user_id)

            if not task:
                # Enhanced error with task list suggestion
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

            # Update task using service
            task = await task_service.update_task(
                session=session,
                task=task,
                title=title,
                description=description,
                completed=completed,
                priority=priority_enum,
                category_id=category_id,
                due_date=due_date_utc if update_due_date else None,
                recurrence_rule=recurrence_rule_value if update_recurrence else None,
            )

            # Get category details if assigned
            category = None
            if task.category_id:
                category = await category_service.get_category_by_id(
                    session, task.category_id, user_id
                )

            logger.info(f"Task updated: user={user_id}, task_id={task_id}")

            # T025: Publish TaskUpdatedEvent to task-events topic
            try:
                # Build updated_fields dictionary
                updated_fields = {}
                if title is not None:
                    updated_fields["title"] = title
                if description is not None:
                    updated_fields["description"] = description
                if completed is not None:
                    updated_fields["completed"] = completed
                if priority is not None:
                    updated_fields["priority"] = priority
                if category_id is not None:
                    updated_fields["category_id"] = category_id
                if update_due_date:
                    updated_fields["due_date"] = task.due_date.isoformat() if task.due_date else None
                if update_recurrence:
                    updated_fields["recurrence_rule"] = task.recurrence_rule

                event = TaskUpdatedEvent(
                    user_id=int(user_id) if user_id.isdigit() else hash(user_id),
                    task_id=task.id,
                    updated_fields=updated_fields,
                )
                await kafka_producer.publish_event(
                    topic="task-events", event=event, key=str(task.id)
                )
                logger.info(f"Published TaskUpdatedEvent for task {task.id}")
            except Exception as e:
                logger.error(f"Failed to publish TaskUpdatedEvent for task {task.id}: {e}")
                # Continue - event publishing is non-blocking

            # Force session sync to ensure write visibility for subsequent reads
            await force_session_sync(session)

            return {
                "status": "updated",
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "category": (
                    {
                        "id": category.id,
                        "name": category.name,
                        "color": category.color,
                    }
                    if category
                    else None
                ),
                "recurrence_rule": task.recurrence_rule,
                "updated_at": task.updated_at.isoformat(),
            }

    except ValueError as e:
        logger.error(f"update_task validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "code": "VALIDATION_ERROR",
        }
    except Exception as e:
        logger.error(f"update_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to update task: {str(e)}",
        }


# ==============================================================================
# Category Management Tools (User Story 2)
# ==============================================================================

from app.services import category_service, search_service, tag_service


@mcp.tool(name="create_category", description="Create a new category for organizing tasks")
async def create_category(user_id: str, name: str, color: str | None = None) -> dict[str, Any]:
    """
    Create a new category for organizing tasks.

    Args:
        user_id: User ID from JWT token
        name: Category name (1-50 characters, unique per user, case-sensitive)
        color: Optional hex color code (e.g., #FF5733)

    Returns:
        dict: Created category with id, name, color, and created_at
    """
    try:
        async with async_session_maker() as session:
            category = await category_service.create_category(
                session=session, user_id=user_id, name=name, color=color
            )

            return {
                "status": "created",
                "category_id": category.id,
                "name": category.name,
                "color": category.color,
                "created_at": category.created_at.isoformat(),
            }

    except ValueError as e:
        logger.error(f"create_category validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "code": "VALIDATION_ERROR",
        }
    except Exception as e:
        logger.error(f"create_category error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to create category: {str(e)}",
        }


@mcp.tool(name="list_categories", description="List all categories with task counts")
async def list_categories(user_id: str) -> list[dict[str, Any]]:
    """
    List all categories for the user with task counts.

    Args:
        user_id: User ID from JWT token

    Returns:
        list: Array of categories with id, name, color, created_at, and task_count
    """
    try:
        async with async_session_maker() as session:
            categories = await category_service.list_categories(session=session, user_id=user_id)

            return [
                {
                    "id": cat["id"],
                    "name": cat["name"],
                    "color": cat["color"],
                    "task_count": cat["task_count"],
                    "created_at": cat["created_at"].isoformat(),
                }
                for cat in categories
            ]

    except Exception as e:
        logger.error(f"list_categories error: {str(e)}")
        return []


@mcp.tool(name="update_category", description="Update category name and/or color")
async def update_category(
    user_id: str, category_id: int, name: str | None = None, color: str | None = None
) -> dict[str, Any]:
    """
    Update category name and/or color.

    Args:
        user_id: User ID from JWT token
        category_id: Category ID to update
        name: Optional new name
        color: Optional new color (hex format)

    Returns:
        dict: Updated category
    """
    try:
        if name is None and color is None:
            return {
                "status": "error",
                "message": "Must provide name or color to update",
                "code": "INVALID_REQUEST",
            }

        async with async_session_maker() as session:
            # Get category with validation
            category = await category_service.get_category_by_id(session, category_id, user_id)

            if not category:
                return {
                    "status": "error",
                    "message": f"Category #{category_id} not found",
                    "code": "CATEGORY_NOT_FOUND",
                }

            # Update category using service
            category = await category_service.update_category(
                session=session, category=category, name=name, color=color
            )

            logger.info(f"Category updated: user={user_id}, category_id={category_id}")

            return {
                "status": "updated",
                "category_id": category.id,
                "name": category.name,
                "color": category.color,
            }

    except ValueError as e:
        logger.error(f"update_category validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "code": "VALIDATION_ERROR",
        }
    except Exception as e:
        logger.error(f"update_category error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to update category: {str(e)}",
        }


@mcp.tool(name="delete_category", description="Delete a category (tasks remain)")
async def delete_category(user_id: str, category_id: int) -> dict[str, Any]:
    """
    Delete a category. Tasks assigned to this category remain but lose their category assignment.

    Args:
        user_id: User ID from JWT token
        category_id: Category ID to delete

    Returns:
        dict: Deletion status with tasks_affected count
    """
    try:
        async with async_session_maker() as session:
            # Get category with validation
            category = await category_service.get_category_by_id(session, category_id, user_id)

            if not category:
                return {
                    "status": "error",
                    "message": f"Category #{category_id} not found",
                    "code": "CATEGORY_NOT_FOUND",
                }

            # Delete category using service
            result = await category_service.delete_category(session=session, category=category)

            logger.info(f"Category deleted: user={user_id}, category_id={category_id}")

            return {
                "status": "deleted",
                "category_id": result["category_id"],
                "name": result["name"],
                "tasks_affected": result["tasks_affected"],
            }

    except Exception as e:
        logger.error(f"delete_category error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to delete category: {str(e)}",
        }


# ==============================================================================
# Tag Management Tools (User Story 3)
# ==============================================================================


@mcp.tool(name="create_tag", description="Create a new tag for flexible task organization")
async def create_tag(user_id: str, name: str, color: str | None = None) -> dict[str, Any]:
    """
    Create a new tag for flexible task organization.

    Args:
        user_id: User ID from JWT token
        name: Tag name (1-30 characters, unique per user, case-sensitive)
        color: Optional hex color code (e.g., #FF0000)

    Returns:
        dict: Created tag with id, name, color, and created_at
    """
    try:
        async with async_session_maker() as session:
            tag = await tag_service.create_tag(
                session=session, user_id=user_id, name=name, color=color
            )

            return {
                "status": "created",
                "tag_id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at.isoformat(),
            }

    except ValueError as e:
        logger.error(f"create_tag validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "code": "VALIDATION_ERROR",
        }
    except Exception as e:
        logger.error(f"create_tag error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to create tag: {str(e)}",
        }


@mcp.tool(name="list_tags", description="List all tags with task counts")
async def list_tags(user_id: str) -> list[dict[str, Any]]:
    """
    List all tags for the user with task counts.

    Args:
        user_id: User ID from JWT token

    Returns:
        list: Array of tags with id, name, color, created_at, and task_count
    """
    try:
        async with async_session_maker() as session:
            tags = await tag_service.list_tags(session=session, user_id=user_id)

            return [
                {
                    "id": tag_data["id"],
                    "name": tag_data["name"],
                    "color": tag_data["color"],
                    "task_count": tag_data["task_count"],
                    "created_at": tag_data["created_at"].isoformat(),
                }
                for tag_data in tags
            ]

    except Exception as e:
        logger.error(f"list_tags error: {str(e)}")
        return []


@mcp.tool(name="update_tag", description="Update tag name and/or color")
async def update_tag(
    user_id: str, tag_id: int, name: str | None = None, color: str | None = None
) -> dict[str, Any]:
    """
    Update tag name and/or color.

    Args:
        user_id: User ID from JWT token
        tag_id: Tag ID to update
        name: Optional new name
        color: Optional new color (hex format)

    Returns:
        dict: Updated tag
    """
    try:
        if name is None and color is None:
            return {
                "status": "error",
                "message": "Must provide name or color to update",
                "code": "INVALID_REQUEST",
            }

        async with async_session_maker() as session:
            # Get tag with validation
            tag = await tag_service.get_tag_by_id(session, tag_id, user_id)

            if not tag:
                return {
                    "status": "error",
                    "message": f"Tag #{tag_id} not found",
                    "code": "TAG_NOT_FOUND",
                }

            # Update tag using service
            tag = await tag_service.update_tag(session=session, tag=tag, name=name, color=color)

            logger.info(f"Tag updated: user={user_id}, tag_id={tag_id}")

            return {
                "status": "updated",
                "tag_id": tag.id,
                "name": tag.name,
                "color": tag.color,
            }

    except ValueError as e:
        logger.error(f"update_tag validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "code": "VALIDATION_ERROR",
        }
    except Exception as e:
        logger.error(f"update_tag error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to update tag: {str(e)}",
        }


@mcp.tool(name="delete_tag", description="Delete a tag (removes from all tasks)")
async def delete_tag(user_id: str, tag_id: int) -> dict[str, Any]:
    """
    Delete a tag. Removes the tag from all tasks it was applied to.

    Args:
        user_id: User ID from JWT token
        tag_id: Tag ID to delete

    Returns:
        dict: Deletion status with tasks_affected count
    """
    try:
        async with async_session_maker() as session:
            # Get tag with validation
            tag = await tag_service.get_tag_by_id(session, tag_id, user_id)

            if not tag:
                return {
                    "status": "error",
                    "message": f"Tag #{tag_id} not found",
                    "code": "TAG_NOT_FOUND",
                }

            # Delete tag using service
            result = await tag_service.delete_tag(session=session, tag=tag)

            logger.info(f"Tag deleted: user={user_id}, tag_id={tag_id}")

            return {
                "status": "deleted",
                "tag_id": result["tag_id"],
                "name": result["name"],
                "tasks_affected": result["tasks_affected"],
            }

    except Exception as e:
        logger.error(f"delete_tag error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to delete tag: {str(e)}",
        }


@mcp.tool(name="add_tag_to_task", description="Add a tag to a task")
async def add_tag_to_task(user_id: str, task_id: int, tag_id: int) -> dict[str, Any]:
    """
    Add a tag to a task (idempotent - returns success if already assigned).

    Args:
        user_id: User ID from JWT token
        task_id: Task ID
        tag_id: Tag ID to add

    Returns:
        dict: Status indicating if tag was added or already assigned
    """
    try:
        async with async_session_maker() as session:
            result = await tag_service.add_tag_to_task(
                session=session, task_id=task_id, tag_id=tag_id, user_id=user_id
            )

            return result

    except ValueError as e:
        logger.error(f"add_tag_to_task validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "code": "VALIDATION_ERROR",
        }
    except Exception as e:
        logger.error(f"add_tag_to_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to add tag to task: {str(e)}",
        }


@mcp.tool(name="remove_tag_from_task", description="Remove a tag from a task")
async def remove_tag_from_task(user_id: str, task_id: int, tag_id: int) -> dict[str, Any]:
    """
    Remove a tag from a task (idempotent - returns success if not assigned).

    Args:
        user_id: User ID from JWT token
        task_id: Task ID
        tag_id: Tag ID to remove

    Returns:
        dict: Status indicating if tag was removed or not assigned
    """
    try:
        async with async_session_maker() as session:
            result = await tag_service.remove_tag_from_task(
                session=session, task_id=task_id, tag_id=tag_id, user_id=user_id
            )

            return result

    except ValueError as e:
        logger.error(f"remove_tag_from_task validation error: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "code": "VALIDATION_ERROR",
        }
    except Exception as e:
        logger.error(f"remove_tag_from_task error: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to remove tag from task: {str(e)}",
        }


# ==============================================================================
# Search Tools (User Story 5)
# ==============================================================================


@mcp.tool(name="search_tasks", description="Search tasks by keyword using full-text search")
async def search_tasks(user_id: str, query: str, limit: int = 50) -> list[dict[str, Any]]:
    """
    Search tasks by keyword using PostgreSQL full-text search with relevance ranking.

    Args:
        user_id: User ID from JWT token
        query: Search query (searches in title and description)
        limit: Maximum number of results (default: 50, max: 100)

    Returns:
        list: Array of tasks ranked by relevance with search_rank score
    """
    try:
        # Validate search query
        is_valid, error = search_service.validate_search_query(query)
        if not is_valid:
            return []

        async with async_session_maker() as session:
            # Search using service
            tasks = await search_service.search_tasks(
                session=session, user_id=user_id, query=query, limit=limit
            )

            # Build category map for efficient lookup
            category_ids = {task.category_id for task in tasks if task.category_id}
            category_map = {}
            if category_ids:
                result = await session.execute(
                    select(Category).where(Category.id.in_(category_ids))
                )
                categories = result.scalars().all()
                category_map = {cat.id: cat for cat in categories}

            # Build tag map for efficient lookup
            from app.models.tag import TagPhaseV
            from app.models.task_tag import TaskTags

            task_ids = [task.id for task in tasks]
            task_tags_map = {}
            if task_ids:
                # Get all task-tag associations
                result = await session.execute(
                    select(TaskTags).where(TaskTags.task_id.in_(task_ids))
                )
                task_tag_assocs = result.scalars().all()

                # Get all unique tag IDs
                tag_id_set = {assoc.tag_id for assoc in task_tag_assocs}

                # Fetch tag details
                tag_map = {}
                if tag_id_set:
                    result = await session.execute(
                        select(TagPhaseV).where(TagPhaseV.id.in_(tag_id_set))
                    )
                    tags_list = result.scalars().all()
                    tag_map = {tag.id: tag for tag in tags_list}

                # Build task -> tags mapping
                for assoc in task_tag_assocs:
                    if assoc.task_id not in task_tags_map:
                        task_tags_map[assoc.task_id] = []
                    if assoc.tag_id in tag_map:
                        tag = tag_map[assoc.tag_id]
                        task_tags_map[assoc.task_id].append(
                            {"id": tag.id, "name": tag.name, "color": tag.color}
                        )

            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "category": (
                        {
                            "id": category_map[task.category_id].id,
                            "name": category_map[task.category_id].name,
                            "color": category_map[task.category_id].color,
                        }
                        if task.category_id and task.category_id in category_map
                        else None
                    ),
                    "tags": task_tags_map.get(task.id, []),
                    "recurrence_rule": task.recurrence_rule,
                    "search_rank": task.search_rank,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
                for task in tasks
            ]

    except Exception as e:
        logger.error(f"search_tasks error: {str(e)}")
        return []


# ============================================================================
# TOOL 18: SET REMINDER
# ============================================================================


@mcp.tool(
    name="set_reminder",
    description="""Set a reminder for a task.

TIME EXPRESSION PARSING (CRITICAL):
Convert natural language time expressions to minutes before due date:
  - "one day before" → remind_before_minutes = 1440 (1 × 24 × 60)
  - "2 hours before" → remind_before_minutes = 120 (2 × 60)
  - "30 minutes before" → remind_before_minutes = 30
  - "one week before" → remind_before_minutes = 10080 (7 × 24 × 60)
  - "48 hours before" → remind_before_minutes = 2880 (48 × 60)

CALCULATION RULES:
  - Days: X × 24 × 60 minutes
  - Hours: X × 60 minutes
  - Weeks: X × 7 × 24 × 60 minutes
  - Minutes: X (no conversion needed)

Extract the number and unit from user input, then calculate minutes.
ALWAYS use remind_before_minutes for relative times like "X days before".
"""
)
async def set_reminder(
    user_id: str,
    task_id: int,
    remind_before_minutes: int | None = None,
    remind_at: str | None = None,
) -> dict[str, Any]:
    """
    Configure a reminder for a task.

    CRITICAL: You must convert natural language time expressions to minutes!

    Use remind_before_minutes for relative times ("X hours/days before due date")
    Use remind_at for absolute times ("remind me on January 5th at 2pm")

    Args:
        user_id: User ID (for authorization) - ALWAYS pass this!
        task_id: Task ID to set reminder for

        remind_before_minutes: Minutes before due_date to send reminder (mutually exclusive with remind_at)
            PARSE FROM NATURAL LANGUAGE:
            - "one day before" → 1440 (1 day = 24 hours = 1440 minutes)
            - "2 hours before" → 120 (2 hours = 120 minutes)
            - "30 minutes before" → 30
            - "one week before" → 10080 (7 × 24 × 60 = 10080 minutes)

            Formula: [number] × [unit multiplier]
            - minutes: ×1
            - hours: ×60
            - days: ×1440 (24 × 60)
            - weeks: ×10080 (7 × 24 × 60)

            Examples: 120 (2 hours), 1440 (1 day), 2880 (2 days), 10080 (1 week)

        remind_at: Specific reminder time in ISO 8601 format (mutually exclusive with remind_before_minutes)
            Examples: "2026-01-03T14:00:00Z", "2026-01-05T09:00:00-05:00", "2026-01-03"

    Returns:
        Dictionary with success status, message, task_id, and calculated remind_at timestamp
        Example: {"success": True, "message": "Reminder set", "task_id": 123, "remind_at": "2026-01-04T21:59:59Z"}

    Raises:
        ValueError: If task not found, belongs to different user, or has no due_date
        ValueError: If both or neither parameters provided
        ValueError: If calculated reminder time would be in the past
    """
    logger.info(
        f"set_reminder called: user={user_id}, task_id={task_id}, "
        f"remind_before_minutes={remind_before_minutes}, remind_at={remind_at}"
    )

    # Validation: exactly one parameter must be provided
    if (remind_before_minutes is None) == (remind_at is None):
        return {
            "success": False,
            "message": "Must provide either remind_before_minutes OR remind_at (not both, not neither)",
            "task_id": task_id,
            "remind_at": None,
        }

    async with async_session_maker() as session:
        try:
            # Fetch the task
            task = await session.get(TaskPhaseIII, task_id)
            if not task:
                return {
                    "success": False,
                    "message": f"Task not found: {task_id}",
                    "task_id": task_id,
                    "remind_at": None,
                }

            # Check authorization
            if task.user_id != user_id:
                return {
                    "success": False,
                    "message": f"Task {task_id} belongs to different user",
                    "task_id": task_id,
                    "remind_at": None,
                }

            # Calculate remind_at based on input method
            calculated_remind_at = None

            if remind_at is not None:
                # Method 1: Parse ISO timestamp directly
                from datetime import datetime, time

                try:
                    dt = datetime.fromisoformat(remind_at.replace("Z", "+00:00"))

                    # If date-only (midnight time), default to current time on that date
                    # This prevents "in the past" errors for same-day reminders
                    if dt.time() == time(0, 0, 0):
                        now = datetime.now(UTC)
                        dt = dt.replace(hour=now.hour, minute=now.minute, second=now.second)
                        logger.info(
                            f"Date-only remind_at detected, using current time: {dt.isoformat()}"
                        )

                    # Convert to UTC and make naive (as per data model)
                    if dt.tzinfo is not None:
                        calculated_remind_at = dt.astimezone(UTC).replace(tzinfo=None)
                    else:
                        calculated_remind_at = dt
                except (ValueError, AttributeError) as e:
                    return {
                        "success": False,
                        "message": f"Invalid remind_at format. Use ISO 8601 (e.g., 2026-01-05T14:00:00Z or 2026-01-05): {str(e)}",
                        "task_id": task_id,
                        "remind_at": None,
                    }
            else:
                # Method 2: Use remind_before_minutes method
                # Validate reminder
                is_valid, error_msg = task_service.validate_reminder(task, remind_before_minutes)
                if not is_valid:
                    return {
                        "success": False,
                        "message": error_msg,
                        "task_id": task_id,
                        "remind_at": None,
                    }

                # Calculate remind_at
                calculated_remind_at = task_service.calculate_remind_at(
                    task.due_date, remind_before_minutes
                )

            # Final validation: remind_at must be in the future
            now = datetime.utcnow()
            if calculated_remind_at <= now:
                return {
                    "success": False,
                    "message": (
                        f"Reminder time would be in the past. "
                        f"Calculated: {calculated_remind_at.isoformat()}Z, "
                        f"Current time: {now.isoformat()}Z. "
                        f"Please choose a future time."
                    ),
                    "task_id": task_id,
                    "remind_at": None,
                }

            logger.info(
                f"Reminder validated: task_id={task_id}, due_date={task.due_date.isoformat() if task.due_date else 'None'}Z, "
                f"remind_at={calculated_remind_at.isoformat()}Z"
            )

            # Publish ReminderSentEvent to task-reminders topic (T006)
            try:
                # Convert user_id for event publishing
                if isinstance(user_id, str):
                    event_user_id = int(user_id) if user_id.isdigit() else hash(user_id)
                else:
                    event_user_id = user_id

                event = ReminderSentEvent(
                    user_id=event_user_id,
                    task_id=task_id,
                    task_title=task.title,
                    task_due_date=task.due_date,
                    reminder_time=calculated_remind_at,
                )
                await kafka_producer.publish_event("task-reminders", event, wait=False)
                logger.info(
                    f"Queued ReminderSentEvent for task_id={task_id}, "
                    f"remind_at={calculated_remind_at.isoformat()}Z"
                )
            except Exception as e:
                logger.error(f"Failed to publish ReminderSentEvent for task_id={task_id}: {e}")
                # Don't fail the request if event publishing fails

            return {
                "success": True,
                "message": f"Reminder configured for task '{task.title}' and queued for processing",
                "task_id": task_id,
                "remind_at": f"{calculated_remind_at.isoformat()}Z",
            }

        except ValueError as e:
            logger.warning(f"set_reminder validation error: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "task_id": task_id,
                "remind_at": None,
            }
        except Exception as e:
            logger.error(f"set_reminder error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to set reminder: {str(e)}",
                "task_id": task_id,
                "remind_at": None,
            }


# Log tools registered
logger.info(
    "✅ MCP tools registered: add_task, list_tasks, complete_task, get_task, delete_task, update_task, "
    "create_category, list_categories, update_category, delete_category, "
    "create_tag, list_tags, update_tag, delete_tag, add_tag_to_task, remove_tag_from_task, "
    "search_tasks, set_reminder"
)
logger.info(
    f"📊 Total tools in mcp instance: {len(mcp._tools) if hasattr(mcp, '_tools') else 'unknown'}"
)
