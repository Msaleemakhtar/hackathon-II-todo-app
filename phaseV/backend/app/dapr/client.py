"""
Dapr HTTP client wrapper for pub/sub, state management, and jobs API.
"""
import httpx
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DaprClient:
    def __init__(self, dapr_http_port: int = 3500):
        self.base_url = f"http://localhost:{dapr_http_port}"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
        raw_payload: bool = True,
        message_key: Optional[str] = None
    ) -> None:
        """
        Publish event to Dapr Pub/Sub.

        Args:
            pubsub_name: Name of the pub/sub component (e.g., "pubsub")
            topic: Topic name to publish to
            data: Event data to publish
            metadata: Optional metadata for the message
            raw_payload: If True, publish raw JSON without CloudEvents wrapping (default: True)
            message_key: Optional Kafka message key for partitioning
        """
        url = f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic}"

        # Build headers
        headers = {"Content-Type": "application/json"}

        # Add rawPayload header to bypass CloudEvents wrapping
        if raw_payload:
            headers["rawPayload"] = "true"

        # Build query parameters for Kafka metadata
        # Dapr Kafka pub/sub requires partition key as query parameter, not header
        # See: https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/
        params = {}
        if message_key:
            params["metadata.partitionKey"] = message_key

        try:
            response = await self.client.post(
                url,
                json=data,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            logger.info(f"Published event to {topic}: {data.get('event_type', 'unknown')}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            raise

    async def save_state(
        self,
        store_name: str,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Save state to Dapr State Store"""
        url = f"{self.base_url}/v1.0/state/{store_name}"
        state_entry = {"key": key, "value": value}
        if metadata:
            state_entry["metadata"] = metadata

        try:
            response = await self.client.post(url, json=[state_entry])
            response.raise_for_status()
            logger.debug(f"Saved state: {key}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to save state {key}: {e}")
            raise

    async def get_state(
        self,
        store_name: str,
        key: str
    ) -> Optional[Any]:
        """Get state from Dapr State Store"""
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"
        try:
            response = await self.client.get(url)
            if response.status_code == 204:
                return None  # Key not found
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get state {key}: {e}")
            raise

    async def delete_state(
        self,
        store_name: str,
        key: str
    ) -> None:
        """Delete state from Dapr State Store"""
        url = f"{self.base_url}/v1.0/state/{store_name}/{key}"
        try:
            response = await self.client.delete(url)
            response.raise_for_status()
            logger.debug(f"Deleted state: {key}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to delete state {key}: {e}")
            raise

    async def schedule_job(
        self,
        job_name: str,
        schedule: str,
        repeats: int = -1,
        due_time: str = "0s",
        ttl: str = "3600s",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Schedule job with Dapr Jobs API (alpha)"""
        url = f"{self.base_url}/v1.0-alpha1/jobs/{job_name}"
        job_definition = {
            "schedule": schedule,
            "repeats": repeats,
            "dueTime": due_time,
            "ttl": ttl,
            "data": data or {}
        }
        try:
            response = await self.client.post(url, json=job_definition)
            response.raise_for_status()
            logger.info(f"Scheduled job: {job_name} ({schedule})")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to schedule job {job_name}: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()