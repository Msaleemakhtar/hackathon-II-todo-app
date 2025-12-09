"""Pydantic schemas for Tag API request/response bodies."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    """Schema for creating a new tag."""

    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(
        None,
        pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        description="Tag color in hex format (e.g., #FF5733)",
    )


class TagUpdate(BaseModel):
    """Schema for updating a tag."""

    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(
        None,
        pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        description="Tag color in hex format (e.g., #FF5733)",
    )


class TagRead(BaseModel):
    """Schema for tag response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")
    color: Optional[str] = Field(None, description="Tag color in hex format")
    user_id: str = Field(..., description="Owner user ID")
