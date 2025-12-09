from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user properties."""

    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """User creation request."""

    password: str = Field(min_length=8, description="Minimum 8 characters")


class UserResponse(UserBase):
    """User response (excludes password)."""

    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
