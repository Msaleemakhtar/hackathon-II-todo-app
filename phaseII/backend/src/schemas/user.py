from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer


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

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime as ISO format with Z suffix to indicate UTC time."""
        if value is not None:
            # For naive datetimes (which we store in UTC), treat them as UTC and append 'Z'
            return value.isoformat() + "Z"
        return value
