"""Category service layer for Phase V task organization."""

import logging
from typing import Any

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.category import Category
from app.models.task import TaskPhaseIII

logger = logging.getLogger(__name__)

MAX_CATEGORIES_PER_USER = 50


async def create_category(
    session: AsyncSession, user_id: str, name: str, color: str | None = None
) -> Category:
    """
    Create a new category with validation.

    Args:
        session: Database session
        user_id: User ID from JWT
        name: Category name (1-50 characters, unique per user)
        color: Optional hex color (#RRGGBB)

    Returns:
        Created category instance

    Raises:
        ValueError: If validation fails or limit exceeded
    """
    # Check category count limit
    result = await session.execute(
        select(func.count()).select_from(Category).where(Category.user_id == user_id)
    )
    count = result.scalar_one()

    if count >= MAX_CATEGORIES_PER_USER:
        raise ValueError(
            f"Maximum {MAX_CATEGORIES_PER_USER} categories reached. Delete unused categories to create new ones."
        )

    # Check for duplicate name (case-sensitive)
    result = await session.execute(
        select(Category).where(Category.user_id == user_id, Category.name == name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise ValueError(f"Category '{name}' already exists for this user")

    # Create category
    category = Category(user_id=user_id, name=name, color=color)

    session.add(category)
    await session.commit()
    await session.refresh(category)

    logger.info(f"Category created: user={user_id}, category_id={category.id}, name={name}")

    return category


async def list_categories(session: AsyncSession, user_id: str) -> list[dict[str, Any]]:
    """
    List all categories for a user with task counts.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        List of categories with task counts
    """
    # Query categories with task counts using LEFT JOIN
    query = (
        select(
            Category,
            func.count(TaskPhaseIII.id).label("task_count"),
        )
        .outerjoin(TaskPhaseIII, Category.id == TaskPhaseIII.category_id)
        .where(Category.user_id == user_id)
        .group_by(Category.id)
        .order_by(Category.created_at.asc())
    )

    result = await session.execute(query)
    rows = result.all()

    categories = [
        {
            "id": category.id,
            "user_id": category.user_id,
            "name": category.name,
            "color": category.color,
            "created_at": category.created_at,
            "task_count": task_count,
        }
        for category, task_count in rows
    ]

    logger.info(f"list_categories: user={user_id}, count={len(categories)}")

    return categories


async def update_category(
    session: AsyncSession, category: Category, name: str | None = None, color: str | None = None
) -> Category:
    """
    Update an existing category.

    Args:
        session: Database session
        category: Category to update
        name: Optional new name
        color: Optional new color

    Returns:
        Updated category instance

    Raises:
        ValueError: If validation fails
    """
    # Update name if provided
    if name is not None:
        # Check for duplicate name (case-sensitive)
        result = await session.execute(
            select(Category).where(
                Category.user_id == category.user_id,
                Category.name == name,
                Category.id != category.id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(f"Category '{name}' already exists for this user")

        category.name = name

    # Update color if provided
    if color is not None:
        category.color = color

    await session.commit()
    await session.refresh(category)

    logger.info(f"Category updated: category_id={category.id}, user={category.user_id}")

    return category


async def delete_category(session: AsyncSession, category: Category) -> dict[str, Any]:
    """
    Delete a category (tasks remain but lose category assignment via ON DELETE SET NULL).

    Args:
        session: Database session
        category: Category to delete

    Returns:
        Dictionary with deletion info and affected task count
    """
    # Count tasks affected (will have category_id set to NULL)
    result = await session.execute(
        select(func.count())
        .select_from(TaskPhaseIII)
        .where(TaskPhaseIII.category_id == category.id)
    )
    tasks_affected = result.scalar_one()

    category_id = category.id
    name = category.name
    user_id = category.user_id

    await session.delete(category)
    await session.commit()

    logger.info(
        f"Category deleted: user={user_id}, category_id={category_id}, tasks_affected={tasks_affected}"
    )

    return {
        "category_id": category_id,
        "name": name,
        "tasks_affected": tasks_affected,
    }


async def get_category_by_id(
    session: AsyncSession, category_id: int, user_id: str
) -> Category | None:
    """
    Get a category by ID with user validation.

    Args:
        session: Database session
        category_id: Category ID
        user_id: User ID for validation

    Returns:
        Category if found and owned by user, None otherwise
    """
    category = await session.get(Category, category_id)
    if category and category.user_id == user_id:
        return category
    return None
