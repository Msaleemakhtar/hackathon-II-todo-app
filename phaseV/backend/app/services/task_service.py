"""Task service layer for Phase V advanced task management."""

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.kafka.events import TaskCompletedEvent, TaskCreatedEvent, TaskUpdatedEvent
from app.kafka.producer import kafka_producer
from app.models.task import PriorityLevel, TaskPhaseIII
from app.utils.rrule_parser import validate_rrule

logger = logging.getLogger(__name__)


def validate_priority(priority: str) -> tuple[bool, str, PriorityLevel | None]:
    """
    Validate priority value.

    Args:
        priority: Priority string to validate

    Returns:
        Tuple of (is_valid, error_message, priority_enum)
    """
    try:
        priority_enum = PriorityLevel(priority.lower())
        return True, "", priority_enum
    except ValueError:
        valid_values = ", ".join([p.value for p in PriorityLevel])
        return (
            False,
            f"Priority must be one of: {valid_values}",
            None,
        )


def validate_task_title(title: str) -> tuple[bool, str]:
    """
    Validate task title.

    Args:
        title: Title to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    title = title.strip()
    if not title:
        return False, "Title cannot be empty"
    if len(title) > 200:
        return False, f"Title must be 200 characters or less (you provided {len(title)})"
    return True, ""


def validate_recurrence_rule(rule: str | None) -> tuple[bool, str]:
    """
    Validate recurrence rule using RRULE parser.

    Args:
        rule: RRULE string to validate (or None)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if rule is None or rule.strip() == "":
        return True, ""
    return validate_rrule(rule)


async def create_task(
    session: AsyncSession,
    user_id: str,
    title: str,
    description: str | None = None,
    priority: PriorityLevel = PriorityLevel.MEDIUM,
    due_date: datetime | None = None,
    category_id: int | None = None,
    recurrence_rule: str | None = None,
) -> TaskPhaseIII:
    """
    Create a new task with validation.

    Args:
        session: Database session
        user_id: User ID from JWT
        title: Task title
        description: Optional description
        priority: Task priority level
        due_date: Optional due date (UTC)
        category_id: Optional category ID
        recurrence_rule: Optional RRULE string

    Returns:
        Created task instance

    Raises:
        ValueError: If validation fails
    """
    # Validate title
    is_valid, error = validate_task_title(title)
    if not is_valid:
        raise ValueError(error)

    # Validate recurrence rule
    if recurrence_rule:
        is_valid, error = validate_recurrence_rule(recurrence_rule)
        if not is_valid:
            raise ValueError(error)

    # Create task
    task = TaskPhaseIII(
        user_id=user_id,
        title=title.strip(),
        description=description.strip() if description else None,
        priority=priority,
        due_date=due_date,
        category_id=category_id,
        recurrence_rule=recurrence_rule,
        completed=False,
        reminder_sent=False,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    logger.info(
        f"Task created: user={user_id}, task_id={task.id}, title={title}, priority={priority.value}"
    )

    # Publish TaskCreatedEvent to Kafka (T004)
    try:
        # Convert user_id: if numeric string, parse it; otherwise hash it
        if isinstance(user_id, str):
            event_user_id = int(user_id) if user_id.isdigit() else hash(user_id)
        else:
            event_user_id = user_id

        event = TaskCreatedEvent(
            user_id=event_user_id,
            task_id=task.id,
            title=task.title,
            description=task.description,
            priority=priority.value if priority else None,
            due_date=due_date,
            recurrence_rule=recurrence_rule,
            category_id=category_id,
        )
        await kafka_producer.publish_event("task-events", event, wait=False)
        logger.info(f"Queued TaskCreatedEvent for task_id={task.id}")
    except Exception as e:
        logger.error(f"Failed to publish TaskCreatedEvent for task_id={task.id}: {e}")
        # Don't fail the request if event publishing fails

    return task


async def update_task(
    session: AsyncSession,
    task: TaskPhaseIII,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None,
    priority: PriorityLevel | None = None,
    due_date: datetime | None = None,
    category_id: int | None = None,
    recurrence_rule: str | None = None,
) -> TaskPhaseIII:
    """
    Update an existing task.

    Args:
        session: Database session
        task: Task to update
        title: Optional new title
        description: Optional new description
        completed: Optional new completed status
        priority: Optional new priority
        due_date: Optional new due date
        category_id: Optional new category ID
        recurrence_rule: Optional new recurrence rule

    Returns:
        Updated task instance

    Raises:
        ValueError: If validation fails
    """
    # Validate and update title
    if title is not None:
        is_valid, error = validate_task_title(title)
        if not is_valid:
            raise ValueError(error)
        task.title = title.strip()

    # Update description
    if description is not None:
        task.description = description.strip() if description else None

    # Update completed status
    if completed is not None:
        task.completed = completed

    # Update priority
    if priority is not None:
        task.priority = priority

    # Update due date
    if due_date is not None:
        task.due_date = due_date

    # Update category
    if category_id is not None:
        task.category_id = category_id

    # Validate and update recurrence rule
    if recurrence_rule is not None:
        is_valid, error = validate_recurrence_rule(recurrence_rule)
        if not is_valid:
            raise ValueError(error)
        task.recurrence_rule = recurrence_rule

    # Track if task was marked as completed (for event publishing)
    was_completed = completed is not None and completed is True

    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)

    logger.info(f"Task updated: task_id={task.id}, user={task.user_id}")

    # Convert user_id for event publishing
    if isinstance(task.user_id, str):
        event_user_id = int(task.user_id) if task.user_id.isdigit() else hash(task.user_id)
    else:
        event_user_id = task.user_id

    # Publish TaskUpdatedEvent to Kafka (T005)
    try:
        event = TaskUpdatedEvent(
            user_id=event_user_id,
            task_id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority.value if task.priority else None,
            due_date=task.due_date,
            completed=task.completed,
            recurrence_rule=task.recurrence_rule,
            category_id=task.category_id,
        )
        await kafka_producer.publish_event("task-events", event, wait=False)
        logger.info(f"Queued TaskUpdatedEvent for task_id={task.id}")
    except Exception as e:
        logger.error(f"Failed to publish TaskUpdatedEvent for task_id={task.id}: {e}")

    # If task was marked completed and has recurrence rule, publish to task-recurrence topic (T027)
    if was_completed and task.recurrence_rule:
        try:
            completed_event = TaskCompletedEvent(
                user_id=event_user_id,
                task_id=task.id,
                recurrence_rule=task.recurrence_rule,
                completed_at=datetime.now(timezone.utc),
            )
            await kafka_producer.publish_event("task-recurrence", completed_event, wait=False)
            logger.info(
                f"Queued TaskCompletedEvent to task-recurrence for task_id={task.id} "
                f"(recurrence_rule={task.recurrence_rule})"
            )
        except Exception as e:
            logger.error(f"Failed to publish TaskCompletedEvent for task_id={task.id}: {e}")

    return task


