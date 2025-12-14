"""Service layer for task management operations."""

from datetime import datetime, timezone
from math import ceil
from typing import List, Optional
import hashlib
import json

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.timezone_utils import get_utc_now
from sqlalchemy.orm import selectinload

from src.core.exceptions import (
    InvalidCategoryValueException,
    InvalidPaginationException,
    InvalidSortFieldException,
    InvalidStatusException,
    TagNotFoundException,
    TaskNotFoundException,
)
from src.core.cache import RedisCache, get_ttl
from src.services.category_service import validate_category_value
from src.models.tag import Tag
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskPartialUpdate, TaskUpdate

# Initialize cache (in production, this should be injected via dependency injection)
try:
    cache = RedisCache()
except Exception:
    # If Redis is not available, disable caching
    cache = None


def _generate_cache_key(user_id: str, **kwargs) -> str:
    """Generate a cache key for task queries.

    Args:
        user_id: User ID
        **kwargs: Query parameters (page, limit, status, priority, tag, q, sort)

    Returns:
        Cache key string
    """
    # Sort kwargs to ensure consistent key generation
    sorted_params = sorted(kwargs.items())
    params_str = json.dumps(sorted_params, sort_keys=True)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
    return f"tasks:{user_id}:{params_hash}"


async def _invalidate_user_task_cache(user_id: str):
    """Invalidate all task caches for a user.

    Called when tasks are created, updated, or deleted.

    Args:
        user_id: User ID whose cache should be invalidated
    """
    if cache:
        try:
            # In a real implementation, we'd use SCAN and DELETE with pattern matching
            # For now, we'll use a simplified approach
            await cache.delete_pattern(f"tasks:{user_id}:*")
        except Exception:
            # Silently fail - caching is not critical
            pass


async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: str) -> Task:
    """Create a new task for the authenticated user.

    Args:
        db: Database session
        task_data: Task creation data
        user_id: ID of the authenticated user

    Returns:
        Created task with user_id assigned

    Raises:
        InvalidCategoryValueException: If priority or status doesn't match user's categories

    """
    # Validate priority against user's priority categories
    is_valid_priority = await validate_category_value(
        db, user_id, "priority", task_data.priority
    )
    if not is_valid_priority:
        raise InvalidCategoryValueException("priority", task_data.priority)

    # Validate status against user's status categories
    is_valid_status = await validate_category_value(
        db, user_id, "status", task_data.status
    )
    if not is_valid_status:
        raise InvalidCategoryValueException("status", task_data.status)

    # Derive completed field from status
    completed = task_data.status == "completed"

    task = Task(
        **task_data.model_dump(exclude={"completed"}),
        completed=completed,
        user_id=user_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task, ["tags", "reminders"])

    # Invalidate cache for this user (FR-013)
    await _invalidate_user_task_cache(user_id)

    return task


async def get_tasks(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = "all",
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    sort: Optional[str] = None,
) -> tuple[List[Task], int]:
    """Get paginated list of tasks for the authenticated user with filtering and sorting.

    Args:
        db: Database session
        user_id: ID of the authenticated user
        page: Page number (>= 1)
        limit: Items per page (1-100, capped at 100)
        status: Filter by status: 'all', 'pending', 'completed'
        priority: Filter by priority: 'low', 'medium', 'high'
        tag: Filter by tag ID (integer) or tag name (string)
        q: Full-text search query for title and description
        sort: Sort field with optional '-' prefix for descending order

    Returns:
        Tuple of (list of tasks, total count)

    Raises:
        InvalidPaginationException: If pagination parameters are invalid
        InvalidStatusException: If status value is invalid
        InvalidSortFieldException: If sort field is invalid

    """
    # Validate pagination
    if page < 1 or limit < 1:
        raise InvalidPaginationException()
    if limit > 100:
        limit = 100

    # Validate status filter
    valid_status_values = ["all", "not_started", "pending", "in_progress", "completed"]
    if status not in valid_status_values:
        raise InvalidStatusException()

    # Check cache first (FR-013)
    cache_params = {
        "page": page,
        "limit": limit,
        "status": status,
        "priority": priority,
        "tag": tag,
        "q": q,
        "sort": sort,
    }
    cache_key = _generate_cache_key(user_id, **cache_params)

    if cache:
        try:
            cached_data = await cache.get(cache_key)
            if cached_data:
                # Return cached result
                return cached_data.get("tasks", []), cached_data.get("total", 0)
        except Exception:
            # If cache fails, continue with database query
            pass

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter using status field
    if status != "all":
        query = query.where(Task.status == status)

    # Apply priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # Apply tag filter
    if tag:
        # Try to parse as integer (tag ID)
        try:
            tag_id = int(tag)
            query = query.join(Task.tags).where(Tag.id == tag_id)
        except ValueError:
            # Treat as tag name
            query = query.join(Task.tags).where(Tag.name == tag)

    # Apply full-text search
    if q:
        search_filter = or_(
            Task.title.ilike(f"%{q}%"),
            Task.description.ilike(f"%{q}%"),
        )
        query = query.where(search_filter)

    # Apply sorting
    if sort:
        descending = sort.startswith("-")
        sort_field = sort[1:] if descending else sort

        # Validate sort field
        valid_sort_fields = ["due_date", "priority", "created_at", "title"]
        if sort_field not in valid_sort_fields:
            raise InvalidSortFieldException()

        # Apply sort
        if sort_field == "priority":
            # Custom sort for priority: high -> medium -> low
            priority_case = func.case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 3),
                else_=4,
            )
            if descending:
                query = query.order_by(desc(priority_case))
            else:
                query = query.order_by(priority_case)
        else:
            column = getattr(Task, sort_field)
            if descending:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(column)

    # Eager load tags and reminders to avoid N+1 queries (FR-012)
    query = query.options(
        selectinload(Task.tags),
        selectinload(Task.reminders)
    )

    # Performance optimization: Fetch limit+1 to check if there are more pages
    # This avoids the expensive COUNT query (saves 50-100ms per request)
    query = query.offset((page - 1) * limit).limit(limit + 1)

    # Execute query
    result = await db.execute(query)
    tasks = list(result.scalars().all())

    # Check if there are more pages
    has_more = len(tasks) > limit
    if has_more:
        tasks = tasks[:limit]  # Return only requested limit

    # Calculate total as best estimate (for backward compatibility)
    # Note: This is an estimate. For exact count, re-enable count query above.
    if has_more:
        # We know there's at least one more page
        total = (page * limit) + 1  # Minimum estimate
    else:
        # This is the last page
        total = ((page - 1) * limit) + len(tasks)

    # Cache the result (FR-013)
    if cache:
        try:
            cache_data = {"tasks": tasks, "total": total}
            ttl = get_ttl("user_tasks")
            await cache.set(cache_key, cache_data, ttl=ttl)
        except Exception:
            # Silently fail - caching is not critical
            pass

    return tasks, total


