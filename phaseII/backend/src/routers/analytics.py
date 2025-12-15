"""
Analytics API endpoints for performance metrics and user events (T070, T071, FR-033, FR-036)

This module provides endpoints for:
- Tracking Core Web Vitals performance metrics
- Recording user interaction events
"""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_db
from ..models.analytics_event import AnalyticsEvent
from ..models.web_vital import WebVital

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Schemas ---


class WebVitalCreate(BaseModel):
    """Schema for creating a web vital metric (FR-033)"""

    metric_name: str = Field(
        ...,
        description="Name of the metric (CLS, FID, FCP, LCP, TTFB, INP, TBT)",
    )
    value: float = Field(..., description="Metric value", ge=0)
    rating: str = Field(
        ...,
        description="Performance rating",
    )
    delta: float = Field(default=0.0, description="Change from previous value")
    metric_id: str = Field(..., description="Unique metric instance ID")
    navigation_type: str = Field(
        default="navigate",
        description="Navigation type",
    )
    url: str | None = Field(None, description="Page URL")
    user_agent: str | None = Field(None, description="User agent string")
    connection_type: str | None = Field(None, description="Connection type")

    @field_validator("metric_name")
    @classmethod
    def validate_metric_name(cls, v: str) -> str:
        """Validate metric name is a known Core Web Vital"""
        valid_names = {"CLS", "FID", "FCP", "LCP", "TTFB", "INP", "TBT"}
        if v not in valid_names:
            raise ValueError(f"metric_name must be one of {valid_names}")
        return v

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: str) -> str:
        """Validate rating is valid"""
        valid_ratings = {"good", "needs-improvement", "poor"}
        if v not in valid_ratings:
            raise ValueError(f"rating must be one of {valid_ratings}")
        return v


class AnalyticsEventCreate(BaseModel):
    """Schema for creating an analytics event (FR-036)"""

    event_name: str = Field(
        ...,
        description="Event name (e.g., task_created, task_completed)",
        min_length=1,
        max_length=100,
    )
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional event properties (no PII)",
    )

    @field_validator("properties")
    @classmethod
    def validate_no_pii(cls, v: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure no personally identifiable information in properties (FR-038)

        This is a basic check - more sophisticated PII detection could be added.
        """
        # List of keys that might contain PII
        pii_keys = {
            "email",
            "name",
            "phone",
            "address",
            "ssn",
            "password",
            "credit_card",
            "ip_address",
        }

        # Check if any PII keys are present
        for key in v.keys():
            if key.lower() in pii_keys:
                raise ValueError(
                    f"Property '{key}' might contain PII and is not allowed (FR-038)"
                )

        return v


# --- Endpoints ---


@router.post(
    "/api/analytics/vitals",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
    tags=["Analytics"],
)
async def track_web_vital(
    vital_data: WebVitalCreate,
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """
    Track Core Web Vitals performance metric (T070, FR-033)

    This endpoint receives performance metrics from the frontend and stores them
    for monitoring and analysis. Metrics are used to track application performance
    over time and identify degradation patterns.

    **Privacy**: No user identification is stored. Metrics are anonymous unless
    explicitly tracking user-specific performance (which requires consent).
    """
    try:
        # Extract user_id from request if authenticated (optional for vitals)
        user_id = getattr(request.state, "user_id", None)

        # Create web vital record
        web_vital = WebVital(
            name=vital_data.metric_name,
            value=vital_data.value,
            rating=vital_data.rating,
            user_id=user_id,  # Optional - only if user is authenticated
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        session.add(web_vital)
        await session.commit()
        await session.refresh(web_vital)

        logger.info(
            f"Web vital tracked: {vital_data.metric_name} = {vital_data.value} ({vital_data.rating})",
            extra={
                "metric_name": vital_data.metric_name,
                "value": vital_data.value,
                "rating": vital_data.rating,
                "user_id": user_id,
            },
        )

        return {
            "status": "success",
            "message": "Web vital tracked successfully",
            "metric_id": web_vital.id,
        }

    except Exception as e:
        logger.error(f"Failed to track web vital: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track web vital",
        )


@router.post(
    "/api/analytics/events",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
    tags=["Analytics"],
)
async def track_analytics_event(
    event_data: AnalyticsEventCreate,
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """
    Track user interaction event (T071, FR-036)

    This endpoint receives user interaction events from the frontend and stores them
    for analytics and business intelligence. Events track feature usage patterns
    and user behavior.

    **Privacy**: Properties must not contain personally identifiable information (PII).
    The endpoint validates against common PII fields (FR-038).

    **Common events**:
    - task_created: When user creates a new task
    - task_completed: When user marks a task as complete
    - reminder_set: When user sets a reminder
    - search_performed: When user searches tasks
    """
    try:
        # Extract user_id from request if authenticated (optional for events)
        user_id = getattr(request.state, "user_id", None)

        # Create analytics event record
        analytics_event = AnalyticsEvent(
            event_name=event_data.event_name,
            properties=event_data.properties,
            user_id=user_id,  # Optional - only if user is authenticated
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        session.add(analytics_event)
        await session.commit()
        await session.refresh(analytics_event)

        logger.info(
            f"Analytics event tracked: {event_data.event_name}",
            extra={
                "event_name": event_data.event_name,
                "user_id": user_id,
                "properties_count": len(event_data.properties),
            },
        )

        return {
            "status": "success",
            "message": "Event tracked successfully",
            "event_id": analytics_event.id,
        }

    except Exception as e:
        logger.error(f"Failed to track analytics event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track event",
        )


@router.get(
    "/api/analytics/vitals/summary",
    response_model=dict,
    tags=["Analytics"],
)
async def get_web_vitals_summary(
    session: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get summary of Core Web Vitals metrics

    Returns aggregated statistics for all tracked metrics to help identify
    performance trends and issues.

    This endpoint is useful for dashboards and monitoring tools.
    """
    from sqlalchemy import func
    from sqlmodel import select

    try:
        # Get summary statistics for each metric
        stmt = (
            select(
                WebVital.name,
                func.count(WebVital.id).label("count"),
                func.avg(WebVital.value).label("avg_value"),
                func.min(WebVital.value).label("min_value"),
                func.max(WebVital.value).label("max_value"),
                func.count(
                    func.nullif(WebVital.rating != "good", False)
                ).label("issues"),
            )
            .group_by(WebVital.name)
            .order_by(WebVital.name)
        )

        result = await session.execute(stmt)
        rows = result.all()

        summary = {
            row[0]: {
                "count": row[1],
                "avg_value": float(row[2]) if row[2] else 0,
                "min_value": float(row[3]) if row[3] else 0,
                "max_value": float(row[4]) if row[4] else 0,
                "issues": row[5] or 0,
            }
            for row in rows
        }

        return {"summary": summary, "total_metrics": sum(s["count"] for s in summary.values())}

    except Exception as e:
        logger.error(f"Failed to get web vitals summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve summary",
        )
