"""Service layer for category management operations."""

from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import (
    CategoryAlreadyExistsException,
    CategoryNotFoundException,
    CannotDeleteDefaultCategoryException,
    CategoryInUseException,
)
from src.models.category import Category
from src.models.task import Task
from src.schemas.category import CategoryCreate, CategoryUpdate

# In-memory cache for category validation (significant performance improvement)
# Cache structure: {user_id: {category_type: {value: True}, expires_at: datetime}}
_category_cache: dict = {}
_CACHE_TTL_SECONDS = 300  # 5 minutes


async def create_category(
    db: AsyncSession, category_data: CategoryCreate, user_id: str
) -> Category:
    """Create a new category for the authenticated user.

    Args:
        db: Database session
        category_data: Category creation data
        user_id: ID of the authenticated user

    Returns:
        Created category with user_id assigned

    Raises:
        CategoryAlreadyExistsException: If a category with the same name and type
            already exists for this user

    """
    category = Category(**category_data.model_dump(), user_id=user_id, is_default=False)
    db.add(category)

    try:
        await db.commit()
        await db.refresh(category)
        # Invalidate cache after creating a category
        invalidate_category_cache(user_id)
    except IntegrityError:
        await db.rollback()
        raise CategoryAlreadyExistsException()

    return category


async def get_categories(
    db: AsyncSession, user_id: str, category_type: Optional[str] = None
) -> List[Category]:
    """Get all categories for the authenticated user, optionally filtered by type.

    Args:
        db: Database session
        user_id: ID of the authenticated user
        category_type: Optional filter for 'priority' or 'status'

    Returns:
        List of categories

    """
    query = select(Category).where(Category.user_id == user_id)

    if category_type:
        query = query.where(Category.type == category_type)

    query = query.order_by(Category.is_default.desc(), Category.name)

    result = await db.execute(query)
    categories = result.scalars().all()
    return list(categories)


async def get_category_by_id(
    db: AsyncSession, category_id: int, user_id: str
) -> Category:
    """Get a single category by ID, enforcing data isolation.

    Args:
        db: Database session
        category_id: Category ID
        user_id: ID of the authenticated user

    Returns:
        Category object

    Raises:
        CategoryNotFoundException: If category not found or not owned by user

    """
    query = select(Category).where(
        Category.id == category_id, Category.user_id == user_id
    )
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise CategoryNotFoundException()

    return category


async def update_category(
    db: AsyncSession, category_id: int, category_data: CategoryUpdate, user_id: str
) -> Category:
    """Update a category, enforcing data isolation.

    Args:
        db: Database session
        category_id: Category ID
        category_data: Category update data
        user_id: ID of the authenticated user

    Returns:
        Updated category

    Raises:
        CategoryNotFoundException: If category not found or not owned by user
        CategoryAlreadyExistsException: If updating to a name that already exists

    """
    category = await get_category_by_id(db, category_id, user_id)

    # Update only provided fields
    for field, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    try:
        await db.commit()
        await db.refresh(category)
        # Invalidate cache after updating a category
        invalidate_category_cache(user_id)
    except IntegrityError:
        await db.rollback()
        raise CategoryAlreadyExistsException()

    return category


async def delete_category(db: AsyncSession, category_id: int, user_id: str) -> None:
    """Delete a category, enforcing data isolation and business rules.

    Args:
        db: Database session
        category_id: Category ID
        user_id: ID of the authenticated user

    Raises:
        CategoryNotFoundException: If category not found or not owned by user
        CannotDeleteDefaultCategoryException: If attempting to delete a default category
        CategoryInUseException: If category is currently in use by tasks

    """
    category = await get_category_by_id(db, category_id, user_id)

    # Protect default categories
    if category.is_default:
        raise CannotDeleteDefaultCategoryException()

    # Check if category is in use by tasks
    if category.type == "priority":
        tasks_query = select(func.count(Task.id)).where(
            Task.user_id == user_id, Task.priority == category.name
        )
    else:  # status
        tasks_query = select(func.count(Task.id)).where(
            Task.user_id == user_id, Task.status == category.name
        )

    result = await db.execute(tasks_query)
    task_count = result.scalar()

    if task_count > 0:
        raise CategoryInUseException()

    await db.delete(category)
    await db.commit()
    # Invalidate cache after deleting a category
    invalidate_category_cache(user_id)


async def initialize_default_categories(db: AsyncSession, user_id: str) -> None:
    """Initialize default categories for a new user.

    Uses batch insert for optimal performance (single INSERT with multiple rows).

    Args:
        db: Database session
        user_id: ID of the new user

    """
    default_categories = [
        # Default priorities
        Category(name="low", type="priority", user_id=user_id, is_default=True),
        Category(name="medium", type="priority", user_id=user_id, is_default=True),
        Category(name="high", type="priority", user_id=user_id, is_default=True),
        # Default statuses
        Category(name="not_started", type="status", user_id=user_id, is_default=True),
        Category(name="pending", type="status", user_id=user_id, is_default=True),
        Category(name="in_progress", type="status", user_id=user_id, is_default=True),
        Category(name="completed", type="status", user_id=user_id, is_default=True),
    ]

    # Use add_all for batch insert - more efficient than individual adds
    db.add_all(default_categories)
    await db.commit()


async def validate_category_value(
    db: AsyncSession, user_id: str, category_type: str, value: str
) -> bool:
    """Validate that a category value exists for the user.

    Uses in-memory caching to avoid repeated DB queries for category validation.
    This provides a significant performance boost for task create/update operations.

    Args:
        db: Database session
        user_id: ID of the user
        category_type: 'priority' or 'status'
        value: The category name to validate

    Returns:
        True if valid, False otherwise

    """
    now = datetime.now()

    # Check cache first
    if user_id in _category_cache:
        user_cache = _category_cache[user_id]
        # Check if cache is still valid
        if user_cache.get('expires_at') and user_cache['expires_at'] > now:
            # Check if this specific category type and value exist in cache
            if category_type in user_cache and value in user_cache[category_type]:
                return True
            # If we have the type cached but value is not there, it's invalid
            if category_type in user_cache:
                return False

    # Cache miss or expired - fetch from DB
    query = select(Category).where(
        Category.user_id == user_id,
        Category.type == category_type,
    )
    result = await db.execute(query)
    categories = result.scalars().all()

    # Build cache for this user
    if user_id not in _category_cache:
        _category_cache[user_id] = {}

    # Cache all categories of this type
    _category_cache[user_id][category_type] = {cat.name: True for cat in categories}
    _category_cache[user_id]['expires_at'] = now + timedelta(seconds=_CACHE_TTL_SECONDS)

    # Return validation result
    return value in _category_cache[user_id][category_type]


def invalidate_category_cache(user_id: str) -> None:
    """Invalidate category cache for a specific user.

    Call this whenever categories are created, updated, or deleted.

    Args:
        user_id: ID of the user whose cache should be invalidated

    """
    if user_id in _category_cache:
        del _category_cache[user_id]