async def get_task_by_id(db: AsyncSession, task_id: int, user_id: str) -> Task:
    """Get a single task by ID, enforcing data isolation.

    Args:
        db: Database session
        task_id: Task ID
        user_id: ID of the authenticated user

    Returns:
        Task object

    Raises:
        TaskNotFoundException: If task not found or not owned by user

    """
    query = (
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
        .options(selectinload(Task.tags), selectinload(Task.reminders))
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundException()

    return task


async def update_task(
    db: AsyncSession, task_id: int, task_data: TaskUpdate, user_id: str
) -> Task:
    """Update a task (full update, PUT), enforcing data isolation.

    Args:
        db: Database session
        task_id: Task ID
        task_data: Task update data
        user_id: ID of the authenticated user

    Returns:
        Updated task

    Raises:
        TaskNotFoundException: If task not found or not owned by user
        InvalidCategoryValueException: If priority or status doesn't match user's categories

    """
    # Get task to update
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundException()

    # Validate priority against user's priority categories
    is_valid_priority = await validate_category_value(
        db, user_id, "priority", task_data.priority
    )
    if not is_valid_priority:
        raise InvalidCategoryValueException("priority", task_data.priority)

    # Validate status against user's status categories
    is_valid_status = await validate_category_value(
        db, user_id, "status", task_data.status
    )
    if not is_valid_status:
        raise InvalidCategoryValueException("status", task_data.status)

    # Update all fields except completed
    for field, value in task_data.model_dump(exclude={"completed"}).items():
        setattr(task, field, value)

    # Derive completed from status
    task.completed = task.status == "completed"
    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await db.commit()
    await db.refresh(task)

    # Re-query the task with relationships loaded for proper serialization
    query = (
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
        .options(selectinload(Task.tags), selectinload(Task.reminders))
    )
    result = await db.execute(query)
    task = result.scalar_one()

    # Invalidate cache for this user (FR-013)
    await _invalidate_user_task_cache(user_id)

    return task


async def partial_update_task(
    db: AsyncSession, task_id: int, task_data: TaskPartialUpdate, user_id: str
) -> Task:
    """Partially update a task (PATCH), enforcing data isolation.

    Args:
        db: Database session
        task_id: Task ID
        task_data: Partial task update data
        user_id: ID of the authenticated user

    Returns:
        Updated task

    Raises:
        TaskNotFoundException: If task not found or not owned by user
        InvalidCategoryValueException: If priority or status doesn't match user's categories

    """
    # Get task to update
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundException()

    # Get only provided fields, excluding completed
    update_data = task_data.model_dump(exclude_unset=True, exclude={"completed"})

    # Validate priority if provided
    if "priority" in update_data:
        is_valid_priority = await validate_category_value(
            db, user_id, "priority", update_data["priority"]
        )
        if not is_valid_priority:
            raise InvalidCategoryValueException("priority", update_data["priority"])

    # Validate status if provided
    if "status" in update_data:
        is_valid_status = await validate_category_value(
            db, user_id, "status", update_data["status"]
        )
        if not is_valid_status:
            raise InvalidCategoryValueException("status", update_data["status"])

    # Update provided fields
    for field, value in update_data.items():
        setattr(task, field, value)

    # Derive completed from status
    task.completed = task.status == "completed"
    task.updated_at = get_utc_now().replace(tzinfo=None)

    await db.commit()
    await db.refresh(task)

    # Re-query the task with relationships loaded for proper serialization
    query = (
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
        .options(selectinload(Task.tags), selectinload(Task.reminders))
    )
    result = await db.execute(query)
    task = result.scalar_one()

    # Invalidate cache for this user (FR-013)
    await _invalidate_user_task_cache(user_id)

    return task


async def delete_task(db: AsyncSession, task_id: int, user_id: str) -> None:
    """Delete a task, enforcing data isolation.

    Args:
        db: Database session
        task_id: Task ID
        user_id: ID of the authenticated user

    Raises:
        TaskNotFoundException: If task not found or not owned by user

    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Deleting task {task_id} for user {user_id}")
        task = await get_task_by_id(db, task_id, user_id)
        logger.info(f"Found task: {task.id}, {task.title}")

        await db.delete(task)
        logger.info("Task marked for deletion")

        await db.commit()
        logger.info("Transaction committed")

        # Invalidate cache for this user (FR-013)
        await _invalidate_user_task_cache(user_id)
        logger.info("Cache invalidated")

    except TaskNotFoundException:
        logger.error(f"Task {task_id} not found for user {user_id}")
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


async def associate_tag_with_task(
    db: AsyncSession, task_id: int, tag_id: int, user_id: str
) -> Task:
    """Associate a tag with a task (many-to-many relationship).

    Args:
        db: Database session
        task_id: Task ID
        tag_id: Tag ID
        user_id: ID of the authenticated user

    Returns:
        Updated task with tags loaded

    Raises:
        TaskNotFoundException: If task not found or not owned by user
        TagNotFoundException: If tag not found or not owned by user

    """
    # Verify task ownership
    # Use direct query with tags loaded to avoid refresh issues
    query = (
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
        .options(selectinload(Task.tags), selectinload(Task.reminders))
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundException()

    # Verify tag ownership
    tag_query = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
    tag_result = await db.execute(tag_query)
    tag = tag_result.scalar_one_or_none()

    if not tag:
        raise TagNotFoundException()

    # Check if already associated (idempotent)
    if tag not in task.tags:
        task.tags.append(tag)
        task.updated_at = get_utc_now().replace(tzinfo=None)
        await db.commit()

    # Re-query with eager loading to ensure tags are fully loaded for response
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
        .options(selectinload(Task.tags), selectinload(Task.reminders))
    )
    return result.scalar_one()


async def dissociate_tag_from_task(
    db: AsyncSession, task_id: int, tag_id: int, user_id: str
) -> None:
    """Dissociate a tag from a task (many-to-many relationship).

    Args:
        db: Database session
        task_id: Task ID
        tag_id: Tag ID
        user_id: ID of the authenticated user

    Raises:
        TaskNotFoundException: If task not found or not owned by user

    """
    # Verify task ownership
    # Use direct query with tags loaded to avoid refresh issues
    query = (
        select(Task)
        .where(Task.id == task_id, Task.user_id == user_id)
        .options(selectinload(Task.tags), selectinload(Task.reminders))
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundException()

    # Remove tag if associated (idempotent)
    task.tags = [t for t in task.tags if t.id != tag_id]
    task.updated_at = get_utc_now().replace(tzinfo=None)

    await db.commit()


async def reorder_tasks(
    db: AsyncSession, task_ids: List[int], user_id: str
) -> None:
    """Reorder tasks for a user (drag-and-drop functionality).

    Creates or updates TaskOrder records for each task to persist the user's
    preferred sort order.

    Args:
        db: Database session
        task_ids: List of task IDs in the desired order
        user_id: User ID

    Raises:
        TaskNotFoundException: If any task ID doesn't exist or doesn't belong to user

    **User Story 5 (P2)**: A visual thinker reorders tasks via drag-and-drop.
    **FR-022**: System MUST allow users to reorder tasks via drag-and-drop.
    **FR-023**: System MUST persist task order to server when reordered.
    """
    from src.models.task_order import TaskOrder

    # Verify all tasks belong to the user
    result = await db.execute(
        select(Task).where(Task.user_id == user_id, Task.id.in_(task_ids))
    )
    user_tasks = result.scalars().all()

    if len(user_tasks) != len(task_ids):
        raise TaskNotFoundException()

    # Delete existing task orders for these tasks
    await db.execute(
        select(TaskOrder)
        .where(TaskOrder.user_id == user_id, TaskOrder.task_id.in_(task_ids))
    )
    existing_orders = (await db.execute(
        select(TaskOrder)
        .where(TaskOrder.user_id == user_id, TaskOrder.task_id.in_(task_ids))
    )).scalars().all()

    for order in existing_orders:
        await db.delete(order)

    # Create new task orders with the specified sort positions
    for index, task_id in enumerate(task_ids):
        task_order = TaskOrder(
            task_id=task_id,
            user_id=user_id,
            sort_order=index,
        )
        db.add(task_order)

    await db.commit()

    # Invalidate cache for this user
    await _invalidate_user_task_cache(user_id)
