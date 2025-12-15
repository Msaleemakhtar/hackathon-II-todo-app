"""AnalyticsEvent model for tracking user interactions."""
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from sqlmodel import Column, Field, SQLModel, JSON
from src.utils.timezone_utils import get_utc_now


class AnalyticsEventBase(SQLModel):
    """Base model for analytics events."""

    event_name: str = Field(min_length=1, max_length=100, index=True)
    properties: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    user_id: Optional[str] = Field(default=None, index=True)


class AnalyticsEvent(AnalyticsEventBase, table=True):
    """AnalyticsEvent entity for tracking user behavior and feature usage."""

    __tablename__ = "analytics_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(
        default_factory=lambda: get_utc_now().replace(tzinfo=None),
        nullable=False,
        index=True,
    )


class AnalyticsEventRead(AnalyticsEventBase):
    """AnalyticsEvent read schema."""

    id: int
    timestamp: datetime


class AnalyticsEventCreate(AnalyticsEventBase):
    """AnalyticsEvent creation schema."""

    pass
