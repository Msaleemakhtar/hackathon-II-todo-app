"""WebVital model for tracking performance metrics."""
from typing import Optional
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel
from src.utils.timezone_utils import get_utc_now


class WebVitalBase(SQLModel):
    """Base model for web vitals."""

    name: str = Field(max_length=50)  # CLS, FID, FCP, LCP, TTFB
    value: float = Field(ge=0.0)
    rating: str = Field(max_length=50)  # "good", "needs-improvement", "poor"
    user_id: Optional[str] = Field(default=None, index=True)


class WebVital(WebVitalBase, table=True):
    """WebVital entity for tracking Core Web Vitals metrics."""

    __tablename__ = "web_vitals"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(
        default_factory=lambda: get_utc_now().replace(tzinfo=None),
        nullable=False,
        index=True,
    )


class WebVitalRead(WebVitalBase):
    """WebVital read schema."""

    id: int
    timestamp: datetime


class WebVitalCreate(WebVitalBase):
    """WebVital creation schema."""

    pass
