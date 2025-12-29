import re
from datetime import datetime

from pydantic import BaseModel, field_validator

# Hex color validation pattern
HEX_COLOR_REGEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


class CategoryCreate(BaseModel):
    """Schema for creating a new category."""

    name: str
    color: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Category name cannot be empty")
        if len(v) > 50:
            raise ValueError("Category name must be 50 characters or less")
        return v.strip()

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not HEX_COLOR_REGEX.match(v):
            raise ValueError("Color must be hex format (e.g., #FF5733)")
        return v.upper()


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: str | None = None
    color: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Category name cannot be empty")
            if len(v) > 50:
                raise ValueError("Category name must be 50 characters or less")
            return v.strip()
        return v

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not HEX_COLOR_REGEX.match(v):
            raise ValueError("Color must be hex format (e.g., #FF5733)")
        return v.upper()


class CategoryResponse(BaseModel):
    """Schema for category responses."""

    id: int
    user_id: str
    name: str
    color: str | None
    created_at: datetime


class CategoryWithCount(BaseModel):
    """Schema for category responses with task count."""

    id: int
    user_id: str
    name: str
    color: str | None
    created_at: datetime
    task_count: int
