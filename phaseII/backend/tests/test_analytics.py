"""Tests for analytics and performance metrics endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.analytics
async def test_track_web_vital(client: AsyncClient, db_session: AsyncSession):
    """Test tracking a Core Web Vital metric."""
    # Prepare web vital data (no authentication required)
    web_vital_data = {
        "metric_name": "LCP",
        "value": 1234.5,
        "rating": "good",
        "delta": 0.0,
        "metric_id": "v3-1234567890",
        "navigation_type": "navigate",
        "url": "http://testserver/dashboard",
        "user_agent": "Mozilla/5.0 Test",
        "connection_type": "4g"
    }

    # Track web vital
    response = await client.post(
        "/api/analytics/vitals",
        json=web_vital_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "metric_id" in data


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.analytics
async def test_track_invalid_web_vital_metric(client: AsyncClient, db_session: AsyncSession):
    """Test tracking a web vital with invalid metric name."""
    # Prepare invalid web vital data
    web_vital_data = {
        "metric_name": "INVALID",  # Invalid metric name
        "value": 1234.5,
        "rating": "good",
        "delta": 0.0,
        "metric_id": "v3-1234567890",
        "navigation_type": "navigate"
    }

    # Try to track invalid web vital
    response = await client.post(
        "/api/analytics/vitals",
        json=web_vital_data
    )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.analytics
async def test_track_analytics_event(client: AsyncClient, db_session: AsyncSession):
    """Test tracking a user analytics event."""
    # Prepare analytics event data
    event_data = {
        "event_name": "task_created",
        "properties": {
            "task_id": "123",
            "priority": "high",
            "source": "dashboard"
        }
    }

    # Track analytics event
    response = await client.post(
        "/api/analytics/events",
        json=event_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "event_id" in data


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.analytics
async def test_track_multiple_web_vitals(client: AsyncClient, db_session: AsyncSession):
    """Test tracking multiple Core Web Vital metrics."""
    # Track multiple metrics
    metrics = ["LCP", "FID", "CLS", "FCP", "TTFB", "INP", "TBT"]

    for metric_name in metrics:
        web_vital_data = {
            "metric_name": metric_name,
            "value": 100.0,
            "rating": "good",
            "delta": 0.0,
            "metric_id": f"v3-{metric_name}-123",
            "navigation_type": "navigate"
        }

        response = await client.post(
            "/api/analytics/vitals",
            json=web_vital_data
        )

        assert response.status_code == 201


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.analytics
async def test_web_vital_validation(client: AsyncClient, db_session: AsyncSession):
    """Test web vital validation rules."""
    # Test negative value (should fail)
    web_vital_data = {
        "metric_name": "LCP",
        "value": -100.0,  # Negative value
        "rating": "good",
        "delta": 0.0,
        "metric_id": "v3-123",
        "navigation_type": "navigate"
    }

    response = await client.post(
        "/api/analytics/vitals",
        json=web_vital_data
    )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.analytics
async def test_analytics_event_pii_validation(client: AsyncClient, db_session: AsyncSession):
    """Test that PII is not allowed in analytics events."""
    # Try to track event with PII
    event_data = {
        "event_name": "user_action",
        "properties": {
            "email": "test@example.com",  # PII not allowed
            "action": "click"
        }
    }

    response = await client.post(
        "/api/analytics/events",
        json=event_data
    )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.analytics
async def test_invalid_web_vital_rating(client: AsyncClient, db_session: AsyncSession):
    """Test tracking web vital with invalid rating."""
    web_vital_data = {
        "metric_name": "LCP",
        "value": 1234.5,
        "rating": "invalid-rating",  # Invalid rating
        "delta": 0.0,
        "metric_id": "v3-123",
        "navigation_type": "navigate"
    }

    response = await client.post(
        "/api/analytics/vitals",
        json=web_vital_data
    )

    assert response.status_code == 422
