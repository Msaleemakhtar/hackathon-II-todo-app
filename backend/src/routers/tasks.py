"""API router for task management endpoints."""

from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.user import User
from src.schemas.task import (
    PaginatedTasks,
    TaskCreate,
    TaskPartialUpdate,
    TaskRead,
    TaskUpdate,
)
from src.services import task_service

router = APIRouter()


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task.

    **User Story 1 (P1)**: An authenticated user creates a new task, which is validated
    and associated with their user ID.

    """
    task = await task_service.create_task(db, task_data, current_user.id)
    return task


@router.get("/", response_model=PaginatedTasks)
async def list_tasks(
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
    current_user: User = Depends(get_current_user),
):
    """List tasks with pagination, filtering, and sorting.

    **User Story 2 (P1)**: An authenticated user views their list of tasks,
    with pagination.

    **User Story 13 (P2)**: An authenticated user filters and searches their
    task list.

    **User Story 14 (P2)**: An authenticated user sorts their task list by
    various fields.

    """
    tasks, total = await task_service.get_tasks(
        db,
        current_user.id,
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


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single task by ID.

    **User Story 3 (P1)**: An authenticated user views the details of a specific task.

    """
    task = await task_service.get_task_by_id(db, task_id, current_user.id)
    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task (full update).

    **User Story 4 (P1)**: An authenticated user updates a task.

    """
    task = await task_service.update_task(db, task_id, task_data, current_user.id)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def partial_update_task(
    task_id: int,
    task_data: TaskPartialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partially update a task.

    **User Story 5 (P1)**: An authenticated user marks a task as complete or incomplete.

    """
    task = await task_service.partial_update_task(
        db, task_id, task_data, current_user.id
    )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task.

    **User Story 6 (P1)**: An authenticated user deletes a task.

    """
    await task_service.delete_task(db, task_id, current_user.id)


@router.post(
    "/{task_id}/tags/{tag_id}",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def associate_tag_with_task(
    task_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Associate a tag with a task.

    **User Story 11 (P2)**: An authenticated user adds a tag to a task.

    """
    task = await task_service.associate_tag_with_task(
        db, task_id, tag_id, current_user.id
    )
    return task


@router.delete("/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def dissociate_tag_from_task(
    task_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dissociate a tag from a task.

    **User Story 12 (P2)**: An authenticated user removes a tag from a task.

    """
    await task_service.dissociate_tag_from_task(db, task_id, tag_id, current_user.id)
