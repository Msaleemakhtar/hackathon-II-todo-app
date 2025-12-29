"""Tag service layer for Phase V flexible task organization."""

import logging
from typing import Any

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.tag import TagPhaseV
from app.models.task import TaskPhaseIII
from app.models.task_tag import TaskTags

logger = logging.getLogger(__name__)

MAX_TAGS_PER_USER = 100
MAX_TAGS_PER_TASK = 10


async def create_tag(
    session: AsyncSession, user_id: str, name: str, color: str | None = None
) -> TagPhaseV:
    """
    Create a new tag with validation.

    Args:
        session: Database session
        user_id: User ID from JWT
        name: Tag name (1-30 characters, unique per user)
        color: Optional hex color (#RRGGBB)

    Returns:
        Created tag instance

    Raises:
        ValueError: If validation fails or limit exceeded
    """
    # Check tag count limit
    result = await session.execute(
        select(func.count()).select_from(TagPhaseV).where(TagPhaseV.user_id == user_id)
    )
    count = result.scalar_one()

    if count >= MAX_TAGS_PER_USER:
        raise ValueError(
            f"Maximum {MAX_TAGS_PER_USER} tags reached. Delete unused tags to create new ones."
        )

    # Check for duplicate name (case-sensitive)
    result = await session.execute(
        select(TagPhaseV).where(TagPhaseV.user_id == user_id, TagPhaseV.name == name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise ValueError(f"Tag '{name}' already exists for this user")

    # Create tag
    tag = TagPhaseV(user_id=user_id, name=name, color=color)

    session.add(tag)
    await session.commit()
    await session.refresh(tag)

    logger.info(f"Tag created: user={user_id}, tag_id={tag.id}, name={name}")

    return tag


async def list_tags(session: AsyncSession, user_id: str) -> list[dict[str, Any]]:
    """
    List all tags for a user with task counts.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        List of tags with task counts
    """
    # Query tags with task counts using LEFT JOIN
    query = (
        select(
            TagPhaseV,
            func.count(TaskTags.task_id).label("task_count"),
        )
        .outerjoin(TaskTags, TagPhaseV.id == TaskTags.tag_id)
        .where(TagPhaseV.user_id == user_id)
        .group_by(TagPhaseV.id)
        .order_by(TagPhaseV.created_at.asc())
    )

    result = await session.execute(query)
    rows = result.all()

    tags = [
        {
            "id": tag.id,
            "user_id": tag.user_id,
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at,
            "task_count": task_count,
        }
        for tag, task_count in rows
    ]

    logger.info(f"list_tags: user={user_id}, count={len(tags)}")

    return tags


async def update_tag(
    session: AsyncSession, tag: TagPhaseV, name: str | None = None, color: str | None = None
) -> TagPhaseV:
    """
    Update an existing tag.

    Args:
        session: Database session
        tag: Tag to update
        name: Optional new name
        color: Optional new color

    Returns:
        Updated tag instance

    Raises:
        ValueError: If validation fails
    """
    # Update name if provided
    if name is not None:
        # Check for duplicate name (case-sensitive)
        result = await session.execute(
            select(TagPhaseV).where(
                TagPhaseV.user_id == tag.user_id, TagPhaseV.name == name, TagPhaseV.id != tag.id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(f"Tag '{name}' already exists for this user")

        tag.name = name

    # Update color if provided
    if color is not None:
        tag.color = color

    await session.commit()
    await session.refresh(tag)

    logger.info(f"Tag updated: tag_id={tag.id}, user={tag.user_id}")

    return tag


async def delete_tag(session: AsyncSession, tag: TagPhaseV) -> dict[str, Any]:
    """
    Delete a tag (removes all task-tag associations via ON DELETE CASCADE).

    Args:
        session: Database session
        tag: Tag to delete

    Returns:
        Dictionary with deletion info and affected task count
    """
    # Count tasks affected (will have tag removed from task_tags table)
    result = await session.execute(
        select(func.count()).select_from(TaskTags).where(TaskTags.tag_id == tag.id)
    )
    tasks_affected = result.scalar_one()

    tag_id = tag.id
    name = tag.name
    user_id = tag.user_id

    await session.delete(tag)
    await session.commit()

    logger.info(f"Tag deleted: user={user_id}, tag_id={tag_id}, tasks_affected={tasks_affected}")

    return {
        "tag_id": tag_id,
        "name": name,
        "tasks_affected": tasks_affected,
    }


async def add_tag_to_task(
    session: AsyncSession, task_id: int, tag_id: int, user_id: str
) -> dict[str, Any]:
    """
    Add a tag to a task with validation.

    Args:
        session: Database session
        task_id: Task ID
        tag_id: Tag ID
        user_id: User ID for validation

    Returns:
        Dictionary with success status

    Raises:
        ValueError: If validation fails or limit exceeded
    """
    # Verify task ownership
    task = await session.get(TaskPhaseIII, task_id)
    if not task or task.user_id != user_id:
        raise ValueError(f"Task #{task_id} not found")

    # Verify tag ownership
    tag = await session.get(TagPhaseV, tag_id)
    if not tag or tag.user_id != user_id:
        raise ValueError(f"Tag #{tag_id} not found")

    # Check tag count limit for this task
    result = await session.execute(
        select(func.count()).select_from(TaskTags).where(TaskTags.task_id == task_id)
    )
    tag_count = result.scalar_one()

    if tag_count >= MAX_TAGS_PER_TASK:
        raise ValueError(f"Maximum {MAX_TAGS_PER_TASK} tags per task exceeded")

    # Check if tag already assigned (idempotent)
    result = await session.execute(
        select(TaskTags).where(TaskTags.task_id == task_id, TaskTags.tag_id == tag_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Already assigned, return success (idempotent)
        logger.info(f"Tag already assigned: task_id={task_id}, tag_id={tag_id}")
        return {"status": "already_assigned", "task_id": task_id, "tag_id": tag_id}

    # Create association
    task_tag = TaskTags(task_id=task_id, tag_id=tag_id)
    session.add(task_tag)
    await session.commit()

    logger.info(f"Tag added to task: task_id={task_id}, tag_id={tag_id}")

    return {"status": "added", "task_id": task_id, "tag_id": tag_id}


async def remove_tag_from_task(
    session: AsyncSession, task_id: int, tag_id: int, user_id: str
) -> dict[str, Any]:
    """
    Remove a tag from a task.

    Args:
        session: Database session
        task_id: Task ID
        tag_id: Tag ID
        user_id: User ID for validation

    Returns:
        Dictionary with success status

    Raises:
        ValueError: If validation fails
    """
    # Verify task ownership
    task = await session.get(TaskPhaseIII, task_id)
    if not task or task.user_id != user_id:
        raise ValueError(f"Task #{task_id} not found")

    # Get association
    result = await session.execute(
        select(TaskTags).where(TaskTags.task_id == task_id, TaskTags.tag_id == tag_id)
    )
    task_tag = result.scalar_one_or_none()

    if not task_tag:
        # Not assigned, return success (idempotent)
        logger.info(f"Tag not assigned to task: task_id={task_id}, tag_id={tag_id}")
        return {"status": "not_assigned", "task_id": task_id, "tag_id": tag_id}

    # Remove association
    await session.delete(task_tag)
    await session.commit()

    logger.info(f"Tag removed from task: task_id={task_id}, tag_id={tag_id}")

    return {"status": "removed", "task_id": task_id, "tag_id": tag_id}


async def get_tag_by_id(session: AsyncSession, tag_id: int, user_id: str) -> TagPhaseV | None:
    """
    Get a tag by ID with user validation.

    Args:
        session: Database session
        tag_id: Tag ID
        user_id: User ID for validation

    Returns:
        Tag if found and owned by user, None otherwise
    """
    tag = await session.get(TagPhaseV, tag_id)
    if tag and tag.user_id == user_id:
        return tag
    return None
