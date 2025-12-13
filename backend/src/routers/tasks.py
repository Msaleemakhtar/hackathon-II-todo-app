"""API router for task management endpoints using user_id in path."""

from datetime import datetime
from math import ceil
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import validate_path_user_id
from src.models.user import User
from src.schemas.task import (
    PaginatedTasks,
    TaskCreate,
    TaskPartialUpdate,
    TaskRead,
    TaskUpdate,
)
from src.services import task_service
from src.services.recurrence_service import RecurrenceService

router = APIRouter()


@router.get("/{user_id}/tasks", response_model=PaginatedTasks)
async def list_tasks(
    user_id: str,
    request: Request,
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    limit: int = Query(
        20, ge=1, le=100, description="Items per page (1-100, capped at 100)"
    ),
    status_filter: Optional[str] = Query(
        "all",
        alias="status",
        description="Filter tasks by status: 'all', 'pending', 'completed'",
    ),
    priority: Optional[str] = Query(
        None, description="Filter tasks by priority: 'low', 'medium', 'high'"
    ),
    tag: Optional[str] = Query(
        None, description="Filter by tag ID (integer) or tag name (string)"
    ),
    q: Optional[str] = Query(
        None, description="Full-text search on title and description"
    ),
    sort: Optional[str] = Query(
        None,
        description=(
            "Sort field: 'due_date', 'priority', 'created_at', 'title'. "
            "Prefix with '-' for descending (e.g., '-created_at')"
        ),
    ),
    db: AsyncSession = Depends(get_db),
):
    """List tasks with pagination, filtering, and sorting for a specific user.

    **User Story 2 (P1)**: An authenticated user views their list of tasks,
    with pagination.

    **User Story 13 (P2)**: An authenticated user filters and searches their
    task list.

    **User Story 14 (P2)**: An authenticated user sorts their task list by
    various fields.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    tasks, total = await task_service.get_tasks(
        db,
        current_user_id,  # Use the JWT user_id rather than the path parameter for security
        page=page,
        limit=limit,
        status=status_filter,
        priority=priority,
        tag=tag,
        q=q,
        sort=sort,
    )

    pages = ceil(total / limit) if total > 0 else 1

    return PaginatedTasks(
        items=tasks,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    request: Request,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new task for a specific user.

    **User Story 1 (P1)**: An authenticated user creates a new task, which is validated
    and associated with their user ID.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    task = await task_service.create_task(db, task_data, current_user_id)
    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get a single task by ID for a specific user.

    **User Story 3 (P1)**: An authenticated user views the details of a specific task.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    task = await task_service.get_task_by_id(db, task_id, current_user_id)
    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: int,
    request: Request,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a task (full update) for a specific user.

    **User Story 4 (P1)**: An authenticated user updates a task.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    task = await task_service.update_task(db, task_id, task_data, current_user_id)
    return task


@router.patch("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def partial_update_task(
    user_id: str,
    task_id: int,
    request: Request,
    task_data: TaskPartialUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partially update a task for a specific user.

    **User Story 5 (P1)**: An authenticated user marks a task as complete or incomplete.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    task = await task_service.partial_update_task(
        db, task_id, task_data, current_user_id
    )
    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete a task for a specific user.

    **User Story 6 (P1)**: An authenticated user deletes a task.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    await task_service.delete_task(db, task_id, current_user_id)


@router.post(
    "/{user_id}/tasks/{task_id}/tags/{tag_id}",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def associate_tag_with_task(
    user_id: str,
    task_id: int,
    tag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Associate a tag with a task for a specific user.

    **User Story 11 (P2)**: An authenticated user adds a tag to a task.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    task = await task_service.associate_tag_with_task(
        db, task_id, tag_id, current_user_id
    )
    return task


@router.delete("/{user_id}/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def dissociate_tag_from_task(
    user_id: str,
    task_id: int,
    tag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Dissociate a tag from a task for a specific user.

    **User Story 12 (P2)**: An authenticated user removes a tag from a task.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    await task_service.dissociate_tag_from_task(db, task_id, tag_id, current_user_id)


# Recurring task endpoints

@router.get(
    "/{user_id}/tasks/recurring/{task_id}/occurrences",
    response_model=List[TaskRead]
)
async def get_recurring_task_occurrences(
    user_id: str,
    task_id: int,
    request: Request,
    start_date: Optional[datetime] = Query(None, description="Start date for occurrences"),
    end_date: Optional[datetime] = Query(None, description="End date for occurrences"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all occurrences of a recurring task within a date range.

    Returns all instances of the recurring task, generating new ones if needed.
    """
    # Validate path user_id matches JWT
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Verify the task belongs to the user
    task = await task_service.get_task_by_id(db, task_id, current_user_id)
    if not task.recurrence_rule:
        raise ValueError("Task is not a recurring task")

    # Expand recurring task
    recurrence_service = RecurrenceService(db)
    instances = await recurrence_service.expand_recurring_task(
        task_id,
        start_date=start_date,
        end_date=end_date
    )

    return instances


