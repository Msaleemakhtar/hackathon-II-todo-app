"""API router for tag management endpoints."""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.user import User
from src.schemas.tag import TagCreate, TagRead, TagUpdate
from src.services import tag_service

router = APIRouter()


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tag.

    **User Story 7 (P2)**: An authenticated user creates a tag.

    """
    tag = await tag_service.create_tag(db, tag_data, current_user.id)
    return tag


@router.get("/", response_model=List[TagRead])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tags for the authenticated user.

    **User Story 8 (P2)**: An authenticated user views their list of tags.

    """
    tags = await tag_service.get_tags(db, current_user.id)
    return tags


@router.put("/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a tag.

    **User Story 9 (P2)**: An authenticated user updates a tag.

    """
    tag = await tag_service.update_tag(db, tag_id, tag_data, current_user.id)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a tag.

    **User Story 10 (P2)**: An authenticated user deletes a tag.

    """
    await tag_service.delete_tag(db, tag_id, current_user.id)
