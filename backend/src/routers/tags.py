"""API router for tag management endpoints using user_id in path."""

from typing import List

from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import validate_path_user_id
from src.models.user import User
from src.schemas.tag import TagCreate, TagRead, TagUpdate, TagPartialUpdate
from src.services import tag_service

router = APIRouter()


@router.get("/{user_id}/tags", response_model=List[TagRead])
async def list_tags(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """List all tags for a specific user.

    **User Story 8 (P2)**: An authenticated user views their list of tags.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    tags = await tag_service.get_tags(db, current_user_id)
    return tags


@router.get("/{user_id}/tags/{tag_id}", response_model=TagRead)
async def get_tag(
    user_id: str,
    tag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get a single tag by ID for a specific user.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    tag = await tag_service.get_tag_by_id(db, tag_id, current_user_id)
    return tag


@router.post("/{user_id}/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    user_id: str,
    request: Request,
    tag_data: TagCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new tag for a specific user.

    **User Story 7 (P2)**: An authenticated user creates a tag.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    tag = await tag_service.create_tag(db, tag_data, current_user_id)
    return tag


@router.put("/{user_id}/tags/{tag_id}", response_model=TagRead)
async def update_tag(
    user_id: str,
    tag_id: int,
    request: Request,
    tag_data: TagUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a tag for a specific user.

    **User Story 9 (P2)**: An authenticated user updates a tag.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    tag = await tag_service.update_tag(db, tag_id, tag_data, current_user_id)
    return tag


@router.patch("/{user_id}/tags/{tag_id}", response_model=TagRead)
async def partial_update_tag(
    user_id: str,
    tag_id: int,
    request: Request,
    tag_data: TagPartialUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partially update a tag for a specific user.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    tag = await tag_service.partial_update_tag(db, tag_id, tag_data, current_user_id)
    return tag


@router.delete("/{user_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    user_id: str,
    tag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete a tag for a specific user.

    **User Story 10 (P2)**: An authenticated user deletes a tag.

    """
    # Validate that the user_id in the path matches the JWT user_id and get authenticated user details
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    await tag_service.delete_tag(db, tag_id, current_user_id)