async def get_task_by_id(session: AsyncSession, task_id: int, user_id: str) -> TaskPhaseIII | None:
    """
    Get a task by ID with user validation.

    Args:
        session: Database session
        task_id: Task ID
        user_id: User ID for validation

    Returns:
        Task if found and owned by user, None otherwise
    """
    task = await session.get(TaskPhaseIII, task_id)
    if task and task.user_id == user_id:
        return task
    return None


async def list_tasks(
    session: AsyncSession,
    user_id: str,
    status: str | None = None,
    priority: PriorityLevel | None = None,
    category_id: int | None = None,
) -> list[TaskPhaseIII]:
    """
    List tasks with optional filters.

    Args:
        session: Database session
        user_id: User ID
        status: Optional status filter ("pending", "completed", "all")
        priority: Optional priority filter
        category_id: Optional category filter

    Returns:
        List of tasks matching filters
    """
    query = select(TaskPhaseIII).where(TaskPhaseIII.user_id == user_id)

    # Apply status filter
    if status == "pending":
        query = query.where(TaskPhaseIII.completed.is_(False))
    elif status == "completed":
        query = query.where(TaskPhaseIII.completed.is_(True))

    # Apply priority filter
    if priority is not None:
        query = query.where(TaskPhaseIII.priority == priority)

    # Apply category filter
    if category_id is not None:
        query = query.where(TaskPhaseIII.category_id == category_id)

    # Order by created_at descending
    query = query.order_by(TaskPhaseIII.created_at.desc())

    result = await session.execute(query)
    tasks = result.scalars().all()

    logger.info(
        f"list_tasks: user={user_id}, status={status}, priority={priority}, count={len(tasks)}"
    )

    return list(tasks)


async def delete_task(session: AsyncSession, task: TaskPhaseIII) -> dict[str, Any]:
    """
    Delete a task.

    Args:
        session: Database session
        task: Task to delete

    Returns:
        Dictionary with deletion info
    """
    task_id = task.id
    title = task.title
    user_id = task.user_id

    await session.delete(task)
    await session.commit()

    logger.info(f"Task deleted: user={user_id}, task_id={task_id}")

    return {"task_id": task_id, "title": title}


def validate_reminder(task: TaskPhaseIII, remind_before_minutes: int) -> tuple[bool, str]:
    """
    Validate that a task can have a reminder set.

    Args:
        task: Task to validate
        remind_before_minutes: Minutes before due_date to send reminder

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if task has a due_date
    if task.due_date is None:
        return False, "Task must have a due_date to set a reminder"

    # Validate remind_before_minutes
    if remind_before_minutes <= 0:
        return False, "remind_before_minutes must be a positive integer"

    # Check that remind_at would be in the future
    from datetime import timedelta

    remind_at = task.due_date - timedelta(minutes=remind_before_minutes)
    now = datetime.utcnow()

    if remind_at <= now:
        return False, f"Reminder time would be in the past (remind_at: {remind_at.isoformat()}Z)"

    return True, ""


def calculate_remind_at(due_date: datetime, remind_before_minutes: int) -> datetime:
    """
    Calculate the remind_at timestamp.

    Args:
        due_date: Task due date
        remind_before_minutes: Minutes before due_date to send reminder

    Returns:
        Calculated remind_at datetime (UTC)
    """
    from datetime import timedelta

    return due_date - timedelta(minutes=remind_before_minutes)
