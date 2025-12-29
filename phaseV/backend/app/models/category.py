from datetime import datetime

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    """
    Category model for organizing tasks into user-defined buckets.
    Examples: Work, Personal, Health, etc.
    """

    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    name: str = Field(max_length=50, nullable=False)
    color: str | None = Field(max_length=7, default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123",
                "name": "Work",
                "color": "#FF5733",
                "created_at": "2025-12-17T10:00:00Z",
            }
        }
