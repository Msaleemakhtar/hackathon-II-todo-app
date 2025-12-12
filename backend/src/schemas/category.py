from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=50, description="Category name")
    type: str = Field(..., pattern="^(priority|status)$", description="Category type")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, max_length=7)


from pydantic import ConfigDict

class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: int
    user_id: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    """Schema for paginated category list."""
    items: List[CategoryResponse]
    total: int
