from datetime import datetime

from sqlmodel import Field, SQLModel


class TagPhaseV(SQLModel, table=True):
    """
    Tag model for flexible cross-categorical organization.
    Examples: #urgent, #meeting, #client-facing, etc.
    """

    __tablename__ = "tags_phasev"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    name: str = Field(max_length=30, nullable=False)
    color: str | None = Field(max_length=7, default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123",
                "name": "urgent",
                "color": "#FF0000",
                "created_at": "2025-12-17T10:00:00Z",
            }
        }