@router.post(
    "/{user_id}/tasks/recurring/{task_id}/expand",
    response_model=List[TaskRead],
    status_code=status.HTTP_201_CREATED
)
async def expand_recurring_task(
    user_id: str,
    task_id: int,
    request: Request,
    start_date: Optional[datetime] = Query(None, description="Start date for expansion"),
    end_date: Optional[datetime] = Query(None, description="End date for expansion"),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger expansion of a recurring task.

    Generates task instances for the specified date range.
    """
    # Validate path user_id matches JWT
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Verify the task belongs to the user
    task = await task_service.get_task_by_id(db, task_id, current_user_id)

    # Expand the recurring task
    recurrence_service = RecurrenceService(db)
    instances = await recurrence_service.expand_recurring_task(
        task_id,
        start_date=start_date,
        end_date=end_date
    )

    return instances


@router.get(
    "/{user_id}/tasks/recurring/{task_id}/next",
    response_model=dict
)
async def get_next_occurrence(
    user_id: str,
    task_id: int,
    request: Request,
    after_date: Optional[datetime] = Query(None, description="Get next occurrence after this date"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the next occurrence date for a recurring task.
    """
    # Validate path user_id matches JWT
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Verify the task belongs to the user
    task = await task_service.get_task_by_id(db, task_id, current_user_id)

    # Get next occurrence
    recurrence_service = RecurrenceService(db)
    next_date = await recurrence_service.get_next_occurrence(task_id, after_date)

    return {"next_occurrence": next_date}


@router.patch(
    "/{user_id}/tasks/recurring/{task_id}/recurrence",
    response_model=TaskRead
)
async def update_recurrence_pattern(
    user_id: str,
    task_id: int,
    request: Request,
    rrule: str = Query(..., description="New RRULE string"),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the recurrence pattern of a recurring task.

    This will delete future uncompleted instances and regenerate them with the new pattern.
    """
    # Validate path user_id matches JWT
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Verify the task belongs to the user
    await task_service.get_task_by_id(db, task_id, current_user_id)

    # Update recurrence pattern
    recurrence_service = RecurrenceService(db)
    updated_task = await recurrence_service.update_recurrence_pattern(task_id, rrule)

    return updated_task


@router.delete(
    "/{user_id}/tasks/recurring/{task_id}/series",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_recurring_series(
    user_id: str,
    task_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a recurring task and all its instances.
    """
    # Validate path user_id matches JWT
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Verify the task belongs to the user
    await task_service.get_task_by_id(db, task_id, current_user_id)

    # Delete the series
    recurrence_service = RecurrenceService(db)
    await recurrence_service.delete_recurring_series(task_id)


@router.delete(
    "/{user_id}/tasks/recurring/instance/{instance_id}/following",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_instance_and_following(
    user_id: str,
    instance_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific instance and all following instances of a recurring task.
    """
    # Validate path user_id matches JWT
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Verify the instance belongs to the user
    await task_service.get_task_by_id(db, instance_id, current_user_id)

    # Delete instance and following
    recurrence_service = RecurrenceService(db)
    await recurrence_service.delete_instance_and_following(instance_id)
