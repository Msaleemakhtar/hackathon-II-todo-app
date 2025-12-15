"""API router for category management endpoints using user_id in path."""

from typing import List, Optional

from fastapi import APIRouter, Depends, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import validate_path_user_id
from src.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from src.services import category_service

router = APIRouter()


@router.get("/{user_id}/categories/metadata")
async def get_categories_metadata(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get all category metadata (priorities and statuses) in a single request.

    This endpoint combines both priority and status categories into one response
    to reduce API roundtrips. Performance optimization for dashboard loading.

    Args:
        user_id: The user ID from the path
        request: The request object (for JWT extraction)
        db: Database session

    Returns:
        Object with priorities and statuses arrays

    Example response:
        {
            "priorities": [...],
            "statuses": [...]
        }
    """
    # Validate that the user_id in the path matches the JWT user_id
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    # Fetch both priority and status categories
    priorities = await category_service.get_categories(db, current_user_id, "priority")
    statuses = await category_service.get_categories(db, current_user_id, "status")

    return {
        "priorities": priorities,
        "statuses": statuses,
    }


@router.get("/{user_id}/categories")
async def list_categories(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    type: Optional[str] = Query(None, pattern="^(priority|status)$"),
):
    """List all categories for a specific user, optionally filtered by type.

    Args:
        user_id: The user ID from the path
        request: The request object (for JWT extraction)
        db: Database session
        type: Optional filter for 'priority' or 'status'

    Returns:
        Object with items list of categories

    """
    # Validate that the user_id in the path matches the JWT user_id
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    categories = await category_service.get_categories(db, current_user_id, type)
    return {"items": categories}


@router.post(
    "/{user_id}/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    user_id: str,
    request: Request,
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new category for a specific user.

    Args:
        user_id: The user ID from the path
        request: The request object (for JWT extraction)
        category_data: Category creation data
        db: Database session

    Returns:
        Created category

    """
    # Validate that the user_id in the path matches the JWT user_id
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    category = await category_service.create_category(db, category_data, current_user_id)
    return category


@router.patch("/{user_id}/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    user_id: str,
    category_id: int,
    request: Request,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a category for a specific user.

    Args:
        user_id: The user ID from the path
        category_id: Category ID
        request: The request object (for JWT extraction)
        category_data: Category update data
        db: Database session

    Returns:
        Updated category

    """
    # Validate that the user_id in the path matches the JWT user_id
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    category = await category_service.update_category(
        db, category_id, category_data, current_user_id
    )
    return category


@router.delete(
    "/{user_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    user_id: str,
    category_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete a category for a specific user.

    Args:
        user_id: The user ID from the path
        category_id: Category ID
        request: The request object (for JWT extraction)
        db: Database session

    Returns:
        None (204 No Content)

    Raises:
        CannotDeleteDefaultCategoryException: If attempting to delete a default category
        CategoryInUseException: If category is currently in use by tasks

    """
    # Validate that the user_id in the path matches the JWT user_id
    current_user_payload = await validate_path_user_id(request, user_id, db)
    current_user_id = current_user_payload.get("sub")

    await category_service.delete_category(db, category_id, current_user_id)
