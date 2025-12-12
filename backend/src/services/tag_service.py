"""Service layer for tag management operations."""

from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import TagAlreadyExistsException, TagNotFoundException
from src.models.tag import Tag
from src.schemas.tag import TagCreate, TagUpdate, TagPartialUpdate


async def create_tag(db: AsyncSession, tag_data: TagCreate, user_id: str) -> Tag:
    """Create a new tag for the authenticated user.

    Args:
        db: Database session
        tag_data: Tag creation data
        user_id: ID of the authenticated user

    Returns:
        Created tag with user_id assigned

    Raises:
        TagAlreadyExistsException: If a tag with the same name already exists
            for this user

    """
    tag = Tag(**tag_data.model_dump(), user_id=user_id)
    db.add(tag)

    try:
        await db.commit()
        await db.refresh(tag)
    except IntegrityError:
        await db.rollback()
        raise TagAlreadyExistsException()

    return tag


async def get_tags(db: AsyncSession, user_id: str) -> List[Tag]:
    """Get all tags for the authenticated user.

    Args:
        db: Database session
        user_id: ID of the authenticated user

    Returns:
        List of tags

    """
    query = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
    result = await db.execute(query)
    tags = result.scalars().all()
    return list(tags)


async def get_tag_by_id(db: AsyncSession, tag_id: int, user_id: str) -> Tag:
    """Get a single tag by ID, enforcing data isolation.

    Args:
        db: Database session
        tag_id: Tag ID
        user_id: ID of the authenticated user

    Returns:
        Tag object

    Raises:
        TagNotFoundException: If tag not found or not owned by user

    """
    query = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
    result = await db.execute(query)
    tag = result.scalar_one_or_none()

    if not tag:
        raise TagNotFoundException()

    return tag


async def update_tag(
    db: AsyncSession, tag_id: int, tag_data: TagUpdate, user_id: str
) -> Tag:
    """Update a tag, enforcing data isolation.

    Args:
        db: Database session
        tag_id: Tag ID
        tag_data: Tag update data
        user_id: ID of the authenticated user

    Returns:
        Updated tag

    Raises:
        TagNotFoundException: If tag not found or not owned by user
        TagAlreadyExistsException: If updating to a name that already exists

    """
    tag = await get_tag_by_id(db, tag_id, user_id)

    # Update all fields
    for field, value in tag_data.model_dump().items():
        setattr(tag, field, value)

    try:
        await db.commit()
        await db.refresh(tag)
    except IntegrityError:
        await db.rollback()
        raise TagAlreadyExistsException()

    return tag


async def partial_update_tag(
    db: AsyncSession, tag_id: int, tag_data: TagPartialUpdate, user_id: str
) -> Tag:
    """Partially update a tag, enforcing data isolation.

    Args:
        db: Database session
        tag_id: Tag ID
        tag_data: Partial tag update data
        user_id: ID of the authenticated user

    Returns:
        Updated tag

    Raises:
        TagNotFoundException: If tag not found or not owned by user
        TagAlreadyExistsException: If updating to a name that already exists

    """
    tag = await get_tag_by_id(db, tag_id, user_id)

    # Update only provided fields
    update_data = tag_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    try:
        await db.commit()
        await db.refresh(tag)
    except IntegrityError:
        await db.rollback()
        raise TagAlreadyExistsException()

    return tag


async def delete_tag(db: AsyncSession, tag_id: int, user_id: str) -> None:
    """Delete a tag, enforcing data isolation.

    Args:
        db: Database session
        tag_id: Tag ID
        user_id: ID of the authenticated user

    Raises:
        TagNotFoundException: If tag not found or not owned by user

    """
    tag = await get_tag_by_id(db, tag_id, user_id)
    await db.delete(tag)
    await db.commit()
